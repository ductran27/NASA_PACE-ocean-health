"""
Ocean Health Analyzer Module
Analyzes ocean health from PACE ocean color measurements
"""

import pandas as pd
import numpy as np
from scipy import stats
import json
from pathlib import Path


class OceanHealthAnalyzer:
    """Analyze ocean health from PACE measurements"""
    
    def __init__(self, config):
        """Initialize analyzer with configuration"""
        self.config = config
        self.results_dir = Path('results')
        self.results_dir.mkdir(exist_ok=True)
        
        # Thresholds
        self.bloom_threshold = config.get('bloom_threshold_mg_m3', 10)
        self.quality_threshold = config.get('quality_threshold', 0.6)
    
    def analyze(self, df):
        """
        Perform comprehensive ocean health analysis
        
        Args:
            df: pandas.DataFrame with PACE measurements
        
        Returns:
            dict: Analysis results
        """
        results = {}
        
        # Filter good quality data
        good_data = df[df['quality_flag'] == 'good'].copy()
        
        # Basic statistics
        results['total_pixels'] = len(df)
        results['good_quality_pixels'] = len(good_data)
        results['mean_chlorophyll'] = float(good_data['chlorophyll_a_mg_m3'].mean())
        results['median_chlorophyll'] = float(good_data['chlorophyll_a_mg_m3'].median())
        results['std_chlorophyll'] = float(good_data['chlorophyll_a_mg_m3'].std())
        results['min_chlorophyll'] = float(good_data['chlorophyll_a_mg_m3'].min())
        results['max_chlorophyll'] = float(good_data['chlorophyll_a_mg_m3'].max())
        
        # Temperature statistics
        results['mean_sst'] = float(good_data['sst_celsius'].mean())
        results['sst_range'] = [float(good_data['sst_celsius'].min()), 
                               float(good_data['sst_celsius'].max())]
        
        # Bloom detection
        results['bloom_count'] = int(good_data['is_harmful_bloom'].sum())
        results['bloom_percentage'] = float(good_data['is_harmful_bloom'].mean() * 100)
        results['bloom_locations'] = self._identify_bloom_zones(good_data)
        
        # Productivity classification
        results['productivity_distribution'] = good_data['productivity_level'].value_counts().to_dict()
        
        # Regional statistics
        results['regional_stats'] = self._analyze_by_region(good_data)
        
        # Ocean health assessment
        results['ocean_health_status'] = self._assess_ocean_health(good_data, results)
        
        # Spatial extent
        results['spatial_extent'] = {
            'lon_range': [float(good_data['longitude'].min()), float(good_data['longitude'].max())],
            'lat_range': [float(good_data['latitude'].min()), float(good_data['latitude'].max())]
        }
        
        # Summary
        results['summary'] = self._generate_summary(results)
        
        # Metadata
        results['analysis_date'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return results
    
    def _identify_bloom_zones(self, df):
        """Identify regions with harmful algal blooms"""
        bloom_data = df[df['is_harmful_bloom'] == True]
        
        if len(bloom_data) == 0:
            return []
        
        zones = bloom_data.groupby('region_name').size().to_dict()
        
        bloom_zones = [{'region': region, 'bloom_pixels': int(count)} 
                      for region, count in zones.items()]
        
        return bloom_zones
    
    def _analyze_by_region(self, df):
        """Analyze statistics by ocean region"""
        regional_stats = {}
        
        for region in df['region_name'].unique():
            region_data = df[df['region_name'] == region]
            regional_stats[region] = {
                'mean_chlorophyll': float(region_data['chlorophyll_a_mg_m3'].mean()),
                'mean_sst': float(region_data['sst_celsius'].mean()),
                'pixel_count': int(len(region_data)),
                'bloom_pixels': int(region_data['is_harmful_bloom'].sum())
            }
        
        return regional_stats
    
    def _assess_ocean_health(self, df, results):
        """Assess overall ocean health status"""
        bloom_pct = results['bloom_percentage']
        mean_chl = results['mean_chlorophyll']
        
        if bloom_pct > 10:
            return 'ALERT - High harmful bloom activity'
        elif bloom_pct > 5:
            return 'WARNING - Elevated bloom risk'
        elif mean_chl > 5:
            return 'HIGH PRODUCTIVITY - Healthy phytoplankton activity'
        elif mean_chl > 1:
            return 'NORMAL - Moderate productivity'
        else:
            return 'LOW PRODUCTIVITY - Oligotrophic conditions'
    
    def _generate_summary(self, results):
        """Generate human-readable summary"""
        status = results['ocean_health_status'].split(' - ')[0]
        chl = results['mean_chlorophyll']
        blooms = results['bloom_count']
        
        summary = f"{status}: Chl-a {chl:.2f} mg/m³"
        if blooms > 0:
            summary += f", {blooms} bloom pixels detected"
        
        return summary
    
    def save_results(self, results, filepath):
        """Save analysis results to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

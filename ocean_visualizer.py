"""
Ocean Visualizer Module
Creates visualizations for PACE ocean color data
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
import cartopy.crs as ccrs
import cartopy.feature as cfeature


class OceanVisualizer:
    """Create visualizations for ocean color data"""
    
    def __init__(self, config):
        """Initialize visualizer with configuration"""
        self.config = config
        self.plots_dir = Path('plots')
        self.plots_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def create_plots(self, df, results):
        """
        Create all visualizations
        
        Args:
            df: pandas.DataFrame with ocean color data
            results: dict with analysis results
        
        Returns:
            list: Paths to created plot files
        """
        plots = []
        
        # Filter good quality data
        good_data = df[df['quality_flag'] == 'good'].copy()
        
        # Chlorophyll concentration map
        plots.append(self._plot_chlorophyll_map(good_data, results))
        
        # Chlorophyll distribution
        plots.append(self._plot_chlorophyll_distribution(good_data, results))
        
        # Regional ocean health
        plots.append(self._plot_regional_health(good_data, results))
        
        return plots
    
    def _plot_chlorophyll_map(self, df, results):
        """Create chlorophyll concentration map"""
        fig = plt.figure(figsize=(18, 10))
        ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
        
        # Set extent to US coastal waters
        ax.set_extent([-130, -65, 15, 50], crs=ccrs.PlateCarree())
        
        # Add geographic features
        ax.add_feature(cfeature.LAND, facecolor='#D3D3D3', alpha=0.5)
        ax.add_feature(cfeature.OCEAN, facecolor='#E8F8FF')
        ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='#333333')
        ax.add_feature(cfeature.BORDERS, linewidth=0.4, edgecolor='#666666', linestyle='--', alpha=0.5)
        ax.add_feature(cfeature.STATES, linewidth=0.2, edgecolor='#888888', alpha=0.3)
        
        # Add gridlines
        gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {'size': 10}
        gl.ylabel_style = {'size': 10}
        
        # Plot chlorophyll concentrations with log scale colormap
        # Use log scale because chlorophyll varies exponentially
        scatter = ax.scatter(df['longitude'], df['latitude'], 
                           c=np.log10(df['chlorophyll_a_mg_m3'] + 0.01),  
                           s=50, cmap='YlGnBu',
                           alpha=0.7, edgecolors='darkgreen', 
                           linewidth=0.5, zorder=5, transform=ccrs.PlateCarree())
        
        # Colorbar with log scale
        cbar = plt.colorbar(scatter, ax=ax, label='Chlorophyll-a (mg/m³, log scale)', 
                           fraction=0.025, pad=0.02, shrink=0.7)
        
        # Add actual values to colorbar labels
        cbar_ticks = cbar.get_ticks()
        cbar.ax.set_yticklabels([f'{10**t:.2f}' for t in cbar_ticks])
        cbar.ax.tick_params(labelsize=9)
        
        # Highlight bloom locations
        bloom_pixels = df[df['is_harmful_bloom'] == True]
        if len(bloom_pixels) > 0:
            ax.scatter(bloom_pixels['longitude'], bloom_pixels['latitude'],
                      s=120, facecolors='none', edgecolors='red', 
                      linewidth=2.5, zorder=6, transform=ccrs.PlateCarree(),
                      label='Harmful Bloom Alert')
            ax.legend(loc='upper left', fontsize=11, framealpha=0.95)
        
        # Title
        ax.set_title('NASA PACE Ocean Color Monitoring\nChlorophyll-a Concentration Map', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Add info box
        status = results['ocean_health_status'].split(' - ')[0]
        info_text = f"Status: {status}\n"
        info_text += f"Mean Chl-a: {results['mean_chlorophyll']:.2f} mg/m³\n"
        info_text += f"Bloom Pixels: {results['bloom_count']}\n"
        info_text += f"Total Pixels: {results['good_quality_pixels']}"
        
        ax.text(0.02, 0.02, info_text, transform=ax.transAxes, 
                fontsize=11, verticalalignment='bottom',
                bbox=dict(boxstyle='round,pad=0.8', facecolor='white', 
                         edgecolor='darkgreen', alpha=0.95, linewidth=2))
        
        plt.tight_layout()
        
        # Save
        timestamp = pd.Timestamp.now().strftime('%Y%m%d')
        filepath = self.plots_dir / f'chlorophyll_map_{timestamp}.png'
        plt.savefig(filepath, dpi=200, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return filepath
    
    def _plot_chlorophyll_distribution(self, df, results):
        """Create chlorophyll distribution plots"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogram with log scale
        ax1.hist(np.log10(df['chlorophyll_a_mg_m3'] + 0.01), bins=25, 
                edgecolor='black', alpha=0.7, color='seagreen')
        ax1.axvline(np.log10(results['mean_chlorophyll']), color='red', 
                   linestyle='--', linewidth=2, 
                   label=f"Mean: {results['mean_chlorophyll']:.2f} mg/m³")
        ax1.set_xlabel('Chlorophyll-a (mg/m³, log scale)', fontsize=11)
        ax1.set_ylabel('Frequency', fontsize=11)
        ax1.set_title('Chlorophyll Distribution', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Convert x-axis to actual values
        xticks = ax1.get_xticks()
        ax1.set_xticklabels([f'{10**t:.2f}' for t in xticks], rotation=45, ha='right')
        
        # Chlorophyll vs Temperature scatter
        ax2.scatter(df['sst_celsius'], df['chlorophyll_a_mg_m3'], 
                   alpha=0.6, s=50, c=df['chlorophyll_a_mg_m3'],
                   cmap='YlGnBu', edgecolors='black', linewidth=0.5)
        ax2.set_xlabel('Sea Surface Temperature (°C)', fontsize=11)
        ax2.set_ylabel('Chlorophyll-a (mg/m³)', fontsize=11)
        ax2.set_title('SST vs Chlorophyll Relationship', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_yscale('log')
        
        plt.tight_layout()
        
        # Save
        timestamp = pd.Timestamp.now().strftime('%Y%m%d')
        filepath = self.plots_dir / f'chlorophyll_dist_{timestamp}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _plot_regional_health(self, df, results):
        """Create regional ocean health comparison"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Regional chlorophyll comparison
        regional_data = results['regional_stats']
        regions = list(regional_data.keys())
        chl_values = [regional_data[r]['mean_chlorophyll'] for r in regions]
        bloom_counts = [regional_data[r]['bloom_pixels'] for r in regions]
        
        # Bar chart with dual y-axis
        ax1_twin = ax1.twinx()
        bars1 = ax1.bar(np.arange(len(regions)), chl_values, alpha=0.7, 
                       color='seagreen', edgecolor='black', label='Chlorophyll-a')
        bars2 = ax1_twin.bar(np.arange(len(regions)) + 0.3, bloom_counts, 
                            width=0.3, alpha=0.7, color='red', 
                            edgecolor='black', label='Bloom Pixels')
        
        ax1.set_xlabel('Ocean Region', fontsize=11)
        ax1.set_ylabel('Chlorophyll-a (mg/m³)', fontsize=11, color='seagreen')
        ax1_twin.set_ylabel('Bloom Pixels', fontsize=11, color='red')
        ax1.set_title('Regional Ocean Health Comparison', fontsize=12, fontweight='bold')
        ax1.set_xticks(np.arange(len(regions)))
        ax1.set_xticklabels(regions, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.tick_params(axis='y', labelcolor='seagreen')
        ax1_twin.tick_params(axis='y', labelcolor='red')
        
        # Productivity pie chart
        productivity = results['productivity_distribution']
        colors_prod = {'high': 'darkgreen', 'medium': 'gold', 'low': 'lightblue'}
        pie_colors = [colors_prod.get(k, 'gray') for k in productivity.keys()]
        
        ax2.pie(productivity.values(), labels=productivity.keys(), autopct='%1.1f%%',
               colors=pie_colors, startangle=90, textprops={'fontsize': 11})
        ax2.set_title('Ocean Productivity Levels', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        # Save
        timestamp = pd.Timestamp.now().strftime('%Y%m%d')
        filepath = self.plots_dir / f'regional_health_{timestamp}.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath

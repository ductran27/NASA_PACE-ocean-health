#!/usr/bin/env python3
"""
NASA PACE Ocean Color Monitoring System
Processes ocean color data to monitor phytoplankton and water quality
"""

import os
import sys
from datetime import datetime
import yaml
from pathlib import Path

from pace_processor import PACEProcessor
from ocean_analyzer import OceanHealthAnalyzer
from ocean_visualizer import OceanVisualizer


def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """Main execution function"""
    print(f"=== NASA PACE Ocean Monitoring System ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load configuration
        config = load_config()
        print(f"Configuration loaded")
        
        # Initialize modules
        processor = PACEProcessor(config['data_sources'])
        analyzer = OceanHealthAnalyzer(config['analysis'])
        visualizer = OceanVisualizer(config['visualization'])
        print(f"Modules initialized")
        
        # Process PACE ocean color data
        print(f"\nProcessing PACE ocean color data...")
        data = processor.process_latest_data()
        if data is None or len(data) == 0:
            print("No new ocean color data available. Waiting for next overpass.")
            return
        print(f"Data processed: {len(data)} ocean pixels")
        
        # Analyze ocean health
        print(f"\nAnalyzing ocean health...")
        results = analyzer.analyze(data)
        print(f"Analysis complete")
        print(f"  - Mean chlorophyll: {results['mean_chlorophyll']:.3f} mg/m³")
        print(f"  - Bloom events: {results['bloom_count']}")
        print(f"  - Ocean health: {results['ocean_health_status']}")
        
        # Generate visualizations
        print(f"\nGenerating visualizations...")
        plots = visualizer.create_plots(data, results)
        print(f"Visualizations created: {len(plots)} plots")
        
        # Save results
        print(f"\nSaving results...")
        result_file = Path('results') / f"ocean_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        result_file.parent.mkdir(exist_ok=True)
        analyzer.save_results(results, result_file)
        print(f"Results saved to {result_file}")
        
        print(f"\n=== Analysis Complete ===")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

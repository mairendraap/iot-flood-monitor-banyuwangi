import os
import sys
import traceback
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))
sys.path.append(str(Path(__file__).parent / 'utils'))

try:
    from data_generator import FloodDataGenerator
    from data_sampler import FloodDataSampler
    from data_analyzer import FloodDataAnalyzer
    from data_visualizer import FloodDataVisualizer
    from helpers import create_directories
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure all required files are in the correct directories")
    sys.exit(1)

def main():
    try:
        print("🚀 Starting IoT Flood Monitoring Banyuwangi Pipeline...")
        print("=" * 60)
        
        # 1. Create directory structure
        print("📁 Creating directory structure...")
        create_directories()
        
        # 2. Generate dataset
        print("\n📊 Generating hydrological data...")
        generator = FloodDataGenerator(seed=42)
        main_data = generator.generate_hydrological_data(days=90)
        
        # 3. Save main dataset
        main_data_path = 'data/raw/iot_floodmonitor_banyuwangi_hydrological_2024_v1.0.csv'
        main_data.to_csv(main_data_path, index=False)
        print(f"💾 Main dataset saved: {main_data_path}")
        print(f"   📈 Records: {len(main_data):,}")
        print(f"   🌊 Rivers: {main_data['river_name'].nunique()}")
        print(f"   📅 Period: {main_data['timestamp'].min().strftime('%Y-%m-%d')} to {main_data['timestamp'].max().strftime('%Y-%m-%d')}")
        
        # 4. Data Sampling
        print("\n🔍 Performing data sampling...")
        sampler = FloodDataSampler(main_data)
        
        # Generate individual samples
        samples_info = {
            'systematic': sampler.systematic_sampling(),
            'stratified': sampler.stratified_sampling(),
            'random': sampler.random_sampling(),
            'temporal_daily': sampler.temporal_sampling(frequency='D'),
            'flood_events': sampler.flood_event_sampling()
        }
        
        # Save samples
        for sample_name, sample_data in samples_info.items():
            if not sample_data.empty:
                filename = f"data/samples/sampling_{sample_name}.csv"
                sample_data.to_csv(filename, index=False)
                print(f"   💾 {sample_name}: {len(sample_data):,} records")
        
        # River-specific samples
        print("\n🌊 Generating river-specific samples...")
        for river in main_data['river_name'].unique():
            river_sample = sampler.river_specific_sampling(river)
            if not river_sample.empty:
                river_filename = f"data/samples/sampling_river_{river.replace(' ', '_')}.csv"
                river_sample.to_csv(river_filename, index=False)
                print(f"   💾 {river}: {len(river_sample):,} records")
        
        # 5. Data Analysis
        print("\n📈 Analyzing data...")
        analyzer = FloodDataAnalyzer(main_data)
        analysis_results = analyzer.generate_comprehensive_report()
        
        # 6. Data Visualization
        print("\n🎨 Generating visualizations...")
        visualizer = FloodDataVisualizer(main_data)
        
        # Create plots directory
        plots_dir = 'outputs/plots/'
        os.makedirs(plots_dir, exist_ok=True)
        
        # Generate plots dengan error handling
        plots_to_create = [
            ('water_level_timeseries', visualizer.plot_water_level_timeseries),
            ('flood_events_distribution', visualizer.plot_flood_events_distribution),
            ('correlation_heatmap', visualizer.plot_correlation_heatmap),
            ('river_comparison', visualizer.plot_river_comparison),
            ('temporal_patterns', visualizer.plot_temporal_patterns)
        ]
        
        plots_created = 0
        for plot_name, plot_function in plots_to_create:
            try:
                plot_function(save_path=f"{plots_dir}{plot_name}.png")
                plots_created += 1
                print(f"   ✅ {plot_name}.png")
            except Exception as e:
                print(f"   ❌ {plot_name}: {e}")
        
        print(f"\n✅ Pipeline completed successfully!")
        print("=" * 60)
        print("📁 Generated Files Summary:")
        print(f"   📊 Main dataset: data/raw/ (1 file)")
        print(f"   🔍 Samples: data/samples/ ({len(samples_info) + main_data['river_name'].nunique()} files)")
        print(f"   🎨 Visualizations: outputs/plots/ ({plots_created}/5 plots)")
        print(f"   📈 Analysis: Comprehensive report generated")
        
    except Exception as e:
        print(f"❌ Pipeline failed with error: {e}")
        print("🔧 Debug info:")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
import os
import sys
import traceback
from pathlib import Path
import pandas as pd

# Add the parent directory to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir / 'src'))
sys.path.append(str(current_dir / 'utils'))

# Import dengan error handling yang lebih baik
try:
    from src.data_sampler import FloodDataSampler
    from src.data_analyzer import FloodDataAnalyzer
    from src.data_visualizer import FloodDataVisualizer
    from utils.helpers import create_directories
    print(" All imports successful")
except ImportError as e:
    print(f" Import error: {e}")
    print(" Trying alternative import method...")
    
    # Coba import langsung
    try:
        from data_sampler import FloodDataSampler
        from data_analyzer import FloodDataAnalyzer
        from data_visualizer import FloodDataVisualizer
        from helpers import create_directories
        print(" Alternative imports successful")
    except ImportError as e2:
        print(f" Alternative import also failed: {e2}")
        print(" Current directory structure:")
        for root, dirs, files in os.walk('.'):
            level = root.replace('.', '').count(os.sep)
            indent = ' ' * 2 * level
            print(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                if file.endswith('.py'):
                    print(f'{subindent}{file}')
        sys.exit(1)

def load_existing_data(csv_file_path):
    """Load existing CSV data dengan handling error"""
    try:
        print(f" Loading data from: {csv_file_path}")
        
        # Load data
        main_data = pd.read_csv(csv_file_path)
        
        # Convert timestamp to datetime
        if 'timestamp' in main_data.columns:
            main_data['timestamp'] = pd.to_datetime(main_data['timestamp'])
        
        print(f" Data loaded successfully!")
        print(f"    Records: {len(main_data):,}")
        print(f"    Rivers: {main_data['river_name'].nunique() if 'river_name' in main_data.columns else 'N/A'}")
        
        if 'timestamp' in main_data.columns:
            print(f"    Period: {main_data['timestamp'].min().strftime('%Y-%m-%d')} to {main_data['timestamp'].max().strftime('%Y-%m-%d')}")
        
        # Show column info
        print(f"    Columns: {list(main_data.columns)}")
        
        return main_data
        
    except FileNotFoundError:
        print(f" File not found: {csv_file_path}")
        print(" Please make sure the CSV file exists in the specified path")
        return None
    except Exception as e:
        print(f" Error loading data: {e}")
        return None

def main():
    try:
        print(" Starting IoT Flood Monitoring Banyuwangi Pipeline...")
        print("=" * 60)
        
        # 1. Create directory structure
        print(" Creating directory structure...")
        create_directories()
        
        # 2. Load existing dataset
        csv_file_path = 'data/raw/iot_floodmonitor_banyuwangi_hydrological_2024_v1.0.csv'
        
        # Check if file exists
        if not os.path.exists(csv_file_path):
            print(f" CSV file not found: {csv_file_path}")
            print(" Please provide the path to your existing CSV file")
            
            # Try to find any CSV file in data directory
            data_files = []
            for root, dirs, files in os.walk('data'):
                for file in files:
                    if file.endswith('.csv'):
                        data_files.append(os.path.join(root, file))
            
            if data_files:
                print(" Found these CSV files:")
                for i, file_path in enumerate(data_files, 1):
                    print(f"   {i}. {file_path}")
                
                # Use the first found CSV file
                if len(data_files) == 1:
                    csv_file_path = data_files[0]
                    print(f" Using: {csv_file_path}")
                else:
                    # For multiple files, you could implement selection logic here
                    csv_file_path = data_files[0]
                    print(f" Using first file: {csv_file_path}")
            else:
                print(" No CSV files found in data directory")
                return 1
        
        main_data = load_existing_data(csv_file_path)
        if main_data is None:
            return 1
        
        # 3. Data Sampling
        print("\n Performing data sampling...")
        sampler = FloodDataSampler(main_data)
        
        # Generate individual samples
        samples_info = {
            'systematic': sampler.systematic_sampling(),
            'stratified': sampler.stratified_sampling(),
            'random': sampler.random_sampling(sample_size=1000),
            'temporal_daily': sampler.temporal_sampling(frequency='D'),
            'flood_events': sampler.flood_event_sampling()
        }
        
        # Save samples
        samples_created = 0
        for sample_name, sample_data in samples_info.items():
            if not sample_data.empty:
                filename = f"data/samples/sampling_{sample_name}.csv"
                sample_data.to_csv(filename, index=False)
                samples_created += 1
                print(f"    {sample_name}: {len(sample_data):,} records") 
        
        # River-specific samples
        print("\n Generating river-specific samples...")
        river_samples_created = 0
        if 'river_name' in main_data.columns:
            for river in main_data['river_name'].unique():
                river_sample = sampler.river_specific_sampling(river)
                if not river_sample.empty:
                    # Clean river name for filename
                    clean_river_name = river.replace(' ', '_').replace('-', '_')
                    river_filename = f"data/samples/sampling_river_{clean_river_name}.csv"
                    river_sample.to_csv(river_filename, index=False)
                    river_samples_created += 1
                    print(f"    {river}: {len(river_sample):,} records")
        else:
            print("    No 'river_name' column found for river-specific sampling")
        
        # 4. Data Analysis
        print("\n Analyzing data...")
        analyzer = FloodDataAnalyzer(main_data)
        analysis_results = analyzer.generate_comprehensive_report()
        
        # Print some key insights
        if 'flood_analysis' in analysis_results:
            flood_analysis = analysis_results['flood_analysis']
            print(f"    Total flood events: {flood_analysis.get('total_flood_events', 0):,}")
        
        if 'basic_stats' in analysis_results:
            water_stats = analysis_results['basic_stats'].get('water_level_cm', {})
            print(f"    Average water level: {water_stats.get('mean', 0):.1f} cm")
        
        # 5. Data Visualization
        print("\n Generating visualizations...")
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
                result = plot_function(save_path=f"{plots_dir}{plot_name}.png")
                if result is not None:  # Only count if plot was actually created
                    plots_created += 1
                    print(f"    {plot_name}.png")
                else:
                    print(f"    {plot_name}: Plot function returned None")
            except Exception as e:
                print(f"    {plot_name}: {str(e)[:100]}...")
        
        print(f"\n Pipeline completed successfully!")
        print("=" * 60)
        print(" Generated Files Summary:")
        print(f"   Source data: {csv_file_path}")
        print(f"   Samples: data/samples/ ({samples_created + river_samples_created} files)")
        print(f"   Visualizations: outputs/plots/ ({plots_created}/5 plots)")
        print(f"   Analysis: Comprehensive report generated in memory")
        
        return 0
        
    except Exception as e:
        print(f" Pipeline failed with error: {e}")
        print(" Debug info:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
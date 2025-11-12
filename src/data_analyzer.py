import pandas as pd
import numpy as np
from scipy import stats
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from config import DATASET_CONFIG
from helpers import detect_flood_events, calculate_flood_duration

class FloodDataAnalyzer:
    def __init__(self, data):
        self.data = data.copy()
        self.analysis_results = {}
    
    def basic_statistics(self):
        """Calculate basic statistics for numerical columns"""
        numerical_cols = ['sensor_distance_cm', 'water_height_cm', 'water_flow_m3s', 
                         'rainfall_mm', 'humidity_pct', 'temperature_c']
        
        # Filter hanya kolom yang ada di data
        available_cols = [col for col in numerical_cols if col in self.data.columns]
        
        if not available_cols:
            print("⚠️ No numerical columns found for analysis")
            return pd.DataFrame()
        
        stats_df = self.data[available_cols].describe()
        
        # Additional statistics
        additional_stats = {}
        for col in available_cols:
            try:
                additional_stats[f'{col}_cv'] = stats.variation(self.data[col].dropna())  # Coefficient of variation
                additional_stats[f'{col}_skew'] = stats.skew(self.data[col].dropna())
                additional_stats[f'{col}_kurtosis'] = stats.kurtosis(self.data[col].dropna())
            except Exception as e:
                print(f"⚠️ Could not calculate additional stats for {col}: {e}")
        
        if additional_stats:
            stats_df = pd.concat([stats_df, pd.DataFrame(additional_stats, index=['additional'])])
        
        self.analysis_results['basic_stats'] = stats_df
        return stats_df
    
    def flood_analysis(self):
        """Analyze flood patterns and statistics"""
        flood_data = self.data[self.data['flood_status'] == 'BANJIR']
        
        if flood_data.empty:
            print("⚠️ No flood events found for analysis")
            return {}
        
        flood_stats = {
            'total_flood_events': len(flood_data['timestamp'].dt.date.unique()),
            'total_flood_records': len(flood_data),
            'max_water_height': flood_data['water_height_cm'].max(),
            'avg_water_height_during_flood': flood_data['water_height_cm'].mean(),
            'max_water_flow': flood_data['water_flow_m3s'].max(),
            'rivers_with_floods': flood_data['river_name'].nunique(),
            'flood_prone_rivers': flood_data['river_name'].value_counts().to_dict()
        }
        
        # Flood duration analysis
        flood_durations = {}
        for river in self.data['river_name'].unique():
            river_data = self.data[self.data['river_name'] == river]
            flood_events = detect_flood_events(river_data['water_height_cm'])
            durations = calculate_flood_duration(flood_events)
            if durations:
                flood_durations[river] = {
                    'avg_duration_hours': np.mean(durations),
                    'max_duration_hours': np.max(durations),
                    'total_flood_hours': np.sum(durations)
                }
        
        flood_stats['flood_durations'] = flood_durations
        self.analysis_results['flood_analysis'] = flood_stats
        return flood_stats
    
    def temporal_analysis(self):
        """Analyze temporal patterns"""
        temporal_data = self.data.copy()
        temporal_data['hour'] = temporal_data['timestamp'].dt.hour
        temporal_data['day_of_week'] = temporal_data['timestamp'].dt.dayofweek
        temporal_data['month'] = temporal_data['timestamp'].dt.month
        
        temporal_patterns = {}
        
        # Hourly patterns
        hourly_stats = temporal_data.groupby('hour').agg({
            'water_height_cm': 'mean',
            'rainfall_mm': 'mean',
            'flood_status': lambda x: (x == 'BANJIR').mean() if 'flood_status' in temporal_data.columns else 0
        }).round(3)
        
        # Monthly patterns
        monthly_stats = temporal_data.groupby('month').agg({
            'water_height_cm': 'mean',
            'rainfall_mm': 'sum',
            'flood_status': lambda x: (x == 'BANJIR').mean() if 'flood_status' in temporal_data.columns else 0
        }).round(3)
        
        temporal_patterns['hourly'] = hourly_stats
        temporal_patterns['monthly'] = monthly_stats
        temporal_patterns['seasonal'] = self._analyze_seasonal_patterns(temporal_data)
        
        self.analysis_results['temporal_analysis'] = temporal_patterns
        return temporal_patterns
    
    def _analyze_seasonal_patterns(self, data):
        """Analyze seasonal patterns in flood data"""
        try:
            data_copy = data.copy()
            data_copy['season'] = data_copy['month'].apply(
                lambda x: 'Rainy' if x in [1, 2, 3, 10, 11, 12] else 'Dry'
            )
            
            seasonal_stats = data_copy.groupby('season').agg({
                'water_height_cm': ['mean', 'std', 'max'],
                'rainfall_mm': ['sum', 'mean'],
                'flood_status': lambda x: (x == 'BANJIR').mean() if 'flood_status' in data_copy.columns else 0,
                'river_name': 'nunique'
            }).round(3)
            
            return seasonal_stats
        except Exception as e:
            print(f"⚠️ Error in seasonal analysis: {e}")
            # Return empty DataFrame dengan struktur yang diharapkan
            return pd.DataFrame()
    
    def correlation_analysis(self):
        """Analyze correlations between variables"""
        numerical_cols = ['water_height_cm', 'water_flow_m3s', 'rainfall_mm', 
                         'humidity_pct', 'temperature_c']
        
        # Filter hanya kolom yang ada
        available_cols = [col for col in numerical_cols if col in self.data.columns]
        
        if len(available_cols) < 2:
            print("⚠️ Not enough numerical columns for correlation analysis")
            return {
                'correlation_matrix': pd.DataFrame(),
                'strong_correlations': {}
            }
        
        correlation_matrix = self.data[available_cols].corr()
        
        # Significant correlations (absolute value > 0.3)
        strong_correlations = {}
        for i, col1 in enumerate(available_cols):
            for j, col2 in enumerate(available_cols):
                if i < j and abs(correlation_matrix.loc[col1, col2]) > 0.3:
                    strong_correlations[f'{col1} vs {col2}'] = round(correlation_matrix.loc[col1, col2], 3)
        
        correlation_results = {
            'correlation_matrix': correlation_matrix,
            'strong_correlations': strong_correlations
        }
        
        self.analysis_results['correlation_analysis'] = correlation_results
        return correlation_results
    
    def river_comparison_analysis(self):
        """Compare statistics across different rivers"""
        try:
            river_stats = self.data.groupby('river_name').agg({
                'water_height_cm': ['mean', 'std', 'max', 'min'],
                'water_flow_m3s': ['mean', 'max'],
                'rainfall_mm': 'sum',
                'flood_status': lambda x: (x == 'BANJIR').sum() if 'flood_status' in self.data.columns else 0,
                'sensor_status': lambda x: (x == 'ERROR').mean() if 'sensor_status' in self.data.columns else 0
            }).round(3)
            
            # Rank rivers by flood frequency jika ada data banjir
            if 'flood_status' in self.data.columns:
                flood_frequency = self.data[self.data['flood_status'] == 'BANJIR']['river_name'].value_counts()
                river_stats['flood_frequency_rank'] = flood_frequency.rank(ascending=False)
            
            self.analysis_results['river_comparison'] = river_stats
            return river_stats
        except Exception as e:
            print(f"⚠️ Error in river comparison: {e}")
            return pd.DataFrame()
    
    def generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        print("📈 Generating Comprehensive Flood Analysis Report...")
        print("=" * 50)
        
        # Run all analyses dengan error handling
        try:
            basic_stats = self.basic_statistics()
            flood_stats = self.flood_analysis()
            temporal_stats = self.temporal_analysis()
            correlation_stats = self.correlation_analysis()
            river_stats = self.river_comparison_analysis()
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            return self.analysis_results
        
        # Print summary
        print(f"📊 Dataset Overview:")
        print(f"   Total Records: {len(self.data):,}")
        print(f"   Rivers Monitored: {self.data['river_name'].nunique()}")
        print(f"   Date Range: {self.data['timestamp'].min()} to {self.data['timestamp'].max()}")
        
        if flood_stats:
            print(f"🌊 Flood Analysis:")
            print(f"   Total Flood Events: {flood_stats.get('total_flood_events', 0)}")
            print(f"   Max Water Height: {flood_stats.get('max_water_height', 0):.1f} cm")
            print(f"   Rivers with Floods: {flood_stats.get('rivers_with_floods', 0)}")
        
        # Seasonal analysis dengan error handling
        if temporal_stats and 'seasonal' in temporal_stats and not temporal_stats['seasonal'].empty:
            seasonal_data = temporal_stats['seasonal']
            try:
                rainy_stats = seasonal_data.loc['Rainy', ('water_height_cm', 'mean')] if 'Rainy' in seasonal_data.index else 0
                dry_stats = seasonal_data.loc['Dry', ('water_height_cm', 'mean')] if 'Dry' in seasonal_data.index else 0
                print(f"⏰ Temporal Patterns:")
                print(f"   Rainy Season Avg Height: {rainy_stats:.1f} cm")
                print(f"   Dry Season Avg Height: {dry_stats:.1f} cm")
            except:
                print(f"⏰ Temporal Patterns: Available (check details)")
        
        # Correlation summary
        if correlation_stats and correlation_stats['strong_correlations']:
            print(f"🔗 Strong Correlations (>0.3):")
            for corr_name, value in list(correlation_stats['strong_correlations'].items())[:3]:
                print(f"   {corr_name}: {value}")
        
        print("=" * 50)
        return self.analysis_results
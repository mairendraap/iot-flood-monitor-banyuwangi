import pandas as pd
import numpy as np
from datetime import timedelta
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from config import SAMPLING_CONFIG

class FloodDataSampler:
    def __init__(self, data):
        self.data = data.copy()
        self.sampling_config = SAMPLING_CONFIG
    
    def systematic_sampling(self, hours=None):
        """Sampling sistematis berdasarkan jam tertentu"""
        if hours is None:
            hours = self.sampling_config['systematic_hours']
        
        sampled_data = self.data[self.data['timestamp'].dt.hour.isin(hours)]
        print(f"🔢 Systematic sampling: {len(sampled_data)} records at hours {hours}")
        return sampled_data
    
    def stratified_sampling(self, stratify_column='flood_status', samples_per_class=None):
        """Sampling stratified berdasarkan kolom tertentu"""
        if samples_per_class is None:
            samples_per_class = self.sampling_config['stratified_samples_per_class']
        
        stratified_samples = []
        
        for class_value in self.data[stratify_column].unique():
            class_data = self.data[self.data[stratify_column] == class_value]
            
            if len(class_data) >= samples_per_class:
                sampled = class_data.sample(n=samples_per_class, random_state=42)
            else:
                sampled = class_data
            
            stratified_samples.append(sampled)
            print(f"   📦 {class_value}: {len(sampled)} samples")
        
        result = pd.concat(stratified_samples)
        print(f"⚖️ Stratified sampling: {len(result)} total records")
        return result
    
    def random_sampling(self, sample_size=None):
        """Simple random sampling"""
        if sample_size is None:
            sample_size = self.sampling_config['random_sample_size']
        
        sampled_data = self.data.sample(n=min(sample_size, len(self.data)), random_state=42)
        print(f"🎲 Random sampling: {len(sampled_data)} records")
        return sampled_data
    
    def temporal_sampling(self, frequency=None, river_specific=None):
        """Sampling temporal dengan aggregasi"""
        if frequency is None:
            frequency = self.sampling_config['temporal_frequency']
        
        if river_specific:
            data = self.data[self.data['river_name'] == river_specific]
        else:
            data = self.data
        
        # Aggregate data by time frequency
        temporal_data = data.groupby([pd.Grouper(key='timestamp', freq=frequency), 'river_name']).agg({
            'water_height_cm': 'mean',
            'water_flow_m3s': 'mean',
            'rainfall_mm': 'sum',
            'flood_status': 'last',
            'flood_level': 'last',
            'temperature_c': 'mean',
            'humidity_pct': 'mean'
        }).reset_index()
        
        print(f"⏰ Temporal sampling ({frequency}): {len(temporal_data)} records")
        return temporal_data
    
    def flood_event_sampling(self, include_before_hours=6, include_after_hours=12):
        """Sampling event banjir dengan window waktu"""
        flood_events = self.data[self.data['flood_status'] == 'BANJIR']
        
        if flood_events.empty:
            print("⚠️ No flood events found for sampling")
            return pd.DataFrame()
        
        event_times = flood_events['timestamp'].unique()
        
        event_windows = []
        for event_time in event_times:
            start_window = event_time - timedelta(hours=include_before_hours)
            end_window = event_time + timedelta(hours=include_after_hours)
            
            window_data = self.data[
                (self.data['timestamp'] >= start_window) & 
                (self.data['timestamp'] <= end_window)
            ].copy()
            
            # Mark event phase
            window_data['event_phase'] = 'BEFORE'
            window_data.loc[window_data['timestamp'] == event_time, 'event_phase'] = 'PEAK'
            window_data.loc[window_data['timestamp'] > event_time, 'event_phase'] = 'AFTER'
            
            event_windows.append(window_data)
        
        result = pd.concat(event_windows) if event_windows else pd.DataFrame()
        print(f"🌊 Flood event sampling: {len(result)} records from {len(event_times)} events")
        return result
    
    def river_specific_sampling(self, river_name):
        """Sampling data untuk sungai tertentu"""
        river_data = self.data[self.data['river_name'] == river_name].copy()
        print(f"🌊 River-specific sampling ({river_name}): {len(river_data)} records")
        return river_data
    
    def generate_all_samples(self):
        """Generate all sampling methods at once"""
        samples = {}
        
        # Systematic sampling
        samples['systematic'] = self.systematic_sampling()
        
        # Stratified sampling
        samples['stratified'] = self.stratified_sampling()
        
        # Random sampling
        samples['random'] = self.random_sampling()
        
        # Temporal sampling (daily)
        samples['temporal_daily'] = self.temporal_sampling(frequency='D')
        
        # Flood events
        samples['flood_events'] = self.flood_event_sampling()
        
        # River-specific samples
        for river in self.data['river_name'].unique():
            samples[f'river_{river}'] = self.river_specific_sampling(river)
        
        return samples
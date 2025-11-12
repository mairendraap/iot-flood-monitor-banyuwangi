import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from config import DATASET_CONFIG, SENSOR_CONFIG
from helpers import calculate_water_flow, get_river_coordinates

class FloodDataGenerator:
    def __init__(self, seed=42):
        self.seed = seed
        self._set_seed()
        self.config = DATASET_CONFIG
        self.sensor_config = SENSOR_CONFIG
        
    def _set_seed(self):
        np.random.seed(self.seed)
        random.seed(self.seed)
    
    def generate_hydrological_data(self, start_date=None, days=None):
        """
        Generate dataset hydrological monitoring
        
        Parameters:
        start_date (str): Tanggal mulai
        days (int): Jumlah hari data
        
        Returns:
        pd.DataFrame: Dataset lengkap
        """
        if start_date is None:
            start_date = self.config['start_date']
        if days is None:
            days = self.config['days']
        
        rivers = self.config['rivers']
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        total_hours = days * 24
        dates = [start_dt + timedelta(hours=i) for i in range(total_hours)]
        
        data = []
        
        for river in rivers:
            print(f"📊 Generating data for {river}...")
            river_lat, river_lon = get_river_coordinates(river)
            
            for timestamp in dates:
                row = self._generate_sensor_reading(timestamp, river, river_lat, river_lon)
                data.append(row)
        
        df = pd.DataFrame(data)
        print(f"✅ Generated {len(df):,} records for {len(rivers)} rivers")
        return df
    
    def _generate_sensor_reading(self, timestamp, river, lat, lon):
        """Generate single sensor reading dengan parameter realistik"""
        # Seasonal pattern (musim hujan Jan-Mar)
        seasonal_factor = 1.3 if timestamp.month in [1, 2, 3] else 1.0
        
        # Diurnal pattern (malam lebih tinggi karena evaporasi rendah)
        diurnal_factor = 1.15 if 18 <= timestamp.hour <= 23 else 1.0
        
        # Base water level dengan variasi per sungai
        base_river_factors = {
            "Sungai_Bajulmati": 1.1,    # Sungai besar
            "Sungai_Kalibendo": 0.9,    # Sungai sedang
            "Sungai_Setail": 1.0,       # Sungai normal
            "Sungai_Sukowidi": 0.8,     # Sungai kecil
            "Sungai_Sumberagung": 1.2,  # Daerah hulu
            "Sungai_Watugede": 0.95     # Sungai normal
        }
        
        river_factor = base_river_factors.get(river, 1.0)
        base_distance = random.uniform(
            self.sensor_config['normal_range_min'], 
            self.sensor_config['normal_range_max']
        ) * river_factor
        
        # Rain events (probabilitas lebih tinggi di musim hujan)
        rain_probability = 0.08 if timestamp.month in [1, 2, 3] else 0.04
        rain_event = random.random() < rain_probability
        
        if rain_event:
            rain_intensity = random.uniform(
                self.sensor_config['rain_effect_min'], 
                self.sensor_config['rain_effect_max']
            )
            base_distance += rain_intensity * seasonal_factor * diurnal_factor
        
        # Sensor measurement dengan error
        measurement_error = random.normalvariate(0, self.sensor_config['measurement_error_std'])
        ultrasonic_distance = max(10, base_distance + measurement_error)
        
        # Calculate derived metrics
        water_height = self.config['sensor_height_cm'] - ultrasonic_distance
        water_flow = calculate_water_flow(water_height)
        
        # Determine flood status
        if water_height > self.config['flood_threshold_cm']:
            flood_status = "BANJIR"
            flood_level = "TINGGI"
        elif water_height > self.config['warning_threshold_cm']:
            flood_status = "WASPADA"
            flood_level = "SEDANG"
        else:
            flood_status = "AMAN"
            flood_level = "RENDAH"
        
        # Sensor status (occasional errors)
        sensor_status = "NORMAL" if random.random() > 0.015 else "ERROR"
        
        # Generate environmental data
        rainfall = self._generate_rainfall(timestamp, rain_event)
        humidity = self._generate_humidity(timestamp, rainfall)
        temperature = self._generate_temperature(timestamp)
        
        return {
            'timestamp': timestamp,
            'river_name': river,
            'sensor_distance_cm': round(ultrasonic_distance, 2),
            'water_height_cm': round(water_height, 2),
            'water_flow_m3s': round(water_flow, 3),
            'flood_status': flood_status,
            'flood_level': flood_level,
            'rainfall_mm': rainfall,
            'humidity_pct': humidity,
            'temperature_c': temperature,
            'sensor_status': sensor_status,
            'latitude': lat,
            'longitude': lon
        }
    
    def _generate_rainfall(self, timestamp, rain_event):
        """Generate rainfall data"""
        if rain_event:
            # Higher rainfall during rainy season
            base_rainfall = random.normalvariate(15, 8) if timestamp.month in [1, 2, 3] else random.normalvariate(10, 6)
        else:
            base_rainfall = random.normalvariate(2, 3)
        
        return round(max(0, base_rainfall), 1)
    
    def _generate_humidity(self, timestamp, rainfall):
        """Generate humidity data"""
        base_humidity = 75 + (rainfall * 0.5)  # Humidity increases with rainfall
        humidity_variation = random.uniform(-10, 5)
        return round(max(60, min(98, base_humidity + humidity_variation)), 1)
    
    def _generate_temperature(self, timestamp):
        """Generate temperature data"""
        # Daily temperature variation
        hour = timestamp.hour
        if 12 <= hour <= 15:  # Afternoon peak
            base_temp = 31
        elif 2 <= hour <= 5:  # Early morning low
            base_temp = 24
        else:
            base_temp = 28
        
        temp_variation = random.uniform(-2, 2)
        return round(base_temp + temp_variation, 1)

# Usage example
if __name__ == "__main__":
    generator = FloodDataGenerator()
    df = generator.generate_hydrological_data()
    
    # Save to CSV
    output_path = './data/raw/iot_floodmonitor_banyuwangi_hydrological_2024_v1.0.csv'
    df.to_csv(output_path, index=False)
    print(f"💾 Data saved to: {output_path}")
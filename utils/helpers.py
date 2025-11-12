import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_directories():
    """Create all necessary directories for the project"""
    directories = [
        'data/raw',
        'data/processed',
        'data/samples',
        'outputs/plots',
        'outputs/reports',
        'notebooks',
        'docs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ Created: {directory}")

def calculate_water_flow(water_height_cm, river_width_m=10, river_slope=0.01):
    """
    Calculate water flow using Manning's equation (simplified)
    """
    # Convert height to meters
    h = water_height_cm / 100
    
    # Simplified Manning's equation
    roughness_coefficient = 0.035  # Typical for natural streams
    cross_sectional_area = h * river_width_m
    hydraulic_radius = cross_sectional_area / (river_width_m + 2 * h)
    
    water_flow = (cross_sectional_area * 
                 (hydraulic_radius ** (2/3)) * 
                 (river_slope ** 0.5) / 
                 roughness_coefficient)
    
    return max(0.1, water_flow)  # Minimum flow 0.1 m³/s

def detect_flood_events(water_levels, threshold=200):
    """
    Detect flood events from water level data
    """
    flood_events = water_levels > threshold
    return flood_events

def calculate_flood_duration(flood_events):
    """
    Calculate duration of flood events
    """
    flood_durations = []
    current_duration = 0
    
    for is_flood in flood_events:
        if is_flood:
            current_duration += 1
        else:
            if current_duration > 0:
                flood_durations.append(current_duration)
                current_duration = 0
    
    return flood_durations

def format_timestamp(timestamp):
    """Format timestamp for consistent display"""
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')

def get_river_coordinates(river_name):
    """Get approximate coordinates for each river"""
    coordinates = {
        "Sungai_Bajulmati": (-8.1892, 114.3678),
        "Sungai_Kalibendo": (-8.2156, 114.3452),
        "Sungai_Setail": (-8.1987, 114.3891),
        "Sungai_Sukowidi": (-8.2345, 114.3216),
        "Sungai_Sumberagung": (-8.1763, 114.3987),
        "Sungai_Watugede": (-8.2251, 114.3562)
    }
    return coordinates.get(river_name, (-8.219094, 114.369141))
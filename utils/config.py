# Dataset Configuration
DATASET_CONFIG = {
    'start_date': '2024-01-01',
    'days': 90,
    'sampling_interval_hours': 1,
    'rivers': [
        "Sungai_Bajulmati", 
        "Sungai_Kalibendo", 
        "Sungai_Setail",
        "Sungai_Sukowidi", 
        "Sungai_Sumberagung", 
        "Sungai_Watugede"
    ],
    'sensor_height_cm': 300,
    'flood_threshold_cm': 200,
    'warning_threshold_cm': 150
}

# Sensor Configuration
SENSOR_CONFIG = {
    'normal_range_min': 50,
    'normal_range_max': 150,
    'rain_effect_min': 30,
    'rain_effect_max': 80,
    'measurement_error_std': 5
}

# File Paths
FILE_PATHS = {
    'raw_data': 'data/raw/iot_floodmonitor_banyuwangi_hydrological_2024_v1.0.csv',
    'processed_dir': 'data/processed/',
    'samples_dir': 'data/samples/',
    'outputs_dir': 'outputs/',
    'plots_dir': 'outputs/plots/',
    'reports_dir': 'outputs/reports/'
}

# Sampling Configuration
SAMPLING_CONFIG = {
    'systematic_hours': [0, 6, 12, 18],
    'stratified_samples_per_class': 300,
    'random_sample_size': 1000,
    'temporal_frequency': 'D'  # D for daily, H for hourly
}

# Visualization Configuration
VISUALIZATION_CONFIG = {
    'style': 'seaborn',
    'color_palette': 'viridis',
    'figure_size': (12, 8),
    'dpi': 300
}
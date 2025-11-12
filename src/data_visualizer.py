import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from config import VISUALIZATION_CONFIG

class FloodDataVisualizer:
    def __init__(self, data):
        self.data = data.copy()
        self.setup_plot_style()
    
    def setup_plot_style(self):
        """Setup matplotlib and seaborn style"""
        plt.style.use(VISUALIZATION_CONFIG['style'])
        sns.set_palette(VISUALIZATION_CONFIG['color_palette'])
        self.fig_size = VISUALIZATION_CONFIG['figure_size']
        self.dpi = VISUALIZATION_CONFIG['dpi']
    
    def plot_water_level_timeseries(self, river_name=None, save_path=None):
        """Plot water level time series"""
        if river_name:
            plot_data = self.data[self.data['river_name'] == river_name]
            title = f'Water Level Time Series - {river_name}'
        else:
            plot_data = self.data
            title = 'Water Level Time Series - All Rivers'
        
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        if river_name:
            ax.plot(plot_data['timestamp'], plot_data['water_height_cm'], 
                   linewidth=1, alpha=0.7)
        else:
            for river in plot_data['river_name'].unique():
                river_data = plot_data[plot_data['river_name'] == river]
                ax.plot(river_data['timestamp'], river_data['water_height_cm'], 
                       linewidth=1, alpha=0.7, label=river)
            ax.legend()
        
        # Add flood threshold line
        ax.axhline(y=200, color='red', linestyle='--', alpha=0.7, label='Flood Threshold')
        ax.axhline(y=150, color='orange', linestyle='--', alpha=0.7, label='Warning Level')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Water Height (cm)')
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        plt.show()
        return fig
    
    def plot_flood_events_distribution(self, save_path=None):
        """Plot distribution of flood events"""
        flood_data = self.data[self.data['flood_status'] == 'BANJIR']
        
        if flood_data.empty:
            print("No flood events to visualize")
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Flood events by river
        flood_by_river = flood_data['river_name'].value_counts()
        ax1.bar(flood_by_river.index, flood_by_river.values)
        ax1.set_title('Flood Events by River', fontweight='bold')
        ax1.set_xlabel('River')
        ax1.set_ylabel('Number of Flood Events')
        ax1.tick_params(axis='x', rotation=45)
        
        # Flood events by month
        flood_data['month'] = flood_data['timestamp'].dt.month
        flood_by_month = flood_data['month'].value_counts().sort_index()
        ax2.bar(flood_by_month.index, flood_by_month.values)
        ax2.set_title('Flood Events by Month', fontweight='bold')
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Number of Flood Events')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        plt.show()
        return fig
    
    def plot_correlation_heatmap(self, save_path=None):
        """Plot correlation heatmap of numerical variables"""
        numerical_cols = ['water_height_cm', 'water_flow_m3s', 'rainfall_mm', 
                         'humidity_pct', 'temperature_c']
        
        correlation_matrix = self.data[numerical_cols].corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, ax=ax)
        ax.set_title('Correlation Matrix - Flood Monitoring Variables', 
                    fontsize=14, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        plt.show()
        return fig
    
    def plot_river_comparison(self, save_path=None):
        """Compare water levels across different rivers"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Box plot of water levels by river
        sns.boxplot(data=self.data, x='river_name', y='water_height_cm', ax=ax1)
        ax1.axhline(y=200, color='red', linestyle='--', alpha=0.7, label='Flood Threshold')
        ax1.set_title('Water Level Distribution by River', fontweight='bold')
        ax1.set_xlabel('River')
        ax1.set_ylabel('Water Height (cm)')
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend()
        
        # Average water flow by river
        avg_flow = self.data.groupby('river_name')['water_flow_m3s'].mean().sort_values(ascending=False)
        ax2.bar(avg_flow.index, avg_flow.values)
        ax2.set_title('Average Water Flow by River', fontweight='bold')
        ax2.set_xlabel('River')
        ax2.set_ylabel('Average Water Flow (m³/s)')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        
        plt.show()
        return fig
    
    def plot_temporal_patterns(self, save_path=None):
        """Plot temporal patterns in the data"""
        self.data['hour'] = self.data['timestamp'].dt.hour
        self.data['month'] = self.data['timestamp'].dt.month
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Hourly pattern
        hourly_avg = self.data.groupby('hour')['water_height_cm'].mean()
        ax1.plot(hourly_avg.index, hourly_avg.values, marker='o')
        ax1.set_title('Average Water Height by Hour', fontweight='bold')
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Average Water Height (cm)')
        ax1.grid(True, alpha=0.3)
        
        # Monthly pattern
        monthly_avg = self.data.groupby('month')['water_height_cm'].mean()
        ax2.bar(monthly_avg.index, monthly_avg.values)
        ax2.set_title('Average Water Height by Month', fontweight='bold')
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Average Water Height (cm)')
        
        # Rainfall pattern
        monthly_rain = self.data.groupby('month')['rainfall_mm'].sum()
        ax3.bar(monthly_rain.index, monthly_rain.values, color='lightblue', alpha=0.7)
        ax3.set_title('Total Rainfall by Month', fontweight='bold')
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Total Rainfall (mm)')
        
        # Flood frequency by month
        flood_data = self.data[self.data['flood_status'] == 'BANJIR']
        if not flood_data.empty:
            flood_by_month = flood_data.groupby('month').size()
            ax4.bar(flood_by_month.index, flood_by_month.values, color='red', alpha=0.7)
            ax4.set
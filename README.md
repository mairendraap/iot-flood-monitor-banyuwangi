# IoT Flood Monitor Banyuwangi

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PHP](https://img.shields.io/badge/php-7.4+-purple.svg)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Real-time flood monitoring system for Banyuwangi district with web dashboard and data analysis capabilities.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)

## Project Overview

**IoT Flood Monitor Banyuwangi** is a comprehensive flood monitoring system that provides real-time data visualization and analysis for 7 major rivers in Banyuwangi district. The system combines web technologies with data science for effective disaster management.

### Key Components:
- **Web Dashboard** - Real-time monitoring interface
- **Data Processing** - Python analysis and visualization  
- **Authentication** - Secure admin access
- **Analytics** - Statistical insights and predictions

## Features

### Web Dashboard
- ** Real-time Monitoring** - Live data for 7 rivers
- ** Interactive Maps** - Leaflet.js with status markers
- ** Data Visualization** - Charts.js for analytics
- ** Admin Panel** - Device management (login required)
- ** Responsive Design** - Mobile-friendly interface

### Python Data Processing
- ** Data Generation** - Realistic sample data
- ** Statistical Analysis** - Correlation and trend analysis
- ** Visualization** - Automated plot generation
- ** Data Export** - CSV, JSON, and image outputs

## Installation

### Prerequisites
- XAMPP (Apache + PHP)
- Python 3.8+
- Modern web browser

### Quick Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/mairendraap/iot-flood-monitor-banyuwangi.git
   cd iot-flood-monitor-banyuwangi

2. **Setup Web Server**
   ```bash
   # Copy to XAMPP htdocs or use PHP built-in server
   php -S localhost:8000
   
3. **Install Python Dependencies**
   ```bash
   pip install pandas numpy matplotlib seaborn scipy
   
4. **Run Data Processing**
   ```bash
   cd python
   python main.py

5. **Access Application**
   ```bash
   Web Dashboard: http://localhost:8000/static/
   Admin Login:   http://localhost:8000/php/login/

**Project Structure**
 
      ├──  WEB DASHBOARD/
      │   ├── static/           # Frontend files
      │   └── php/             # Backend PHP
      ├──  PYTHON DATA PROCESSING/
      │   ├── main.py          # Main entry point
      │   ├── data_sampler.py  # Data generation
      │   ├── data_analyzer.py # Statistical analysis
      │   ├── data_visualizer.py # Plot creation
      │   └── outputs/         # Generated files
      └──  Documentation
          └── README.md

**Technology Stack**

**Frontend:**
HTML5 - Semantic structure
CSS3 - Responsive styling with CSS Grid/Flexbox
JavaScript ES6+ - Interactive features
Chart.js - Data visualization
Leaflet.js - Interactive maps
Font Awesome - Icons

**Backend**
PHP - Authentication and routing
Python - Data processing and analysis
Pandas - Data manipulation
Matplotlib/Seaborn - Visualization
NumPy/SciPy - Scientific computing
Data Format
JSON - Configuration and data storage
CSV - Data export
PNG/SVG - Plot outputs

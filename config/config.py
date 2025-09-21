"""
Configuration settings for the CDC Datathon 4L application
"""

import os
from datetime import datetime, timedelta

# Application Settings
APP_TITLE = "CDC Datathon 4L Dashboard"
APP_ICON = "🏥"
LAYOUT = "wide"

# Data Settings
DEFAULT_DATA_SOURCE = "Sample Data"
DATA_SOURCES = [
    "CDC Public Data",
    "Custom Dataset", 
    "Sample Data"
]

# Date Settings
DEFAULT_DATE_RANGE = (datetime.now() - timedelta(days=30), datetime.now())
MAX_DATE = datetime.now()

# Visualization Settings
DEFAULT_CHART_HEIGHT = 400
DEFAULT_CHART_WIDTH = 600
COLOR_PALETTE = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]

# Health Conditions
HEALTH_CONDITIONS = [
    'Respiratory',
    'Cardiovascular', 
    'Diabetes',
    'Mental Health',
    'Infectious Disease',
    'Cancer',
    'Neurological',
    'Others'
]

# Sample Data Settings
SAMPLE_DATA_SIZE = 1000
AGE_RANGE = (18, 85)
HEALTH_SCORE_RANGE = (1, 100)
TREATMENT_DAYS_RANGE = (1, 30)
COST_RANGE = (100, 5000)

# File Paths
DATA_DIR = "data"
PAGES_DIR = "pages"
UTILS_DIR = "utils"
CONFIG_DIR = "config"

# API Settings (if needed)
API_TIMEOUT = 30
MAX_RETRIES = 3

# Styling
CUSTOM_CSS = """
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stAlert > div {
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
"""

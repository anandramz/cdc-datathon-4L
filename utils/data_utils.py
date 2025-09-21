"""
Utility functions for data processing and manipulation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
from config.config import *

@st.cache_data
def generate_sample_healthcare_data(size=SAMPLE_DATA_SIZE):
    """
    Generate sample healthcare data for demonstration purposes
    
    Args:
        size (int): Number of records to generate
        
    Returns:
        pd.DataFrame: Sample healthcare dataset
    """
    np.random.seed(42)
    
    data = {
        'patient_id': range(1, size + 1),
        'age': np.random.randint(AGE_RANGE[0], AGE_RANGE[1], size),
        'gender': np.random.choice(['Male', 'Female', 'Other'], size, p=[0.48, 0.48, 0.04]),
        'condition': np.random.choice(HEALTH_CONDITIONS, size),
        'health_score': np.random.randint(HEALTH_SCORE_RANGE[0], HEALTH_SCORE_RANGE[1], size),
        'treatment_days': np.random.randint(TREATMENT_DAYS_RANGE[0], TREATMENT_DAYS_RANGE[1], size),
        'cost': np.random.randint(COST_RANGE[0], COST_RANGE[1], size),
        'admission_date': pd.date_range(
            start=datetime.now() - timedelta(days=365),
            end=datetime.now(),
            periods=size
        ),
        'state': np.random.choice([
            'CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI'
        ], size),
        'severity': np.random.choice(['Low', 'Medium', 'High'], size, p=[0.5, 0.3, 0.2])
    }
    
    df = pd.DataFrame(data)
    
    # Add some correlations to make data more realistic
    df.loc[df['age'] > 65, 'health_score'] = df.loc[df['age'] > 65, 'health_score'] * 0.8
    df.loc[df['severity'] == 'High', 'cost'] = df.loc[df['severity'] == 'High', 'cost'] * 1.5
    df.loc[df['condition'] == 'Cardiovascular', 'treatment_days'] = df.loc[df['condition'] == 'Cardiovascular', 'treatment_days'] * 1.2
    
    return df

def load_data(data_source, date_range=None):
    """
    Load data based on the selected data source
    
    Args:
        data_source (str): Source of the data
        date_range (tuple): Start and end dates for filtering
        
    Returns:
        pd.DataFrame: Loaded dataset
    """
    if data_source == "Sample Data":
        df = generate_sample_healthcare_data()
    elif data_source == "CDC Public Data":
        # Placeholder for actual CDC data loading
        st.warning("CDC Public Data integration not yet implemented. Using sample data.")
        df = generate_sample_healthcare_data()
    elif data_source == "Custom Dataset":
        # Placeholder for custom data loading
        st.warning("Custom Dataset loading not yet implemented. Using sample data.")
        df = generate_sample_healthcare_data()
    else:
        df = generate_sample_healthcare_data()
    
    # Filter by date range if provided
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        df = df[
            (df['admission_date'].dt.date >= start_date) & 
            (df['admission_date'].dt.date <= end_date)
        ]
    
    return df

def calculate_key_metrics(df):
    """
    Calculate key metrics from the healthcare dataset
    
    Args:
        df (pd.DataFrame): Healthcare dataset
        
    Returns:
        dict: Dictionary containing key metrics
    """
    metrics = {
        'total_records': len(df),
        'unique_patients': df['patient_id'].nunique(),
        'avg_age': df['age'].mean(),
        'avg_health_score': df['health_score'].mean(),
        'avg_treatment_days': df['treatment_days'].mean(),
        'total_cost': df['cost'].sum(),
        'avg_cost': df['cost'].mean(),
        'condition_counts': df['condition'].value_counts().to_dict(),
        'severity_distribution': df['severity'].value_counts(normalize=True).to_dict(),
        'gender_distribution': df['gender'].value_counts(normalize=True).to_dict()
    }
    
    return metrics

def filter_data(df, filters):
    """
    Apply filters to the dataset
    
    Args:
        df (pd.DataFrame): Dataset to filter
        filters (dict): Dictionary of filters to apply
        
    Returns:
        pd.DataFrame: Filtered dataset
    """
    filtered_df = df.copy()
    
    if 'age_range' in filters:
        min_age, max_age = filters['age_range']
        filtered_df = filtered_df[
            (filtered_df['age'] >= min_age) & 
            (filtered_df['age'] <= max_age)
        ]
    
    if 'conditions' in filters and filters['conditions']:
        filtered_df = filtered_df[filtered_df['condition'].isin(filters['conditions'])]
    
    if 'severity' in filters and filters['severity']:
        filtered_df = filtered_df[filtered_df['severity'].isin(filters['severity'])]
    
    if 'gender' in filters and filters['gender']:
        filtered_df = filtered_df[filtered_df['gender'].isin(filters['gender'])]
    
    return filtered_df

def export_data(df, format='csv'):
    """
    Export data in the specified format
    
    Args:
        df (pd.DataFrame): Dataset to export
        format (str): Export format ('csv', 'excel', 'json')
        
    Returns:
        bytes: Exported data as bytes
    """
    if format == 'csv':
        return df.to_csv(index=False).encode('utf-8')
    elif format == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Healthcare_Data')
        return output.getvalue()
    elif format == 'json':
        return df.to_json(orient='records', date_format='iso').encode('utf-8')
    else:
        raise ValueError(f"Unsupported format: {format}")

def validate_data(df):
    """
    Validate the healthcare dataset
    
    Args:
        df (pd.DataFrame): Dataset to validate
        
    Returns:
        dict: Validation results
    """
    validation_results = {
        'is_valid': True,
        'issues': [],
        'warnings': []
    }
    
    # Check for missing values
    missing_values = df.isnull().sum()
    if missing_values.any():
        validation_results['warnings'].append(f"Missing values found: {missing_values[missing_values > 0].to_dict()}")
    
    # Check for duplicate patient IDs
    if df['patient_id'].duplicated().any():
        validation_results['issues'].append("Duplicate patient IDs found")
        validation_results['is_valid'] = False
    
    # Check for invalid age values
    if (df['age'] < 0).any() or (df['age'] > 150).any():
        validation_results['issues'].append("Invalid age values found")
        validation_results['is_valid'] = False
    
    # Check for invalid health scores
    if (df['health_score'] < 1).any() or (df['health_score'] > 100).any():
        validation_results['issues'].append("Invalid health score values found")
        validation_results['is_valid'] = False
    
    return validation_results

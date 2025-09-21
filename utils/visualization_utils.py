"""
Utility functions for creating visualizations
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st
from config.config import COLOR_PALETTE, DEFAULT_CHART_HEIGHT

def create_age_distribution_chart(df):
    """
    Create an age distribution histogram
    
    Args:
        df (pd.DataFrame): Healthcare dataset
        
    Returns:
        plotly.graph_objects.Figure: Age distribution chart
    """
    fig = px.histogram(
        df, 
        x='age', 
        nbins=20,
        title="Age Distribution of Patients",
        labels={'age': 'Age', 'count': 'Number of Patients'},
        color_discrete_sequence=[COLOR_PALETTE[0]]
    )
    
    fig.update_layout(
        height=DEFAULT_CHART_HEIGHT,
        showlegend=False
    )
    
    return fig

def create_condition_distribution_chart(df):
    """
    Create a pie chart showing condition distribution
    
    Args:
        df (pd.DataFrame): Healthcare dataset
        
    Returns:
        plotly.graph_objects.Figure: Condition distribution chart
    """
    condition_counts = df['condition'].value_counts()
    
    fig = px.pie(
        values=condition_counts.values,
        names=condition_counts.index,
        title="Distribution of Health Conditions",
        color_discrete_sequence=COLOR_PALETTE
    )
    
    fig.update_layout(height=DEFAULT_CHART_HEIGHT)
    
    return fig

def create_health_score_by_age_scatter(df):
    """
    Create a scatter plot of health score vs age
    
    Args:
        df (pd.DataFrame): Healthcare dataset
        
    Returns:
        plotly.graph_objects.Figure: Scatter plot
    """
    fig = px.scatter(
        df, 
        x='age', 
        y='health_score',
        color='condition',
        title="Health Score vs Age by Condition",
        labels={'age': 'Age', 'health_score': 'Health Score'},
        color_discrete_sequence=COLOR_PALETTE
    )
    
    fig.update_layout(height=DEFAULT_CHART_HEIGHT)
    
    return fig

def create_cost_analysis_chart(df):
    """
    Create a box plot showing cost distribution by condition
    
    Args:
        df (pd.DataFrame): Healthcare dataset
        
    Returns:
        plotly.graph_objects.Figure: Cost analysis chart
    """
    fig = px.box(
        df, 
        x='condition', 
        y='cost',
        title="Treatment Cost Distribution by Condition",
        labels={'condition': 'Health Condition', 'cost': 'Treatment Cost ($)'},
        color='condition',
        color_discrete_sequence=COLOR_PALETTE
    )
    
    fig.update_layout(
        height=DEFAULT_CHART_HEIGHT,
        xaxis_tickangle=-45
    )
    
    return fig

def create_monthly_trends_chart(df):
    """
    Create a line chart showing monthly admission trends
    
    Args:
        df (pd.DataFrame): Healthcare dataset
        
    Returns:
        plotly.graph_objects.Figure: Monthly trends chart
    """
    # Group by month and count admissions
    df['month'] = df['admission_date'].dt.to_period('M')
    monthly_counts = df.groupby('month').size().reset_index(name='admissions')
    monthly_counts['month'] = monthly_counts['month'].astype(str)
    
    fig = px.line(
        monthly_counts, 
        x='month', 
        y='admissions',
        title="Monthly Admission Trends",
        labels={'month': 'Month', 'admissions': 'Number of Admissions'},
        markers=True
    )
    
    fig.update_traces(line_color=COLOR_PALETTE[0])
    fig.update_layout(
        height=DEFAULT_CHART_HEIGHT,
        xaxis_tickangle=-45
    )
    
    return fig

def create_severity_by_condition_chart(df):
    """
    Create a stacked bar chart showing severity distribution by condition
    
    Args:
        df (pd.DataFrame): Healthcare dataset
        
    Returns:
        plotly.graph_objects.Figure: Severity by condition chart
    """
    # Create crosstab
    severity_condition = pd.crosstab(df['condition'], df['severity'])
    
    fig = go.Figure()
    
    for i, severity in enumerate(['Low', 'Medium', 'High']):
        if severity in severity_condition.columns:
            fig.add_trace(go.Bar(
                name=severity,
                x=severity_condition.index,
                y=severity_condition[severity],
                marker_color=COLOR_PALETTE[i]
            ))
    
    fig.update_layout(
        title="Severity Distribution by Health Condition",
        xaxis_title="Health Condition",
        yaxis_title="Number of Cases",
        barmode='stack',
        height=DEFAULT_CHART_HEIGHT,
        xaxis_tickangle=-45
    )
    
    return fig

def create_treatment_duration_chart(df):
    """
    Create a violin plot showing treatment duration distribution
    
    Args:
        df (pd.DataFrame): Healthcare dataset
        
    Returns:
        plotly.graph_objects.Figure: Treatment duration chart
    """
    fig = px.violin(
        df, 
        x='condition', 
        y='treatment_days',
        title="Treatment Duration Distribution by Condition",
        labels={'condition': 'Health Condition', 'treatment_days': 'Treatment Days'},
        color='condition',
        color_discrete_sequence=COLOR_PALETTE
    )
    
    fig.update_layout(
        height=DEFAULT_CHART_HEIGHT,
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    return fig

def create_geographic_distribution_chart(df):
    """
    Create a bar chart showing patient distribution by state
    
    Args:
        df (pd.DataFrame): Healthcare dataset
        
    Returns:
        plotly.graph_objects.Figure: Geographic distribution chart
    """
    state_counts = df['state'].value_counts()
    
    fig = px.bar(
        x=state_counts.index,
        y=state_counts.values,
        title="Patient Distribution by State",
        labels={'x': 'State', 'y': 'Number of Patients'},
        color_discrete_sequence=[COLOR_PALETTE[1]]
    )
    
    fig.update_layout(height=DEFAULT_CHART_HEIGHT)
    
    return fig

def create_correlation_heatmap(df):
    """
    Create a correlation heatmap for numerical variables
    
    Args:
        df (pd.DataFrame): Healthcare dataset
        
    Returns:
        plotly.graph_objects.Figure: Correlation heatmap
    """
    # Select numerical columns
    numerical_cols = ['age', 'health_score', 'treatment_days', 'cost']
    correlation_matrix = df[numerical_cols].corr()
    
    fig = px.imshow(
        correlation_matrix,
        title="Correlation Matrix of Numerical Variables",
        color_continuous_scale='RdBu_r',
        aspect='auto'
    )
    
    fig.update_layout(height=DEFAULT_CHART_HEIGHT)
    
    return fig

def create_dashboard_summary_charts(df):
    """
    Create a set of summary charts for the dashboard
    
    Args:
        df (pd.DataFrame): Healthcare dataset
        
    Returns:
        dict: Dictionary containing multiple charts
    """
    charts = {
        'age_distribution': create_age_distribution_chart(df),
        'condition_distribution': create_condition_distribution_chart(df),
        'health_score_scatter': create_health_score_by_age_scatter(df),
        'cost_analysis': create_cost_analysis_chart(df),
        'monthly_trends': create_monthly_trends_chart(df),
        'severity_by_condition': create_severity_by_condition_chart(df),
        'treatment_duration': create_treatment_duration_chart(df),
        'geographic_distribution': create_geographic_distribution_chart(df),
        'correlation_heatmap': create_correlation_heatmap(df)
    }
    
    return charts

def create_custom_metric_cards(metrics):
    """
    Create custom HTML for metric cards
    
    Args:
        metrics (dict): Dictionary of metrics
        
    Returns:
        str: HTML string for metric cards
    """
    html = """
    <div style="display: flex; justify-content: space-around; margin: 20px 0;">
    """
    
    metric_items = [
        ("Total Patients", f"{metrics['total_records']:,}", "👥"),
        ("Avg Age", f"{metrics['avg_age']:.1f}", "📅"),
        ("Avg Health Score", f"{metrics['avg_health_score']:.1f}", "💯"),
        ("Total Cost", f"${metrics['total_cost']:,}", "💰")
    ]
    
    for title, value, icon in metric_items:
        html += f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 20px; border-radius: 10px; 
                    text-align: center; min-width: 150px; margin: 0 10px;">
            <div style="font-size: 2em;">{icon}</div>
            <div style="font-size: 1.5em; font-weight: bold;">{value}</div>
            <div style="font-size: 0.9em; opacity: 0.8;">{title}</div>
        </div>
        """
    
    html += "</div>"
    return html

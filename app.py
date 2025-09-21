import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="CDC Datathon 4L",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
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
</style>
""", unsafe_allow_html=True)

def main():
    # Main header
    st.markdown('<h1 class="main-header">🏥 CDC Datathon 4L Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Home", "Data Analysis", "Visualizations", "Insights", "About"]
        )
        
        st.markdown("---")
        st.header("⚙️ Settings")
        
        # Date range selector
        date_range = st.date_input(
            "Select date range:",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
        
        # Data source selector
        data_source = st.selectbox(
            "Data Source:",
            ["CDC Public Data", "Custom Dataset", "Sample Data"]
        )
    
    # Main content based on selected page
    if page == "Home":
        show_home_page()
    elif page == "Data Analysis":
        show_data_analysis()
    elif page == "Visualizations":
        show_visualizations()
    elif page == "Insights":
        show_insights()
    elif page == "About":
        show_about()

def show_home_page():
    st.header("Welcome to CDC Datathon 4L")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📈 Total Records",
            value="1,234,567",
            delta="12.5%"
        )
    
    with col2:
        st.metric(
            label="🏥 Healthcare Facilities",
            value="2,456",
            delta="3.2%"
        )
    
    with col3:
        st.metric(
            label="📊 Data Sources",
            value="15",
            delta="2"
        )
    
    with col4:
        st.metric(
            label="🔍 Active Analyses",
            value="8",
            delta="-1"
        )
    
    st.markdown("---")
    
    # Welcome message and project description
    st.markdown("""
    ## 🎯 Project Overview
    
    This dashboard is designed for the CDC Datathon 4L challenge, focusing on public health data analysis 
    and visualization. Our goal is to provide actionable insights from healthcare data to support 
    evidence-based decision making.
    
    ### 🚀 Key Features:
    - **Interactive Data Exploration**: Dive deep into healthcare datasets
    - **Advanced Visualizations**: Create compelling charts and graphs
    - **Statistical Analysis**: Perform comprehensive data analysis
    - **Real-time Insights**: Generate actionable recommendations
    
    ### 📋 Getting Started:
    1. Use the sidebar to navigate between different sections
    2. Select your preferred data source and date range
    3. Explore the various analysis and visualization tools
    4. Generate insights and export results
    """)
    
    # Quick link to the Star Wars page
    try:
        st.page_link("pages/1_🎬_Star_Wars_This_or_That.py", label="🎬 Open Star Wars: This or That", icon="✨")
    except Exception:
        pass
    
    # Sample data preview
    st.header("📋 Sample Data Preview")
    
    # Generate sample healthcare data
    sample_data = generate_sample_data()
    st.dataframe(sample_data, width='stretch')
    
    # Quick stats
    st.header("📊 Quick Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            x=['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            y=[100, 120, 140, 110, 160],
            title="Monthly Health Incidents"
        )
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        fig = px.pie(
            values=[30, 25, 20, 15, 10],
            names=['Respiratory', 'Cardiovascular', 'Diabetes', 'Mental Health', 'Others'],
            title="Health Condition Distribution"
        )
        st.plotly_chart(fig, width='stretch')

def show_data_analysis():
    st.header("📊 Data Analysis")
    
    st.info("This section will contain detailed data analysis tools and results.")
    
    # Placeholder for data analysis content
    tab1, tab2, tab3 = st.tabs(["Descriptive Stats", "Correlation Analysis", "Trend Analysis"])
    
    with tab1:
        st.subheader("Descriptive Statistics")
        sample_data = generate_sample_data()
        st.write(sample_data.describe())
    
    with tab2:
        st.subheader("Correlation Analysis")
        st.write("Correlation analysis tools will be implemented here.")
    
    with tab3:
        st.subheader("Trend Analysis")
        st.write("Trend analysis visualizations will be shown here.")

def show_visualizations():
    st.header("📈 Visualizations")
    
    st.info("Advanced visualization tools and interactive charts will be available here.")
    
    # Sample visualization
    sample_data = generate_sample_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.scatter(
            sample_data, 
            x='age', 
            y='health_score',
            color='condition',
            title="Age vs Health Score by Condition"
        )
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        fig = px.histogram(
            sample_data,
            x='age',
            nbins=20,
            title="Age Distribution"
        )
        st.plotly_chart(fig, width='stretch')

def show_insights():
    st.header("💡 Insights & Recommendations")
    
    st.success("Key insights and recommendations based on data analysis will be presented here.")
    
    # Sample insights
    insights = [
        "📈 Healthcare incidents show a seasonal pattern with peaks in winter months",
        "🏥 Respiratory conditions account for 30% of all reported cases",
        "👥 Age group 65+ shows higher vulnerability to cardiovascular conditions",
        "📍 Urban areas report 40% more mental health cases than rural areas"
    ]
    
    for insight in insights:
        st.markdown(f"- {insight}")

def show_about():
    st.header("ℹ️ About This Project")
    
    st.markdown("""
    ## CDC Datathon 4L Project
    
    **Team**: 4L Analytics Team
    **Challenge**: Public Health Data Analysis
    **Technology Stack**: Streamlit, Python, Pandas, Plotly
    
    ### 🎯 Objectives:
    - Analyze public health data trends
    - Identify key health indicators
    - Provide actionable insights for healthcare policy
    - Create interactive visualizations for stakeholders
    
    ### 📧 Contact:
    For questions or feedback, please reach out to the development team.
    
    ### 🔗 Resources:
    - [CDC Open Data](https://data.cdc.gov/)
    - [Streamlit Documentation](https://docs.streamlit.io/)
    - [Plotly Documentation](https://plotly.com/python/)
    """)

def generate_sample_data():
    """Generate sample healthcare data for demonstration"""
    np.random.seed(42)
    
    conditions = ['Respiratory', 'Cardiovascular', 'Diabetes', 'Mental Health', 'Others']
    
    data = {
        'patient_id': range(1, 101),
        'age': np.random.randint(18, 85, 100),
        'condition': np.random.choice(conditions, 100),
        'health_score': np.random.randint(1, 100, 100),
        'treatment_days': np.random.randint(1, 30, 100),
        'cost': np.random.randint(100, 5000, 100)
    }
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    main()

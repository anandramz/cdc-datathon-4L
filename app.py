import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Star Wars Fandom Generator",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FFD700;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #FFD700;
        color: white;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0f0f23, #1a1a2e);
        color: white;
    }
    .stApp {
        background: linear-gradient(135deg, #0f0f23, #1a1a2e, #16213e);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Main header
    st.markdown('<h1 class="main-header">⭐ Star Wars Fandom Generator</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🌌 Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Home", "Fan Quiz", "Your Result", "Network Analysis", "Model Management", "About"]
        )
        
        st.markdown("---")
        st.header("⚙️ Settings")
        
        # Galaxy selector
        galaxy = st.selectbox(
            "Select Galaxy:",
            ["Main Galaxy", "Unknown Regions", "Wild Space", "Deep Core"]
        )
        
        # Era selector
        era = st.selectbox(
            "Select Era:",
            ["Original Trilogy", "Prequel Trilogy", "Sequel Trilogy", "High Republic", "Legends"]
        )
    
    # Main content based on selected page
    if page == "Home":
        show_home_page()
    elif page == "Fan Quiz":
        st.switch_page("pages/1_📝_Fan_Quiz.py")
    elif page == "Your Result":
        st.switch_page("pages/2_🏆_Your_Result.py")
    elif page == "Network Analysis":
        st.switch_page("pages/3_📊_CDC_Network_Analysis.py")
    elif page == "Model Management":
        st.switch_page("pages/7_⚙️_Model_Management.py")
    elif page == "About":
        show_about()

def show_home_page():
    st.header("Welcome to the Star Wars Fandom Generator")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="⭐ Fan Clusters",
            value="9",
            delta="New!"
        )
    
    with col2:
        st.metric(
            label="🌌 Characters Analyzed",
            value="2,456",
            delta="+127"
        )
    
    with col3:
        st.metric(
            label="📊 Quiz Responses",
            value="15,847",
            delta="+1,234"
        )
    
    with col4:
        st.metric(
            label="🔍 Active Explorers",
            value="8,421",
            delta="+567"
        )
    
    st.markdown("---")
    
    # Welcome message and project description
    st.markdown("""
    ## 🎯 Project Overview
    
    Welcome to the **Star Wars Fandom Generator** - an interactive platform that uses machine learning 
    to analyze Star Wars fan preferences and discover hidden patterns in the galaxy far, far away! 
    Our goal is to help you discover which fan cluster you belong to and explore the connections 
    between different Star Wars elements.
    
    ### 🚀 Key Features:
    - **📝 Fan Quiz**: Discover your Star Wars fan cluster through our interactive quiz
    - **🏆 Personal Results**: Get detailed insights about your fan profile
    - **📊 Network Analysis**: Explore the galaxy of connections between characters, planets, and more
    - **🔬 Cluster Explorer**: Dive deep into different fan clusters and their characteristics
    - **⚙️ Model Management**: Train and manage the AI that powers our analysis
    
    ### 📋 Getting Started:
    1. Take the **Fan Quiz** to discover your cluster
    2. View your **Personal Results** to understand your fan profile
    3. Explore **Network Analysis** to see how different elements connect
    4. Use **Model Management** to train or reload the AI model
    """)
    
    # Quick links to main features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.page_link("pages/1_📝_Fan_Quiz.py", label="📝 Take the Fan Quiz", icon="📝")
    
    with col2:
        st.page_link("pages/3_📊_CDC_Network_Analysis.py", label="📊 Explore the Galaxy", icon="📊")
    
    with col3:
        st.page_link("pages/7_⚙️_Model_Management.py", label="⚙️ Manage AI Model", icon="⚙️")
    
    # Sample data preview
    st.header("📋 Fan Data Preview")
    
    # Generate sample Star Wars fan data
    sample_data = generate_sample_data()
    st.dataframe(sample_data, width='stretch')
    
    # Quick stats
    st.header("📊 Galaxy Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            x=['Heroes', 'Villains', 'Droids', 'Aliens', 'Jedi'],
            y=[45, 30, 15, 25, 35],
            title="Character Type Popularity",
            color_discrete_sequence=['#FFD700', '#C0C0C0', '#CD7F32', '#4B0082', '#00CED1']
        )
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        fig = px.pie(
            values=[35, 25, 20, 15, 5],
            names=['Original Trilogy', 'Prequel Trilogy', 'Sequel Trilogy', 'TV Shows', 'Legends'],
            title="Fan Preference by Era",
            color_discrete_sequence=['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        )
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, width='stretch')


def show_about():
    st.header("ℹ️ About This Project")
    
    st.markdown("""
    ## Star Wars Fandom Generator
    
    **Team**: 4L Analytics Team
    **Project**: Star Wars Fan Analysis & Clustering
    **Technology Stack**: Streamlit, Python, Pandas, Plotly, Scikit-learn
    
    ### 🎯 Objectives:
    - Analyze Star Wars fan preferences and patterns
    - Discover hidden connections between characters, planets, and films
    - Create personalized fan cluster assignments
    - Build interactive visualizations of the Star Wars universe
    - Use machine learning to understand fan behavior
    
    ### 🌟 Features:
    - **Machine Learning Clustering**: 9 distinct fan clusters based on preferences
    - **Interactive Network Analysis**: Visualize connections between Star Wars elements
    - **Personalized Quiz**: Discover which fan cluster you belong to
    - **Real-time Visualization**: Dynamic charts and graphs
    - **Comprehensive Analytics**: Deep insights into fan patterns
    
    ### 📧 Contact:
    For questions or feedback about the Star Wars Fandom Generator, please reach out to the development team.
    
    ### 🔗 Resources:
    - [Star Wars Official Site](https://www.starwars.com/)
    - [Streamlit Documentation](https://docs.streamlit.io/)
    - [Plotly Documentation](https://plotly.com/python/)
    - [Scikit-learn Documentation](https://scikit-learn.org/)
    """)

def generate_sample_data():
    """Generate sample Star Wars fan data for demonstration"""
    np.random.seed(42)
    
    characters = ['Luke Skywalker', 'Darth Vader', 'Princess Leia', 'Han Solo', 'Yoda', 'Obi-Wan Kenobi', 'R2-D2', 'C-3PO', 'Chewbacca', 'Boba Fett']
    planets = ['Tatooine', 'Coruscant', 'Hoth', 'Endor', 'Dagobah', 'Bespin', 'Naboo', 'Alderaan', 'Kashyyyk', 'Mandalore']
    films = ['A New Hope', 'The Empire Strikes Back', 'Return of the Jedi', 'The Phantom Menace', 'Attack of the Clones', 'Revenge of the Sith', 'The Force Awakens', 'The Last Jedi', 'The Rise of Skywalker']
    
    data = {
        'fan_id': range(1, 101),
        'age': np.random.randint(16, 65, 100),
        'favorite_character': np.random.choice(characters, 100),
        'favorite_planet': np.random.choice(planets, 100),
        'favorite_film': np.random.choice(films, 100),
        'fan_score': np.random.randint(1, 100, 100),
        'years_fan': np.random.randint(1, 45, 100),
        'cluster': np.random.randint(0, 9, 100)
    }
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    main()

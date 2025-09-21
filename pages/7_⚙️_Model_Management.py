import streamlit as st
import pandas as pd
from pathlib import Path
from backend.clustering import (
    train_and_save_clustering_model, 
    load_clustering_artifacts
)

st.set_page_config(layout="wide", page_title="⚙️ Model Management")

st.title("⚙️ Model Management")
st.caption("Train, load, and manage the clustering model for the Star Wars fan analysis")

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "starwars.csv"
MODELS_DIR = BASE_DIR / "models"

# --- State Management ---
def initialize_state():
    if 'artifacts_loaded' not in st.session_state:
        st.session_state.artifacts_loaded = False
    if 'kmeans_model' not in st.session_state:
        st.session_state.kmeans_model = None
    if 'encoder' not in st.session_state:
        st.session_state.encoder = None
    if 'top_features' not in st.session_state:
        st.session_state.top_features = None

initialize_state()

# --- Model Status Section ---
st.header("📊 Model Status")

# Check if model artifacts exist
artifacts_exist = all([
    (MODELS_DIR / "kmeans_model.joblib").exists(),
    (MODELS_DIR / "encoder.joblib").exists(),
    (MODELS_DIR / "top_features.joblib").exists()
])

col1, col2, col3 = st.columns(3)

with col1:
    if artifacts_exist:
        st.success("✅ Model artifacts found!")
    else:
        st.error("❌ Model artifacts not found")

with col2:
    if st.session_state.artifacts_loaded:
        st.success("✅ Model loaded in session")
    else:
        st.warning("⚠️ Model not loaded in session")

with col3:
    if artifacts_exist:
        # Show file sizes
        kmeans_size = (MODELS_DIR / "kmeans_model.joblib").stat().st_size / 1024
        encoder_size = (MODELS_DIR / "encoder.joblib").stat().st_size / 1024
        features_size = (MODELS_DIR / "top_features.joblib").stat().st_size / 1024
        total_size = kmeans_size + encoder_size + features_size
        st.metric("Total Size", f"{total_size:.1f} KB")

# --- Model Actions Section ---
st.header("🔧 Model Actions")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Load Model")
    st.caption("Load existing model artifacts into the current session")
    
    if st.button("🔄 Reload Model Artifacts", type="secondary", use_container_width=True):
        with st.spinner("Loading model artifacts..."):
            model, enc, features = load_clustering_artifacts()
            if model is not None:
                st.session_state.kmeans_model = model
                st.session_state.encoder = enc
                st.session_state.top_features = features
                st.session_state.artifacts_loaded = True
                st.success("✅ Model loaded successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to load artifacts")

with col2:
    st.subheader("Train New Model")
    st.caption("Train a new clustering model (this will overwrite existing models)")
    
    if st.button("🚀 Train Clustering Model", type="primary", use_container_width=True):
        with st.spinner("Training model... This might take a minute."):
            model, enc, features = train_and_save_clustering_model()
            if model is not None:
                st.session_state.kmeans_model = model
                st.session_state.encoder = enc
                st.session_state.top_features = features
                st.session_state.artifacts_loaded = True
                st.success("✅ Model trained and saved successfully!")
                st.rerun()
            else:
                st.error("❌ Model training failed")

# --- Model Information Section ---
if st.session_state.artifacts_loaded and st.session_state.kmeans_model is not None:
    st.header("📈 Model Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if hasattr(st.session_state.kmeans_model, 'n_clusters'):
            st.metric("Number of Clusters", st.session_state.kmeans_model.n_clusters)
        else:
            st.metric("Number of Clusters", "Unknown")
    
    with col2:
        if st.session_state.top_features is not None:
            st.metric("Top Features", len(st.session_state.top_features))
        else:
            st.metric("Top Features", "Unknown")
    
    with col3:
        if st.session_state.encoder is not None:
            if hasattr(st.session_state.encoder, 'n_features_in_'):
                st.metric("Input Features", st.session_state.encoder.n_features_in_)
            else:
                st.metric("Input Features", "Unknown")
        else:
            st.metric("Input Features", "Unknown")

# --- Data Information Section ---
st.header("📋 Data Information")

if DATA_PATH.exists():
    df = pd.read_csv(DATA_PATH)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", f"{len(df):,}")
    
    with col2:
        fav_cols = [c for c in df.columns if c.lower().startswith("fav_")]
        st.metric("Favorite Categories", len(fav_cols))
    
    with col3:
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        st.metric("Missing Data", f"{missing_pct:.1f}%")
    
    # Show sample of the data
    st.subheader("Sample Data")
    st.dataframe(df.head(), use_container_width=True)
else:
    st.error(f"❌ Data file not found at {DATA_PATH}")

# --- Navigation Section ---
st.header("🧭 Navigation")
st.markdown("""
**Quick Links:**
- 📝 [Fan Quiz](pages/1_📝_Fan_Quiz.py) - Take the quiz to find your cluster
- 🏆 [Your Result](pages/2_🏆_Your_Result.py) - View your cluster assignment
- 🔬 [Cluster Explorer](pages/6_🔬_Cluster_Explorer.py) - Explore different clusters
- 📊 [Network Analysis](pages/3_📊_CDC_Network_Analysis.py) - Visualize connections
""")

# --- Instructions Section ---
st.header("📖 Instructions")
st.markdown("""
### How to Use This Page:

1. **Check Model Status**: The status indicators show if model files exist and if they're loaded
2. **Load Model**: If model files exist but aren't loaded, use the "Reload Model Artifacts" button
3. **Train Model**: If no model exists or you want to retrain, use the "Train Clustering Model" button
4. **Monitor Progress**: Watch the spinners and success/error messages for feedback

### When to Train a New Model:
- First time using the application
- Data has been updated or changed
- Model performance needs improvement
- Switching between different datasets

### Troubleshooting:
- If loading fails, try training a new model
- If training fails, check that the data file exists and is properly formatted
- Make sure you have write permissions to the models directory
""")

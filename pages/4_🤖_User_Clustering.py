import streamlit as st
import pandas as pd
from pathlib import Path
from backend.clustering import (
    train_and_save_clustering_model, 
    load_clustering_artifacts, 
    predict_cluster
)

st.set_page_config(layout="wide", page_title="🤖 User Clustering")

st.title("🤖 Star Wars Fan Clustering")
st.caption("Train a model based on user preferences and classify new fans into clusters.")

# --- Paths and Data Loading ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "starwars.csv"
MODELS_DIR = BASE_DIR / "models"

@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        st.error(f"Data file not found at {DATA_PATH}")
        return None
    return pd.read_csv(DATA_PATH)

df = load_data()

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

# --- Sidebar for Training and Model Info ---
with st.sidebar:
    st.header("Model Management")
    
    # Check if model artifacts exist
    artifacts_exist = all([
        (MODELS_DIR / "kmeans_model.joblib").exists(),
        (MODELS_DIR / "encoder.joblib").exists(),
        (MODELS_DIR / "top_features.joblib").exists()
    ])

    if artifacts_exist:
        st.success("✅ Model artifacts found!")
        if st.button("Reload Model Artifacts") or not st.session_state.artifacts_loaded:
            with st.spinner("Loading model artifacts..."):
                model, enc, features = load_clustering_artifacts()
                if model is not None:
                    st.session_state.kmeans_model = model
                    st.session_state.encoder = enc
                    st.session_state.top_features = features
                    st.session_state.artifacts_loaded = True
                    st.rerun()
                else:
                    st.error("Failed to load artifacts.")
    else:
        st.warning("Model artifacts not found. Please train the model.")

    st.subheader("Train Model")
    st.caption("Run this if you haven't trained the model or if the data has changed.")
    if st.button("Train Clustering Model", type="primary"):
        with st.spinner("Training model... This might take a minute."):
            model, enc, features = train_and_save_clustering_model()
            if model is not None:
                st.session_state.kmeans_model = model
                st.session_state.encoder = enc
                st.session_state.top_features = features
                st.session_state.artifacts_loaded = True
                st.success("Model trained and saved successfully!")
                st.rerun()
            else:
                st.error("Model training failed.")

# --- Main Page Content ---
if not st.session_state.artifacts_loaded:
    st.info("Please train or load the model using the sidebar to continue.")
    st.stop()

# --- Display Top Features for Context ---
st.header("Top 8 Most Predictive Features")
st.caption("These features were identified by a Decision Tree as the most influential for predicting a user's favorite film. The clustering is based on them.")

if st.session_state.top_features:
    # Clean up feature names for display
    cleaned_features = [f.replace('fav_heroe_', 'Hero: ').replace('fav_villain_', 'Villain: ').replace('fav_planet_', 'Planet: ').replace('fav_spaceship_', 'Ship: ').replace('_', ' ') for f in st.session_state.top_features]
    st.code('\n'.join(cleaned_features), language='text')
else:
    st.warning("Top features not loaded.")

# --- User Input Form for Classification ---
st.header("Classify a New Fan")
st.caption("Fill out the form below to determine which fan cluster you belong to.")

if df is not None:
    feature_cols = ["fav_heroe", "fav_villain", "fav_soundtrack", 
                    "fav_spaceship", "fav_planet", "fav_robot"]
    
    user_preferences = {}
    cols = st.columns(2)
    
    for i, col_name in enumerate(feature_cols):
        with cols[i % 2]:
            # Get unique, non-null options from the dataframe
            options = df[col_name].dropna().unique().tolist()
            options.sort()
            user_preferences[col_name] = st.selectbox(
                f"Favorite {col_name.replace('fav_', '').replace('_', ' ').title()}", 
                options
            )

    if st.button("Classify Me!", type="primary", use_container_width=True):
        with st.spinner("Finding your cluster..."):
            predicted_cluster = predict_cluster(
                user_preferences,
                st.session_state.kmeans_model,
                st.session_state.encoder,
                st.session_state.top_features
            )
            
            st.success(f"## You belong to Cluster #{predicted_cluster}!")
            
            # You can add descriptions for each cluster here
            cluster_descriptions = {
                0: "This cluster is defined by...",
                1: "Fans in this group tend to prefer...",
                # ... add descriptions for all k clusters
            }
            
            st.write(cluster_descriptions.get(predicted_cluster, "No description available for this cluster yet."))
else:
    st.error("Cannot create user input form because the data could not be loaded.")

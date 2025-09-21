import streamlit as st
import pandas as pd
from pathlib import Path
from backend.clustering import (
    train_and_save_clustering_model, 
    load_clustering_artifacts, 
    predict_cluster
)

st.set_page_config(layout="centered", page_title="📝 Star Wars Fan Quiz")

st.title("📝 Star Wars Fan Quiz")
st.caption("Answer these questions to find out which fan cluster you belong to!")

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


# --- Main Page Content ---

# --- Display Top Features for Context ---
if not st.session_state.artifacts_loaded:
    st.warning("⚠️ The clustering model is not loaded. Please visit the Model Management page to train or load the model.")
    st.page_link("pages/7_⚙️_Model_Management.py", label="Go to Model Management", icon="⚙️")
    st.stop()

# --- User Input Form for Classification ---
st.header("Your Preferences")

if df is not None:
    with st.form(key='fan_quiz_form'):
        feature_cols = ["fav_heroe", "fav_villain", "fav_soundtrack", 
                        "fav_spaceship", "fav_planet", "fav_robot"]
        
        user_preferences = {}
        st.subheader("Select your favorites from each category:")

        # Display name mapping for better user experience
        display_names = {
            "fav_heroe": "Hero",
            "fav_villain": "Villain", 
            "fav_soundtrack": "Soundtrack",
            "fav_spaceship": "Spaceship",
            "fav_planet": "Planet",
            "fav_robot": "Robot"
        }
        
        for col_name in feature_cols:
            options = df[col_name].dropna().unique().tolist()
            options.sort()
            display_name = display_names.get(col_name, col_name.replace('fav_', '').replace('_', ' ').title())
            user_preferences[col_name] = st.selectbox(
                f"**Favorite {display_name}**", 
                options,
                index=None, # No default selection
                placeholder="Choose an option..."
            )

        submitted = st.form_submit_button("Find My Cluster!", use_container_width=True)

        if submitted:
            # Validate that all fields are filled
            if any(val is None for val in user_preferences.values()):
                st.error("Please answer all questions before submitting.")
            else:
                # Save preferences to session state and switch page
                st.session_state.user_quiz_answers = user_preferences
                st.switch_page("pages/2_🏆_Your_Result.py")
else:
    st.error("Cannot create the quiz because the data could not be loaded.")

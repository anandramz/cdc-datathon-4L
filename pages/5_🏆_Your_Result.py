import streamlit as st
from backend.clustering import load_clustering_artifacts, predict_cluster

st.set_page_config(layout="centered", page_title="🏆 Your Result")

# --- Check for Quiz Answers ---
if 'user_quiz_answers' not in st.session_state or not st.session_state.user_quiz_answers:
    st.warning("You need to complete the quiz first!")
    st.page_link("pages/4_📝_Fan_Quiz.py", label="Take the Star Wars Fan Quiz", icon="📝")
    st.stop()

# --- Load Model and Predict ---
st.title("🏆 Your Fan Cluster Result")

with st.spinner("Analyzing your answers..."):
    # Load the clustering model and other artifacts
    kmeans_model, encoder, top_features = load_clustering_artifacts()

    if kmeans_model is None:
        st.error("The clustering model is not available. Please contact the administrator.")
        st.stop()

    # Get user answers from session state
    user_preferences = st.session_state.user_quiz_answers

    # Predict the cluster
    predicted_cluster = predict_cluster(
        user_preferences,
        kmeans_model,
        encoder,
        top_features
    )

# --- Display Result ---
st.success(f"## You belong to Fan Cluster #{predicted_cluster}!")

st.markdown("--- ")

# --- Cluster Descriptions (Placeholders) ---
st.subheader("What does this mean?")

# You can define more detailed and engaging descriptions for each cluster here.
cluster_descriptions = {
    0: "**The Original Trilogy Purist:** You have a deep appreciation for the classics. Your choices suggest a love for the foundational characters and stories that started it all, like Luke Skywalker's journey and the iconic conflict with Darth Vader.",
    1: "**The Prequel Enthusiast:** You're drawn to the epic scale and complex politics of the Prequel era. You likely enjoy the dazzling lightsaber duels and the tragic story of Anakin Skywalker's fall from grace.",
    2: "**The Modern Saga Fan:** You connect with the newer stories and characters from the Sequel Trilogy and beyond. You appreciate the fresh perspectives and the continuation of the Skywalker saga in a new generation.",
    3: "**The Galactic Explorer:** Your interests are broad, spanning different eras and types of characters. You love the richness of the Star Wars universe itself, from its diverse planets to its unique spaceships and droids.",
    4: "**The Empire Loyalist:** You have a fascination with the order and power of the Galactic Empire. You might be drawn to the sleek designs of Imperial ships and the commanding presence of its villains.",
    5: "**The Rebel Alliance Sympathizer:** You stand with the underdogs. Your preferences align with the heroes of the Rebellion, their iconic starfighters, and their fight for freedom across the galaxy.",
    6: "**The Scum and Villainy Aficionado:** You find the galaxy's underworld captivating. From bounty hunters to smugglers, you're interested in the characters who operate in the gray areas of the Star Wars universe.",
    7: "**The Force Follower:** Your choices indicate a strong connection to the mystical aspects of Star Wars. Whether it's the Jedi or the Sith, you are most interested in stories centered around the Force."
}

# Get the number of clusters from the model
num_clusters = kmeans_model.n_clusters

# Display the appropriate description
description = cluster_descriptions.get(predicted_cluster, "This cluster represents a unique combination of preferences! As we gather more data, a clearer profile for this group will emerge.")
st.markdown(f"> {description}")

st.markdown("--- ")

# --- Display User's Answers for Confirmation ---
with st.expander("See Your Answers"):
    for category, choice in user_preferences.items():
        st.write(f"- **Favorite {category.replace('fav_', '').replace('_', ' ').title()}:** {choice}")

# --- Retake Quiz Button ---
if st.button("Take the Quiz Again", use_container_width=True):
    # Clear the answers from the session state
    if 'user_quiz_answers' in st.session_state:
        del st.session_state['user_quiz_answers']
    st.switch_page("pages/4_📝_Fan_Quiz.py")

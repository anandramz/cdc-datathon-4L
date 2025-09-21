import streamlit as st
from backend.clustering import load_clustering_artifacts, predict_cluster, analyze_clusters

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

    # Store the predicted cluster in session state for use in other pages
    st.session_state.user_cluster = predicted_cluster

    # Analyze all clusters to get the summary for the user's cluster
    cluster_summary, _ = analyze_clusters()

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

# --- Show Cluster Statistics ---
if cluster_summary and predicted_cluster in cluster_summary:
    summary = cluster_summary[predicted_cluster]
    st.subheader(f"Profile of Cluster #{predicted_cluster}")

    col1, col2 = st.columns(2)
    col1.metric("Fans in this Cluster", f"{summary['size']:,}")
    col2.metric("Share of Total Fans", f"{summary['percentage']:.1f}%")

    st.markdown("**How Your Answers Compare to Your Cluster:**")

    feature_cols = ["fav_heroe", "fav_villain", "fav_planet", "fav_robot", "fav_spaceship", "fav_soundtrack"]
    
    for col_name in feature_cols:
        st.markdown("--- ")
        category_name = col_name.replace('fav_', '').replace('_', ' ').title()
        st.subheader(f"Favorite {category_name}")

        user_answer = user_preferences.get(col_name, "N/A")
        top_cluster_choice = summary['top_answers'].get(col_name, [])

        if top_cluster_choice:
            cluster_answer = top_cluster_choice[0][0]
            cluster_percentage = top_cluster_choice[0][2]

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Your Answer**")
                st.info(user_answer)
            
            with col2:
                st.markdown("**Your Cluster's Top Pick**")
                st.success(f"{cluster_answer} ({cluster_percentage:.1f}%)")

            if user_answer == cluster_answer:
                st.write("✅ You picked the most popular choice for your cluster!")
        else:
            st.write(f"Your Answer: {user_answer}")
            st.write("No dominant preference found for this category in your cluster.")


st.markdown("--- ")

# --- Display User's Answers for Confirmation ---
with st.expander("See Your Answers"):
    for category, choice in user_preferences.items():
        st.write(f"- **Favorite {category.replace('fav_', '').replace('_', ' ').title()}:** {choice}")

# --- Action Buttons ---
col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 Explore My Cluster's Network", use_container_width=True):
        st.switch_page("pages/3_📊_CDC_Network_Analysis.py")

with col2:
    if st.button("🔄 Take the Quiz Again", use_container_width=True):
        # Clear the answers from the session state
        if 'user_quiz_answers' in st.session_state:
            del st.session_state['user_quiz_answers']
        if 'user_cluster' in st.session_state:
            del st.session_state['user_cluster']
        st.switch_page("pages/4_📝_Fan_Quiz.py")

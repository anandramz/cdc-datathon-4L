import streamlit as st
from backend.clustering import load_clustering_artifacts, predict_cluster, analyze_clusters

st.set_page_config(layout="centered", page_title="🏆 Your Result")

# --- Check for Quiz Answers ---
if 'user_quiz_answers' not in st.session_state or not st.session_state.user_quiz_answers:
    st.warning("You need to complete the quiz first!")
    st.page_link("pages/1_📝_Fan_Quiz.py", label="Take the Star Wars Fan Quiz", icon="📝")
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
    0: "**The Senate Scholars:** This group is drawn to the intricate political maneuvering and grand-scale conflicts of the Republic era. They appreciate the complex characters and sophisticated starship designs that defined the fall of the Jedi and the rise of the Empire.",
    1: "**The Core World Purists:** Fans in this cluster gravitate towards the foundational stories and characters of the original saga. Their preferences suggest a deep appreciation for the classic heroes' journey, the iconic struggle against tyranny, and the timeless aesthetic of the Galactic Civil War.",
    2: "**The Outer Rim Mavericks:** This cluster identifies with the smugglers, bounty hunters, and independent spirits of the galaxy. They prefer the gritty, lived-in feel of frontier worlds like Tatooine and are fascinated by those who operate on the edges of the law.",
    3: "**The Imperial Loyalists:** Adherents to order and power, this group is fascinated by the formidable presence of the Galactic Empire. They are drawn to its imposing military might, from the sleek design of TIE Fighters to the commanding presence of its dark-sided leaders.",
    4: "**The Rebel Alliance Sympathizers:** This group stands with the underdogs and heroes fighting for freedom. Their choices reflect a love for the Rebellion's iconic starfighters, the camaraderie of its pilots, and the enduring hope that fuels their cause against overwhelming odds.",
    5: "**The Force Mystics:** For this cluster, the heart of the saga lies in the mystical energy that binds the galaxy together. Whether Jedi or Sith, their interest is primarily in the characters who wield the Force and the ancient prophecies that surround them.",
    6: "**The Republic Veterans:** This group's preferences are firmly rooted in the Clone Wars era. They are captivated by the epic battles, the diverse legions of clone troopers, and the tragic heroes who navigated the turbulent end of the Republic.",
    7: "**The Scum and Villainy Aficionados:** Fans in this cluster are most interested in the galaxy's shadowy underworld. They appreciate the stories that unfold in cantinas and criminal dens, focusing on the complex motivations of those who thrive outside the law.",
    8: "**The Skywalker Saga Devotees:** This group is focused on the central family drama that spans the first six films. Their choices indicate a deep investment in the intertwined destinies of the Skywalker lineage, from Anakin's fall to Luke's redemption."
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
        st.markdown("--- ")
        category_name = display_names.get(col_name, col_name.replace('fav_', '').replace('_', ' ').title())
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
        st.switch_page("pages/1_📝_Fan_Quiz.py")

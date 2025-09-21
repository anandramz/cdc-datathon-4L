import streamlit as st
import pandas as pd
from backend.clustering import analyze_clusters, load_clustering_artifacts

st.set_page_config(layout="wide", page_title="🔬 Cluster Explorer")

st.title("🔬 Star Wars Fan Cluster Explorer")
st.caption("Interactively explore the characteristics of each fan cluster to understand their defining preferences.")

# --- Load Model and Analyze Clusters ---
@st.cache_data
def load_analysis():
    # First, ensure model artifacts exist, otherwise, analysis is not possible
    model, _, _ = load_clustering_artifacts()
    if model is None:
        return None, None
    return analyze_clusters()

cluster_summary, num_clusters = load_analysis()

if cluster_summary is None:
    st.error("Model artifacts not found. Please train the model first on the 'Fan Quiz' page.")
    st.page_link("pages/4_📝_Fan_Quiz.py", label="Go to Quiz Page to Train Model", icon="📝")
    st.stop()

# --- Interactive Cluster Selection ---
st.header("Select a Cluster to Analyze")

selected_cluster = st.slider(
    "Cluster ID", 
    min_value=0, 
    max_value=num_clusters - 1, 
    value=0, 
    step=1
)

st.markdown("--- ")

# --- Display Cluster Details ---
if selected_cluster in cluster_summary:
    summary = cluster_summary[selected_cluster]
    
    st.header(f"Cluster #{selected_cluster} Profile")
    
    # --- Key Metrics ---
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Cluster Size (Number of Fans)", f"{summary['size']:,}")
    with col2:
        st.metric("Percentage of Total Fans", f"{summary['percentage']:.1f}%")

    st.subheader("Most Popular Choices for this Cluster")
    st.caption("This shows the top answers for each category and what percentage of fans in this cluster chose them.")

    # --- Display Top Answers in Columns ---
    feature_cols = ["fav_heroe", "fav_villain", "fav_soundtrack", 
                    "fav_spaceship", "fav_planet", "fav_robot"]
    
    display_cols = st.columns(3)
    col_idx = 0

    for cat_col in feature_cols:
        with display_cols[col_idx % 3]:
            st.markdown(f"**Favorite {cat_col.replace('fav_', '').replace('_', ' ').title()}**")
            
            top_answers = summary['top_answers'].get(cat_col, [])
            
            if top_answers:
                # Create a DataFrame for better display
                df_answers = pd.DataFrame(top_answers, columns=["Answer", "Count", "Percentage"])
                df_answers['Percentage'] = df_answers['Percentage'].map('{:.1f}%'.format)
                
                # Highlight the top answer
                def highlight_top(s):
                    return ['background-color: #2E4053' if i == 0 else '' for i in range(len(s))]

                st.dataframe(
                    df_answers[['Answer', 'Percentage']].style.apply(highlight_top, axis=0),
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.write("No data available.")
        
        col_idx += 1
else:
    st.warning("Selected cluster not found.")


st.markdown("--- ")
st.info("Use this data to brainstorm descriptive labels for each cluster. For example, a cluster that overwhelmingly prefers 'Darth Vader' and 'The Imperial March' could be labeled 'The Imperial Loyalist'.")

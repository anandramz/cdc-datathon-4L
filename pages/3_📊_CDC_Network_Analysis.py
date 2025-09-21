import itertools, collections, math, os, tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
from backend.clustering import load_clustering_artifacts  # <-- for cluster labels

st.title("📊 CDC Network Analysis")
st.caption("Interactive network visualization of Star Wars preferences co-occurrence patterns (cluster-aware)")

# -------------------------------
# Helper function to fix data types
# -------------------------------
def _coerce_scalar_strings(df_in, cols):
    """Ensure fav_* columns are plain strings (not lists) so the saved encoder can transform."""
    df = df_in.copy()
    for c in cols:
        df[c] = df[c].apply(
            lambda v: (v[0] if isinstance(v, list) and len(v) > 0 else v)
                      if (isinstance(v, list) or isinstance(v, tuple)) else v
        )
        # force to string for non-null
        df[c] = df[c].astype("string")
    return df

# -------------------------------
# Module-level Jaccard
# -------------------------------
def jaccard(a: str, b: str, pairs: dict, freq: dict) -> float:
    """Jaccard = (#both) / (#either) on review-level co-mentions."""
    key = (a, b) if (a, b) in pairs else (b, a)
    inter = pairs.get(key, 0)
    denom = freq[a] + freq[b] - inter
    return inter / denom if denom else 0.0

# -------------------------------
# Load data
# -------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    local_path = Path(__file__).resolve().parent.parent / "data" / "starwars.csv"
    if local_path.exists():
        df = pd.read_csv(local_path)
    else:
        CSV_URL = "https://file.notion.so/f/f/480fe70d-ee65-4488-92ae-8d4ac37ffce6/b225252d-c56f-4474-948d-9070669832b6/Pop_Culture.csv?table=block&id=27233ee0-9d2c-802d-9775-ccdd8127eecb&spaceId=480fe70d-ee65-4488-92ae-8d4ac37ffce6&expirationTimestamp=1758420000000&signature=5oTANnbAtDKr0CVnVO8-ME364fgmZe8q41NHIiDYVrs&downloadName=Pop_Culture.csv"
        df = pd.read_csv(CSV_URL)
    return df

df = load_data()
st.write(f"**Dataset shape:** {df.shape[0]:,} rows × {df.shape[1]} columns")

# -------------------------------
# Prepare items & co-occurrence
# -------------------------------
@st.cache_data(show_spinner=False)
def process_data(df_in: pd.DataFrame):
    fav_cols = [c for c in df_in.columns if c.lower().startswith("fav_")]
    if not fav_cols:
        return None, None, None, None

    # Build "type:value" tokens per row (dataset uses 'heroe' spelling)
    def prefixed_items(row):
        items = []
        # Display name mapping for better user experience
        type_mapping = {
            "heroe": "hero",
            "villain": "villain", 
            "soundtrack": "soundtrack",
            "spaceship": "spaceship",
            "planet": "planet",
            "robot": "robot",
            "film": "film"
        }
        
        for c in fav_cols:
            typ = c.lower().replace("fav_", "")
            # Use mapped type for display, but keep original for processing
            display_typ = type_mapping.get(typ, typ)
            val = row[c]
            if pd.notna(val) and str(val).strip():
                items.append(f"{display_typ}:{val}")
        return items

    df_items = df_in.copy()
    df_items["_items"] = df_items.apply(prefixed_items, axis=1)

    freq = collections.Counter()
    pairs = collections.Counter()
    for items in df_items["_items"]:
        u = sorted(set(items))
        for a in u: freq[a] += 1
        for a, b in itertools.combinations(u, 2):
            pairs[(a, b)] += 1

    def split_tag(tag):
        return (tag.split(":", 1)[0], tag.split(":", 1)[1]) if ":" in tag else ("item", tag)

    item_types = {it: split_tag(it)[0] for it in freq}
    raw_labels = {it: split_tag(it)[1] for it in freq}
    return freq, pairs, item_types, raw_labels

# -------------------------------
# Add cluster labels to every row
# -------------------------------
@st.cache_data(show_spinner=False)
def add_cluster_labels(df_in: pd.DataFrame):
    model, enc, top_features = load_clustering_artifacts()
    if model is None or enc is None:
        st.error("❌ Could not load clustering artifacts. Train the model on the 'User Clustering' page.")
        st.stop()

    # Columns encoder expects (from training)
    base_cols = list(getattr(enc, "feature_names_in_", []))
    if not base_cols:
        base_cols = [c for c in df_in.columns if c.lower().startswith("fav_")]

    # 🔧 make sure they are scalar strings (not lists)
    df_use = _coerce_scalar_strings(df_in, base_cols)

    # Transform and align with top_features
    X_enc = enc.transform(df_use[base_cols])
    X_arr = X_enc.toarray() if hasattr(X_enc, "toarray") else np.asarray(X_enc)
    feat_names = enc.get_feature_names_out(base_cols)
    X_df = pd.DataFrame(X_arr, columns=feat_names, index=df_use.index)

    use_cols = [c for c in (top_features or []) if c in X_df.columns]
    if not use_cols:
        st.warning("top_features missing/mismatched; using ALL encoded features.")
        use_cols = list(X_df.columns)

    labels = model.predict(X_df[use_cols].values)
    out = df_in.copy()
    out["cluster"] = labels

    # Debug: confirm we really have 9 clusters
    vc = pd.Series(labels).value_counts().sort_index()
    st.caption("Cluster counts: " + ", ".join([f"{i}:{int(c)}" for i,c in vc.items()]))
    if hasattr(model, "n_clusters"):
        st.caption(f"KMeans n_clusters = **{model.n_clusters}**")

    return out, sorted(vc.index.tolist())

df_all, cluster_ids = add_cluster_labels(df)

# -------------------------------
# Sidebar controls (cluster first)
# -------------------------------
with st.sidebar:
    st.header("🎛️ Network Configuration")

    # Check if user has a stored cluster from quiz
    default_index = 0
    if 'user_cluster' in st.session_state and st.session_state.user_cluster in cluster_ids:
        # Find the index of the user's cluster
        user_cluster = st.session_state.user_cluster
        cluster_options = ["All clusters"] + [f"Cluster {i}" for i in cluster_ids]
        try:
            default_index = cluster_options.index(f"Cluster {user_cluster}")
        except ValueError:
            default_index = 0
    
    cluster_choice = st.selectbox(
        "Filter by cluster",
        options=["All clusters"] + [f"Cluster {i}" for i in cluster_ids],
        index=default_index
    )
    
    # Show a message if user's cluster is pre-selected
    if 'user_cluster' in st.session_state and cluster_choice == f"Cluster {st.session_state.user_cluster}":
        st.info(f"🎯 Showing your assigned cluster (Cluster {st.session_state.user_cluster}) from the quiz!")
    
    
# Choose subset for the graph
if cluster_choice == "All clusters":
    df_view = df_all
    st.caption(f"Showing **all clusters** ({len(df_view):,} rows)")
else:
    cid = int(cluster_choice.split()[-1])
    df_view = df_all[df_all["cluster"] == cid]
    st.caption(f"Showing **Cluster {cid}** only ({len(df_view):,} rows)")

# Build co-occurrence on the chosen subset
freq, pairs, item_types, raw_labels = process_data(df_view)
if freq is None:
    st.error("No favorites columns found (prefixed with 'fav_').")
    st.stop()

types_present = sorted(set(item_types.values()))

# Remaining sidebar controls (now that we know types present)
with st.sidebar:
    include_types = st.multiselect(
        "Item types to include",
        options=types_present,
        default=[t for t in ["hero", "villain", "film", "planet"] if t in types_present]
    )

    node_min_support = st.slider("Min item frequency", 5, 100, 20, 1)
    edge_min_pair_count = st.slider("Min co-mentions", 2, 50, 12, 1)
    edge_min_jaccard = st.slider("Min Jaccard", 0.00, 0.30, 0.10, 0.01)
    max_edges = st.slider("Max edges", 200, 5000, 1500, 100)

# -------------------------------
# Build + render the network
# -------------------------------
TYPE_COLORS = {
    "heroe": "#4cc9f0", "hero": "#4cc9f0",
    "villain": "#ef233c", "planet": "#2ecc71",
    "film": "#ffd166", "spaceship": "#9b59b6",
    "soundtrack": "#f39c12", "robot": "#95a5a6"
}
DEFAULT_NODE_COLOR = "#c8d6e5"

@st.cache_data(show_spinner=False)
def build_galaxy_html(include_types, node_min_support, edge_min_pair_count, edge_min_jaccard, max_edges, cache_key):
    allowed = {it for it in freq if item_types.get(it) in include_types and freq[it] >= node_min_support}
    if not allowed:
        return "<p style='color:#fff;padding:24px;text-align:center'>No items meet the threshold.</p>"

    edges = []
    for (a, b), inter in pairs.items():
        if a not in allowed or b not in allowed or inter < edge_min_pair_count:
            continue
        jac = jaccard(a, b, pairs, freq)
        if jac >= edge_min_jaccard:
            edges.append((a, b, inter, jac))
    if not edges:
        return "<p style='color:#fff;padding:24px;text-align:center'>No edges meet the thresholds.</p>"

    edges.sort(key=lambda x: (x[3], x[2]), reverse=True)
    edges = edges[:max_edges]

    # Only include nodes that have at least one connection meeting the thresholds
    connected_nodes = set()
    for a, b, inter, jac in edges:
        connected_nodes.add(a)
        connected_nodes.add(b)

    net = Network(height="700px", width="100%", bgcolor="#000", font_color="#fff", notebook=False)
    net.barnes_hut(gravity=-8000, central_gravity=0.28, spring_length=190, spring_strength=0.01, damping=0.9)

    # Only add nodes that have connections
    for it in connected_nodes:
        typ = item_types.get(it, "item")
        label = raw_labels.get(it, it)
        size = 12 + 6 * math.log10(max(freq[it], 10))
        net.add_node(it, label=label, title=f"<b>{label}</b><br>Type: {typ}<br>Count: {freq[it]}",
                     color=TYPE_COLORS.get(typ, DEFAULT_NODE_COLOR), size=size)

    j_min, j_max = min(e[3] for e in edges), max(e[3] for e in edges)
    span = (j_max - j_min) or 1.0
    for a, b, inter, jac in edges:
        width = 1 + 8 * ((jac - j_min) / span)
        net.add_edge(a, b, title=f"Co-mentions: {inter} • Jaccard: {jac:.3f}", width=width)

    net.set_options("""
      { "nodes":{"borderWidth":1,"shadow":true},
        "edges":{"color":{"color":"#9aa3a7"},"smooth":{"enabled":true,"type":"dynamic"}},
        "physics":{"solver":"barnesHut","stabilization":{"iterations":200}},
        "interaction":{"hover":true,"dragNodes":true,"dragView":true,"zoomView":true} }
    """)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        html_path = Path(tmp.name)
    net.save_graph(str(html_path))
    html = html_path.read_text("utf-8")
    try: os.remove(html_path)
    except Exception: pass
    return html

# Unique cache key so different clusters/selections re-render
cache_key = (
    cluster_choice,
    tuple(sorted(include_types)),
    node_min_support, edge_min_pair_count, edge_min_jaccard, max_edges,
    len(freq), len(types_present)
)

col_left, col_right = st.columns([3, 1], gap="large")

with col_left:
    st.subheader("🌌 Network Visualization")
    html = build_galaxy_html(include_types, node_min_support, edge_min_pair_count, edge_min_jaccard, max_edges, cache_key)
    components.html(html, height=720, scrolling=True)

with col_right:
    st.subheader("📈 Stats")
    filtered_items = [it for it in freq if item_types.get(it) in include_types and freq[it] >= node_min_support]
    st.metric("Nodes (filtered)", len(filtered_items))

    edge_count = 0
    for (a, b), inter in pairs.items():
        if a in filtered_items and b in filtered_items and inter >= edge_min_pair_count and jaccard(a, b, pairs, freq) >= edge_min_jaccard:
            edge_count += 1
    st.metric("Edges (filtered)", min(edge_count, max_edges))

    # Cohesion quick check (justify clustering): avg Jaccard among top items in this subset
    def avg_j(items):
        vals = []
        for x, y in itertools.combinations(items, 2):
            if x in freq and y in freq:
                vals.append(jaccard(x, y, pairs, freq))
        return float(np.mean(vals)) if vals else float("nan")

    topN = sorted(filtered_items, key=lambda it: freq[it], reverse=True)[:12]
    if len(topN) >= 3:
        st.metric("Avg Jaccard among top items", f"{avg_j(topN):.3f}")

st.markdown("---")
st.markdown("""
**Reading the graph:** Nodes are items (size=popularity).  
Edges connect items that co-appear in user favorites; edge thickness is **Jaccard** (normalized co-occurrence).  
Use the **cluster selector** to see the galaxy **within a specific segment**.
""")
import streamlit as st
import pandas as pd
import numpy as np
import itertools
import collections
import math
import tempfile
import os
from pathlib import Path
import streamlit.components.v1 as components
from pyvis.network import Network

st.title("📊 CDC Network Analysis")
st.caption("Interactive network visualization of Star Wars preferences co-occurrence patterns")

# -------------------------------
# Module-level jaccard function (picklable)
# -------------------------------
def jaccard(a, b, pairs, freq):
    """Calculate Jaccard similarity between two items"""
    # Treat key order-invariant
    key = (a, b) if (a, b) in pairs else (b, a)
    inter = pairs.get(key, 0)
    denom = freq[a] + freq[b] - inter
    return inter / denom if denom else 0.0

# -------------------------------
# Data Loading
# -------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    """Load the Star Wars CSV data"""
    try:
        # Try local file first
        local_path = Path(__file__).resolve().parent.parent / "data" / "starwars.csv"
        if local_path.exists():
            df = pd.read_csv(local_path)
            st.success("✅ Loaded local starwars.csv")
        else:
            # Fallback to URL
            CSV_URL = "https://file.notion.so/f/f/480fe70d-ee65-4488-92ae-8d4ac37ffce6/b225252d-c56f-4474-948d-9070669832b6/Pop_Culture.csv?table=block&id=27233ee0-9d2c-802d-9775-ccdd8127eecb&spaceId=480fe70d-ee65-4488-92ae-8d4ac37ffce6&expirationTimestamp=1758420000000&signature=5oTANnbAtDKr0CVnVO8-ME364fgmZe8q41NHIiDYVrs&downloadName=Pop_Culture.csv"
            df = pd.read_csv(CSV_URL)
            st.success("✅ Loaded from URL")
        
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None

df = load_data()
if df is None:
    st.stop()

st.write(f"**Dataset shape:** {df.shape[0]:,} rows × {df.shape[1]} columns")

# -------------------------------
# Data Processing
# -------------------------------
@st.cache_data(show_spinner=False)
def process_data(df):
    """Process the dataframe to extract item co-occurrences"""
    
    # Find favorite columns
    FAV_COLS = [c for c in df.columns if c.lower().startswith("fav_")]
    
    if not FAV_COLS:
        st.error("No columns found starting with 'fav_'")
        return None, None, None, None
    
    st.write(f"**Favorite columns found:** {', '.join(FAV_COLS)}")
    
    # Process favorites into item lists with type prefixes
    def prefixed_items(row):
        items = []
        for c in FAV_COLS:
            typ = c.lower().replace("fav_", "")  # e.g., 'heroe','villain','planet'
            val = row[c]
            if pd.notna(val):
                items.append(f"{typ}:{val}")
        return items
    
    df["_items"] = df.apply(prefixed_items, axis=1)
    
    # Count individual item frequency and pair co-occurrence
    freq = collections.Counter()
    pairs = collections.Counter()
    
    for items in df["_items"]:
        uniq = sorted(set(items))
        for a in uniq:
            freq[a] += 1
        for a, b in itertools.combinations(uniq, 2):
            pairs[(a, b)] += 1  # store as ordered tuple (a<b)
    
    # Convenience: map item -> type and raw label
    def split_tag(tag):
        # "heroe:Luke Skywalker" -> ("heroe", "Luke Skywalker")
        if ":" in tag:
            t, v = tag.split(":", 1)
            return t, v
        return "item", tag
    
    item_types = {it: split_tag(it)[0] for it in freq.keys()}
    raw_labels = {it: split_tag(it)[1] for it in freq.keys()}
    
    return freq, pairs, item_types, raw_labels

freq, pairs, item_types, raw_labels = process_data(df)
if freq is None:
    st.stop()

st.write(f"**Unique items:** {len(freq):,}")
st.write(f"**Unique pairs:** {len(pairs):,}")

# Get available types
types_present = sorted(set(item_types.values()))
st.write(f"**Item types:** {', '.join(types_present)}")

# -------------------------------
# Configuration Sidebar
# -------------------------------
with st.sidebar:
    st.header("🎛️ Network Configuration")
    
    st.subheader("Item Types")
    include_types = st.multiselect(
        "Select types to include:",
        options=types_present,
        default=[t for t in ["heroe", "villain", "film", "planet"] if t in types_present]
    )
    
    st.subheader("Thresholds")
    node_min_support = st.slider(
        "Min item frequency", 
        min_value=5, max_value=100, value=15, step=1,
        help="Minimum times an item must appear to be included"
    )
    
    edge_min_pair_count = st.slider(
        "Min co-occurrence count", 
        min_value=2, max_value=50, value=8, step=1,
        help="Minimum times a pair must co-appear"
    )
    
    edge_min_jaccard = st.slider(
        "Min Jaccard similarity", 
        min_value=0.00, max_value=0.50, value=0.10, step=0.01,
        help="Minimum normalized similarity strength"
    )
    
    max_edges = st.slider(
        "Max edges (performance)", 
        min_value=100, max_value=3000, value=1200, step=100,
        help="Maximum number of edges to display"
    )

# -------------------------------
# Network Visualization
# -------------------------------

# Visual config (colors per type)
TYPE_COLORS = {
    "heroe": "#4cc9f0", "hero": "#4cc9f0", "villain": "#ef233c", 
    "film": "#ffd166", "planet": "#2ecc71", "ship": "#9b59b6", 
    "spaceship": "#9b59b6", "soundtrack": "#f39c12", "robot": "#95a5a6"
}
DEFAULT_NODE_COLOR = "#c8d6e5"

@st.cache_data(show_spinner=False)
def build_galaxy_html(include_types, node_min_support, edge_min_pair_count, edge_min_jaccard, max_edges):
    """Build the network visualization HTML"""
    
    if not include_types:
        return "<p style='color:#fff; text-align:center; padding:50px;'>Please select at least one item type from the sidebar.</p>"
    
    # Filter nodes by type & support
    allowed = {
        it for it in freq
        if item_types.get(it, "item") in include_types and freq[it] >= node_min_support
    }
    
    if not allowed:
        return "<p style='color:#fff; text-align:center; padding:50px;'>No items meet the minimum support threshold. Try lowering the minimum frequency.</p>"
    
    # Pre-calc edge list with thresholds
    edges = []
    for (a, b), inter in pairs.items():
        if a not in allowed or b not in allowed:
            continue
        if inter < edge_min_pair_count:
            continue
        jac = jaccard(a, b, pairs, freq)
        if jac < edge_min_jaccard:
            continue
        edges.append((a, b, inter, jac))
    
    if not edges:
        return "<p style='color:#fff; text-align:center; padding:50px;'>No edges meet the thresholds. Try lowering the minimum values.</p>"
    
    # Keep strongest edges first
    edges.sort(key=lambda x: (x[3], x[2]), reverse=True)
    edges = edges[:max_edges]
    
    # Build graph
    net = Network(
        height="700px",
        width="100%",
        bgcolor="#000000",
        font_color="#ffffff",
        notebook=False,
        directed=False
    )
    net.barnes_hut(
        gravity=-8000, 
        central_gravity=0.3, 
        spring_length=180,
        spring_strength=0.01, 
        damping=0.9
    )
    
    # Add nodes
    for it in allowed:
        typ = item_types.get(it, "item")
        color = TYPE_COLORS.get(typ, DEFAULT_NODE_COLOR)
        label = raw_labels.get(it, it)
        title = f"<b>{label}</b><br>Type: {typ}<br>Frequency: {freq[it]}"
        size = 12 + 6 * math.log10(max(freq[it], 10))  # size by popularity
        net.add_node(it, label=label, title=title, color=color, size=size)
    
    # Normalize widths by Jaccard for aesthetics
    j_min = min(e[3] for e in edges)
    j_max = max(e[3] for e in edges)
    span = (j_max - j_min) or 1.0
    
    for a, b, inter, jac in edges:
        width = 1 + 8 * ((jac - j_min) / span)
        title = f"Co-appears: {inter} times • Jaccard: {jac:.3f}"
        net.add_edge(a, b, title=title, width=width)
    
    net.set_options("""
    {
      "nodes": { "borderWidth": 1, "shadow": true },
      "edges": { "color": {"color": "#9aa3a7"}, "smooth": {"enabled": true, "type": "dynamic"} },
      "physics": { "solver": "barnesHut", "stabilization": {"iterations": 200} },
      "interaction": { "hover": true, "dragNodes": true, "dragView": true, "zoomView": true }
    }
    """)
    
    # Save to temp file and return HTML
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        html_path = Path(tmp.name)
    
    net.save_graph(str(html_path))
    html = html_path.read_text(encoding="utf-8")
    
    try:
        os.remove(html_path)
    except Exception:
        pass
    
    return html

# -------------------------------
# Main Layout
# -------------------------------
col_left, col_right = st.columns([3, 1], gap="large")

with col_left:
    st.subheader("🌌 Network Visualization")
    
    with st.spinner("Generating network..."):
        html = build_galaxy_html(
            include_types, 
            node_min_support, 
            edge_min_pair_count, 
            edge_min_jaccard, 
            max_edges
        )
    
    components.html(html, height=720, scrolling=True)

with col_right:
    st.subheader("📈 Statistics")
    
    if include_types:
        # Filter stats based on current selection
        filtered_items = {
            it for it in freq
            if item_types.get(it, "item") in include_types and freq[it] >= node_min_support
        }
        
        st.metric("Nodes (filtered)", len(filtered_items))
        
        # Count edges that would be shown
        edge_count = 0
        for (a, b), inter in pairs.items():
            if (a in filtered_items and b in filtered_items and 
                inter >= edge_min_pair_count and 
                jaccard(a, b, pairs, freq) >= edge_min_jaccard):
                edge_count += 1
        
        st.metric("Edges (filtered)", min(edge_count, max_edges))
        
        # Top items by type
        st.subheader("🏆 Top Items by Type")
        for typ in include_types:
            items_of_type = [
                (raw_labels.get(it, it), freq[it]) 
                for it in freq 
                if item_types.get(it) == typ and freq[it] >= node_min_support
            ]
            if items_of_type:
                items_of_type.sort(key=lambda x: x[1], reverse=True)
                st.write(f"**{typ.title()}:**")
                for name, count in items_of_type[:5]:
                    st.write(f"• {name}: {count}")
    
    st.subheader("🔍 Item Search")
    search_query = st.text_input("Search for an item:", placeholder="e.g., Luke Skywalker")
    
    if search_query:
        # Find matching items
        matches = [
            (it, raw_labels.get(it, it), freq[it], item_types.get(it, "item"))
            for it in freq
            if search_query.lower() in raw_labels.get(it, it).lower()
        ]
        
        if matches:
            matches.sort(key=lambda x: x[2], reverse=True)  # Sort by frequency
            st.write("**Matches:**")
            for it, label, count, typ in matches[:10]:
                st.write(f"• **{label}** ({typ}): {count}")
                
                # Show top connections
                connections = []
                for (a, b), inter in pairs.items():
                    other = None
                    if a == it:
                        other = b
                    elif b == it:
                        other = a
                    
                    if other and inter >= 5:  # Minimum threshold for display
                        jac = jaccard(it, other, pairs, freq)
                        connections.append((raw_labels.get(other, other), inter, jac))
                
                if connections:
                    connections.sort(key=lambda x: x[2], reverse=True)  # Sort by Jaccard
                    st.write(f"  Top connections: {', '.join([f'{name} ({jac:.2f})' for name, _, jac in connections[:3]])}")
        else:
            st.write("No matches found.")

# -------------------------------
# Footer Info
# -------------------------------
st.markdown("---")
st.markdown("""
**About this visualization:**
- **Nodes** represent Star Wars items (heroes, villains, films, etc.) sized by popularity
- **Edges** connect items that frequently appear together in user preferences  
- **Edge thickness** represents Jaccard similarity (normalized co-occurrence strength)
- **Colors** distinguish different item types
- **Interactive:** Hover for details, drag nodes, zoom and pan
""")

st.markdown("""
**Tips:**
- Adjust thresholds in the sidebar to explore different network densities
- Lower thresholds show more connections but may be cluttered
- Higher thresholds focus on the strongest relationships
- Use the search box to find specific items and their connections
""")

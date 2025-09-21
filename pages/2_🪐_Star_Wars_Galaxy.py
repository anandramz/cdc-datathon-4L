import itertools, collections, math, re, unicodedata, tempfile, os
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

# NOTE: Do not call set_page_config here; it's set in app.py
st.title("⭐ Star Wars Co-Occurrence Galaxy")
st.caption("Pick types (e.g., heroe, villain, film, planet), tune thresholds, and explore the item–item network.")

# -------------------------------
# UI: local CSV (default) or URL/upload
# -------------------------------
LOCAL_CSV = Path(__file__).resolve().parent.parent / "data" / "starwars.csv"
DEFAULT_URL = "https://file.notion.so/f/f/480fe70d-ee65-4488-92ae-8d4ac37ffce6/b225252d-c56f-4474-948d-9070669832b6/Pop_Culture.csv?table=block&id=27233ee0-9d2c-802d-9775-ccdd8127eecb&spaceId=480fe70d-ee65-4488-92ae-8d4ac37ffce6&expirationTimestamp=1758420000000&signature=5oTANnbAtDKr0CVnVO8-ME364fgmZe8q41NHIiDYVrs&downloadName=Pop_Culture.csv"

with st.sidebar:
    st.header("Data")
    st.radio("Source", ["Local file", "URL", "Upload"], index=0, key="sw_source")
    if st.session_state.sw_source == "Local file":
        st.write("Using:", f"data/starwars.csv" if LOCAL_CSV.exists() else "Default URL (fallback)")
    url = st.text_input("CSV URL", value=DEFAULT_URL)
    uploaded = st.file_uploader("...or upload Pop_Culture.csv", type=["csv"]) 

@st.cache_data(show_spinner=False)
def load_df(source_choice: str, local_csv: Path, url: str, uploaded_file):
    if source_choice == "Upload" and uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    if source_choice == "Local file" and local_csv.exists():
        return pd.read_csv(local_csv)
    return pd.read_csv(url)

try:
    df = load_df(st.session_state.sw_source, LOCAL_CSV, url, uploaded)
except Exception as e:
    st.error(f"Failed to load CSV. {e}")
    st.stop()

# -------------------------------
# Parse favorites into items
# -------------------------------
# Normalize headers a bit
df.columns = [unicodedata.normalize("NFKC", c).strip() for c in df.columns]
FAV_COLS = [c for c in df.columns if c.lower().startswith("fav_")]
if not FAV_COLS:
    st.error("No columns found starting with 'fav_'. Check the CSV.")
    st.stop()

def to_list(cell):
    if pd.isna(cell):
        return []
    return [t.strip() for t in str(cell).split(",") if t.strip()]

for c in FAV_COLS:
    df[c] = df[c].apply(to_list)

# Build combined item tokens with type prefix
# IMPORTANT: dataset uses 'heroe' spelling; we keep it but everything stays dynamic.

def prefixed_items(row):
    items = []
    for c in FAV_COLS:
        typ = c.lower().replace("fav_", "")  # e.g., heroe, villain, planet, film, ...
        for v in row[c]:
            items.append(f"{typ}:{v}")
    return items

df["_items"] = df.apply(prefixed_items, axis=1)

@st.cache_data(show_spinner=False)
def build_counts(items_col):
    freq = collections.Counter()
    pairs = collections.Counter()
    for items in items_col:
        u = sorted(set(items))
        for a in u:
            freq[a] += 1
        for i in range(len(u)):
            for j in range(i + 1, len(u)):
                pairs[(u[i], u[j])] += 1
    return freq, pairs

freq, pairs = build_counts(df["_items"])

# Helpers to split tags

def split_tag(tag: str):
    if ":" in tag:
        t, v = tag.split(":", 1)
        return t, v
    return "item", tag

item_types = {it: split_tag(it)[0] for it in freq.keys()}
raw_labels = {it: split_tag(it)[1] for it in freq.keys()}
types_present = sorted(set(item_types.values()))

with st.sidebar:
    st.header("Types & thresholds")
    st.caption("Pick which item types to include in the graph. The list comes from the data itself.")
    include_types = st.multiselect(
        "include_types",
        options=types_present,
        default=[t for t in ["heroe", "villain", "film", "planet"] if t in types_present],
    )

    node_min_support = st.slider("node_min_support (min item count)", 5, 100, 20, step=1)
    edge_min_pair_count = st.slider("edge_min_pair_count (min co-mentions)", 2, 50, 12, step=1)
    edge_min_jaccard = st.slider("edge_min_jaccard (min normalized strength)", 0.00, 0.30, 0.10, step=0.01)
    max_edges = st.slider("max_edges (cap for performance)", 200, 5000, 1500, step=100)

# Jaccard helper

def jaccard(a, b):
    key = (a, b) if (a, b) in pairs else (b, a)
    inter = pairs.get(key, 0)
    denom = freq[a] + freq[b] - inter
    return inter / denom if denom else 0.0

# Colors per type (add 'heroe' explicitly)
TYPE_COLORS = {
    "heroe": "#4cc9f0",  # dataset's spelling
    "hero": "#4cc9f0",
    "villain": "#ef233c",
    "planet": "#2ecc71",
    "film": "#ffd166",
    "spaceship": "#9b59b6",
    "soundtrack": "#f39c12",
    "robot": "#95a5a6",
}
DEFAULT_NODE_COLOR = "#c8d6e5"

# -------------------------------
# Build the graph HTML
# -------------------------------

def build_galaxy_html(include_types, node_min_support, edge_min_pair_count, edge_min_jaccard, max_edges):
    if not include_types:
        return "<p style='color:#fff'>Select at least one type.</p>"

    # Filter allowed nodes by support and type
    allowed = {it for it in freq if item_types.get(it) in include_types and freq[it] >= node_min_support}

    # Gather edges meeting thresholds
    edges = []
    for (a, b), inter in pairs.items():
        if inter < edge_min_pair_count:
            continue
        if a not in allowed or b not in allowed:
            continue
        jac = jaccard(a, b)
        if jac < edge_min_jaccard:
            continue
        edges.append((a, b, inter, jac))

    edges.sort(key=lambda x: (x[3], x[2]), reverse=True)
    edges = edges[:max_edges]

    if not edges:
        return "<p style='color:#fff'>No edges after thresholds. Loosen sliders and try again.</p>"

    net = Network(height="780px", width="100%", bgcolor="#000000", font_color="#ffffff", notebook=False)
    net.barnes_hut(gravity=-8000, central_gravity=0.28, spring_length=190, spring_strength=0.01, damping=0.9)

    # Add nodes
    for it in allowed:
        typ = item_types.get(it, "item")
        color = TYPE_COLORS.get(typ, DEFAULT_NODE_COLOR)
        label = raw_labels.get(it, it)
        size = 12 + 6 * math.log10(max(freq[it], 10))
        title = f"<b>{label}</b><br>Type: {typ}<br>Count: {freq[it]}"
        net.add_node(it, label=label, title=title, color=color, size=size)

    # Edge widths by Jaccard
    if edges:
        j_min = min(e[3] for e in edges)
        j_max = max(e[3] for e in edges)
        span = (j_max - j_min) or 1.0
    else:
        j_min = j_max = span = 1.0

    for a, b, inter, jac in edges:
        width = 1 + 8 * ((jac - j_min) / span)
        title = f"Co-mentions: {inter} • Jaccard: {jac:.3f}"
        net.add_edge(a, b, title=title, width=width)

    net.set_options(
        """
          const options = {
            nodes: { borderWidth: 1, shadow: true },
            edges: { color: { color: '#9aa3a7' }, smooth: { enabled: true, type: 'dynamic' } },
            physics: { solver: 'barnesHut', stabilization: { iterations: 200 } },
            interaction: { hover: true, dragNodes: true, dragView: true, zoomView: true }
          }
        """
    )

    # write to temp file and return HTML string
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
# Render
# -------------------------------
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.subheader("Galaxy")
    html = build_galaxy_html(include_types, node_min_support, edge_min_pair_count, edge_min_jaccard, max_edges)
    components.html(html, height=800, scrolling=True)

with col_right:
    st.subheader("Neighbor explorer")
    st.caption("Type an item label (e.g., Luke Skywalker, Tatooine, Millennium Falcon) to see its strongest neighbors by Jaccard.")
    q = st.text_input("Item label", value="")
    k = st.slider("Top K neighbors", 3, 20, 8)
    min_pair = st.slider("Min pair_count (for neighbors)", 1, 50, 10)

    def resolve_label_to_tag(label: str):
        # exact match on raw label; fall back to case-insensitive contains
        exact = [t for t, lbl in raw_labels.items() if lbl == label]
        if exact:
            return exact[0]
        if label:
            cand = [t for t, lbl in raw_labels.items() if label.lower() in lbl.lower()]
            return cand[0] if cand else None
        return None

    if q:
        tag = resolve_label_to_tag(q)
        if tag is None:
            st.info("No matching item found. Check spelling or try a shorter substring.")
        else:
            rows = []
            for (a, b), inter in pairs.items():
                if inter < min_pair:
                    continue
                x, y = (a, b) if a == tag else ((b, a) if b == tag else (None, None))
                if x is None:
                    continue
                rows.append({
                    "neighbor_label": raw_labels.get(y, y),
                    "neighbor_type": item_types.get(y, "item"),
                    "pair_count": inter,
                    "jaccard": jaccard(tag, y),
                })
            if rows:
                out = (
                    pd.DataFrame(rows)
                    .sort_values(["jaccard", "pair_count"], ascending=False)
                    .head(k)
                    .reset_index(drop=True)
                )
                st.dataframe(out, width='stretch')
            else:
                st.write("No neighbors at these thresholds.")

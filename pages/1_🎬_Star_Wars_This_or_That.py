import streamlit as st
import json
import os

st.set_page_config(page_title="Star Wars This or That", page_icon="✨", layout="wide")

# -----------------------
# Styling (Star Wars vibe)
# -----------------------
st.markdown(
    """
    <style>
    .sw-title { 
        font-family: monospace; font-weight: 700; 
        text-transform: uppercase; letter-spacing: 4px; 
        background: linear-gradient(45deg, #FFE81F, #FFF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .choice-btn {
        background: rgba(0,0,0,0.85);
        border: 2px solid #FFE81F; color: #fff;
        border-radius: 14px; padding: 28px 20px; width: 100%;
        font-size: 1.2rem; text-transform: uppercase; letter-spacing: 2px;
        box-shadow: 0 0 20px rgba(255,232,31,0.25), inset 0 0 20px rgba(255,232,31,0.08);
    }
    .next-btn {
        background: linear-gradient(45deg, #FFE81F, #FFA500);
        color: #000; border: none; border-radius: 30px; padding: 14px 36px;
        font-weight: 700; letter-spacing: 1px;
    }
    .metric-pill {
        background: rgba(255, 232, 31, 0.08); border: 1px solid #FFE81F; 
        border-radius: 999px; padding: 6px 14px; font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------
# Data
# -----------------------
categories = [
    {"name": "Favorite Hero", "key": "fav_heroe", "options": [
        "Anakin Skywalker", "Luke Skywalker", "Yoda", "Han Solo", "Obi-Wan Kenobi", "Chewbacca", "Leia", "Qui-Gon Jinn", "Jar Jar Binks"
    ]},
    {"name": "Favorite Villain", "key": "fav_villain", "options": [
        "Darth Maul", "Count Dooku", "Wilhuff Tarkin", "Palpatine", "Darth Vader", "General Grievous"
    ]},
    {"name": "Favorite Film", "key": "fav_film", "options": [
        "Episode IV - A New Hope", "Episode V - The Empire Strikes Back", "Episode VI - Return of the Jedi", 
        "Episode I - The Phantom Menace", "Episode III - Revenge of the Sith", "Episode II - Attack of the Clones"
    ]},
    {"name": "Favorite Soundtrack", "key": "fav_soundtrack", "options": [
        "Across the Stars", "The Throne Room", "Star Wars (Main Theme)", "Imperial March", "Anakin vs. Obi-Wan"
    ]},
    {"name": "Favorite Spaceship", "key": "fav_spaceship", "options": [
        "Naboo Starfighter", "Millennium Falcon", "TIE Fighter", "Death Star"
    ]},
    {"name": "Favorite Planet", "key": "fav_planet", "options": [
        "Tatooine", "Endor", "Naboo", "Dagobah", "Alderaan"
    ]},
    {"name": "Favorite Robot", "key": "fav_robot", "options": [
        "R2-D2", "Battle Droid", "C-3PO", "Droideka"
    ]},
]

# -----------------------
# Session State
# -----------------------
if "sw_idx" not in st.session_state:
    st.session_state.sw_idx = 0                     # which category
if "sw_queue" not in st.session_state:
    st.session_state.sw_queue = []                 # remaining options for current category
if "sw_current" not in st.session_state:
    st.session_state.sw_current = (None, None)     # (left, right)
if "sw_selected" not in st.session_state:
    st.session_state.sw_selected = None            # which of the two was chosen
if "sw_results" not in st.session_state:
    st.session_state.sw_results = {}               # key -> winner


def start_or_reset_category():
    cat = categories[st.session_state.sw_idx]
    st.session_state.sw_queue = list(cat["options"])  # copy
    # start with two
    left = st.session_state.sw_queue.pop(0)
    right = st.session_state.sw_queue.pop(0)
    st.session_state.sw_current = (left, right)
    st.session_state.sw_selected = None


def choose(side: str):
    left, right = st.session_state.sw_current
    winner = left if side == "left" else right
    # if more options remain, replace the losing side and continue the bracket
    if st.session_state.sw_queue:
        if side == "left":
            # left stays, right replaced
            right = st.session_state.sw_queue.pop(0)
        else:
            # right stays, left replaced
            left = st.session_state.sw_queue.pop(0)
        st.session_state.sw_current = (left, right)
        st.session_state.sw_selected = None
    else:
        # category finished, store the winner
        cat = categories[st.session_state.sw_idx]
        st.session_state.sw_results[cat["key"]] = winner
        st.session_state.sw_selected = winner


def go_next():
    # Move to next category or finish
    if st.session_state.sw_selected is None:
        return
    st.session_state.sw_idx += 1
    if st.session_state.sw_idx < len(categories):
        start_or_reset_category()
    else:
        # Completed all categories
        pass


def restart():
    st.session_state.sw_idx = 0
    st.session_state.sw_results = {}
    start_or_reset_category()


# Initialize first category on first load
if st.session_state.sw_current == (None, None):
    start_or_reset_category()

# -----------------------
# UI
# -----------------------
st.markdown("<h1 class='sw-title'>Star Wars — This or That</h1>", unsafe_allow_html=True)

if st.session_state.sw_idx < len(categories):
    cat = categories[st.session_state.sw_idx]
    left, right = st.session_state.sw_current

    top_c1, top_c2 = st.columns([3, 1])
    with top_c1:
        st.markdown(f"<span class='metric-pill'>Category {st.session_state.sw_idx + 1} of {len(categories)}</span>", unsafe_allow_html=True)
        st.subheader(cat["name"]) 

    # Two choices side by side
    c1, c2 = st.columns(2)
    with c1:
        if st.button(left, key=f"left_{st.session_state.sw_idx}_{left}", use_container_width=True):
            choose("left")
    with c2:
        if st.button(right, key=f"right_{st.session_state.sw_idx}_{right}", use_container_width=True):
            choose("right")

    # Show Next only when a category winner exists (i.e., when queue exhausted)
    if st.session_state.sw_selected is not None:
        st.success(f"Winner: {st.session_state.sw_selected}")
        st.button("Next", on_click=go_next, type="primary")
else:
    # Completed
    st.markdown("## 🌟 The Force Has Spoken!")
    st.write("Your preferences have been logged.")

    # Vector in fixed order of keys
    ordered_keys = [c["key"] for c in categories]
    vector = [st.session_state.sw_results.get(k) for k in ordered_keys]

    st.markdown("**Result Vector (ordered by categories):**")
    st.write(vector)

    # Persist in session_state for later use by other pages
    st.session_state.star_wars_vector = vector

    # Download as JSON
    payload = {
        "vector": vector,
        "mapping": {k: st.session_state.sw_results.get(k) for k in ordered_keys},
    }
    # Save to file for reuse across sessions
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, "star_wars_vector.json"), "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        st.info("Saved to data/star_wars_vector.json")
    except Exception as e:
        st.warning(f"Could not save vector to file: {e}")
    st.download_button(
        label="Download Results (JSON)",
        data=json.dumps(payload, indent=2).encode("utf-8"),
        file_name="star_wars_vector.json",
        mime="application/json",
    )

    st.button("Restart", on_click=restart)

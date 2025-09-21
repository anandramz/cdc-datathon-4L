import pandas as pd
import joblib
from pathlib import Path
from sklearn.preprocessing import OneHotEncoder, normalize
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

# --- Model artifacts paths ---
KMEANS_MODEL_PATH = MODELS_DIR / "kmeans_model.joblib"
ENCODER_PATH = MODELS_DIR / "encoder.joblib"
TOP_FEATURES_PATH = MODELS_DIR / "top_features.joblib"


def get_top_features_by_cart(df, target_col, feature_cols, n_features=8):
    """Trains a CART model to find the most predictive features."""
    X = df[feature_cols].astype(str)
    y = df[target_col].astype(str)
    
    # One-hot encode features
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    X_enc = encoder.fit_transform(X)
    
    # Train a Decision Tree to get feature importances
    tree = DecisionTreeClassifier(max_depth=5, random_state=42)
    tree.fit(X_enc, y)
    
    importances = tree.feature_importances_
    feat_names = encoder.get_feature_names_out(feature_cols)
    
    feat_imp = pd.Series(importances, index=feat_names).sort_values(ascending=False)
    
    top_features = feat_imp.head(n_features).index.tolist()
    
    return top_features, encoder


def train_and_save_clustering_model(n_features=8):
    """Full pipeline to train the clustering model and save artifacts."""
    print("Starting clustering model training...")
    
    # 1. Load data
    try:
        df = pd.read_csv(DATA_DIR / "starwars.csv")
        print(f"Loaded data: {df.shape}")
    except FileNotFoundError:
        print(f"Error: starwars.csv not found in {DATA_DIR}")
        return None, None, None

    # 2. Define features and target
    feature_cols = ["fav_heroe", "fav_villain", "fav_soundtrack", 
                    "fav_spaceship", "fav_planet", "fav_robot"]
    target_col = "fav_film"
    
    # 3. Get top features using CART
    print(f"Identifying top {n_features} features using CART...")
    top_features, encoder = get_top_features_by_cart(df, target_col, feature_cols, n_features)
    print(f"Top features identified: {top_features}")
    
    # 4. Prepare data for clustering
    X = df[feature_cols].astype(str)
    X_enc = encoder.transform(X)
    all_feature_names = encoder.get_feature_names_out(feature_cols)
    
    # Get indices of top features
    top_idx = [list(all_feature_names).index(f) for f in top_features]
    X_top = X_enc[:, top_idx]
    
    # Normalize for cosine distance
    Xn = normalize(X_top)
    
    # 5. Find optimal k and train KMeans
    print("Finding optimal k for KMeans...")
    best = None
    for k in range(3, 10):
        km = KMeans(n_clusters=k, n_init='auto', random_state=42).fit(Xn)
        s = silhouette_score(Xn, km.labels_, metric="cosine")
        if best is None or s > best[0]:
            best = (s, k, km)
    
    sil, k, kmeans_model = best
    print(f"Best clustering found: k={k} with silhouette score={sil:.3f}")
    
    # 6. Save model, encoder, and top features
    print(f"Saving artifacts to {MODELS_DIR}...")
    joblib.dump(kmeans_model, KMEANS_MODEL_PATH)
    joblib.dump(encoder, ENCODER_PATH)
    joblib.dump(top_features, TOP_FEATURES_PATH)
    
    print("✅ Training complete and artifacts saved.")
    return kmeans_model, encoder, top_features


def load_clustering_artifacts():
    """Loads the saved clustering model, encoder, and feature list."""
    if not all([KMEANS_MODEL_PATH.exists(), ENCODER_PATH.exists(), TOP_FEATURES_PATH.exists()]):
        print("Model artifacts not found. Please train the model first.")
        return None, None, None
    
    kmeans_model = joblib.load(KMEANS_MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)
    top_features = joblib.load(TOP_FEATURES_PATH)
    
    print("✅ Clustering artifacts loaded successfully.")
    return kmeans_model, encoder, top_features


def predict_cluster(user_preferences, kmeans_model, encoder, top_features):
    """
    Predicts the cluster for a new user based on their preferences.
    
    Args:
        user_preferences (dict): A dictionary where keys are feature columns 
                                 (e.g., 'fav_heroe') and values are the user's choices.
        kmeans_model: The trained KMeans model.
        encoder: The fitted OneHotEncoder.
        top_features (list): The list of top features used for clustering.

    Returns:
        int: The predicted cluster ID.
    """
    # Create a DataFrame from user preferences
    user_df = pd.DataFrame([user_preferences])
    
    # Ensure all feature columns are present
    feature_cols = ["fav_heroe", "fav_villain", "fav_soundtrack", 
                    "fav_spaceship", "fav_planet", "fav_robot"]
    for col in feature_cols:
        if col not in user_df.columns:
            user_df[col] = "None" # Or some other default/null value
            
    user_df = user_df[feature_cols].astype(str)
    
    # One-hot encode the user data
    user_enc = encoder.transform(user_df)
    all_feature_names = encoder.get_feature_names_out(feature_cols)
    
    # Select only the top features
    top_idx = [list(all_feature_names).index(f) for f in top_features]
    user_top = user_enc[:, top_idx]
    
    # Normalize and predict
    user_norm = normalize(user_top)
    cluster = kmeans_model.predict(user_norm)[0]
    
    return cluster


# --- Example Usage (for testing) ---
def analyze_clusters():
    """Analyzes the dataset to find the defining characteristics of each cluster."""
    print("Analyzing cluster characteristics...")
    
    # 1. Load artifacts and data
    kmeans_model, encoder, top_features = load_clustering_artifacts()
    if kmeans_model is None:
        return None, None

    try:
        df = pd.read_csv(DATA_DIR / "starwars.csv")
    except FileNotFoundError:
        print(f"Error: starwars.csv not found in {DATA_DIR}")
        return None, None

    # 2. Assign clusters to the full dataset
    feature_cols = ["fav_heroe", "fav_villain", "fav_soundtrack", 
                    "fav_spaceship", "fav_planet", "fav_robot"]
    X = df[feature_cols].astype(str)
    X_enc = encoder.transform(X)
    all_feature_names = encoder.get_feature_names_out(feature_cols)
    
    top_idx = [list(all_feature_names).index(f) for f in top_features]
    X_top = X_enc[:, top_idx]
    Xn = normalize(X_top)
    
    df['cluster'] = kmeans_model.predict(Xn)
    print("Assigned clusters to the full dataset.")

    # 3. Analyze each cluster
    cluster_summary = {}
    num_clusters = kmeans_model.n_clusters

    for i in range(num_clusters):
        cluster_df = df[df['cluster'] == i]
        summary = {
            'size': len(cluster_df),
            'percentage': 100 * len(cluster_df) / len(df),
            'top_answers': {}
        }
        
        for col in feature_cols:
            # Get top 3 most common answers and their percentage
            counts = cluster_df[col].value_counts().nlargest(3)
            percentages = 100 * counts / len(cluster_df)
            summary['top_answers'][col] = list(zip(counts.index, counts, percentages))
            
        cluster_summary[i] = summary
    
    print("✅ Cluster analysis complete.")
    return cluster_summary, num_clusters


if __name__ == '__main__':
    # Train the model if artifacts don't exist
    if not KMEANS_MODEL_PATH.exists():
        train_and_save_clustering_model()
    
    # Load the artifacts
    model, enc, features = load_clustering_artifacts()
    
    if model:
        # Example user
        new_user = {
            'fav_heroe': 'Luke Skywalker',
            'fav_villain': 'Darth Vader',
            'fav_soundtrack': 'The Imperial March',
            'fav_spaceship': 'Millennium Falcon',
            'fav_planet': 'Tatooine',
            'fav_robot': 'R2-D2'
        }
        
        predicted_cluster = predict_cluster(new_user, model, enc, features)
        print(f"\nExample user preferences: {new_user}")
        print(f"Predicted cluster: {predicted_cluster}")
        
        # Another example user
        new_user_2 = {
            'fav_heroe': 'Anakin Skywalker',
            'fav_villain': 'Darth Maul',
            'fav_soundtrack': 'Duel of the Fates',
            'fav_spaceship': 'TIE Fighter',
            'fav_planet': 'Naboo',
            'fav_robot': 'C-3PO'
        }
        
        predicted_cluster_2 = predict_cluster(new_user_2, model, enc, features)
        print(f"\nExample user preferences: {new_user_2}")
        print(f"Predicted cluster: {predicted_cluster_2}")

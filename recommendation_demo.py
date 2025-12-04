import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load data
products = pd.read_csv("products.csv")
ratings = pd.read_csv("ratings.csv")

# --- Content-based model ---
def build_product_profiles(df_products):
    # Create a text field combining name, category, brand, price bucket, and rating
    def price_bucket(p):
        if p < 500: return "very_cheap"
        if p < 1500: return "cheap"
        if p < 4000: return "midrange"
        if p < 10000: return "expensive"
        return "luxury"
    df = df_products.copy()
    df['price_bucket'] = df['price'].apply(price_bucket)
    df['profile'] = (df['product_name'].fillna('') + ' ' +
                     df['category'].fillna('') + ' ' +
                     df['brand'].fillna('') + ' ' +
                     df['price_bucket'] + ' ' +
                     df['rating'].astype(str))
    return df[['product_id','profile']].set_index('product_id')

def content_recommend(product_id, topn=5):
    profiles = build_product_profiles(products)
    tfidf = TfidfVectorizer(stop_words='english')
    X = tfidf.fit_transform(profiles['profile'])
    ids = profiles.index.tolist()
    idx = ids.index(product_id)
    sim = cosine_similarity(X[idx], X).flatten()
    pairs = list(zip(ids, sim))
    pairs = sorted(pairs, key=lambda x: x[1], reverse=True)
    recommended = [pid for pid, score in pairs if pid != product_id][:topn]
    return products[products['product_id'].isin(recommended)][['product_id','product_name','category','brand','price']]

# --- Collaborative Filtering (user-based) ---
def build_user_item_matrix(df_ratings):
    return df_ratings.pivot_table(index='user_id', columns='product_id', values='rating').fillna(0)

def predict_ratings_user_based(user_id, user_item_matrix, topn=5):
    # compute user similarity
    from sklearn.metrics.pairwise import cosine_similarity
    sim = cosine_similarity(user_item_matrix)
    sim_df = pd.DataFrame(sim, index=user_item_matrix.index, columns=user_item_matrix.index)
    # weighted sum of ratings
    if user_id not in user_item_matrix.index:
        return pd.DataFrame([], columns=['product_id','predicted_rating'])
    user_ratings = user_item_matrix.loc[user_id].values.reshape(1, -1)
    weights = sim_df.loc[user_id].values.reshape(1, -1)
    pred = weights.dot(user_item_matrix.values) / (np.abs(weights).sum() + 1e-8)
    pred = pred.flatten()
    preds = pd.Series(pred, index=user_item_matrix.columns)
    # exclude already rated items
    rated = user_item_matrix.loc[user_id] > 0
    preds = preds[~rated]
    top = preds.sort_values(ascending=False).head(topn)
    return products[products['product_id'].isin(top.index)][['product_id','product_name','category','brand','price']]

# --- Hybrid recommendation ---
def hybrid_recommend_for_user(user_id, topn=5, alpha=0.6):
    # alpha weight for collaborative, (1-alpha) for content
    uim = build_user_item_matrix(ratings)
    cf_candidates = predict_ratings_user_based(user_id, uim, topn=20)
    # Score CF candidates by predicted rating (we'll compute predicted rating scores)
    # For simplicity, use CF predicted ranking + content similarity to user's top-rated product
    if user_id not in uim.index:
        return content_recommend(products['product_id'].iloc[0], topn=topn)
    # Find user's top rated product (if any)
    user_rated = ratings[ratings['user_id']==user_id].sort_values('rating', ascending=False)
    if user_rated.empty:
        return content_recommend(products['product_id'].iloc[0], topn=topn)
    favorite_pid = user_rated.iloc[0]['product_id']
    # content scores relative to favorite
    profiles = build_product_profiles(products)
    tfidf = TfidfVectorizer(stop_words='english')
    X = tfidf.fit_transform(profiles['profile'])
    ids = profiles.index.tolist()
    fav_idx = ids.index(favorite_pid)
    content_sims = cosine_similarity(X[fav_idx], X).flatten()
    content_series = pd.Series(content_sims, index=ids)
    # CF predicted ratings for all products (simple approach)
    sim = cosine_similarity(uim)
    sim_df = pd.DataFrame(sim, index=uim.index, columns=uim.index)
    weights = sim_df.loc[user_id].values.reshape(1, -1)
    pred = weights.dot(uim.values) / (np.abs(weights).sum() + 1e-8)
    preds = pd.Series(pred.flatten(), index=uim.columns)
    # normalize scores
    cf_norm = (preds - preds.min()) / (preds.max() - preds.min() + 1e-8)
    content_norm = (content_series - content_series.min()) / (content_series.max() - content_series.min() + 1e-8)
    hybrid_score = alpha * cf_norm.reindex(products['product_id']).fillna(0) + (1-alpha) * content_norm.reindex(products['product_id']).fillna(0)
    hybrid_top = hybrid_score.sort_values(ascending=False).head(topn).index.tolist()
    return products[products['product_id'].isin(hybrid_top)][['product_id','product_name','category','brand','price']]

# Example usage
if __name__ == "__main__":
    print("Content-based recommendations for product_id=1:")
    print(content_recommend(1, topn=5).to_string(index=False))
    uim = build_user_item_matrix(ratings)
    print("\\nCF recommendations for user_id=110:")
    print(predict_ratings_user_based(110, uim, topn=5).to_string(index=False))
    print("\\nHybrid recommendations for user_id=110:")
    print(hybrid_recommend_for_user(110, topn=5).to_string(index=False))

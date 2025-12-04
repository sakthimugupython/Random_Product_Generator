import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import json

class RecommendationEngine:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.products = None
        self.users = None
        self.transactions = None
        self.ratings = None
        self.tfidf_matrix = None
        self.user_item_matrix = None
        self.product_similarity = None
        self.user_similarity = None
        self.load_data()
        self.build_models()

    def load_data(self):
        """Load CSV files once at startup"""
        try:
            self.products = pd.read_csv(os.path.join(self.data_dir, 'products.csv'))
            self.users = pd.read_csv(os.path.join(self.data_dir, 'users.csv'))
            self.transactions = pd.read_csv(os.path.join(self.data_dir, 'transactions.csv'))
            self.ratings = pd.read_csv(os.path.join(self.data_dir, 'ratings.csv'))
            print("Data loaded successfully")
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def build_models(self):
        """Build TF-IDF and collaborative filtering models"""
        self._build_tfidf_model()
        self._build_user_item_matrix()
        self._build_user_similarity()

    def _build_tfidf_model(self):
        """Build TF-IDF model for content-based filtering"""
        try:
            # Combine product attributes
            self.products['combined_features'] = (
                self.products.get('product_name', '').fillna('').astype(str) + ' ' +
                self.products.get('category', '').fillna('').astype(str) + ' ' +
                self.products.get('brand', '').fillna('').astype(str)
            )
            
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            self.tfidf_matrix = vectorizer.fit_transform(self.products['combined_features'])
            self.product_similarity = cosine_similarity(self.tfidf_matrix)
            print("TF-IDF model built successfully")
        except Exception as e:
            print(f"Error building TF-IDF model: {e}")

    def _build_user_item_matrix(self):
        """Build user-item rating matrix for collaborative filtering"""
        try:
            if self.ratings is not None and len(self.ratings) > 0:
                self.user_item_matrix = self.ratings.pivot_table(
                    index='user_id',
                    columns='product_id',
                    values='rating',
                    fill_value=0
                )
                print("User-item matrix built successfully")
            else:
                print("No ratings data available")
        except Exception as e:
            print(f"Error building user-item matrix: {e}")

    def _build_user_similarity(self):
        """Build user similarity matrix using cosine similarity"""
        try:
            if self.user_item_matrix is not None and self.user_item_matrix.shape[0] > 0:
                self.user_similarity = cosine_similarity(self.user_item_matrix)
                print("User similarity matrix built successfully")
        except Exception as e:
            print(f"Error building user similarity: {e}")

    def get_content_based_recommendations(self, product_id, n_recommendations=5):
        """Content-based filtering using TF-IDF similarity"""
        try:
            product_idx = self.products[self.products['product_id'] == product_id].index
            if len(product_idx) == 0:
                return []
            
            product_idx = product_idx[0]
            sim_scores = list(enumerate(self.product_similarity[product_idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:n_recommendations + 1]
            
            product_indices = [i[0] for i in sim_scores]
            recommendations = self.products.iloc[product_indices].copy()
            recommendations = recommendations.rename(columns={
                'product_id': 'id',
                'product_name': 'name'
            })
            
            return recommendations.to_dict('records')
        except Exception as e:
            print(f"Error in content-based recommendations: {e}")
            return []

    def get_collaborative_recommendations(self, user_id, n_recommendations=5):
        """User-based collaborative filtering"""
        try:
            if self.user_item_matrix is None or user_id not in self.user_item_matrix.index:
                # If user not in matrix, return popular products
                return self._get_popular_products(n_recommendations)
            
            user_idx = self.user_item_matrix.index.get_loc(user_id)
            user_similarities = self.user_similarity[user_idx]
            
            # Get top similar users (excluding self)
            similar_users_idx = user_similarities.argsort()[::-1][1:10]
            
            if len(similar_users_idx) == 0:
                return self._get_popular_products(n_recommendations)
            
            similar_users = self.user_item_matrix.index[similar_users_idx]
            similar_users_ratings = self.user_item_matrix.loc[similar_users]
            
            user_ratings = self.user_item_matrix.loc[user_id]
            unrated_products = user_ratings[user_ratings == 0].index
            
            recommendations = []
            for product_id in unrated_products:
                # Get ratings from similar users for this product
                product_ratings = similar_users_ratings[product_id]
                rated_count = (product_ratings > 0).sum()
                
                if rated_count > 0:
                    avg_rating = product_ratings[product_ratings > 0].mean()
                    recommendations.append({
                        'product_id': product_id,
                        'predicted_rating': float(avg_rating),
                        'rated_by': int(rated_count)
                    })
            
            # Sort by predicted rating and number of ratings
            recommendations = sorted(
                recommendations, 
                key=lambda x: (x['predicted_rating'], x['rated_by']), 
                reverse=True
            )
            recommendations = recommendations[:n_recommendations]
            
            if not recommendations:
                return self._get_popular_products(n_recommendations)
            
            # Merge with product details
            product_ids = [r['product_id'] for r in recommendations]
            product_details = self.products[self.products['product_id'].isin(product_ids)].copy()
            product_details = product_details.rename(columns={
                'product_id': 'id',
                'product_name': 'name'
            })
            
            return product_details.to_dict('records')
        except Exception as e:
            print(f"Error in collaborative recommendations: {e}")
            return self._get_popular_products(n_recommendations)
    
    def _get_popular_products(self, n_recommendations=5):
        """Get top-rated products as fallback"""
        try:
            popular = self.products.nlargest(n_recommendations, 'rating').copy()
            popular = popular.rename(columns={
                'product_id': 'id',
                'product_name': 'name'
            })
            return popular.to_dict('records')
        except Exception as e:
            print(f"Error getting popular products: {e}")
            return []

    def get_hybrid_recommendations(self, user_id, n_recommendations=5):
        """Hybrid model combining content-based and collaborative filtering"""
        try:
            # Get user's rated products to understand preferences
            user_preferences = self._get_user_preferences(user_id)
            
            # Get collaborative recommendations
            collab_recs = self.get_collaborative_recommendations(user_id, n_recommendations * 3)
            
            if not collab_recs:
                return []
            
            # For each collaborative recommendation, get similar products
            hybrid_recs = {}
            for product in collab_recs:
                product_id = product.get('id') or product.get('product_id')
                
                # Add the collaborative recommendation itself
                if product_id not in hybrid_recs:
                    hybrid_recs[product_id] = product
                
                # Get similar products based on content
                similar = self.get_content_based_recommendations(product_id, 1)
                for sim_product in similar:
                    sim_id = sim_product.get('id') or sim_product.get('product_id')
                    if sim_id not in hybrid_recs and sim_id not in user_preferences:
                        hybrid_recs[sim_id] = sim_product
            
            # Return top N, excluding already-rated products
            result = [p for pid, p in hybrid_recs.items() if pid not in user_preferences][:n_recommendations]
            return result
        except Exception as e:
            print(f"Error in hybrid recommendations: {e}")
            return []
    
    def _get_user_preferences(self, user_id):
        """Get products already rated by user"""
        try:
            if self.user_item_matrix is None or user_id not in self.user_item_matrix.index:
                return set()
            
            user_ratings = self.user_item_matrix.loc[user_id]
            rated_products = set(user_ratings[user_ratings > 0].index)
            return rated_products
        except Exception as e:
            print(f"Error getting user preferences: {e}")
            return set()

# Global engine instance
_engine = None

def get_engine():
    """Get or create the recommendation engine"""
    global _engine
    if _engine is None:
        _engine = RecommendationEngine()
    return _engine

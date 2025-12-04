# Product Recommendation Engine - Django AI/ML Project

A complete AI/ML-based product recommendation system built with Django, featuring content-based filtering, collaborative filtering, and a hybrid recommendation model.

## Project Structure

```
.
├── data/                          # CSV datasets
│   ├── products.csv
│   ├── users.csv
│   ├── transactions.csv
│   └── ratings.csv
├── backend/                       # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── recommender/                   # Main recommendation app
│   ├── engine.py                  # ML recommendation engine
│   ├── views.py                   # API and frontend views
│   ├── urls.py                    # URL routing
│   ├── apps.py                    # App configuration
│   └── templates/
│       └── recommender/
│           ├── base.html          # Base template
│           ├── index.html         # Product listing page
│           └── product.html       # Product detail page
├── manage.py                      # Django management script
└── README.md
```

## Features

### 1. Content-Based Filtering
- Uses TF-IDF vectorization on product attributes (name, category, brand, price bucket)
- Computes cosine similarity between products
- Returns similar products based on product features
- **Endpoint:** `/api/recommend/similar/<product_id>/`

### 2. User-Based Collaborative Filtering
- Builds user-item rating matrix from ratings data
- Computes user similarity using cosine similarity
- Recommends products rated highly by similar users
- Filters out already-rated products

### 3. Hybrid Model
- Combines collaborative filtering with content-based recommendations
- Gets collaborative recommendations for a user
- Finds similar products to those recommendations
- Provides diverse, personalized recommendations
- **Endpoint:** `/api/recommend/user/<user_id>/`

### 4. Frontend Features
- Product catalog with search and category filtering
- Product detail pages with recommendations
- Responsive Bootstrap UI
- Real-time API integration
- User-specific recommendation section

## Installation & Setup

### 1. Install Dependencies
```bash
pip install django scikit-learn pandas numpy
```

### 2. Prepare Data
Ensure CSV files are in the `data/` folder:
- `products.csv` - Product information
- `users.csv` - User information
- `transactions.csv` - Transaction history
- `ratings.csv` - User ratings (user_id, product_id, rating)

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Start Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000/`

## API Endpoints

### Get Similar Products (Content-Based)
```
GET /api/recommend/similar/<product_id>/?n=5
```
**Response:**
```json
{
  "status": "success",
  "product_id": 1,
  "recommendations": [
    {
      "id": 2,
      "name": "Product Name",
      "category": "Category",
      "price": 99.99,
      "rating": 4.5
    }
  ]
}
```

### Get User Recommendations (Hybrid)
```
GET /api/recommend/user/<user_id>/?n=5
```
**Response:**
```json
{
  "status": "success",
  "user_id": 1,
  "recommendations": [
    {
      "id": 5,
      "name": "Recommended Product",
      "category": "Category",
      "price": 79.99,
      "rating": 4.8
    }
  ]
}
```

### Get All Products
```
GET /api/products/
```

### Get Product Details
```
GET /api/product/<product_id>/
```

## ML Engine Details

### RecommendationEngine Class (`engine.py`)

**Initialization:**
- Loads all CSV files once at startup
- Builds TF-IDF matrix for content-based filtering
- Creates user-item rating matrix
- Computes user similarity matrix

**Key Methods:**
- `get_content_based_recommendations(product_id, n)` - Content-based filtering
- `get_collaborative_recommendations(user_id, n)` - Collaborative filtering
- `get_hybrid_recommendations(user_id, n)` - Hybrid approach

**Performance:**
- Data loaded once at app startup (singleton pattern)
- Pre-computed similarity matrices for fast recommendations
- Efficient numpy/pandas operations

## CSV Data Format

### products.csv
```
id, name, category, brand, price, price_bucket, rating, description
```

### users.csv
```
id, name, email, signup_date
```

### ratings.csv
```
user_id, product_id, rating, timestamp
```

### transactions.csv
```
id, user_id, product_id, quantity, amount, date
```

## Frontend Pages

### Home Page (`/`)
- Displays all products in a grid
- Search functionality
- Category filtering
- Links to product detail pages

### Product Detail Page (`/product/<product_id>/`)
- Product information and specifications
- Similar products (content-based)
- Personalized recommendations (hybrid model)
- User ID input for custom recommendations

## Configuration

### Django Settings
- **DEBUG:** True (development)
- **ALLOWED_HOSTS:** [] (configure for production)
- **DATABASE:** SQLite (default)
- **INSTALLED_APPS:** Includes 'recommender' app

### Engine Configuration
- **Data Directory:** `data/` (relative to project root)
- **TF-IDF Features:** 100 max features
- **Recommendation Count:** Default 5 (customizable via API)

## Performance Considerations

1. **Data Loading:** All CSV files loaded once at startup
2. **Matrix Caching:** Similarity matrices pre-computed
3. **Vectorization:** TF-IDF matrix cached for reuse
4. **Scalability:** Suitable for datasets up to ~100k products/users

## Future Enhancements

- Matrix factorization (SVD) for better collaborative filtering
- Deep learning models (neural networks)
- Real-time model updates
- A/B testing framework
- User feedback loop
- Caching layer (Redis)
- Batch recommendation generation
- Admin dashboard for model monitoring

## Troubleshooting

### Engine not initializing
- Check that CSV files exist in `data/` folder
- Verify CSV column names match expected format
- Check console for error messages

### No recommendations returned
- Ensure user/product IDs exist in the data
- Check that ratings data is not empty
- Verify data quality and format

### Slow performance
- Reduce dataset size for testing
- Increase TF-IDF max_features if needed
- Consider implementing caching

## License

MIT License - Feel free to use and modify for your projects.

from django.urls import path
from . import views

app_name = 'recommender'

urlpatterns = [
    # Frontend pages
    path('', views.index, name='index'),
    path('product/<int:product_id>/', views.product_page, name='product_detail'),
    
    # API endpoints
    path('api/recommend/similar/<int:product_id>/', views.recommend_similar, name='recommend_similar'),
    path('api/recommend/user/<int:user_id>/', views.recommend_for_user, name='recommend_for_user'),
    path('api/products/', views.products_list, name='products_list'),
    path('api/product/<int:product_id>/', views.product_detail, name='product_api_detail'),
]

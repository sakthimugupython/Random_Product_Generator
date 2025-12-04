from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .engine import get_engine
import json

engine = get_engine()

def get_product_image(product_id=None, product_name=None):
    """Get product image URL based on product name mapping"""
    # Mapping of product names to image files
    product_image_map = {
        'Wireless Earbuds': '/static/images/product_1.png',
        'Bluetooth Speaker': '/static/images/product_2.png',
        'Smart Watch': '/static/images/product_3.png',
        'Fitness Band': '/static/images/product_4.png',
        'Laptop Backpack': '/static/images/product_5.png',
        "Men's Running Shoes": '/static/images/product_6.png',
        "Women's Casual Shoes": '/static/images/product_7.png',
        'Cotton T-Shirt': '/static/images/product_8.png',
        'Jeans': '/static/images/product_9.png',
        'DSLR Camera': '/static/images/product_10.png',
        'USB-C Cable': '/static/images/product_11.png',
        'Portable Hard Disk': '/static/images/product_12.png',
        'Oven Toaster Grill': '/static/images/product_13.png',
        'Mixer Grinder': '/static/images/product_14.png',
        'Induction Stove': '/static/images/product_15.png',
        'Pressure Cooker': '/static/images/product_16.png',
        'Office Chair': '/static/images/product_17.png',
        'Study Table': '/static/images/product_18.png',
        'Bed Mattress': '/static/images/product_19.png',
        'Table Lamp': '/static/images/product_20.png',
    }
    
    # Try to get image by product name
    if product_name and product_name in product_image_map:
        return product_image_map[product_name]
    
    # Fallback to generated images by product_id
    if product_id:
        return f'/static/images/product_{product_id}.jpg'
    
    # Default fallback
    return '/static/images/product_1.jpg'

@require_http_methods(["GET"])
def recommend_similar(request, product_id):
    """API endpoint for content-based recommendations"""
    try:
        n = int(request.GET.get('n', 5))
        recommendations = engine.get_content_based_recommendations(product_id, n)
        
        # Add image URLs to recommendations
        for rec in recommendations:
            product_name = rec.get('name') or rec.get('product_name')
            rec['image'] = get_product_image(product_name=product_name)
        
        return JsonResponse({
            'status': 'success',
            'product_id': product_id,
            'recommendations': recommendations
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_http_methods(["GET"])
def recommend_for_user(request, user_id):
    """API endpoint for hybrid recommendations"""
    try:
        n = int(request.GET.get('n', 5))
        recommendations = engine.get_hybrid_recommendations(user_id, n)
        
        # Add image URLs to recommendations
        for rec in recommendations:
            product_name = rec.get('name') or rec.get('product_name')
            rec['image'] = get_product_image(product_name=product_name)
        
        return JsonResponse({
            'status': 'success',
            'user_id': user_id,
            'recommendations': recommendations
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_http_methods(["GET"])
def products_list(request):
    """Get all products"""
    try:
        products_df = engine.products.copy()
        # Add image URL based on product name (local images)
        products_df['image'] = products_df['product_name'].apply(lambda name: get_product_image(product_name=name))
        # Rename columns for API consistency
        products_df = products_df.rename(columns={
            'product_id': 'id',
            'product_name': 'name'
        })
        products = products_df.to_dict('records')
        return JsonResponse({
            'status': 'success',
            'products': products
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_http_methods(["GET"])
def product_detail(request, product_id):
    """Get product details"""
    try:
        product_row = engine.products[engine.products['product_id'] == product_id]
        if product_row.empty:
            return JsonResponse({
                'status': 'error',
                'message': 'Product not found'
            }, status=404)
        
        product = product_row.iloc[0].to_dict()
        product_name = product.get('product_name', 'Product')
        # Rename for API consistency
        product['id'] = product.pop('product_id', product_id)
        product['name'] = product.pop('product_name', 'Product')
        # Add image URL based on product name
        product['image'] = get_product_image(product_name=product_name)
        
        return JsonResponse({
            'status': 'success',
            'product': product
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def index(request):
    """Frontend index page"""
    return render(request, 'recommender/index.html')

def product_page(request, product_id):
    """Product detail page"""
    return render(request, 'recommender/product.html', {'product_id': product_id})

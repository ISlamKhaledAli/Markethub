"""
DEPRECATED: Use the Django management command instead:

    python manage.py seed_data
    python manage.py seed_data --flush

This HTTP script remains for reference only.
"""
import requests
import sys
import json

BASE_URL = "http://127.0.0.1:8000/api"

def get_token(email, password):
    """Log in and return the JWT access token."""
    url = f"{BASE_URL}/auth/login/"
    try:
        response = requests.post(url, json={"email": email, "password": password})
        if response.status_code == 200:
            res_json = response.json()
            # The API wraps response in a 'data' key
            if "data" in res_json and "access" in res_json["data"]:
                return res_json["data"]["access"]
            return res_json.get('access')
        else:
            print(f"Failed to login: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Error during login: {e}")
        sys.exit(1)

def create_categories(token):
    """Create categories and return a mapping of {slug: id}."""
    url = f"{BASE_URL}/products/categories/"
    headers = {"Authorization": f"Bearer {token}"}
    
    categories = [
        {"name": "Electronics",   "slug": "electronics"},
        {"name": "Fashion",       "slug": "fashion"},
        {"name": "Home & Living", "slug": "home-living"},
        {"name": "Accessories",   "slug": "accessories"},
        {"name": "Footwear",      "slug": "footwear"},
        {"name": "Essentials",    "slug": "essentials"},
    ]
    
    category_map = {}
    
    # First, fetch existing categories to avoid conflicts and populate the map
    try:
        existing_res = requests.get(url)
        if existing_res.status_code == 200:
            res_data = existing_res.json()
            # Handle potential API wrapping in 'data' key
            items = res_data.get('data', res_data) if isinstance(res_data, dict) else res_data
            for cat in items:
                category_map[cat['slug']] = cat['id']
    except Exception as e:
        print(f"Warning: Could not fetch existing categories: {e}")

    print("\n--- Creating Categories ---")
    for cat_data in categories:
        if cat_data['slug'] in category_map:
            print(f"Skipped (already exists): {cat_data['name']}")
            continue
            
        try:
            response = requests.post(url, json=cat_data, headers=headers)
            if response.status_code == 201:
                res_json = response.json()
                new_cat = res_json.get('data', res_json)
                category_map[new_cat['slug']] = new_cat['id']
                print(f"Created category: {cat_data['name']} (id={new_cat['id']})")
            elif response.status_code == 400 and "slug" in response.text:
                print(f"Skipped (already exists): {cat_data['name']}")
            else:
                print(f"Error creating category {cat_data['name']}: {response.text}")
        except Exception as e:
            print(f"Exception creating category {cat_data['name']}: {e}")
            
    return category_map

def create_products(token, category_map):
    """Create 20 sample products."""
    url = f"{BASE_URL}/products/seller/my-products/"
    headers = {"Authorization": f"Bearer {token}"}
    
    products = [
        {
            "name": "Urban Shell Parka",
            "slug": "urban-shell-parka",
            "description": "A premium waterproof parka designed for modern urban environments. Features a slim fit silhouette with sealed seams and a detachable hood.",
            "category_slug": "fashion",
            "price": "245.00",
            "discount_price": None,
            "stock": 42,
        },
        {
            "name": "Supima Essential Tee",
            "slug": "supima-essential-tee",
            "description": "Crafted from 100% Supima cotton, this essential tee offers unmatched softness and durability. A wardrobe foundation piece.",
            "category_slug": "essentials",
            "price": "45.00",
            "discount_price": None,
            "stock": 150,
        },
        {
            "name": "Nexus Arc Frames",
            "slug": "nexus-arc-frames",
            "description": "Designer eyeglasses with a bold architectural silhouette. Lightweight titanium frame with UV-400 polarized lenses.",
            "category_slug": "accessories",
            "price": "225.00",
            "discount_price": "180.00",
            "stock": 28,
        },
        {
            "name": "Heritage Loafers",
            "slug": "heritage-loafers",
            "description": "Hand-stitched leather loafers inspired by classic British craftsmanship. Full-grain leather upper with leather sole.",
            "category_slug": "footwear",
            "price": "320.00",
            "discount_price": None,
            "stock": 19,
        },
        {
            "name": "ProMax Wireless Earbuds",
            "slug": "promax-wireless-earbuds",
            "description": "Active noise cancellation with 30-hour battery life. IPX5 water resistance and hi-res audio certification.",
            "category_slug": "electronics",
            "price": "199.00",
            "discount_price": "149.00",
            "stock": 75,
        },
        {
            "name": "Ceramic Pour-Over Set",
            "slug": "ceramic-pour-over-set",
            "description": "A handcrafted ceramic pour-over coffee set. Includes dripper, carafe, and a pack of natural filters. Minimalist design.",
            "category_slug": "home-living",
            "price": "89.00",
            "discount_price": None,
            "stock": 35,
        },
        {
            "name": "Merino Wool Scarf",
            "slug": "merino-wool-scarf",
            "description": "Ultra-fine 100% merino wool scarf. Naturally temperature-regulating, soft against skin, and machine washable.",
            "category_slug": "accessories",
            "price": "75.00",
            "discount_price": "55.00",
            "stock": 60,
        },
        {
            "name": "Running Pro X1",
            "slug": "running-pro-x1",
            "description": "High-performance running shoe with carbon fiber plate and responsive foam midsole. Engineered for marathon distances.",
            "category_slug": "footwear",
            "price": "180.00",
            "discount_price": None,
            "stock": 44,
        },
        {
            "name": "Smart Home Hub",
            "slug": "smart-home-hub",
            "description": "Central control hub for all your smart home devices. Compatible with 500+ devices, voice control, and energy monitoring.",
            "category_slug": "electronics",
            "price": "129.00",
            "discount_price": None,
            "stock": 22,
        },
        {
            "name": "Linen Throw Blanket",
            "slug": "linen-throw-blanket",
            "description": "Pre-washed stonewashed linen throw. Gets softer with every wash. Available in 6 earth tones.",
            "category_slug": "home-living",
            "price": "95.00",
            "discount_price": "70.00",
            "stock": 48,
        },
        {
            "name": "Structured Blazer",
            "slug": "structured-blazer",
            "description": "A modern single-breasted blazer in Japanese wool-blend fabric. Fully canvassed construction with interior pockets.",
            "category_slug": "fashion",
            "price": "385.00",
            "discount_price": None,
            "stock": 15,
        },
        {
            "name": "Titanium Mechanical Watch",
            "slug": "titanium-mechanical-watch",
            "description": "Swiss automatic movement in a lightweight titanium case. 200m water resistance, sapphire crystal glass.",
            "category_slug": "accessories",
            "price": "850.00",
            "discount_price": None,
            "stock": 8,
        },
        {
            "name": "Portable Laptop Stand",
            "slug": "portable-laptop-stand",
            "description": "Foldable aluminum laptop stand compatible with 10–17 inch screens. Ergonomic height adjustment, weighs only 280g.",
            "category_slug": "electronics",
            "price": "49.00",
            "discount_price": "35.00",
            "stock": 110,
        },
        {
            "name": "Canvas Weekender Bag",
            "slug": "canvas-weekender-bag",
            "description": "Heavy-duty waxed canvas weekender with full-grain leather handles and brass hardware. 40L capacity.",
            "category_slug": "accessories",
            "price": "165.00",
            "discount_price": None,
            "stock": 30,
        },
        {
            "name": "Organic Linen Shirt",
            "slug": "organic-linen-shirt",
            "description": "GOTS-certified organic linen shirt with a relaxed fit and mother-of-pearl buttons. Garment dyed in natural tones.",
            "category_slug": "fashion",
            "price": "115.00",
            "discount_price": "90.00",
            "stock": 55,
        },
        {
            "name": "Bamboo Desk Organizer",
            "slug": "bamboo-desk-organizer",
            "description": "Sustainably sourced bamboo desk organizer with 7 compartments. FSC-certified, natural finish.",
            "category_slug": "home-living",
            "price": "38.00",
            "discount_price": None,
            "stock": 80,
        },
        {
            "name": "Chelsea Boots",
            "slug": "chelsea-boots",
            "description": "Classic elastic-sided Chelsea boots in full-grain calf leather. Leather sole with rubber toe cap.",
            "category_slug": "footwear",
            "price": "275.00",
            "discount_price": "220.00",
            "stock": 25,
        },
        {
            "name": "4K Webcam Pro",
            "slug": "4k-webcam-pro",
            "description": "4K 30fps webcam with built-in ring light and dual noise-cancelling mics. Plug-and-play USB-C.",
            "category_slug": "electronics",
            "price": "89.00",
            "discount_price": None,
            "stock": 67,
        },
        {
            "name": "Cashmere Crew Neck",
            "slug": "cashmere-crew-neck",
            "description": "Grade-A Mongolian cashmere crew neck sweater. 2-ply construction for warmth without bulk.",
            "category_slug": "essentials",
            "price": "195.00",
            "discount_price": "155.00",
            "stock": 33,
        },
        {
            "name": "Aroma Diffuser Set",
            "slug": "aroma-diffuser-set",
            "description": "Ultrasonic aroma diffuser with 7-color LED ambient light. Includes 5 premium essential oil blends.",
            "category_slug": "home-living",
            "price": "65.00",
            "discount_price": None,
            "stock": 90,
        },
    ]

    print("\n--- Creating Products ---")
    for prod_data in products:
        category_slug = prod_data.pop('category_slug')
        category_id = category_map.get(category_slug)
        
        if not category_id:
            print(f"Skipping {prod_data['name']}: Category slug '{category_slug}' not found.")
            continue
            
        prod_data['category'] = category_id
        
        try:
            response = requests.post(url, json=prod_data, headers=headers)
            if response.status_code == 201:
                res_json = response.json()
                new_prod = res_json.get('data', res_json)
                print(f"Created product: {prod_data['name']} (id={new_prod.get('id')})")
            elif response.status_code == 400 and "slug" in response.text:
                print(f"Skipped (already exists): {prod_data['name']}")
            else:
                print(f"Error creating product {prod_data['name']}: {response.text}")
        except Exception as e:
            print(f"Exception creating product {prod_data['name']}: {e}")

if __name__ == "__main__":
    print("NexusCommerce Data Seed Script")
    print("---------------------------------")
    email = input("Admin Email: ")
    password = input("Admin Password: ")
    
    token = get_token(email, password)
    print("Logged in successfully.")
    
    category_map = create_categories(token)
    create_products(token, category_map)
    
    print("\nSeeding complete.")

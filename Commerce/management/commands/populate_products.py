import os
from django.core.management.base import BaseCommand
from Commerce.models import Category, Product
from django.conf import settings

class Command(BaseCommand):
    help = 'Populate database with sample products'

    def handle(self, *args, **kwargs):
        # Clear existing data (optional)
        Product.objects.all().delete()
        Category.objects.all().delete()

        # Create Categories
        categories_data = [
            {'name': 'Electronics', 'description': 'Latest gadgets and electronic devices'},
            {'name': 'Fashion', 'description': 'Clothing, shoes and accessories'},
            {'name': 'Groceries', 'description': 'Fresh food and household essentials'},
            {'name': 'Home & Kitchen', 'description': 'Furniture, decor and kitchenware'},
            {'name': 'Sports', 'description': 'Sports equipment and outdoor gear'},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = category

        # Sample Products Data
        products_data = [
            # ELECTRONICS
            {
                'name': 'iPhone 15 Pro',
                'description': 'Latest Apple iPhone with A17 Pro chip, titanium design, and advanced camera system. Features 6.1-inch Super Retina XDR display, 48MP main camera, and all-day battery life.',
                'price': 999.99,
                'category': categories['Electronics'],
                'stock': 25,
                'calories': None
            },
            {
                'name': 'Samsung Galaxy S24',
                'description': 'Powerful Android smartphone with AI features, 200MP camera, and Snapdragon 8 Gen 3 processor. Includes S Pen and 5000mAh battery.',
                'price': 849.99,
                'category': categories['Electronics'],
                'stock': 30,
                'calories': None
            },
            {
                'name': 'MacBook Air M3',
                'description': '13-inch laptop with Apple M3 chip, 8GB RAM, 256GB SSD. Ultra-thin design, Retina display, and 18-hour battery life.',
                'price': 1099.99,
                'category': categories['Electronics'],
                'stock': 15,
                'calories': None
            },
            {
                'name': 'Sony WH-1000XM5',
                'description': 'Industry-leading noise canceling headphones with 30-hour battery life, touch controls, and exceptional sound quality.',
                'price': 399.99,
                'category': categories['Electronics'],
                'stock': 40,
                'calories': None
            },
            {
                'name': 'iPad Air',
                'description': '10.9-inch Liquid Retina display, M1 chip, 64GB storage. Perfect for work, creativity, and entertainment.',
                'price': 599.99,
                'category': categories['Electronics'],
                'stock': 20,
                'calories': None
            },

            # FASHION
            {
                'name': 'Classic White Sneakers',
                'description': 'Versatile white leather sneakers with comfortable cushioning. Perfect for casual wear with jeans, shorts, or dresses.',
                'price': 89.99,
                'category': categories['Fashion'],
                'stock': 50,
                'calories': None
            },
            {
                'name': 'Denim Jacket',
                'description': 'Medium wash denim jacket with classic fit. Features button-front closure and chest pockets. Perfect for layering.',
                'price': 65.99,
                'category': categories['Fashion'],
                'stock': 35,
                'calories': None
            },
            {
                'name': 'Cotton T-Shirt Pack',
                'description': 'Pack of 3 basic cotton t-shirts in assorted colors. Soft, breathable fabric with crew neck design.',
                'price': 24.99,
                'category': categories['Fashion'],
                'stock': 100,
                'calories': None
            },
            {
                'name': 'Running Shoes',
                'description': 'Lightweight running shoes with responsive cushioning and breathable mesh upper. Ideal for jogging and gym workouts.',
                'price': 119.99,
                'category': categories['Fashion'],
                'stock': 40,
                'calories': None
            },
            {
                'name': 'Winter Parka',
                'description': 'Water-resistant winter coat with faux fur hood. Insulated with thermal padding to keep you warm in cold weather.',
                'price': 199.99,
                'category': categories['Fashion'],
                'stock': 25,
                'calories': None
            },

            # GROCERIES
            {
                'name': 'Organic Bananas',
                'description': 'Fresh organic bananas, rich in potassium and perfect for smoothies, baking, or healthy snacks.',
                'price': 0.99,
                'category': categories['Groceries'],
                'stock': 200,
                'calories': 105
            },
            {
                'name': 'Free-Range Eggs',
                'description': 'Dozen large free-range eggs from humanely raised chickens. Perfect for breakfast, baking, and cooking.',
                'price': 4.99,
                'category': categories['Groceries'],
                'stock': 80,
                'calories': 70
            },
            {
                'name': 'Whole Wheat Bread',
                'description': 'Freshly baked whole wheat bread with no artificial preservatives. High in fiber and perfect for sandwiches.',
                'price': 3.49,
                'category': categories['Groceries'],
                'stock': 60,
                'calories': 80
            },
            {
                'name': 'Fresh Salmon Fillet',
                'description': 'Atlantic salmon fillet, rich in omega-3 fatty acids. Perfect for grilling, baking, or pan-searing.',
                'price': 12.99,
                'category': categories['Groceries'],
                'stock': 30,
                'calories': 206
            },
            {
                'name': 'Organic Spinach',
                'description': 'Fresh organic spinach leaves, packed with iron and vitamins. Great for salads, smoothies, and cooking.',
                'price': 2.99,
                'category': categories['Groceries'],
                'stock': 75,
                'calories': 23
            },

            # HOME & KITCHEN
            {
                'name': 'Non-Stick Cookware Set',
                'description': '10-piece non-stick cookware set including pots, pans, and utensils. Dishwasher safe and oven safe up to 350°F.',
                'price': 149.99,
                'category': categories['Home & Kitchen'],
                'stock': 20,
                'calories': None
            },
            {
                'name': 'Memory Foam Pillow',
                'description': 'Queen-size memory foam pillow that contours to your head and neck. Hypoallergenic and machine washable.',
                'price': 39.99,
                'category': categories['Home & Kitchen'],
                'stock': 45,
                'calories': None
            },
            {
                'name': 'Ceramic Dinner Set',
                'description': '16-piece ceramic dinner set for 4 people. Includes dinner plates, salad plates, bowls, and mugs. Microwave and dishwasher safe.',
                'price': 79.99,
                'category': categories['Home & Kitchen'],
                'stock': 30,
                'calories': None
            },
            {
                'name': 'Air Purifier',
                'description': 'HEPA air purifier for rooms up to 500 sq ft. Removes 99.97% of dust, pollen, and airborne particles.',
                'price': 129.99,
                'category': categories['Home & Kitchen'],
                'stock': 15,
                'calories': None
            },
            {
                'name': 'Desk Lamp',
                'description': 'LED desk lamp with adjustable brightness and color temperature. USB charging port and touch controls.',
                'price': 34.99,
                'category': categories['Home & Kitchen'],
                'stock': 50,
                'calories': None
            },

            # SPORTS
            {
                'name': 'Yoga Mat',
                'description': 'Non-slip yoga mat with carrying strap. Extra thick for comfort during yoga, pilates, and floor exercises.',
                'price': 29.99,
                'category': categories['Sports'],
                'stock': 60,
                'calories': None
            },
            {
                'name': 'Dumbbell Set',
                'description': 'Adjustable dumbbell set with 5-25kg weight range. Perfect for home workouts and strength training.',
                'price': 89.99,
                'category': categories['Sports'],
                'stock': 25,
                'calories': None
            },
            {
                'name': 'Running Watch',
                'description': 'GPS running watch with heart rate monitoring, activity tracking, and smartphone notifications.',
                'price': 199.99,
                'category': categories['Sports'],
                'stock': 20,
                'calories': None
            },
            {
                'name': 'Basketball',
                'description': 'Official size basketball with durable rubber construction. Ideal for indoor and outdoor play.',
                'price': 24.99,
                'category': categories['Sports'],
                'stock': 40,
                'calories': None
            },
            {
                'name': 'Camping Tent',
                'description': '4-person camping tent with waterproof rainfly and ventilation windows. Easy setup in 10 minutes.',
                'price': 129.99,
                'category': categories['Sports'],
                'stock': 15,
                'calories': None
            },
        ]

        # Create Products
        for product_data in products_data:
            Product.objects.create(**product_data)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated database with {len(products_data)} products across {len(categories)} categories!'
            )
        )
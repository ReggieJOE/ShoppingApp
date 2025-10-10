import os
from django.core.management.base import BaseCommand
from Commerce.models import Category, Product
from django.core.files import File
from django.conf import settings


class Command(BaseCommand):
    help = 'Populate database with sample products'

    def handle(self, *args, **kwargs):
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

        # Sample Products Data with Image Paths
        products_data = [
            # ELECTRONICS
            {
                'name': 'iPhone 15 Pro',
                'description': 'Latest Apple iPhone with A17 Pro chip, titanium design, and advanced camera system.',
                'price': 56.99,
                'category': categories['Electronics'],
                'stock': 25,
                'calories': None,
                'image_path': 'products/electronics/iphone 15.jpg'
            },
            {
                'name': 'Samsung Galaxy S24',
                'description': 'Powerful Android smartphone with AI features, 200MP camera.',
                'price': 849.99,
                'category': categories['Electronics'],
                'stock': 30,
                'calories': None,
                'image_path': 'products/electronics/samsung galaxy.jpg'
            },
            {
                'name': 'MacBook Air M3',
                'description': '13-inch laptop with Apple M3 chip, 8GB RAM, 256GB SSD.',
                'price': 1099.99,
                'category': categories['Electronics'],
                'stock': 15,
                'calories': None,
                'image_path': 'products/electronics/macbook.jpg'
            },
            {
                'name': 'Sony WH-1000XM5',
                'description': 'Industry-leading noise canceling headphones with 30-hour battery life.',
                'price': 399.99,
                'category': categories['Electronics'],
                'stock': 40,
                'calories': None,
                'image_path': 'products/electronics/sony mx.jpg'
            },
            {
                'name': 'iPad Air',
                'description': '10.9-inch Liquid Retina display, M1 chip, 64GB storage.',
                'price': 599.99,
                'category': categories['Electronics'],
                'stock': 20,
                'calories': None,
                'image_path': 'products/electronics/ipad air.jpg'
            },

            # FASHION - Add similar image_path for all products...
            {
                'name': 'Classic White Sneakers',
                'description': 'Versatile white leather sneakers with comfortable cushioning.',
                'price': 89.99,
                'category': categories['Fashion'],
                'stock': 50,
                'calories': None,
                'image_path': 'products/fashion/whte sneakers.jpg'
            },
            {
                'name': 'Denim Jacket',

                'description': 'Medium wash denim jacket with classic fit.',
                'price': 65.99,
                'category': categories['Fashion'],
                'stock': 35,
                'calories': None,
                'image_path': 'products/fashion/Jacket.jpg'
            },

            {
                'name': 'Cotton T-Shirt Pack',
                'description': 'Pack of 3 basic cotton t-shirts in assorted colors. Soft, breathable fabric with crew neck design.',
                'price': 24.99,
                'category': categories['Fashion'],
                'stock': 100,
                'calories': None,
                'image_path': 'products/fashion/Tshirt.jpg'
            },
            {
                'name': 'Running Shoes',
                'description': 'Lightweight running shoes with responsive cushioning and breathable mesh upper. Ideal for jogging and gym workouts.',
                'price': 119.99,
                'category': categories['Fashion'],
                'stock': 40,
                'calories': None,
                'image_path': 'products/fashion/running shoe.jpg'
            },
            {
                'name': 'Winter Parka',
                'description': 'Water-resistant winter coat with faux fur hood. Insulated with thermal padding to keep you warm in cold weather.',
                'price': 199.99,
                'category': categories['Fashion'],
                'stock': 25,
                'calories': None,
                'image_path': 'products/fashion/winter parker.jpg'
            },

            # GROCERIES
            {
                'name': 'Organic Bananas',
                'description': 'Fresh organic bananas, rich in potassium and perfect for smoothies, baking, or healthy snacks.',
                'price': 0.99,
                'category': categories['Groceries'],
                'stock': 200,
                'calories': 105,
                'image_path': 'products/groceries/banana.jpg'
            },
            {
                'name': 'Free-Range Eggs',
                'description': 'Dozen large free-range eggs from humanely raised chickens. Perfect for breakfast, baking, and cooking.',
                'price': 4.99,
                'category': categories['Groceries'],
                'stock': 80,
                'calories': 70,
                'image_path': 'products/groceries/eggs.jpg'
            },
            {
                'name': 'Whole Wheat Bread',
                'description': 'Freshly baked whole wheat bread with no artificial preservatives. High in fiber and perfect for sandwiches.',
                'price': 3.49,
                'category': categories['Groceries'],
                'stock': 60,
                'calories': 80,
                'image_path': 'products/groceries/wheat bread.jpg'
            },
            {
                'name': 'Fresh Salmon Fillet',
                'description': 'Atlantic salmon fillet, rich in omega-3 fatty acids. Perfect for grilling, baking, or pan-searing.',
                'price': 12.99,
                'category': categories['Groceries'],
                'stock': 30,
                'calories': 206,
                'image_path': 'products/groceries/salmon fillet.jpg'
            },
            {
                'name': 'Organic Spinach',
                'description': 'Fresh organic spinach leaves, packed with iron and vitamins. Great for salads, smoothies, and cooking.',
                'price': 2.99,
                'category': categories['Groceries'],
                'stock': 75,
                'calories': 23,
                'image_path': 'products/groceries/spinach.jpg'
            },

            # HOME & KITCHEN
            {
                'name': 'Non-Stick Cookware Set',
                'description': '10-piece non-stick cookware set including pots, pans, and utensils. Dishwasher safe and oven safe up to 350°F.',
                'price': 149.99,
                'category': categories['Home & Kitchen'],
                'stock': 20,
                'calories': None,
                'image_path': 'products/home_kitchen/non stick cooking set.jpg'

            },
            {
                'name': 'Memory Foam Pillow',
                'description': 'Queen-size memory foam pillow that contours to your head and neck. Hypoallergenic and machine washable.',
                'price': 39.99,
                'category': categories['Home & Kitchen'],
                'stock': 45,
                'calories': None,
                'image_path': 'products/home_kitchen/pillow.jpg'
            },
            {
                'name': 'Ceramic Dinner Set',
                'description': '16-piece ceramic dinner set for 4 people. Includes dinner plates, salad plates, bowls, and mugs. Microwave and dishwasher safe.',
                'price': 79.99,
                'category': categories['Home & Kitchen'],
                'stock': 30,
                'calories': None,
                'image_path': 'products/home_kitchen/dinner set].jpg'
            },
            {
                'name': 'Air Purifier',
                'description': 'HEPA air purifier for rooms up to 500 sq ft. Removes 99.97% of dust, pollen, and airborne particles.',
                'price': 129.99,
                'category': categories['Home & Kitchen'],
                'stock': 15,
                'calories': None,
                'image_path': 'products/home_kitchen/air purifier.jpg'
            },
            {
                'name': 'Desk Lamp',
                'description': 'LED desk lamp with adjustable brightness and color temperature. USB charging port and touch controls.',
                'price': 34.99,
                'category': categories['Home & Kitchen'],
                'stock': 50,
                'calories': None,
                'image_path': 'products/home_kitchen/desk lamp.jpg'
            },

            # SPORTS
            {
                'name': 'Yoga Mat',
                'description': 'Non-slip yoga mat with carrying strap. Extra thick for comfort during yoga, pilates, and floor exercises.',
                'price': 29.99,
                'category': categories['Sports'],
                'stock': 60,
                'calories': None,
                'image_path': 'products/sports/yoga mat.jpg'
            },
            {
                'name': 'Dumbbell Set',
                'description': 'Adjustable dumbbell set with 5-25kg weight range. Perfect for home workouts and strength training.',
                'price': 89.99,
                'category': categories['Sports'],
                'stock': 25,
                'calories': None,
                'image_path': 'products/sports/dumbell set.jpg'
            },
            {
                'name': 'Running Watch',
                'description': 'GPS running watch with heart rate monitoring, activity tracking, and smartphone notifications.',
                'price': 199.99,
                'category': categories['Sports'],
                'stock': 20,
                'calories': None,
                'image_path': 'products/sports/running watch.jpg'
            },
            {
                'name': 'Basketball',
                'description': 'Official size basketball with durable rubber construction. Ideal for indoor and outdoor play.',
                'price': 24.99,
                'category': categories['Sports'],
                'stock': 40,
                'calories': None,
                'image_path': 'products/sports/basketball.jpg'
            },
            {
                'name': 'Camping Tent',
                'description': '4-person camping tent with waterproof rainfly and ventilation windows. Easy setup in 10 minutes.',
                'price': 129.99,
                'category': categories['Sports'],
                'stock': 15,
                'calories': None,
                'image_path': 'products/sports/camping tent.jpg'
            },
        ]

        products_created = 0
        images_assigned = 0

        for product_data in products_data:
            image_path = product_data.pop('image_path', None)
            product = Product.objects.create(**product_data)
            products_created += 1

            # Add image if path exists and file exists
            if image_path:
                full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
                if os.path.exists(full_image_path):
                    try:
                        with open(full_image_path, 'rb') as f:
                            product.image.save(os.path.basename(image_path), File(f), save=True)
                        images_assigned += 1
                        self.stdout.write(f'✓ Added image to {product.name}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error adding image to {product.name}: {e}')
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Image not found: {full_image_path}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {products_created} products and assigned {images_assigned} images!'
            )
        )

        # Create Products with Images
        for product_data in products_data:
            image_path = product_data.pop('image_path', None)  # Remove image_path from product data
            product = Product.objects.create(**product_data)

            # Add image if path exists and file exists
            if image_path:
                full_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
                if os.path.exists(full_image_path):
                    with open(full_image_path, 'rb') as f:
                        product.image.save(os.path.basename(image_path), File(f), save=True)
                    self.stdout.write(f'Added image to {product.name}')
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Image not found: {full_image_path}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated database with {len(products_data)} products!'
            )
        )

#!/usr/bin/env python3
"""
Script to create demo data for the appointment management system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from main import app, db
from models.user import User
from models.store import Store
from models.service import Service
from models.subscription import SubscriptionPlan, Subscription
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def create_demo_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create subscription plans
        starter_plan = SubscriptionPlan(
            name='Starter',
            price=29.00,
            billing_cycle='monthly',
            max_bookings=100,
            features=['Basic calendar integration', 'Email notifications', 'Standard support']
        )
        
        professional_plan = SubscriptionPlan(
            name='Professional',
            price=79.00,
            billing_cycle='monthly',
            max_bookings=-1,  # Unlimited
            features=['Advanced calendar sync', 'SMS + Email notifications', 'Payment processing', 'Priority support', 'Custom branding']
        )
        
        enterprise_plan = SubscriptionPlan(
            name='Enterprise',
            price=199.00,
            billing_cycle='monthly',
            max_bookings=-1,  # Unlimited
            features=['Everything in Professional', 'Multi-location support', 'Advanced analytics', 'API access', 'Dedicated support', 'Custom integrations']
        )
        
        db.session.add_all([starter_plan, professional_plan, enterprise_plan])
        db.session.commit()
        
        # Create demo users
        admin_user = User(
            email='admin@demo.com',
            password_hash=generate_password_hash('password123'),
            first_name='Admin',
            last_name='User',
            role='admin',
            phone_number='+30 123 456 7890',
            is_active=True,
            email_verified=True
        )
        
        manager_user = User(
            email='manager@demo.com',
            password_hash=generate_password_hash('password123'),
            first_name='Store',
            last_name='Manager',
            role='store_manager',
            phone_number='+30 123 456 7891',
            is_active=True,
            email_verified=True
        )
        
        client_user = User(
            email='client@demo.com',
            password_hash=generate_password_hash('password123'),
            first_name='John',
            last_name='Client',
            role='client',
            phone_number='+30 123 456 7892',
            is_active=True,
            email_verified=True
        )
        
        db.session.add_all([admin_user, manager_user, client_user])
        db.session.commit()
        
        # Create demo store
        demo_store = Store(
            name='Bella Salon & Spa',
            slug='bella-salon-spa',
            description='Premium beauty and wellness services in the heart of Athens',
            address='123 Ermou Street',
            city='Athens',
            country='Greece',
            postal_code='10563',
            phone_number='+30 210 123 4567',
            email='info@bellasalon.gr',
            website='https://bellasalon.gr',
            owner_id=manager_user.id,
            is_active=True,
            business_hours={
                'monday': {'open': '09:00', 'close': '19:00'},
                'tuesday': {'open': '09:00', 'close': '19:00'},
                'wednesday': {'open': '09:00', 'close': '19:00'},
                'thursday': {'open': '09:00', 'close': '19:00'},
                'friday': {'open': '09:00', 'close': '20:00'},
                'saturday': {'open': '10:00', 'close': '18:00'},
                'sunday': {'closed': True}
            }
        )
        
        db.session.add(demo_store)
        db.session.commit()
        
        # Create subscription for the store
        store_subscription = Subscription(
            store_id=demo_store.id,
            plan_id=professional_plan.id,
            status='active',
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30),
            stripe_subscription_id='sub_demo_123'
        )
        
        db.session.add(store_subscription)
        db.session.commit()
        
        # Create demo services
        services = [
            Service(
                name='Hair Cut & Style',
                description='Professional haircut with styling',
                duration=60,
                price=65.00,
                store_id=demo_store.id,
                is_active=True
            ),
            Service(
                name='Hair Color',
                description='Full hair coloring service',
                duration=120,
                price=95.00,
                store_id=demo_store.id,
                is_active=True
            ),
            Service(
                name='Manicure',
                description='Classic manicure with nail polish',
                duration=45,
                price=35.00,
                store_id=demo_store.id,
                is_active=True
            ),
            Service(
                name='Facial Treatment',
                description='Deep cleansing facial with moisturizing',
                duration=75,
                price=80.00,
                store_id=demo_store.id,
                is_active=True
            ),
            Service(
                name='Massage Therapy',
                description='Relaxing full body massage',
                duration=90,
                price=100.00,
                store_id=demo_store.id,
                is_active=True
            )
        ]
        
        db.session.add_all(services)
        db.session.commit()
        
        print("Demo data created successfully!")
        print("\nDemo accounts:")
        print("Admin: admin@demo.com / password123")
        print("Store Manager: manager@demo.com / password123")
        print("Client: client@demo.com / password123")
        print(f"\nDemo store: {demo_store.name} (slug: {demo_store.slug})")
        print(f"Services created: {len(services)}")

if __name__ == '__main__':
    create_demo_data()


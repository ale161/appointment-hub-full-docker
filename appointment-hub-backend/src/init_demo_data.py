"""
Initialize demo data for the appointment management system
"""

from models.user import User, UserRole
from models.store import Store
from models.service import Service
from models.subscription import SubscriptionPlan, Subscription
from datetime import datetime, timedelta

def init_demo_data(db):
    """Initialize demo data if database is empty"""
    
    # Check if data already exists
    if User.query.first():
        return
    
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
        password_hash=User.hash_password('password123'),
        first_name='Admin',
        last_name='User',
        role=UserRole.ADMIN,
        phone_number='+30 123 456 7890'
    )
    
    manager_user = User(
        email='manager@demo.com',
        password_hash=User.hash_password('password123'),
        first_name='Store',
        last_name='Manager',
        role=UserRole.STORE_MANAGER,
        phone_number='+30 123 456 7891'
    )
    
    client_user = User(
        email='client@demo.com',
        password_hash=User.hash_password('password123'),
        first_name='John',
        last_name='Client',
        role=UserRole.CLIENT,
        phone_number='+30 123 456 7892'
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
        manager_user_id=manager_user.id,
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
    
    # Update manager's store_id
    manager_user.store_id = demo_store.id
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
    
    print("Demo data initialized successfully!")


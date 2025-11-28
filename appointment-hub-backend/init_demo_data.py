"""
Initialize demo data for the appointment management system
"""

from src.models.user import User, UserRole
from src.models.store import Store
from src.models.service import Service
from src.models.booking import Booking, BookingStatus, BookingPaymentStatus
from src.models.payment import Payment, PaymentStatus
from src.models.subscription import SubscriptionPlan, Subscription, SubscriptionInterval
from datetime import datetime, timedelta, date, time

def init_demo_data(db):
    """Initialize demo data if database is empty"""
    
    # Check if data already exists
    if User.query.first():
        return
    
    # Create subscription plans
    starter_plan = SubscriptionPlan(
        name='Starter',
        price_amount=29.00,
        interval=SubscriptionInterval.MONTH,
        features=['Basic calendar integration', 'Email notifications', 'Standard support']
    )

    professional_plan = SubscriptionPlan(
        name='Professional',
        price_amount=79.00,
        interval=SubscriptionInterval.MONTH,
        features=['Advanced calendar sync', 'SMS + Email notifications', 'Payment processing', 'Priority support', 'Custom branding']
    )

    enterprise_plan = SubscriptionPlan(
        name='Enterprise',
        price_amount=199.00,
        interval=SubscriptionInterval.MONTH,
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

    # Create additional demo users (clients)
    client_users = [
        User(
            email='sarah.johnson@email.com',
            password_hash=User.hash_password('password123'),
            first_name='Sarah',
            last_name='Johnson',
            role=UserRole.CLIENT,
            phone_number='+30 690 123 4567',
            age=28
        ),
        User(
            email='mike.chen@email.com',
            password_hash=User.hash_password('password123'),
            first_name='Mike',
            last_name='Chen',
            role=UserRole.CLIENT,
            phone_number='+30 690 123 4568',
            age=35
        ),
        User(
            email='emma.davis@email.com',
            password_hash=User.hash_password('password123'),
            first_name='Emma',
            last_name='Davis',
            role=UserRole.CLIENT,
            phone_number='+30 690 123 4569',
            age=26
        ),
        User(
            email='alex.papadopoulos@email.com',
            password_hash=User.hash_password('password123'),
            first_name='Alex',
            last_name='Papadopoulos',
            role=UserRole.CLIENT,
            phone_number='+30 690 123 4570',
            age=42
        ),
        User(
            email='lisa.wilson@email.com',
            password_hash=User.hash_password('password123'),
            first_name='Lisa',
            last_name='Wilson',
            role=UserRole.CLIENT,
            phone_number='+30 690 123 4571',
            age=31
        )
    ]

    db.session.add_all(client_users)
    db.session.commit()

    # Create additional stores
    additional_stores = [
        Store(
            name='Athens Fitness Center',
            slug='athens-fitness',
            description='Premium gym and fitness services',
            address='456 Kolonaki Square',
            city='Athens',
            country='Greece',
            postal_code='10673',
            phone_number='+30 210 987 6543',
            email='info@athensfitness.gr',
            website='https://athensfitness.gr',
            manager_user_id=manager_user.id,  # Same manager for demo
            is_active=True,
            business_hours={
                'monday': {'open': '06:00', 'close': '22:00'},
                'tuesday': {'open': '06:00', 'close': '22:00'},
                'wednesday': {'open': '06:00', 'close': '22:00'},
                'thursday': {'open': '06:00', 'close': '22:00'},
                'friday': {'open': '06:00', 'close': '22:00'},
                'saturday': {'open': '08:00', 'close': '20:00'},
                'sunday': {'open': '10:00', 'close': '18:00'}
            }
        ),
        Store(
            name='Wellness Spa Retreat',
            slug='wellness-spa',
            description='Luxury spa and wellness treatments',
            address='789 Plaka District',
            city='Athens',
            country='Greece',
            postal_code='10558',
            phone_number='+30 210 555 1234',
            email='spa@wellnessretreat.gr',
            website='https://wellnessretreat.gr',
            manager_user_id=manager_user.id,  # Same manager for demo
            is_active=True,
            business_hours={
                'monday': {'open': '10:00', 'close': '20:00'},
                'tuesday': {'open': '10:00', 'close': '20:00'},
                'wednesday': {'open': '10:00', 'close': '20:00'},
                'thursday': {'open': '10:00', 'close': '20:00'},
                'friday': {'open': '10:00', 'close': '21:00'},
                'saturday': {'open': '09:00', 'close': '21:00'},
                'sunday': {'open': '11:00', 'close': '19:00'}
            }
        )
    ]

    db.session.add_all(additional_stores)
    db.session.commit()

    # Create services for additional stores
    fitness_services = [
        Service(
            name='Personal Training Session',
            description='One-on-one personal training',
            duration=60,
            price=80.00,
            store_id=additional_stores[0].id,
            is_active=True
        ),
        Service(
            name='Group Fitness Class',
            description='High-intensity group workout',
            duration=45,
            price=25.00,
            store_id=additional_stores[0].id,
            is_active=True
        ),
        Service(
            name='Nutrition Consultation',
            description='Personalized nutrition planning',
            duration=30,
            price=60.00,
            store_id=additional_stores[0].id,
            is_active=True
        )
    ]

    spa_services = [
        Service(
            name='Swedish Massage',
            description='Relaxing full body massage',
            duration=90,
            price=120.00,
            store_id=additional_stores[1].id,
            is_active=True
        ),
        Service(
            name='Hot Stone Therapy',
            description='Therapeutic hot stone massage',
            duration=75,
            price=140.00,
            store_id=additional_stores[1].id,
            is_active=True
        ),
        Service(
            name='Aromatherapy Session',
            description='Essential oils and relaxation',
            duration=60,
            price=85.00,
            store_id=additional_stores[1].id,
            is_active=True
        )
    ]

    db.session.add_all(fitness_services + spa_services)
    db.session.commit()

    # Create sample bookings
    today = date.today()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)
    next_week = today + timedelta(days=7)

    bookings = [
        # Bella Salon bookings
        Booking(
            store_id=demo_store.id,
            client_user_id=client_users[0].id,  # Sarah Johnson
            service_id=services[0].id,  # Hair Cut & Style
            booking_date=tomorrow,
            start_time=time(10, 0),
            end_time=time(11, 0),
            number_of_persons=1,
            status=BookingStatus.CONFIRMED,
            total_amount=65.00,
            advance_payment_amount=32.50,
            payment_status=BookingPaymentStatus.PARTIAL
        ),
        Booking(
            store_id=demo_store.id,
            client_user_id=client_users[1].id,  # Mike Chen
            service_id=services[1].id,  # Hair Color
            booking_date=today,
            start_time=time(14, 30),
            end_time=time(16, 30),
            number_of_persons=1,
            status=BookingStatus.CONFIRMED,
            total_amount=95.00,
            advance_payment_amount=95.00,
            payment_status=BookingPaymentStatus.PAID
        ),
        Booking(
            store_id=demo_store.id,
            client_user_id=client_users[2].id,  # Emma Davis
            service_id=services[4].id,  # Massage Therapy
            booking_date=yesterday,
            start_time=time(16, 0),
            end_time=time(17, 30),
            number_of_persons=1,
            status=BookingStatus.COMPLETED,
            total_amount=100.00,
            advance_payment_amount=100.00,
            payment_status=BookingPaymentStatus.PAID
        ),
        Booking(
            store_id=demo_store.id,
            client_user_id=client_users[3].id,  # Alex Papadopoulos
            service_id=services[2].id,  # Manicure
            booking_date=next_week,
            start_time=time(11, 0),
            end_time=time(11, 45),
            number_of_persons=1,
            status=BookingStatus.PENDING,
            total_amount=35.00,
            advance_payment_amount=0.00,
            payment_status=BookingPaymentStatus.UNPAID
        ),
        Booking(
            store_id=demo_store.id,
            client_user_id=client_users[4].id,  # Lisa Wilson
            service_id=services[3].id,  # Facial Treatment
            booking_date=tomorrow,
            start_time=time(15, 0),
            end_time=time(16, 15),
            number_of_persons=1,
            status=BookingStatus.CONFIRMED,
            total_amount=80.00,
            advance_payment_amount=80.00,
            payment_status=BookingPaymentStatus.PAID
        ),

        # Fitness Center bookings
        Booking(
            store_id=additional_stores[0].id,
            client_user_id=client_users[0].id,
            service_id=fitness_services[0].id,  # Personal Training
            booking_date=tomorrow,
            start_time=time(9, 0),
            end_time=time(10, 0),
            number_of_persons=1,
            status=BookingStatus.CONFIRMED,
            total_amount=80.00,
            advance_payment_amount=80.00,
            payment_status=BookingPaymentStatus.PAID
        ),

        # Spa bookings
        Booking(
            store_id=additional_stores[1].id,
            client_user_id=client_users[1].id,
            service_id=spa_services[0].id,  # Swedish Massage
            booking_date=next_week,
            start_time=time(14, 0),
            end_time=time(15, 30),
            number_of_persons=1,
            status=BookingStatus.CONFIRMED,
            total_amount=120.00,
            advance_payment_amount=60.00,
            payment_status=BookingPaymentStatus.PARTIAL
        )
    ]

    db.session.add_all(bookings)
    db.session.commit()

    # Create payments for bookings
    payments = []
    for booking in bookings:
        if booking.advance_payment_amount and booking.advance_payment_amount > 0:
            payment = Payment(
                store_id=booking.store_id,
                user_id=booking.client_user_id,
                booking_id=booking.id,
                amount=booking.advance_payment_amount,
                currency='EUR',
                status=PaymentStatus.SUCCEEDED,
                payment_method='card',
                payment_date=datetime.utcnow() - timedelta(days=1),
                stripe_charge_id=f'ch_demo_{booking.id[:8]}',
                stripe_payment_intent_id=f'pi_demo_{booking.id[:8]}'
            )
            payments.append(payment)

    # Add subscription payment
    subscription_payment = Payment(
        store_id=demo_store.id,
        user_id=manager_user.id,
        subscription_id=store_subscription.id,
        amount=professional_plan.price_amount,
        currency='EUR',
        status=PaymentStatus.SUCCEEDED,
        payment_method='card',
        payment_date=datetime.utcnow() - timedelta(days=30),
        stripe_charge_id='ch_sub_demo_123',
        stripe_payment_intent_id='pi_sub_demo_123'
    )
    payments.append(subscription_payment)

    db.session.add_all(payments)
    db.session.commit()

    print("Demo data initialized successfully!")


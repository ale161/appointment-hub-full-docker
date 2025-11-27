from src.models.user import db
from datetime import datetime
import enum

class PaymentStatus(enum.Enum):
    PENDING = 'pending'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    REFUNDED = 'refunded'

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    
    # Multi-tenancy
    store_id = db.Column(db.String(36), db.ForeignKey('stores.id'), nullable=False, index=True)
    
    # Payment relationships
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)  # Client or manager
    booking_id = db.Column(db.String(36), db.ForeignKey('bookings.id'), nullable=True, index=True)  # For service payments
    subscription_id = db.Column(db.String(36), db.ForeignKey('subscriptions.id'), nullable=True, index=True)  # For subscription payments
    
    # Stripe integration
    stripe_charge_id = db.Column(db.String(255), unique=True)
    stripe_payment_intent_id = db.Column(db.String(255), unique=True)
    
    # Payment details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='EUR')
    status = db.Column(db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, index=True)
    payment_method = db.Column(db.String(100))
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    store = db.relationship('Store', back_populates='payments')
    user = db.relationship('User', back_populates='payments')
    booking = db.relationship('Booking', back_populates='payments')
    subscription = db.relationship('Subscription', back_populates='payments')

    def __repr__(self):
        return f'<Payment {self.id} ({self.status.value}) - {self.amount} {self.currency}>'

    def to_dict(self):
        return {
            'id': self.id,
            'store_id': self.store_id,
            'user_id': self.user_id,
            'booking_id': self.booking_id,
            'subscription_id': self.subscription_id,
            'stripe_charge_id': self.stripe_charge_id,
            'stripe_payment_intent_id': self.stripe_payment_intent_id,
            'amount': float(self.amount) if self.amount else None,
            'currency': self.currency,
            'status': self.status.value,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def is_service_payment(self):
        """Check if this is a payment for a service booking"""
        return self.booking_id is not None

    def is_subscription_payment(self):
        """Check if this is a payment for a subscription"""
        return self.subscription_id is not None

    def is_successful(self):
        """Check if payment was successful"""
        return self.status == PaymentStatus.SUCCEEDED

    def can_be_refunded(self):
        """Check if payment can be refunded"""
        return self.status == PaymentStatus.SUCCEEDED

    @staticmethod
    def create_from_stripe_intent(stripe_payment_intent, store_id, user_id, booking_id=None, subscription_id=None):
        """Create a Payment record from a Stripe PaymentIntent"""
        payment = Payment(
            store_id=store_id,
            user_id=user_id,
            booking_id=booking_id,
            subscription_id=subscription_id,
            stripe_payment_intent_id=stripe_payment_intent.id,
            amount=stripe_payment_intent.amount / 100,  # Stripe amounts are in cents
            currency=stripe_payment_intent.currency.upper(),
            status=PaymentStatus.PENDING,
            payment_method=stripe_payment_intent.payment_method_types[0] if stripe_payment_intent.payment_method_types else None
        )
        return payment

    def update_from_stripe_event(self, stripe_event):
        """Update payment status based on Stripe webhook event"""
        if stripe_event.type == 'payment_intent.succeeded':
            self.status = PaymentStatus.SUCCEEDED
            if hasattr(stripe_event.data.object, 'charges') and stripe_event.data.object.charges.data:
                self.stripe_charge_id = stripe_event.data.object.charges.data[0].id
        elif stripe_event.type == 'payment_intent.payment_failed':
            self.status = PaymentStatus.FAILED
        elif stripe_event.type == 'charge.dispute.created':
            self.status = PaymentStatus.REFUNDED


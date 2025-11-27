from src.models.user import db
from datetime import datetime
import enum
import json

class SubscriptionInterval(enum.Enum):
    MONTH = 'month'
    YEAR = 'year'

class SubscriptionStatus(enum.Enum):
    ACTIVE = 'active'
    CANCELLED = 'cancelled'
    PAST_DUE = 'past_due'
    TRIALING = 'trialing'
    ENDED = 'ended'

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    
    # Plan details
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price_amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='EUR')
    interval = db.Column(db.Enum(SubscriptionInterval), nullable=False)
    
    # Plan features (stored as JSON)
    features = db.Column(db.JSON)  # e.g., {"max_stores": 1, "max_services": 10, "max_bookings": 100}
    
    # Stripe integration
    stripe_price_id = db.Column(db.String(255), unique=True)  # Link to Stripe product/price
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', back_populates='plan')
    stores_with_plan = db.relationship('Store', back_populates='current_subscription_plan', foreign_keys='Store.current_subscription_plan_id')

    def __repr__(self):
        return f'<SubscriptionPlan {self.name} - {self.price_amount} {self.currency}/{self.interval.value}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price_amount': float(self.price_amount) if self.price_amount else None,
            'currency': self.currency,
            'interval': self.interval.value,
            'features': self.features,
            'stripe_price_id': self.stripe_price_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_feature_limit(self, feature_name, default=None):
        """Get a specific feature limit from the features JSON"""
        if self.features and isinstance(self.features, dict):
            return self.features.get(feature_name, default)
        return default

    def has_feature(self, feature_name):
        """Check if plan has a specific feature"""
        return self.get_feature_limit(feature_name) is not None


class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    
    # Subscription relationships
    store_id = db.Column(db.String(36), db.ForeignKey('stores.id'), nullable=False, index=True)
    plan_id = db.Column(db.String(36), db.ForeignKey('subscription_plans.id'), nullable=False, index=True)
    
    # Subscription period
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)  # For expired/cancelled subscriptions
    
    # Status
    status = db.Column(db.Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE, index=True)
    
    # Stripe integration
    stripe_subscription_id = db.Column(db.String(255), unique=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    store = db.relationship('Store', back_populates='subscriptions')
    plan = db.relationship('SubscriptionPlan', back_populates='subscriptions')
    payments = db.relationship('Payment', back_populates='subscription')

    def __repr__(self):
        return f'<Subscription {self.id} ({self.status.value}) - Store: {self.store_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'store_id': self.store_id,
            'plan_id': self.plan_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status.value,
            'stripe_subscription_id': self.stripe_subscription_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == SubscriptionStatus.ACTIVE

    def is_expired(self):
        """Check if subscription has expired"""
        if self.end_date:
            return datetime.utcnow() > self.end_date
        return False

    def days_remaining(self):
        """Calculate days remaining in subscription"""
        if self.end_date:
            remaining = self.end_date - datetime.utcnow()
            return max(0, remaining.days)
        return None

    def can_be_cancelled(self):
        """Check if subscription can be cancelled"""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]

    def cancel(self):
        """Cancel the subscription"""
        if self.can_be_cancelled():
            self.status = SubscriptionStatus.CANCELLED
            self.end_date = datetime.utcnow()

    @staticmethod
    def create_from_stripe_subscription(stripe_subscription, store_id, plan_id):
        """Create a Subscription record from a Stripe subscription"""
        subscription = Subscription(
            store_id=store_id,
            plan_id=plan_id,
            stripe_subscription_id=stripe_subscription.id,
            start_date=datetime.fromtimestamp(stripe_subscription.current_period_start),
            end_date=datetime.fromtimestamp(stripe_subscription.current_period_end),
            status=SubscriptionStatus.ACTIVE if stripe_subscription.status == 'active' else SubscriptionStatus.TRIALING
        )
        return subscription

    def update_from_stripe_event(self, stripe_event):
        """Update subscription status based on Stripe webhook event"""
        stripe_subscription = stripe_event.data.object
        
        if stripe_event.type == 'customer.subscription.created':
            self.status = SubscriptionStatus.ACTIVE
        elif stripe_event.type == 'customer.subscription.updated':
            if stripe_subscription.status == 'active':
                self.status = SubscriptionStatus.ACTIVE
            elif stripe_subscription.status == 'past_due':
                self.status = SubscriptionStatus.PAST_DUE
            elif stripe_subscription.status == 'canceled':
                self.status = SubscriptionStatus.CANCELLED
                self.end_date = datetime.utcnow()
        elif stripe_event.type == 'customer.subscription.deleted':
            self.status = SubscriptionStatus.ENDED
            self.end_date = datetime.utcnow()


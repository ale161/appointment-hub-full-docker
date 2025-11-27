from src.models.user import db
from datetime import datetime
import enum

class PriceType(enum.Enum):
    FIXED = 'fixed'
    PER_HOUR = 'per_hour'
    PER_PERSON = 'per_person'

class AdvancePaymentType(enum.Enum):
    FIXED = 'fixed'
    PERCENT = 'percent'

class RecurringInterval(enum.Enum):
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    
    # Multi-tenancy
    store_id = db.Column(db.String(36), db.ForeignKey('stores.id'), nullable=False, index=True)
    
    # Service details
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, nullable=False)
    min_persons = db.Column(db.Integer, default=1, nullable=False)
    max_persons = db.Column(db.Integer, default=1, nullable=False)
    
    # Pricing
    price_type = db.Column(db.Enum(PriceType), nullable=False)
    base_price_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Payment settings
    payment_enabled = db.Column(db.Boolean, default=False, nullable=False)
    advance_payment_type = db.Column(db.Enum(AdvancePaymentType))
    advance_payment_amount = db.Column(db.Numeric(10, 2))
    
    # Recurring settings
    is_recurring = db.Column(db.Boolean, default=False, nullable=False)
    recurring_interval = db.Column(db.Enum(RecurringInterval))
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    store = db.relationship('Store', back_populates='services')
    bookings = db.relationship('Booking', back_populates='service')

    def __repr__(self):
        return f'<Service {self.name} (Store: {self.store_id})>'

    def to_dict(self):
        return {
            'id': self.id,
            'store_id': self.store_id,
            'name': self.name,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'min_persons': self.min_persons,
            'max_persons': self.max_persons,
            'price_type': self.price_type.value,
            'base_price_amount': float(self.base_price_amount) if self.base_price_amount else None,
            'payment_enabled': self.payment_enabled,
            'advance_payment_type': self.advance_payment_type.value if self.advance_payment_type else None,
            'advance_payment_amount': float(self.advance_payment_amount) if self.advance_payment_amount else None,
            'is_recurring': self.is_recurring,
            'recurring_interval': self.recurring_interval.value if self.recurring_interval else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def calculate_total_price(self, num_persons=1, duration_hours=None):
        """Calculate total price based on price type and parameters"""
        base_amount = float(self.base_price_amount)
        
        if self.price_type == PriceType.FIXED:
            return base_amount
        elif self.price_type == PriceType.PER_PERSON:
            return base_amount * num_persons
        elif self.price_type == PriceType.PER_HOUR:
            hours = duration_hours or (self.duration_minutes / 60.0)
            return base_amount * hours
        
        return base_amount

    def calculate_advance_payment(self, total_amount):
        """Calculate advance payment amount"""
        if not self.payment_enabled or not self.advance_payment_type:
            return 0
        
        if self.advance_payment_type == AdvancePaymentType.FIXED:
            return float(self.advance_payment_amount)
        elif self.advance_payment_type == AdvancePaymentType.PERCENT:
            return total_amount * (float(self.advance_payment_amount) / 100.0)
        
        return 0


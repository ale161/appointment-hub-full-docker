from src.models.user import db
from datetime import datetime, date, time
import enum

class BookingStatus(enum.Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    RESCHEDULED = 'rescheduled'

class BookingPaymentStatus(enum.Enum):
    UNPAID = 'unpaid'
    PARTIAL = 'partial'
    PAID = 'paid'
    REFUNDED = 'refunded'

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    
    # Multi-tenancy
    store_id = db.Column(db.String(36), db.ForeignKey('stores.id'), nullable=False, index=True)
    
    # Booking relationships
    client_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    service_id = db.Column(db.String(36), db.ForeignKey('services.id'), nullable=False, index=True)
    
    # Booking details
    booking_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    number_of_persons = db.Column(db.Integer, nullable=False, default=1)
    
    # Status tracking
    status = db.Column(db.Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING, index=True)
    
    # Payment information
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    advance_payment_amount = db.Column(db.Numeric(10, 2))
    payment_status = db.Column(db.Enum(BookingPaymentStatus), nullable=False, default=BookingPaymentStatus.UNPAID, index=True)
    
    # Calendly integration
    calendly_event_uri = db.Column(db.String(500))  # Link to Calendly event for sync
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    store = db.relationship('Store', back_populates='bookings')
    client = db.relationship('User', back_populates='client_bookings', foreign_keys=[client_user_id])
    service = db.relationship('Service', back_populates='bookings')
    payments = db.relationship('Payment', back_populates='booking')

    def __repr__(self):
        return f'<Booking {self.id} ({self.status.value}) - Store: {self.store_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'store_id': self.store_id,
            'client_user_id': self.client_user_id,
            'service_id': self.service_id,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'number_of_persons': self.number_of_persons,
            'status': self.status.value,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'advance_payment_amount': float(self.advance_payment_amount) if self.advance_payment_amount else None,
            'payment_status': self.payment_status.value,
            'calendly_event_uri': self.calendly_event_uri,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_booking_datetime(self):
        """Combine booking date and start time into a datetime object"""
        if self.booking_date and self.start_time:
            return datetime.combine(self.booking_date, self.start_time)
        return None

    def get_end_datetime(self):
        """Combine booking date and end time into a datetime object"""
        if self.booking_date and self.end_time:
            return datetime.combine(self.booking_date, self.end_time)
        return None

    def is_past_booking(self):
        """Check if the booking is in the past"""
        booking_datetime = self.get_booking_datetime()
        if booking_datetime:
            return booking_datetime < datetime.now()
        return False

    def can_be_cancelled(self):
        """Check if booking can be cancelled"""
        return (self.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED] and 
                not self.is_past_booking())

    def can_be_rescheduled(self):
        """Check if booking can be rescheduled"""
        return (self.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED] and 
                not self.is_past_booking())

    def calculate_remaining_payment(self):
        """Calculate remaining payment amount"""
        total = float(self.total_amount) if self.total_amount else 0
        advance = float(self.advance_payment_amount) if self.advance_payment_amount else 0
        return max(0, total - advance)

    def is_calendly_synced(self):
        """Check if this booking is synced with Calendly"""
        return bool(self.calendly_event_uri)


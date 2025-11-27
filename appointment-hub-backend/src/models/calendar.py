from src.models.user import db
from datetime import datetime

class Calendar(db.Model):
    __tablename__ = 'calendars'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    
    # Multi-tenancy
    store_id = db.Column(db.String(36), db.ForeignKey('stores.id'), nullable=False, index=True)
    
    # Calendar details
    name = db.Column(db.String(255), nullable=False)
    
    # Calendly integration
    calendly_event_type_id = db.Column(db.String(255))  # Link to Calendly event type if synced
    calendly_organization_url = db.Column(db.String(255))  # For webhook setup
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    store = db.relationship('Store', back_populates='calendars')
    slots = db.relationship('CalendarSlot', back_populates='calendar', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Calendar {self.name} (Store: {self.store_id})>'

    def to_dict(self):
        return {
            'id': self.id,
            'store_id': self.store_id,
            'name': self.name,
            'calendly_event_type_id': self.calendly_event_type_id,
            'calendly_organization_url': self.calendly_organization_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def is_calendly_synced(self):
        """Check if this calendar is synced with Calendly"""
        return bool(self.calendly_event_type_id)


class CalendarSlot(db.Model):
    __tablename__ = 'calendar_slots'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    
    # Calendar relationship
    calendar_id = db.Column(db.String(36), db.ForeignKey('calendars.id'), nullable=False, index=True)
    
    # Time slot details
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False, index=True)
    
    # Booking status
    is_booked = db.Column(db.Boolean, default=False, nullable=False)
    capacity_available = db.Column(db.Integer)  # For max/min persons
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    calendar = db.relationship('Calendar', back_populates='slots')

    def __repr__(self):
        return f'<CalendarSlot {self.start_time} - {self.end_time} (Calendar: {self.calendar_id})>'

    def to_dict(self):
        return {
            'id': self.id,
            'calendar_id': self.calendar_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_booked': self.is_booked,
            'capacity_available': self.capacity_available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def is_available(self, required_capacity=1):
        """Check if slot is available for booking"""
        if self.is_booked:
            return False
        
        if self.capacity_available is not None:
            return self.capacity_available >= required_capacity
        
        return True

    def book_slot(self, capacity_used=1):
        """Book the slot or reduce available capacity"""
        if self.capacity_available is not None:
            self.capacity_available -= capacity_used
            if self.capacity_available <= 0:
                self.is_booked = True
        else:
            self.is_booked = True


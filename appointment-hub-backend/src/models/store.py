from src.models.user import db
from datetime import datetime
import json

class Store(db.Model):
    __tablename__ = 'stores'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)  # For URL: web-app-url/slug
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(255))
    website = db.Column(db.String(255))
    description = db.Column(db.Text)
    photos_url = db.Column(db.JSON)  # Array of photo URLs
    
    # Manager relationship (one-to-one)
    manager_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # External integrations
    calendly_api_key = db.Column(db.Text)  # Encrypted storage recommended
    stripe_enabled = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    business_hours = db.Column(db.JSON)  # Store business hours as JSON

    # Subscription
    current_subscription_plan_id = db.Column(db.String(36), db.ForeignKey('subscription_plans.id'))
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manager = db.relationship('User', foreign_keys=[manager_user_id])
    services = db.relationship('Service', back_populates='store', cascade='all, delete-orphan')
    calendars = db.relationship('Calendar', back_populates='store', cascade='all, delete-orphan')
    bookings = db.relationship('Booking', back_populates='store', cascade='all, delete-orphan')
    payments = db.relationship('Payment', back_populates='store', cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', back_populates='store', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='store', cascade='all, delete-orphan')
    current_subscription_plan = db.relationship('SubscriptionPlan', foreign_keys=[current_subscription_plan_id])

    def __repr__(self):
        return f'<Store {self.name} ({self.slug})>'

    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'address': self.address,
            'city': self.city,
            'postal_code': self.postal_code,
            'country': self.country,
            'phone_number': self.phone_number,
            'email': self.email,
            'website': self.website,
            'description': self.description,
            'photos_url': self.photos_url,
            'manager_user_id': self.manager_user_id,
            'stripe_enabled': self.stripe_enabled,
            'is_active': self.is_active,
            'business_hours': self.business_hours,
            'current_subscription_plan_id': self.current_subscription_plan_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data['calendly_api_key'] = self.calendly_api_key
            
        return data

    def get_photos_list(self):
        """Helper method to get photos as a list"""
        if self.photos_url and isinstance(self.photos_url, list):
            return self.photos_url
        return []

    def add_photo(self, photo_url):
        """Helper method to add a photo URL"""
        photos = self.get_photos_list()
        if photo_url not in photos:
            photos.append(photo_url)
            self.photos_url = photos

    def remove_photo(self, photo_url):
        """Helper method to remove a photo URL"""
        photos = self.get_photos_list()
        if photo_url in photos:
            photos.remove(photo_url)
            self.photos_url = photos


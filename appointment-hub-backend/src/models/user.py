from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    CLIENT = 'client'
    STORE_MANAGER = 'store_manager'
    ADMIN = 'admin'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    age = db.Column(db.Integer)  # Nullable for managers/admins
    role = db.Column(db.Enum(UserRole), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Multi-tenancy: store_id for store managers, nullable for admins
    # Note: This is for data filtering, not a direct relationship
    store_id = db.Column(db.String(36), nullable=True, index=True)
    
    # Relationships
    client_bookings = db.relationship('Booking', back_populates='client', foreign_keys='Booking.client_user_id')
    payments = db.relationship('Payment', back_populates='user')
    notifications = db.relationship('Notification', back_populates='recipient')

    def __repr__(self):
        return f'<User {self.email} ({self.role.value})>'

    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone_number': self.phone_number,
            'address': self.address,
            'age': self.age,
            'role': self.role.value,
            'store_id': self.store_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
            
        return data

    @staticmethod
    def hash_password(password):
        from werkzeug.security import generate_password_hash
        return generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)


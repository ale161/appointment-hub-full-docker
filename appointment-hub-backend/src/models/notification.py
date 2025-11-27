from src.models.user import db
from datetime import datetime
import enum

class NotificationType(enum.Enum):
    EMAIL = 'email'
    SMS = 'sms'

class NotificationStatus(enum.Enum):
    SENT = 'sent'
    FAILED = 'failed'
    DELIVERED = 'delivered'
    READ = 'read'

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
    
    # Multi-tenancy
    store_id = db.Column(db.String(36), db.ForeignKey('stores.id'), nullable=False, index=True)
    
    # Notification relationships
    recipient_user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    booking_id = db.Column(db.String(36), db.ForeignKey('bookings.id'), nullable=True, index=True)
    
    # Notification details
    type = db.Column(db.Enum(NotificationType), nullable=False, index=True)
    subject = db.Column(db.String(500))  # Nullable for SMS
    body = db.Column(db.Text, nullable=False)
    
    # Status tracking
    status = db.Column(db.Enum(NotificationStatus), nullable=False, default=NotificationStatus.SENT, index=True)
    
    # External service integration
    external_message_id = db.Column(db.String(255))  # e.g., EasySMS message ID for delivery reports
    
    sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    store = db.relationship('Store', back_populates='notifications')
    recipient = db.relationship('User', back_populates='notifications')
    booking = db.relationship('Booking', foreign_keys=[booking_id])

    def __repr__(self):
        return f'<Notification {self.type.value} to {self.recipient_user_id} ({self.status.value})>'

    def to_dict(self):
        return {
            'id': self.id,
            'store_id': self.store_id,
            'recipient_user_id': self.recipient_user_id,
            'booking_id': self.booking_id,
            'type': self.type.value,
            'subject': self.subject,
            'body': self.body,
            'status': self.status.value,
            'external_message_id': self.external_message_id,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def is_email(self):
        """Check if this is an email notification"""
        return self.type == NotificationType.EMAIL

    def is_sms(self):
        """Check if this is an SMS notification"""
        return self.type == NotificationType.SMS

    def is_delivered(self):
        """Check if notification was delivered"""
        return self.status == NotificationStatus.DELIVERED

    def is_failed(self):
        """Check if notification failed to send"""
        return self.status == NotificationStatus.FAILED

    def mark_as_delivered(self):
        """Mark notification as delivered"""
        self.status = NotificationStatus.DELIVERED
        self.updated_at = datetime.utcnow()

    def mark_as_failed(self):
        """Mark notification as failed"""
        self.status = NotificationStatus.FAILED
        self.updated_at = datetime.utcnow()

    def mark_as_read(self):
        """Mark notification as read (for emails with tracking)"""
        self.status = NotificationStatus.READ
        self.updated_at = datetime.utcnow()

    @staticmethod
    def create_booking_confirmation(store_id, recipient_user_id, booking_id, booking_details):
        """Create a booking confirmation notification"""
        subject = f"Booking Confirmation - {booking_details.get('service_name', 'Service')}"
        body = f"""
        Your booking has been confirmed!
        
        Service: {booking_details.get('service_name', 'N/A')}
        Date: {booking_details.get('booking_date', 'N/A')}
        Time: {booking_details.get('start_time', 'N/A')} - {booking_details.get('end_time', 'N/A')}
        Number of persons: {booking_details.get('number_of_persons', 1)}
        Total amount: {booking_details.get('total_amount', 0)} EUR
        
        Thank you for choosing our services!
        """
        
        return Notification(
            store_id=store_id,
            recipient_user_id=recipient_user_id,
            booking_id=booking_id,
            type=NotificationType.EMAIL,
            subject=subject,
            body=body.strip()
        )

    @staticmethod
    def create_booking_reminder(store_id, recipient_user_id, booking_id, booking_details):
        """Create a booking reminder notification"""
        subject = f"Booking Reminder - {booking_details.get('service_name', 'Service')}"
        body = f"""
        This is a reminder for your upcoming booking:
        
        Service: {booking_details.get('service_name', 'N/A')}
        Date: {booking_details.get('booking_date', 'N/A')}
        Time: {booking_details.get('start_time', 'N/A')} - {booking_details.get('end_time', 'N/A')}
        
        We look forward to seeing you!
        """
        
        return Notification(
            store_id=store_id,
            recipient_user_id=recipient_user_id,
            booking_id=booking_id,
            type=NotificationType.EMAIL,
            subject=subject,
            body=body.strip()
        )

    @staticmethod
    def create_booking_cancellation(store_id, recipient_user_id, booking_id, booking_details):
        """Create a booking cancellation notification"""
        subject = f"Booking Cancelled - {booking_details.get('service_name', 'Service')}"
        body = f"""
        Your booking has been cancelled:
        
        Service: {booking_details.get('service_name', 'N/A')}
        Date: {booking_details.get('booking_date', 'N/A')}
        Time: {booking_details.get('start_time', 'N/A')} - {booking_details.get('end_time', 'N/A')}
        
        If you have any questions, please contact us.
        """
        
        return Notification(
            store_id=store_id,
            recipient_user_id=recipient_user_id,
            booking_id=booking_id,
            type=NotificationType.EMAIL,
            subject=subject,
            body=body.strip()
        )


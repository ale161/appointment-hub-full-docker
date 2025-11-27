from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from src.models import (
    db, Notification, NotificationType, NotificationStatus, 
    Booking, User, UserRole
)
from src.utils.auth import get_current_user, ensure_store_access, require_role

notification_bp = Blueprint('notification', __name__)

# EasySMS integration (placeholder - would need actual EasySMS SDK)
def send_sms_via_easysms(phone_number, message):
    """Send SMS via EasySMS (placeholder implementation)"""
    # In production, this would use the actual EasySMS API:
    # import requests
    # api_key = os.environ.get('EASYSMS_API_KEY')
    # response = requests.post('https://api.easysms.gr/api/sms/send', {
    #     'api_key': api_key,
    #     'to': phone_number,
    #     'message': message
    # })
    # return response.json()
    
    # Placeholder response
    return {
        'status': 'success',
        'message_id': f'sms_mock_{phone_number}',
        'cost': 0.05
    }

def send_email_via_easysms(email, subject, message):
    """Send email via EasySMS (placeholder implementation)"""
    # In production, this would use the actual EasySMS email API
    # Placeholder response
    return {
        'status': 'success',
        'message_id': f'email_mock_{email}',
        'cost': 0.01
    }

@notification_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get notifications based on user role"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        if current_user.role == UserRole.ADMIN:
            # Admin can see all notifications
            notifications = Notification.query.all()
        elif current_user.role == UserRole.STORE_MANAGER:
            # Store manager can see notifications for their store
            notifications = Notification.query.filter_by(store_id=current_user.store_id).all()
        else:
            # Clients can see notifications sent to them
            notifications = Notification.query.filter_by(recipient_user_id=current_user.id).all()
        
        return jsonify([notification.to_dict() for notification in notifications]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/notifications/<notification_id>', methods=['GET'])
@jwt_required()
def get_notification(notification_id):
    """Get a specific notification"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        notification = Notification.query.get(notification_id)
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        # Authorization check
        if (current_user.role == UserRole.CLIENT and notification.recipient_user_id != current_user.id) or \
           (current_user.role == UserRole.STORE_MANAGER and notification.store_id != current_user.store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(notification.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/notifications', methods=['POST'])
@jwt_required()
@require_role([UserRole.ADMIN, UserRole.STORE_MANAGER])
def send_notification():
    """Send a notification (Admin or Store Manager only)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['recipient_user_id', 'type', 'body']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate notification type
        try:
            notification_type = NotificationType(data['type'])
        except ValueError:
            return jsonify({'error': 'Invalid notification type'}), 400
        
        # Get recipient
        recipient = User.query.get(data['recipient_user_id'])
        if not recipient:
            return jsonify({'error': 'Recipient not found'}), 404
        
        # Determine store_id
        if current_user.role == UserRole.STORE_MANAGER:
            store_id = current_user.store_id
        else:
            store_id = data.get('store_id')
            if not store_id:
                return jsonify({'error': 'store_id is required for admin'}), 400
        
        # Authorization check for store manager
        if current_user.role == UserRole.STORE_MANAGER:
            # Ensure recipient is a client of their store
            if recipient.role == UserRole.CLIENT:
                booking_exists = Booking.query.filter_by(
                    client_user_id=recipient.id,
                    store_id=store_id
                ).first()
                if not booking_exists:
                    return jsonify({'error': 'Recipient is not a client of your store'}), 403
        
        # Create notification record
        notification = Notification(
            store_id=store_id,
            recipient_user_id=data['recipient_user_id'],
            booking_id=data.get('booking_id'),
            type=notification_type,
            subject=data.get('subject'),
            body=data['body'],
            status=NotificationStatus.SENT
        )
        
        # Send the actual notification
        try:
            if notification_type == NotificationType.SMS:
                if not recipient.phone_number:
                    return jsonify({'error': 'Recipient has no phone number'}), 400
                
                response = send_sms_via_easysms(recipient.phone_number, data['body'])
                if response.get('status') == 'success':
                    notification.external_message_id = response.get('message_id')
                    notification.status = NotificationStatus.DELIVERED
                else:
                    notification.status = NotificationStatus.FAILED
            
            elif notification_type == NotificationType.EMAIL:
                if not recipient.email:
                    return jsonify({'error': 'Recipient has no email address'}), 400
                
                subject = data.get('subject', 'Notification')
                response = send_email_via_easysms(recipient.email, subject, data['body'])
                if response.get('status') == 'success':
                    notification.external_message_id = response.get('message_id')
                    notification.status = NotificationStatus.DELIVERED
                else:
                    notification.status = NotificationStatus.FAILED
        
        except Exception as e:
            notification.status = NotificationStatus.FAILED
        
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'message': 'Notification sent successfully',
            'notification': notification.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/bookings/<booking_id>/send-confirmation', methods=['POST'])
@jwt_required()
@require_role([UserRole.ADMIN, UserRole.STORE_MANAGER])
def send_booking_confirmation(booking_id):
    """Send booking confirmation notification"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Authorization check
        if current_user.role == UserRole.STORE_MANAGER and booking.store_id != current_user.store_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        notification_type = data.get('type', 'email')
        
        try:
            notification_type = NotificationType(notification_type)
        except ValueError:
            return jsonify({'error': 'Invalid notification type'}), 400
        
        # Prepare booking details
        booking_details = {
            'service_name': booking.service.name,
            'booking_date': booking.booking_date.strftime('%Y-%m-%d'),
            'start_time': booking.start_time.strftime('%H:%M'),
            'end_time': booking.end_time.strftime('%H:%M'),
            'number_of_persons': booking.number_of_persons,
            'total_amount': float(booking.total_amount) if booking.total_amount else 0
        }
        
        # Create notification
        notification = Notification.create_booking_confirmation(
            store_id=booking.store_id,
            recipient_user_id=booking.client_user_id,
            booking_id=booking_id,
            booking_details=booking_details
        )
        
        notification.type = notification_type
        
        # Send the notification
        recipient = booking.client
        try:
            if notification_type == NotificationType.SMS:
                if not recipient.phone_number:
                    return jsonify({'error': 'Client has no phone number'}), 400
                
                response = send_sms_via_easysms(recipient.phone_number, notification.body)
                if response.get('status') == 'success':
                    notification.external_message_id = response.get('message_id')
                    notification.status = NotificationStatus.DELIVERED
                else:
                    notification.status = NotificationStatus.FAILED
            
            elif notification_type == NotificationType.EMAIL:
                response = send_email_via_easysms(recipient.email, notification.subject, notification.body)
                if response.get('status') == 'success':
                    notification.external_message_id = response.get('message_id')
                    notification.status = NotificationStatus.DELIVERED
                else:
                    notification.status = NotificationStatus.FAILED
        
        except Exception as e:
            notification.status = NotificationStatus.FAILED
        
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'message': 'Booking confirmation sent successfully',
            'notification': notification.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/bookings/<booking_id>/send-reminder', methods=['POST'])
@jwt_required()
@require_role([UserRole.ADMIN, UserRole.STORE_MANAGER])
def send_booking_reminder(booking_id):
    """Send booking reminder notification"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Authorization check
        if current_user.role == UserRole.STORE_MANAGER and booking.store_id != current_user.store_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        notification_type = data.get('type', 'email')
        
        try:
            notification_type = NotificationType(notification_type)
        except ValueError:
            return jsonify({'error': 'Invalid notification type'}), 400
        
        # Prepare booking details
        booking_details = {
            'service_name': booking.service.name,
            'booking_date': booking.booking_date.strftime('%Y-%m-%d'),
            'start_time': booking.start_time.strftime('%H:%M'),
            'end_time': booking.end_time.strftime('%H:%M')
        }
        
        # Create notification
        notification = Notification.create_booking_reminder(
            store_id=booking.store_id,
            recipient_user_id=booking.client_user_id,
            booking_id=booking_id,
            booking_details=booking_details
        )
        
        notification.type = notification_type
        
        # Send the notification
        recipient = booking.client
        try:
            if notification_type == NotificationType.SMS:
                if not recipient.phone_number:
                    return jsonify({'error': 'Client has no phone number'}), 400
                
                response = send_sms_via_easysms(recipient.phone_number, notification.body)
                if response.get('status') == 'success':
                    notification.external_message_id = response.get('message_id')
                    notification.status = NotificationStatus.DELIVERED
                else:
                    notification.status = NotificationStatus.FAILED
            
            elif notification_type == NotificationType.EMAIL:
                response = send_email_via_easysms(recipient.email, notification.subject, notification.body)
                if response.get('status') == 'success':
                    notification.external_message_id = response.get('message_id')
                    notification.status = NotificationStatus.DELIVERED
                else:
                    notification.status = NotificationStatus.FAILED
        
        except Exception as e:
            notification.status = NotificationStatus.FAILED
        
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'message': 'Booking reminder sent successfully',
            'notification': notification.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/easysms-webhook', methods=['POST'])
def easysms_webhook():
    """Handle EasySMS webhook events for delivery reports"""
    try:
        data = request.get_json()
        
        message_id = data.get('message_id')
        status = data.get('status')  # 'delivered', 'failed', etc.
        
        if message_id and status:
            notification = Notification.query.filter_by(external_message_id=message_id).first()
            
            if notification:
                if status == 'delivered':
                    notification.mark_as_delivered()
                elif status == 'failed':
                    notification.mark_as_failed()
                
                db.session.commit()
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


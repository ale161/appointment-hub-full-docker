from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from src.models import (
    db, Booking, BookingStatus, BookingPaymentStatus, Service, Store, User, UserRole
)
from src.utils.auth import get_current_user, ensure_store_access
from datetime import datetime, date, time

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/bookings', methods=['GET'])
@jwt_required()
def get_bookings():
    """Get bookings based on user role"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        if current_user.role == UserRole.ADMIN:
            # Admin can see all bookings
            bookings = Booking.query.all()
        elif current_user.role == UserRole.STORE_MANAGER:
            # Store manager can see bookings for their store
            bookings = Booking.query.filter_by(store_id=current_user.store_id).all()
        else:
            # Clients can see their own bookings
            bookings = Booking.query.filter_by(client_user_id=current_user.id).all()
        
        # Include related data
        booking_data = []
        for booking in bookings:
            data = booking.to_dict()
            data['service'] = booking.service.to_dict() if booking.service else None
            data['store'] = booking.store.to_dict() if booking.store else None
            data['client'] = booking.client.to_dict() if booking.client else None
            booking_data.append(data)
        
        return jsonify(booking_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/stores/<store_id>/bookings', methods=['GET'])
@jwt_required()
def get_store_bookings(store_id):
    """Get bookings for a specific store"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Authorization check
        if not ensure_store_access(current_user, store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        bookings = Booking.query.filter_by(store_id=store_id).all()
        
        # Include related data
        booking_data = []
        for booking in bookings:
            data = booking.to_dict()
            data['service'] = booking.service.to_dict() if booking.service else None
            data['client'] = booking.client.to_dict() if booking.client else None
            booking_data.append(data)
        
        return jsonify(booking_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/bookings/<booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """Get a specific booking"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Authorization check
        if (current_user.role == UserRole.CLIENT and booking.client_user_id != current_user.id) or \
           (current_user.role == UserRole.STORE_MANAGER and booking.store_id != current_user.store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        # Include related data
        data = booking.to_dict()
        data['service'] = booking.service.to_dict() if booking.service else None
        data['store'] = booking.store.to_dict() if booking.store else None
        data['client'] = booking.client.to_dict() if booking.client else None
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    """Create a new booking"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['service_id', 'booking_date', 'start_time', 'end_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Get service and validate
        service = Service.query.get(data['service_id'])
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        # Parse date and time
        try:
            booking_date = datetime.strptime(data['booking_date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Invalid date or time format'}), 400
        
        # Validate booking is in the future
        booking_datetime = datetime.combine(booking_date, start_time)
        if booking_datetime <= datetime.now():
            return jsonify({'error': 'Booking must be in the future'}), 400
        
        # Validate number of persons
        num_persons = data.get('number_of_persons', 1)
        if num_persons < service.min_persons or num_persons > service.max_persons:
            return jsonify({
                'error': f'Number of persons must be between {service.min_persons} and {service.max_persons}'
            }), 400
        
        # Calculate pricing
        total_amount = service.calculate_total_price(num_persons)
        advance_payment_amount = service.calculate_advance_payment(total_amount)
        
        # Check for conflicts (simplified - in production, integrate with calendar system)
        existing_booking = Booking.query.filter_by(
            service_id=data['service_id'],
            booking_date=booking_date,
            start_time=start_time
        ).filter(Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])).first()
        
        if existing_booking:
            return jsonify({'error': 'Time slot is already booked'}), 409
        
        # Create booking
        booking = Booking(
            store_id=service.store_id,
            client_user_id=current_user.id,
            service_id=data['service_id'],
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            number_of_persons=num_persons,
            status=BookingStatus.PENDING,
            total_amount=total_amount,
            advance_payment_amount=advance_payment_amount,
            payment_status=BookingPaymentStatus.UNPAID
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Include related data in response
        response_data = booking.to_dict()
        response_data['service'] = service.to_dict()
        response_data['store'] = service.store.to_dict()
        
        return jsonify({
            'message': 'Booking created successfully',
            'booking': response_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/bookings/<booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    """Update a booking"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Authorization check
        if (current_user.role == UserRole.CLIENT and booking.client_user_id != current_user.id) or \
           (current_user.role == UserRole.STORE_MANAGER and booking.store_id != current_user.store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update allowed fields based on role
        if current_user.role in [UserRole.ADMIN, UserRole.STORE_MANAGER]:
            # Managers and admins can update status
            if 'status' in data:
                try:
                    booking.status = BookingStatus(data['status'])
                except ValueError:
                    return jsonify({'error': 'Invalid status'}), 400
            
            if 'payment_status' in data:
                try:
                    booking.payment_status = BookingPaymentStatus(data['payment_status'])
                except ValueError:
                    return jsonify({'error': 'Invalid payment status'}), 400
        
        # Clients can reschedule if allowed
        if current_user.role == UserRole.CLIENT and booking.can_be_rescheduled():
            if 'booking_date' in data or 'start_time' in data or 'end_time' in data:
                try:
                    if 'booking_date' in data:
                        booking.booking_date = datetime.strptime(data['booking_date'], '%Y-%m-%d').date()
                    if 'start_time' in data:
                        booking.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
                    if 'end_time' in data:
                        booking.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
                    
                    booking.status = BookingStatus.RESCHEDULED
                except ValueError:
                    return jsonify({'error': 'Invalid date or time format'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'Booking updated successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/bookings/<booking_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_booking(booking_id):
    """Cancel a booking"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Authorization check
        if (current_user.role == UserRole.CLIENT and booking.client_user_id != current_user.id) or \
           (current_user.role == UserRole.STORE_MANAGER and booking.store_id != current_user.store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        if not booking.can_be_cancelled():
            return jsonify({'error': 'Booking cannot be cancelled'}), 409
        
        booking.status = BookingStatus.CANCELLED
        db.session.commit()
        
        return jsonify({
            'message': 'Booking cancelled successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/bookings/<booking_id>/confirm', methods=['POST'])
@jwt_required()
def confirm_booking(booking_id):
    """Confirm a booking (Store Manager or Admin only)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        if current_user.role not in [UserRole.ADMIN, UserRole.STORE_MANAGER]:
            return jsonify({'error': 'Access denied'}), 403
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Authorization check for store manager
        if current_user.role == UserRole.STORE_MANAGER and booking.store_id != current_user.store_id:
            return jsonify({'error': 'Access denied'}), 403
        
        if booking.status != BookingStatus.PENDING:
            return jsonify({'error': 'Only pending bookings can be confirmed'}), 409
        
        booking.status = BookingStatus.CONFIRMED
        db.session.commit()
        
        return jsonify({
            'message': 'Booking confirmed successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/bookings/calendar', methods=['GET'])
@jwt_required()
def get_bookings_calendar():
    """Get bookings in calendar format"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Booking.query
        
        # Apply user-based filtering
        if current_user.role == UserRole.CLIENT:
            query = query.filter_by(client_user_id=current_user.id)
        elif current_user.role == UserRole.STORE_MANAGER:
            query = query.filter_by(store_id=current_user.store_id)
        
        # Apply date filtering
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Booking.booking_date >= start_date)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format'}), 400
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Booking.booking_date <= end_date)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format'}), 400
        
        bookings = query.all()
        
        # Format for calendar
        calendar_events = []
        for booking in bookings:
            event = {
                'id': booking.id,
                'title': f"{booking.service.name} - {booking.client.first_name} {booking.client.last_name}",
                'start': f"{booking.booking_date}T{booking.start_time}",
                'end': f"{booking.booking_date}T{booking.end_time}",
                'status': booking.status.value,
                'service_name': booking.service.name,
                'client_name': f"{booking.client.first_name} {booking.client.last_name}",
                'number_of_persons': booking.number_of_persons,
                'total_amount': float(booking.total_amount) if booking.total_amount else None
            }
            calendar_events.append(event)
        
        return jsonify(calendar_events), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


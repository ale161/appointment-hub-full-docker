from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from src.models import db, Service, Store, UserRole, PriceType, AdvancePaymentType, RecurringInterval
from src.utils.auth import get_current_user, ensure_store_access

service_bp = Blueprint('service', __name__)

@service_bp.route('/stores/<store_id>/services', methods=['GET'])
def get_store_services(store_id):
    """Get all services for a store (public endpoint)"""
    try:
        store = Store.query.get(store_id)
        if not store:
            return jsonify({'error': 'Store not found'}), 404
        
        services = Service.query.filter_by(store_id=store_id).all()
        return jsonify([service.to_dict() for service in services]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@service_bp.route('/stores/<store_slug>/services', methods=['GET'])
def get_store_services_by_slug(store_slug):
    """Get all services for a store by slug (public endpoint)"""
    try:
        store = Store.query.filter_by(slug=store_slug).first()
        if not store:
            return jsonify({'error': 'Store not found'}), 404
        
        services = Service.query.filter_by(store_id=store.id).all()
        return jsonify([service.to_dict() for service in services]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@service_bp.route('/services/<service_id>', methods=['GET'])
def get_service(service_id):
    """Get a specific service (public endpoint)"""
    try:
        service = Service.query.get(service_id)
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        return jsonify(service.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@service_bp.route('/stores/<store_id>/services', methods=['POST'])
@jwt_required()
def create_service(store_id):
    """Create a new service for a store"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Authorization check
        if not ensure_store_access(current_user, store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        store = Store.query.get(store_id)
        if not store:
            return jsonify({'error': 'Store not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'duration_minutes', 'price_type', 'base_price_amount']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate enums
        try:
            price_type = PriceType(data['price_type'])
        except ValueError:
            return jsonify({'error': 'Invalid price_type'}), 400
        
        advance_payment_type = None
        if data.get('advance_payment_type'):
            try:
                advance_payment_type = AdvancePaymentType(data['advance_payment_type'])
            except ValueError:
                return jsonify({'error': 'Invalid advance_payment_type'}), 400
        
        recurring_interval = None
        if data.get('recurring_interval'):
            try:
                recurring_interval = RecurringInterval(data['recurring_interval'])
            except ValueError:
                return jsonify({'error': 'Invalid recurring_interval'}), 400
        
        service = Service(
            store_id=store_id,
            name=data['name'],
            description=data.get('description'),
            duration_minutes=data['duration_minutes'],
            min_persons=data.get('min_persons', 1),
            max_persons=data.get('max_persons', 1),
            price_type=price_type,
            base_price_amount=data['base_price_amount'],
            payment_enabled=data.get('payment_enabled', False),
            advance_payment_type=advance_payment_type,
            advance_payment_amount=data.get('advance_payment_amount'),
            is_recurring=data.get('is_recurring', False),
            recurring_interval=recurring_interval
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify({
            'message': 'Service created successfully',
            'service': service.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@service_bp.route('/services/<service_id>', methods=['PUT'])
@jwt_required()
def update_service(service_id):
    """Update a service"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        service = Service.query.get(service_id)
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        # Authorization check
        if not ensure_store_access(current_user, service.store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = [
            'name', 'description', 'duration_minutes', 'min_persons', 'max_persons',
            'base_price_amount', 'payment_enabled', 'advance_payment_amount',
            'is_recurring'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(service, field, data[field])
        
        # Handle enum fields
        if 'price_type' in data:
            try:
                service.price_type = PriceType(data['price_type'])
            except ValueError:
                return jsonify({'error': 'Invalid price_type'}), 400
        
        if 'advance_payment_type' in data:
            if data['advance_payment_type']:
                try:
                    service.advance_payment_type = AdvancePaymentType(data['advance_payment_type'])
                except ValueError:
                    return jsonify({'error': 'Invalid advance_payment_type'}), 400
            else:
                service.advance_payment_type = None
        
        if 'recurring_interval' in data:
            if data['recurring_interval']:
                try:
                    service.recurring_interval = RecurringInterval(data['recurring_interval'])
                except ValueError:
                    return jsonify({'error': 'Invalid recurring_interval'}), 400
            else:
                service.recurring_interval = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Service updated successfully',
            'service': service.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@service_bp.route('/services/<service_id>', methods=['DELETE'])
@jwt_required()
def delete_service(service_id):
    """Delete a service"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        service = Service.query.get(service_id)
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        # Authorization check
        if not ensure_store_access(current_user, service.store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if service has active bookings
        from src.models import Booking, BookingStatus
        active_bookings = Booking.query.filter_by(service_id=service_id).filter(
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        ).count()
        
        if active_bookings > 0:
            return jsonify({'error': 'Cannot delete service with active bookings'}), 409
        
        db.session.delete(service)
        db.session.commit()
        
        return jsonify({'message': 'Service deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@service_bp.route('/services/<service_id>/calculate-price', methods=['POST'])
def calculate_service_price(service_id):
    """Calculate total price for a service booking"""
    try:
        service = Service.query.get(service_id)
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        data = request.get_json()
        num_persons = data.get('num_persons', 1)
        duration_hours = data.get('duration_hours')
        
        total_price = service.calculate_total_price(num_persons, duration_hours)
        advance_payment = service.calculate_advance_payment(total_price)
        
        return jsonify({
            'total_price': total_price,
            'advance_payment': advance_payment,
            'remaining_payment': total_price - advance_payment,
            'currency': 'EUR'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


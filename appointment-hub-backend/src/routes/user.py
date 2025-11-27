from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, User, UserRole
from src.utils.auth import require_role, get_current_user

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get users - Admin can see all, Store Manager can see store clients"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        if current_user.role == UserRole.ADMIN:
            # Admin can see all users
            users = User.query.all()
        elif current_user.role == UserRole.STORE_MANAGER:
            # Store manager can see clients who have bookings in their store
            from src.models import Booking
            client_ids = db.session.query(Booking.client_user_id).filter_by(store_id=current_user.store_id).distinct().all()
            client_ids = [id[0] for id in client_ids]
            users = User.query.filter(User.id.in_(client_ids)).all()
        else:
            # Clients can only see themselves
            users = [current_user]
        
        return jsonify([user.to_dict() for user in users]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users', methods=['POST'])
@jwt_required()
@require_role([UserRole.ADMIN])
def create_user():
    """Create a new user (Admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate role
        try:
            role = UserRole(data['role'])
        except ValueError:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # For store managers, store_id is required
        if role == UserRole.STORE_MANAGER and not data.get('store_id'):
            return jsonify({'error': 'store_id is required for store managers'}), 400
        
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password_hash=User.hash_password(data['password']),
            phone_number=data.get('phone_number'),
            address=data.get('address'),
            age=data.get('age'),
            role=role,
            store_id=data.get('store_id') if role == UserRole.STORE_MANAGER else None
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get a specific user"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Authorization check
        if current_user.role == UserRole.CLIENT and current_user.id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        elif current_user.role == UserRole.STORE_MANAGER:
            # Store manager can see clients from their store or themselves
            if user.role == UserRole.CLIENT:
                from src.models import Booking
                booking_exists = Booking.query.filter_by(
                    client_user_id=user_id,
                    store_id=current_user.store_id
                ).first()
                if not booking_exists and current_user.id != user_id:
                    return jsonify({'error': 'Access denied'}), 403
            elif current_user.id != user_id:
                return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update a user"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Authorization check
        if current_user.role == UserRole.CLIENT and current_user.id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        elif current_user.role == UserRole.STORE_MANAGER and current_user.id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update allowed fields based on role
        if current_user.role == UserRole.ADMIN:
            allowed_fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'age', 'role', 'store_id']
        else:
            allowed_fields = ['first_name', 'last_name', 'phone_number', 'address', 'age']
        
        for field in allowed_fields:
            if field in data:
                if field == 'role' and data[field]:
                    try:
                        setattr(user, field, UserRole(data[field]))
                    except ValueError:
                        return jsonify({'error': 'Invalid role'}), 400
                else:
                    setattr(user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
@require_role([UserRole.ADMIN])
def delete_user(user_id):
    """Delete a user (Admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


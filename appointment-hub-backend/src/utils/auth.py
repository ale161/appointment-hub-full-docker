from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from src.models import User, UserRole

def get_current_user():
    """Get the current authenticated user"""
    user_id = get_jwt_identity()
    if user_id:
        return User.query.get(user_id)
    return None

def require_role(allowed_roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            if current_user.role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_store_access(f):
    """Decorator to ensure user has access to the specified store"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Admin has access to all stores
        if current_user.role == UserRole.ADMIN:
            return f(*args, **kwargs)
        
        # Store manager can only access their own store
        if current_user.role == UserRole.STORE_MANAGER:
            store_id = kwargs.get('store_id') or kwargs.get('store_slug')
            if store_id and current_user.store_id != store_id:
                return jsonify({'error': 'Access denied to this store'}), 403
        
        # Clients can access any store for viewing/booking
        return f(*args, **kwargs)
    return decorated_function

def get_store_filter(current_user):
    """Get the appropriate store filter for the current user"""
    if current_user.role == UserRole.ADMIN:
        return None  # No filter, can see all stores
    elif current_user.role == UserRole.STORE_MANAGER:
        return current_user.store_id  # Only their store
    else:
        return None  # Clients can see all stores for browsing

def ensure_store_access(current_user, store_id):
    """Ensure the current user has access to the specified store"""
    if current_user.role == UserRole.ADMIN:
        return True
    elif current_user.role == UserRole.STORE_MANAGER:
        return current_user.store_id == store_id
    else:
        return True  # Clients can access any store for viewing/booking


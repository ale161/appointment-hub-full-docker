from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, Store, User, UserRole
from src.utils.auth import require_role, get_current_user, ensure_store_access
import re

store_bp = Blueprint('store', __name__)

def generate_slug(name):
    """Generate a URL-friendly slug from store name"""
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

@store_bp.route('/stores', methods=['GET'])
def get_stores():
    """Get all stores (public endpoint for browsing)"""
    try:
        stores = Store.query.all()
        return jsonify([store.to_dict() for store in stores]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@store_bp.route('/stores/<store_slug>', methods=['GET'])
def get_store_by_slug(store_slug):
    """Get store by slug (public endpoint for client access)"""
    try:
        store = Store.query.filter_by(slug=store_slug).first()
        if not store:
            return jsonify({'error': 'Store not found'}), 404
        
        # Include services and other public information
        store_data = store.to_dict()
        store_data['services'] = [service.to_dict() for service in store.services]
        
        return jsonify(store_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@store_bp.route('/stores', methods=['POST'])
@jwt_required()
@require_role([UserRole.ADMIN])
def create_store():
    """Create a new store (Admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'manager_user_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Verify manager exists and is a store manager
        manager = User.query.get(data['manager_user_id'])
        if not manager:
            return jsonify({'error': 'Manager not found'}), 404
        
        if manager.role != UserRole.STORE_MANAGER:
            return jsonify({'error': 'User must be a store manager'}), 400
        
        if manager.store_id:
            return jsonify({'error': 'Manager is already assigned to a store'}), 409
        
        # Generate slug
        slug = data.get('slug') or generate_slug(data['name'])
        
        # Check if slug is unique
        if Store.query.filter_by(slug=slug).first():
            return jsonify({'error': 'Store slug already exists'}), 409
        
        store = Store(
            name=data['name'],
            slug=slug,
            address=data.get('address'),
            city=data.get('city'),
            country=data.get('country'),
            phone_number=data.get('phone_number'),
            email=data.get('email'),
            description=data.get('description'),
            photos_url=data.get('photos_url', []),
            manager_user_id=data['manager_user_id'],
            calendly_api_key=data.get('calendly_api_key'),
            stripe_enabled=data.get('stripe_enabled', False)
        )
        
        db.session.add(store)
        
        # Update manager's store_id
        manager.store_id = store.id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Store created successfully',
            'store': store.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@store_bp.route('/stores/<store_id>', methods=['PUT'])
@jwt_required()
def update_store(store_id):
    """Update store information"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        store = Store.query.get(store_id)
        if not store:
            return jsonify({'error': 'Store not found'}), 404
        
        # Authorization check
        if not ensure_store_access(current_user, store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['name', 'address', 'city', 'country', 'phone_number', 'email', 'description']
        
        # Admin can update additional fields
        if current_user.role == UserRole.ADMIN:
            allowed_fields.extend(['slug', 'manager_user_id', 'calendly_api_key', 'stripe_enabled'])
        
        for field in allowed_fields:
            if field in data:
                if field == 'slug' and data[field]:
                    # Check slug uniqueness
                    existing_store = Store.query.filter_by(slug=data[field]).first()
                    if existing_store and existing_store.id != store_id:
                        return jsonify({'error': 'Store slug already exists'}), 409
                
                setattr(store, field, data[field])
        
        # Handle photos separately
        if 'photos_url' in data:
            store.photos_url = data['photos_url']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Store updated successfully',
            'store': store.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@store_bp.route('/stores/<store_id>', methods=['DELETE'])
@jwt_required()
@require_role([UserRole.ADMIN])
def delete_store(store_id):
    """Delete a store (Admin only)"""
    try:
        store = Store.query.get(store_id)
        if not store:
            return jsonify({'error': 'Store not found'}), 404
        
        # Update manager's store_id to None
        if store.manager:
            store.manager.store_id = None
        
        db.session.delete(store)
        db.session.commit()
        
        return jsonify({'message': 'Store deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@store_bp.route('/stores/<store_id>/photos', methods=['POST'])
@jwt_required()
def add_store_photo(store_id):
    """Add a photo to store"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        store = Store.query.get(store_id)
        if not store:
            return jsonify({'error': 'Store not found'}), 404
        
        # Authorization check
        if not ensure_store_access(current_user, store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        photo_url = data.get('photo_url')
        
        if not photo_url:
            return jsonify({'error': 'photo_url is required'}), 400
        
        store.add_photo(photo_url)
        db.session.commit()
        
        return jsonify({
            'message': 'Photo added successfully',
            'photos': store.get_photos_list()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@store_bp.route('/stores/<store_id>/photos', methods=['DELETE'])
@jwt_required()
def remove_store_photo(store_id):
    """Remove a photo from store"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        store = Store.query.get(store_id)
        if not store:
            return jsonify({'error': 'Store not found'}), 404
        
        # Authorization check
        if not ensure_store_access(current_user, store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        photo_url = data.get('photo_url')
        
        if not photo_url:
            return jsonify({'error': 'photo_url is required'}), 400
        
        store.remove_photo(photo_url)
        db.session.commit()
        
        return jsonify({
            'message': 'Photo removed successfully',
            'photos': store.get_photos_list()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@store_bp.route('/my-store', methods=['GET'])
@jwt_required()
@require_role([UserRole.STORE_MANAGER])
def get_my_store():
    """Get current manager's store"""
    try:
        current_user = get_current_user()
        if not current_user or not current_user.store_id:
            return jsonify({'error': 'No store assigned'}), 404
        
        store = Store.query.get(current_user.store_id)
        if not store:
            return jsonify({'error': 'Store not found'}), 404
        
        # Include additional information for store manager
        store_data = store.to_dict(include_sensitive=True)
        store_data['services'] = [service.to_dict() for service in store.services]
        store_data['calendars'] = [calendar.to_dict() for calendar in store.calendars]
        
        return jsonify(store_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


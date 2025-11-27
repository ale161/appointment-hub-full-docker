from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from src.models import (
    db, SubscriptionPlan, Subscription, SubscriptionInterval, 
    SubscriptionStatus, UserRole, Store
)
from src.utils.auth import get_current_user, require_role, ensure_store_access

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/subscription-plans', methods=['GET'])
def get_subscription_plans():
    """Get all active subscription plans (public endpoint)"""
    try:
        plans = SubscriptionPlan.query.filter_by(is_active=True).all()
        return jsonify([plan.to_dict() for plan in plans]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/subscription-plans', methods=['POST'])
@jwt_required()
@require_role([UserRole.ADMIN])
def create_subscription_plan():
    """Create a new subscription plan (Admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'price_amount', 'interval']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate interval
        try:
            interval = SubscriptionInterval(data['interval'])
        except ValueError:
            return jsonify({'error': 'Invalid interval'}), 400
        
        plan = SubscriptionPlan(
            name=data['name'],
            description=data.get('description'),
            price_amount=data['price_amount'],
            currency=data.get('currency', 'EUR'),
            interval=interval,
            features=data.get('features', {}),
            stripe_price_id=data.get('stripe_price_id'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Subscription plan created successfully',
            'plan': plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/subscription-plans/<plan_id>', methods=['GET'])
def get_subscription_plan(plan_id):
    """Get a specific subscription plan"""
    try:
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan:
            return jsonify({'error': 'Subscription plan not found'}), 404
        
        return jsonify(plan.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/subscription-plans/<plan_id>', methods=['PUT'])
@jwt_required()
@require_role([UserRole.ADMIN])
def update_subscription_plan(plan_id):
    """Update a subscription plan (Admin only)"""
    try:
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan:
            return jsonify({'error': 'Subscription plan not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['name', 'description', 'price_amount', 'currency', 'features', 'stripe_price_id', 'is_active']
        
        for field in allowed_fields:
            if field in data:
                setattr(plan, field, data[field])
        
        # Handle interval separately
        if 'interval' in data:
            try:
                plan.interval = SubscriptionInterval(data['interval'])
            except ValueError:
                return jsonify({'error': 'Invalid interval'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'Subscription plan updated successfully',
            'plan': plan.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/subscription-plans/<plan_id>', methods=['DELETE'])
@jwt_required()
@require_role([UserRole.ADMIN])
def delete_subscription_plan(plan_id):
    """Delete a subscription plan (Admin only)"""
    try:
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan:
            return jsonify({'error': 'Subscription plan not found'}), 404
        
        # Check if plan has active subscriptions
        active_subscriptions = Subscription.query.filter_by(
            plan_id=plan_id,
            status=SubscriptionStatus.ACTIVE
        ).count()
        
        if active_subscriptions > 0:
            return jsonify({'error': 'Cannot delete plan with active subscriptions'}), 409
        
        db.session.delete(plan)
        db.session.commit()
        
        return jsonify({'message': 'Subscription plan deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/subscriptions', methods=['GET'])
@jwt_required()
def get_subscriptions():
    """Get subscriptions based on user role"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        if current_user.role == UserRole.ADMIN:
            # Admin can see all subscriptions
            subscriptions = Subscription.query.all()
        elif current_user.role == UserRole.STORE_MANAGER:
            # Store manager can see their store's subscriptions
            subscriptions = Subscription.query.filter_by(store_id=current_user.store_id).all()
        else:
            return jsonify({'error': 'Access denied'}), 403
        
        # Include plan details
        subscription_data = []
        for subscription in subscriptions:
            data = subscription.to_dict()
            data['plan'] = subscription.plan.to_dict() if subscription.plan else None
            data['store'] = subscription.store.to_dict() if subscription.store else None
            subscription_data.append(data)
        
        return jsonify(subscription_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/stores/<store_id>/subscriptions', methods=['GET'])
@jwt_required()
def get_store_subscriptions(store_id):
    """Get subscriptions for a specific store"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Authorization check
        if not ensure_store_access(current_user, store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        subscriptions = Subscription.query.filter_by(store_id=store_id).all()
        
        # Include plan details
        subscription_data = []
        for subscription in subscriptions:
            data = subscription.to_dict()
            data['plan'] = subscription.plan.to_dict() if subscription.plan else None
            subscription_data.append(data)
        
        return jsonify(subscription_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/stores/<store_id>/subscribe', methods=['POST'])
@jwt_required()
def create_subscription(store_id):
    """Create a new subscription for a store"""
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
        plan_id = data.get('plan_id')
        
        if not plan_id:
            return jsonify({'error': 'plan_id is required'}), 400
        
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan or not plan.is_active:
            return jsonify({'error': 'Invalid or inactive subscription plan'}), 404
        
        # Check if store already has an active subscription
        existing_subscription = Subscription.query.filter_by(
            store_id=store_id,
            status=SubscriptionStatus.ACTIVE
        ).first()
        
        if existing_subscription:
            return jsonify({'error': 'Store already has an active subscription'}), 409
        
        # Create subscription
        subscription = Subscription(
            store_id=store_id,
            plan_id=plan_id,
            status=SubscriptionStatus.ACTIVE
        )
        
        db.session.add(subscription)
        
        # Update store's current subscription plan
        store.current_subscription_plan_id = plan_id
        
        db.session.commit()
        
        # Include plan details in response
        response_data = subscription.to_dict()
        response_data['plan'] = plan.to_dict()
        
        return jsonify({
            'message': 'Subscription created successfully',
            'subscription': response_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/subscriptions/<subscription_id>', methods=['GET'])
@jwt_required()
def get_subscription(subscription_id):
    """Get a specific subscription"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return jsonify({'error': 'Subscription not found'}), 404
        
        # Authorization check
        if not ensure_store_access(current_user, subscription.store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        # Include plan details
        data = subscription.to_dict()
        data['plan'] = subscription.plan.to_dict() if subscription.plan else None
        data['store'] = subscription.store.to_dict() if subscription.store else None
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/subscriptions/<subscription_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription(subscription_id):
    """Cancel a subscription"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return jsonify({'error': 'Subscription not found'}), 404
        
        # Authorization check
        if not ensure_store_access(current_user, subscription.store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        if not subscription.can_be_cancelled():
            return jsonify({'error': 'Subscription cannot be cancelled'}), 409
        
        subscription.cancel()
        
        # Update store's current subscription plan
        store = subscription.store
        store.current_subscription_plan_id = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Subscription cancelled successfully',
            'subscription': subscription.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/subscriptions/<subscription_id>/upgrade', methods=['POST'])
@jwt_required()
def upgrade_subscription(subscription_id):
    """Upgrade a subscription to a different plan"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return jsonify({'error': 'Subscription not found'}), 404
        
        # Authorization check
        if not ensure_store_access(current_user, subscription.store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        new_plan_id = data.get('plan_id')
        
        if not new_plan_id:
            return jsonify({'error': 'plan_id is required'}), 400
        
        new_plan = SubscriptionPlan.query.get(new_plan_id)
        if not new_plan or not new_plan.is_active:
            return jsonify({'error': 'Invalid or inactive subscription plan'}), 404
        
        if subscription.plan_id == new_plan_id:
            return jsonify({'error': 'Already subscribed to this plan'}), 409
        
        if not subscription.is_active():
            return jsonify({'error': 'Can only upgrade active subscriptions'}), 409
        
        # Cancel current subscription
        subscription.cancel()
        
        # Create new subscription
        new_subscription = Subscription(
            store_id=subscription.store_id,
            plan_id=new_plan_id,
            status=SubscriptionStatus.ACTIVE
        )
        
        db.session.add(new_subscription)
        
        # Update store's current subscription plan
        store = subscription.store
        store.current_subscription_plan_id = new_plan_id
        
        db.session.commit()
        
        # Include plan details in response
        response_data = new_subscription.to_dict()
        response_data['plan'] = new_plan.to_dict()
        
        return jsonify({
            'message': 'Subscription upgraded successfully',
            'subscription': response_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@subscription_bp.route('/my-subscription', methods=['GET'])
@jwt_required()
@require_role([UserRole.STORE_MANAGER])
def get_my_subscription():
    """Get current store manager's subscription"""
    try:
        current_user = get_current_user()
        if not current_user or not current_user.store_id:
            return jsonify({'error': 'No store assigned'}), 404
        
        subscription = Subscription.query.filter_by(
            store_id=current_user.store_id,
            status=SubscriptionStatus.ACTIVE
        ).first()
        
        if not subscription:
            return jsonify({'error': 'No active subscription found'}), 404
        
        # Include plan details
        data = subscription.to_dict()
        data['plan'] = subscription.plan.to_dict() if subscription.plan else None
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


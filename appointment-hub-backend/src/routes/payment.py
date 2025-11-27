from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from src.models import db, Payment, PaymentStatus, Booking, Subscription, UserRole
from src.utils.auth import get_current_user, ensure_store_access
import os

payment_bp = Blueprint('payment', __name__)

# Stripe integration (placeholder - would need actual Stripe SDK)
def create_stripe_payment_intent(amount, currency='eur', metadata=None):
    """Create a Stripe PaymentIntent (placeholder implementation)"""
    # In production, this would use the actual Stripe SDK:
    # import stripe
    # stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
    # return stripe.PaymentIntent.create(amount=amount, currency=currency, metadata=metadata)
    
    # Placeholder response
    return {
        'id': f'pi_mock_{amount}_{currency}',
        'client_secret': f'pi_mock_{amount}_{currency}_secret',
        'amount': amount,
        'currency': currency,
        'status': 'requires_payment_method'
    }

@payment_bp.route('/payments', methods=['GET'])
@jwt_required()
def get_payments():
    """Get payments based on user role"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        if current_user.role == UserRole.ADMIN:
            # Admin can see all payments
            payments = Payment.query.all()
        elif current_user.role == UserRole.STORE_MANAGER:
            # Store manager can see payments for their store
            payments = Payment.query.filter_by(store_id=current_user.store_id).all()
        else:
            # Clients can see their own payments
            payments = Payment.query.filter_by(user_id=current_user.id).all()
        
        return jsonify([payment.to_dict() for payment in payments]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/payments/<payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Get a specific payment"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Authorization check
        if (current_user.role == UserRole.CLIENT and payment.user_id != current_user.id) or \
           (current_user.role == UserRole.STORE_MANAGER and payment.store_id != current_user.store_id):
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(payment.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/bookings/<booking_id>/create-payment-intent', methods=['POST'])
@jwt_required()
def create_booking_payment_intent(booking_id):
    """Create a payment intent for a booking"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        # Authorization check - only the client who made the booking can pay
        if booking.client_user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if store has Stripe enabled
        if not booking.store.stripe_enabled:
            return jsonify({'error': 'Payment not enabled for this store'}), 400
        
        # Check if service has payment enabled
        if not booking.service.payment_enabled:
            return jsonify({'error': 'Payment not required for this service'}), 400
        
        data = request.get_json()
        payment_type = data.get('payment_type', 'full')  # 'advance' or 'full'
        
        # Calculate amount
        if payment_type == 'advance':
            amount = booking.advance_payment_amount or 0
        else:
            amount = booking.calculate_remaining_payment()
        
        if amount <= 0:
            return jsonify({'error': 'No payment required'}), 400
        
        # Convert to cents for Stripe
        amount_cents = int(float(amount) * 100)
        
        # Create Stripe PaymentIntent
        payment_intent = create_stripe_payment_intent(
            amount=amount_cents,
            currency='eur',
            metadata={
                'booking_id': booking_id,
                'store_id': booking.store_id,
                'payment_type': payment_type
            }
        )
        
        # Create Payment record
        payment = Payment.create_from_stripe_intent(
            payment_intent,
            store_id=booking.store_id,
            user_id=current_user.id,
            booking_id=booking_id
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'payment_intent': {
                'id': payment_intent['id'],
                'client_secret': payment_intent['client_secret'],
                'amount': amount,
                'currency': 'EUR'
            },
            'payment': payment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/subscriptions/<subscription_id>/create-payment-intent', methods=['POST'])
@jwt_required()
def create_subscription_payment_intent(subscription_id):
    """Create a payment intent for a subscription"""
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
        
        # Get subscription plan amount
        amount = float(subscription.plan.price_amount)
        amount_cents = int(amount * 100)
        
        # Create Stripe PaymentIntent
        payment_intent = create_stripe_payment_intent(
            amount=amount_cents,
            currency=subscription.plan.currency.lower(),
            metadata={
                'subscription_id': subscription_id,
                'store_id': subscription.store_id,
                'plan_id': subscription.plan_id
            }
        )
        
        # Create Payment record
        payment = Payment.create_from_stripe_intent(
            payment_intent,
            store_id=subscription.store_id,
            user_id=current_user.id,
            subscription_id=subscription_id
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'payment_intent': {
                'id': payment_intent['id'],
                'client_secret': payment_intent['client_secret'],
                'amount': amount,
                'currency': subscription.plan.currency
            },
            'payment': payment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    try:
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        # In production, verify the webhook signature:
        # event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        
        # For now, parse the JSON payload directly (in production, use the verified event)
        import json
        event_data = json.loads(payload)
        
        event_type = event_data.get('type')
        event_object = event_data.get('data', {}).get('object', {})
        
        if event_type in ['payment_intent.succeeded', 'payment_intent.payment_failed']:
            # Find payment by Stripe PaymentIntent ID
            payment_intent_id = event_object.get('id')
            payment = Payment.query.filter_by(stripe_payment_intent_id=payment_intent_id).first()
            
            if payment:
                payment.update_from_stripe_event(event_data)
                
                # Update booking payment status if it's a booking payment
                if payment.booking_id:
                    booking = payment.booking
                    if payment.is_successful():
                        if payment.amount >= booking.total_amount:
                            booking.payment_status = PaymentStatus.PAID
                        else:
                            booking.payment_status = PaymentStatus.PARTIAL
                    else:
                        booking.payment_status = PaymentStatus.UNPAID
                
                db.session.commit()
        
        elif event_type in ['customer.subscription.created', 'customer.subscription.updated', 'customer.subscription.deleted']:
            # Handle subscription events
            stripe_subscription_id = event_object.get('id')
            subscription = Subscription.query.filter_by(stripe_subscription_id=stripe_subscription_id).first()
            
            if subscription:
                subscription.update_from_stripe_event(event_data)
                db.session.commit()
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@payment_bp.route('/payments/<payment_id>/refund', methods=['POST'])
@jwt_required()
def refund_payment(payment_id):
    """Refund a payment (Admin or Store Manager only)"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        if current_user.role not in [UserRole.ADMIN, UserRole.STORE_MANAGER]:
            return jsonify({'error': 'Access denied'}), 403
        
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Authorization check for store manager
        if current_user.role == UserRole.STORE_MANAGER and payment.store_id != current_user.store_id:
            return jsonify({'error': 'Access denied'}), 403
        
        if not payment.can_be_refunded():
            return jsonify({'error': 'Payment cannot be refunded'}), 409
        
        data = request.get_json()
        refund_amount = data.get('amount')  # If not provided, refund full amount
        
        # In production, create actual Stripe refund:
        # refund = stripe.Refund.create(
        #     charge=payment.stripe_charge_id,
        #     amount=int(refund_amount * 100) if refund_amount else None
        # )
        
        # Update payment status
        payment.status = PaymentStatus.REFUNDED
        db.session.commit()
        
        return jsonify({
            'message': 'Payment refunded successfully',
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


import os
import stripe
from typing import Dict, List, Optional
from decimal import Decimal

class StripeIntegration:
    """Stripe API integration for payments and subscriptions"""
    
    def __init__(self, secret_key: str, webhook_secret: str = None):
        self.secret_key = secret_key
        self.webhook_secret = webhook_secret
        stripe.api_key = secret_key
    
    def create_payment_intent(self, amount: int, currency: str = 'eur', 
                            customer_id: str = None, metadata: Dict = None) -> Optional[Dict]:
        """Create a PaymentIntent for one-time payments"""
        try:
            intent_data = {
                'amount': amount,  # Amount in cents
                'currency': currency,
                'automatic_payment_methods': {'enabled': True}
            }
            
            if customer_id:
                intent_data['customer'] = customer_id
            
            if metadata:
                intent_data['metadata'] = metadata
            
            payment_intent = stripe.PaymentIntent.create(**intent_data)
            
            return {
                'success': True,
                'payment_intent': payment_intent,
                'client_secret': payment_intent.client_secret
            }
            
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_customer(self, email: str, name: str = None, 
                       phone: str = None, metadata: Dict = None) -> Optional[Dict]:
        """Create a Stripe customer"""
        try:
            customer_data = {'email': email}
            
            if name:
                customer_data['name'] = name
            if phone:
                customer_data['phone'] = phone
            if metadata:
                customer_data['metadata'] = metadata
            
            customer = stripe.Customer.create(**customer_data)
            
            return {
                'success': True,
                'customer': customer
            }
            
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_product(self, name: str, description: str = None, 
                      metadata: Dict = None) -> Optional[Dict]:
        """Create a Stripe product"""
        try:
            product_data = {'name': name}
            
            if description:
                product_data['description'] = description
            if metadata:
                product_data['metadata'] = metadata
            
            product = stripe.Product.create(**product_data)
            
            return {
                'success': True,
                'product': product
            }
            
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_price(self, product_id: str, unit_amount: int, currency: str = 'eur',
                    recurring: Dict = None, metadata: Dict = None) -> Optional[Dict]:
        """Create a Stripe price"""
        try:
            price_data = {
                'product': product_id,
                'unit_amount': unit_amount,
                'currency': currency
            }
            
            if recurring:
                price_data['recurring'] = recurring
            if metadata:
                price_data['metadata'] = metadata
            
            price = stripe.Price.create(**price_data)
            
            return {
                'success': True,
                'price': price
            }
            
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_subscription(self, customer_id: str, price_id: str,
                          trial_period_days: int = None, metadata: Dict = None) -> Optional[Dict]:
        """Create a Stripe subscription"""
        try:
            subscription_data = {
                'customer': customer_id,
                'items': [{'price': price_id}]
            }
            
            if trial_period_days:
                subscription_data['trial_period_days'] = trial_period_days
            if metadata:
                subscription_data['metadata'] = metadata
            
            subscription = stripe.Subscription.create(**subscription_data)
            
            return {
                'success': True,
                'subscription': subscription
            }
            
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> Optional[Dict]:
        """Cancel a Stripe subscription"""
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)
            
            return {
                'success': True,
                'subscription': subscription
            }
            
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_refund(self, payment_intent_id: str = None, charge_id: str = None,
                     amount: int = None, reason: str = None) -> Optional[Dict]:
        """Create a refund"""
        try:
            refund_data = {}
            
            if payment_intent_id:
                refund_data['payment_intent'] = payment_intent_id
            elif charge_id:
                refund_data['charge'] = charge_id
            else:
                return {
                    'success': False,
                    'error': 'Either payment_intent_id or charge_id is required'
                }
            
            if amount:
                refund_data['amount'] = amount
            if reason:
                refund_data['reason'] = reason
            
            refund = stripe.Refund.create(**refund_data)
            
            return {
                'success': True,
                'refund': refund
            }
            
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def retrieve_payment_intent(self, payment_intent_id: str) -> Optional[Dict]:
        """Retrieve a PaymentIntent"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'success': True,
                'payment_intent': payment_intent
            }
            
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def retrieve_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Retrieve a subscription"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                'success': True,
                'subscription': subscription
            }
            
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def construct_webhook_event(self, payload: bytes, sig_header: str) -> Optional[Dict]:
        """Construct and verify webhook event"""
        try:
            if not self.webhook_secret:
                return {
                    'success': False,
                    'error': 'Webhook secret not configured'
                }
            
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            
            return {
                'success': True,
                'event': event
            }
            
        except ValueError as e:
            return {
                'success': False,
                'error': f'Invalid payload: {e}'
            }
        except stripe.error.SignatureVerificationError as e:
            return {
                'success': False,
                'error': f'Invalid signature: {e}'
            }
    
    def process_webhook_event(self, event: Dict) -> Dict:
        """Process webhook event and return structured data"""
        event_type = event['type']
        event_data = event['data']['object']
        
        if event_type == 'payment_intent.succeeded':
            return {
                'type': 'payment_succeeded',
                'payment_intent_id': event_data['id'],
                'amount': event_data['amount'],
                'currency': event_data['currency'],
                'customer_id': event_data.get('customer'),
                'metadata': event_data.get('metadata', {})
            }
        
        elif event_type == 'payment_intent.payment_failed':
            return {
                'type': 'payment_failed',
                'payment_intent_id': event_data['id'],
                'amount': event_data['amount'],
                'currency': event_data['currency'],
                'customer_id': event_data.get('customer'),
                'last_payment_error': event_data.get('last_payment_error'),
                'metadata': event_data.get('metadata', {})
            }
        
        elif event_type == 'customer.subscription.created':
            return {
                'type': 'subscription_created',
                'subscription_id': event_data['id'],
                'customer_id': event_data['customer'],
                'status': event_data['status'],
                'current_period_start': event_data['current_period_start'],
                'current_period_end': event_data['current_period_end'],
                'metadata': event_data.get('metadata', {})
            }
        
        elif event_type == 'customer.subscription.updated':
            return {
                'type': 'subscription_updated',
                'subscription_id': event_data['id'],
                'customer_id': event_data['customer'],
                'status': event_data['status'],
                'current_period_start': event_data['current_period_start'],
                'current_period_end': event_data['current_period_end'],
                'metadata': event_data.get('metadata', {})
            }
        
        elif event_type == 'customer.subscription.deleted':
            return {
                'type': 'subscription_deleted',
                'subscription_id': event_data['id'],
                'customer_id': event_data['customer'],
                'status': event_data['status'],
                'metadata': event_data.get('metadata', {})
            }
        
        elif event_type == 'invoice.payment_succeeded':
            return {
                'type': 'invoice_paid',
                'invoice_id': event_data['id'],
                'subscription_id': event_data.get('subscription'),
                'customer_id': event_data['customer'],
                'amount_paid': event_data['amount_paid'],
                'currency': event_data['currency']
            }
        
        elif event_type == 'invoice.payment_failed':
            return {
                'type': 'invoice_payment_failed',
                'invoice_id': event_data['id'],
                'subscription_id': event_data.get('subscription'),
                'customer_id': event_data['customer'],
                'amount_due': event_data['amount_due'],
                'currency': event_data['currency']
            }
        
        else:
            return {
                'type': 'unknown',
                'event_type': event_type,
                'raw_data': event_data
            }
    
    def format_amount_for_stripe(self, amount: Decimal, currency: str = 'eur') -> int:
        """Convert decimal amount to Stripe's integer format (cents)"""
        # Most currencies use 2 decimal places, but some use 0 or 3
        if currency.lower() in ['jpy', 'krw']:  # Zero-decimal currencies
            return int(amount)
        else:  # Two-decimal currencies (EUR, USD, etc.)
            return int(amount * 100)
    
    def format_amount_from_stripe(self, amount: int, currency: str = 'eur') -> Decimal:
        """Convert Stripe's integer amount to decimal"""
        if currency.lower() in ['jpy', 'krw']:  # Zero-decimal currencies
            return Decimal(str(amount))
        else:  # Two-decimal currencies
            return Decimal(str(amount)) / 100

# Factory function to create Stripe integration instance
def create_stripe_integration(secret_key: str = None, webhook_secret: str = None) -> Optional[StripeIntegration]:
    """Create a Stripe integration instance"""
    if not secret_key:
        secret_key = os.environ.get('STRIPE_SECRET_KEY')
    
    if not webhook_secret:
        webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    if not secret_key:
        print("Stripe secret key not provided")
        return None
    
    return StripeIntegration(secret_key, webhook_secret)

# Subscription plan helpers
class SubscriptionPlanHelper:
    """Helper class for managing subscription plans in Stripe"""
    
    @staticmethod
    def create_monthly_plan(stripe_integration: StripeIntegration, name: str, 
                          price_amount: Decimal, description: str = None) -> Optional[Dict]:
        """Create a monthly subscription plan"""
        # Create product
        product_result = stripe_integration.create_product(
            name=name,
            description=description
        )
        
        if not product_result['success']:
            return product_result
        
        product_id = product_result['product']['id']
        
        # Create price
        price_result = stripe_integration.create_price(
            product_id=product_id,
            unit_amount=stripe_integration.format_amount_for_stripe(price_amount),
            recurring={'interval': 'month'}
        )
        
        if not price_result['success']:
            return price_result
        
        return {
            'success': True,
            'product': product_result['product'],
            'price': price_result['price']
        }
    
    @staticmethod
    def create_yearly_plan(stripe_integration: StripeIntegration, name: str, 
                         price_amount: Decimal, description: str = None) -> Optional[Dict]:
        """Create a yearly subscription plan"""
        # Create product
        product_result = stripe_integration.create_product(
            name=name,
            description=description
        )
        
        if not product_result['success']:
            return product_result
        
        product_id = product_result['product']['id']
        
        # Create price
        price_result = stripe_integration.create_price(
            product_id=product_id,
            unit_amount=stripe_integration.format_amount_for_stripe(price_amount),
            recurring={'interval': 'year'}
        )
        
        if not price_result['success']:
            return price_result
        
        return {
            'success': True,
            'product': product_result['product'],
            'price': price_result['price']
        }


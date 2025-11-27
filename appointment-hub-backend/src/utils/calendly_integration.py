import os
import requests
from datetime import datetime
from typing import Dict, List, Optional

class CalendlyIntegration:
    """Calendly API v2 integration for calendar synchronization"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.calendly.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current user information"""
        try:
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting current user: {e}")
            return None
    
    def get_event_types(self, user_uri: str) -> List[Dict]:
        """Get event types for a user"""
        try:
            response = requests.get(
                f"{self.base_url}/event_types",
                headers=self.headers,
                params={"user": user_uri}
            )
            response.raise_for_status()
            return response.json().get("collection", [])
        except requests.RequestException as e:
            print(f"Error getting event types: {e}")
            return []
    
    def get_scheduled_events(self, user_uri: str, start_time: str = None, end_time: str = None) -> List[Dict]:
        """Get scheduled events for a user"""
        try:
            params = {"user": user_uri}
            if start_time:
                params["min_start_time"] = start_time
            if end_time:
                params["max_start_time"] = end_time
            
            response = requests.get(
                f"{self.base_url}/scheduled_events",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json().get("collection", [])
        except requests.RequestException as e:
            print(f"Error getting scheduled events: {e}")
            return []
    
    def create_webhook_subscription(self, url: str, events: List[str], organization_uri: str) -> Optional[Dict]:
        """Create a webhook subscription"""
        try:
            data = {
                "url": url,
                "events": events,
                "organization": organization_uri,
                "scope": "organization"
            }
            
            response = requests.post(
                f"{self.base_url}/webhook_subscriptions",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error creating webhook subscription: {e}")
            return None
    
    def delete_webhook_subscription(self, webhook_uuid: str) -> bool:
        """Delete a webhook subscription"""
        try:
            response = requests.delete(
                f"{self.base_url}/webhook_subscriptions/{webhook_uuid}",
                headers=self.headers
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error deleting webhook subscription: {e}")
            return False
    
    def process_webhook_event(self, event_data: Dict) -> Dict:
        """Process incoming webhook event"""
        event_type = event_data.get("event")
        payload = event_data.get("payload", {})
        
        if event_type == "invitee.created":
            return {
                "type": "booking_created",
                "event_uri": payload.get("event", {}).get("uri"),
                "invitee_uri": payload.get("uri"),
                "invitee_email": payload.get("email"),
                "start_time": payload.get("event", {}).get("start_time"),
                "end_time": payload.get("event", {}).get("end_time"),
                "event_type_name": payload.get("event", {}).get("event_type", {}).get("name")
            }
        elif event_type == "invitee.canceled":
            return {
                "type": "booking_canceled",
                "event_uri": payload.get("event", {}).get("uri"),
                "invitee_uri": payload.get("uri"),
                "invitee_email": payload.get("email"),
                "cancellation_reason": payload.get("cancellation", {}).get("reason")
            }
        
        return {"type": "unknown", "raw_data": event_data}
    
    def sync_booking_to_calendly(self, booking_data: Dict) -> Optional[str]:
        """Sync a booking to Calendly (placeholder - actual implementation would depend on Calendly's booking API)"""
        # Note: Calendly API v2 doesn't have a direct booking creation endpoint
        # This would typically be handled through Calendly's booking page integration
        # or by creating calendar events directly if using calendar integration
        
        print(f"Would sync booking to Calendly: {booking_data}")
        return f"calendly_event_mock_{booking_data.get('id')}"
    
    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str, webhook_signing_key: str) -> bool:
        """Verify Calendly webhook signature"""
        import hmac
        import hashlib
        import base64
        
        try:
            expected_signature = base64.b64encode(
                hmac.new(
                    webhook_signing_key.encode(),
                    payload,
                    hashlib.sha256
                ).digest()
            ).decode()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            print(f"Error verifying webhook signature: {e}")
            return False

# Factory function to create Calendly integration instance
def create_calendly_integration(api_key: str = None) -> Optional[CalendlyIntegration]:
    """Create a Calendly integration instance"""
    if not api_key:
        api_key = os.environ.get('CALENDLY_API_KEY')
    
    if not api_key:
        print("Calendly API key not provided")
        return None
    
    return CalendlyIntegration(api_key)


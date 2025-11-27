import os
import requests
from typing import Dict, List, Optional

class EasySMSIntegration:
    """EasySMS API integration for email and SMS notifications"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.easysms.gr"
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def send_sms(self, to: str, message: str, sender: str = None) -> Dict:
        """Send SMS message"""
        try:
            data = {
                "api_key": self.api_key,
                "to": to,
                "message": message
            }
            
            if sender:
                data["sender"] = sender
            
            response = requests.post(
                f"{self.base_url}/api/sms/send",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message_id": result.get("message_id"),
                    "cost": result.get("cost"),
                    "credits_remaining": result.get("credits_remaining")
                }
            else:
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code
                }
                
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_email(self, to: str, subject: str, message: str, sender_email: str = None, sender_name: str = None) -> Dict:
        """Send email message"""
        try:
            data = {
                "api_key": self.api_key,
                "to": to,
                "subject": subject,
                "message": message
            }
            
            if sender_email:
                data["sender_email"] = sender_email
            if sender_name:
                data["sender_name"] = sender_name
            
            response = requests.post(
                f"{self.base_url}/api/email/send",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message_id": result.get("message_id"),
                    "cost": result.get("cost")
                }
            else:
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code
                }
                
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_account_balance(self) -> Dict:
        """Get account balance and credits"""
        try:
            response = requests.get(
                f"{self.base_url}/api/account/balance",
                headers=self.headers,
                params={"api_key": self.api_key}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "balance": result.get("balance"),
                    "credits": result.get("credits"),
                    "currency": result.get("currency", "EUR")
                }
            else:
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code
                }
                
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_delivery_report(self, message_id: str) -> Dict:
        """Get delivery report for a message"""
        try:
            response = requests.get(
                f"{self.base_url}/api/reports/delivery",
                headers=self.headers,
                params={
                    "api_key": self.api_key,
                    "message_id": message_id
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message_id": result.get("message_id"),
                    "status": result.get("status"),
                    "delivered_at": result.get("delivered_at"),
                    "error_code": result.get("error_code"),
                    "error_message": result.get("error_message")
                }
            else:
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code
                }
                
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_bulk_sms(self, recipients: List[str], message: str, sender: str = None) -> Dict:
        """Send SMS to multiple recipients"""
        try:
            data = {
                "api_key": self.api_key,
                "recipients": recipients,
                "message": message
            }
            
            if sender:
                data["sender"] = sender
            
            response = requests.post(
                f"{self.base_url}/api/sms/bulk",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "batch_id": result.get("batch_id"),
                    "total_messages": result.get("total_messages"),
                    "total_cost": result.get("total_cost"),
                    "credits_remaining": result.get("credits_remaining")
                }
            else:
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code
                }
                
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_webhook_event(self, event_data: Dict) -> Dict:
        """Process incoming webhook event for delivery reports"""
        message_id = event_data.get("message_id")
        status = event_data.get("status")
        delivered_at = event_data.get("delivered_at")
        error_code = event_data.get("error_code")
        error_message = event_data.get("error_message")
        
        return {
            "message_id": message_id,
            "status": status,
            "delivered_at": delivered_at,
            "error_code": error_code,
            "error_message": error_message,
            "is_delivered": status == "delivered",
            "is_failed": status == "failed"
        }
    
    def format_phone_number(self, phone: str, country_code: str = "+30") -> str:
        """Format phone number for Greek numbers"""
        # Remove any non-digit characters
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Handle Greek mobile numbers
        if clean_phone.startswith("69") and len(clean_phone) == 10:
            return f"+30{clean_phone}"
        elif clean_phone.startswith("30") and len(clean_phone) == 12:
            return f"+{clean_phone}"
        elif clean_phone.startswith("0030") and len(clean_phone) == 14:
            return f"+{clean_phone[2:]}"
        
        # Default formatting
        if not clean_phone.startswith(country_code.replace("+", "")):
            return f"{country_code}{clean_phone}"
        
        return f"+{clean_phone}"
    
    def create_personalized_message(self, template: str, variables: Dict) -> str:
        """Create personalized message from template"""
        message = template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            message = message.replace(placeholder, str(value))
        return message

# Factory function to create EasySMS integration instance
def create_easysms_integration(api_key: str = None) -> Optional[EasySMSIntegration]:
    """Create an EasySMS integration instance"""
    if not api_key:
        api_key = os.environ.get('EASYSMS_API_KEY')
    
    if not api_key:
        print("EasySMS API key not provided")
        return None
    
    return EasySMSIntegration(api_key)

# Message templates
class MessageTemplates:
    """Predefined message templates for common notifications"""
    
    BOOKING_CONFIRMATION = """
Your booking has been confirmed!

Service: {service_name}
Date: {booking_date}
Time: {start_time} - {end_time}
Persons: {number_of_persons}
Total: {total_amount} EUR

Thank you for choosing our services!
"""
    
    BOOKING_REMINDER = """
Reminder: You have an upcoming appointment

Service: {service_name}
Date: {booking_date}
Time: {start_time}

We look forward to seeing you!
"""
    
    BOOKING_CANCELLATION = """
Your booking has been cancelled:

Service: {service_name}
Date: {booking_date}
Time: {start_time}

If you have any questions, please contact us.
"""
    
    PAYMENT_CONFIRMATION = """
Payment confirmed!

Amount: {amount} EUR
Service: {service_name}
Date: {booking_date}

Thank you for your payment!
"""


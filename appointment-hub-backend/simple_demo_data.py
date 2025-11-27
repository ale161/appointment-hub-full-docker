#!/usr/bin/env python3
"""
Simple script to create demo users via API calls
"""

import requests
import json

BASE_URL = 'http://localhost:5001'

def create_demo_users():
    # Demo users data
    users = [
        {
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'admin@demo.com',
            'password': 'password123',
            'role': 'admin',
            'phone_number': '+30 123 456 7890'
        },
        {
            'first_name': 'Store',
            'last_name': 'Manager',
            'email': 'manager@demo.com',
            'password': 'password123',
            'role': 'store_manager',
            'phone_number': '+30 123 456 7891'
        },
        {
            'first_name': 'John',
            'last_name': 'Client',
            'email': 'client@demo.com',
            'password': 'password123',
            'role': 'client',
            'phone_number': '+30 123 456 7892'
        }
    ]
    
    print("Creating demo users...")
    for user_data in users:
        try:
            response = requests.post(
                f'{BASE_URL}/auth/register',
                headers={'Content-Type': 'application/json'},
                json=user_data
            )
            
            if response.status_code == 200 or response.status_code == 201:
                print(f"✓ Created user: {user_data['email']}")
            else:
                print(f"✗ Failed to create user {user_data['email']}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Error creating user {user_data['email']}: {e}")
    
    print("\nDemo accounts created:")
    print("Admin: admin@demo.com / password123")
    print("Store Manager: manager@demo.com / password123")
    print("Client: client@demo.com / password123")

if __name__ == '__main__':
    create_demo_users()


#!/usr/bin/env python3
import requests
import json

# Test login with email
print("Testing login with email...")
response_email = requests.post(
    'http://localhost:8000/graphql',
    json={
        "query": 'mutation { login(input: {username: "admin@multipult.dev", password: "AdminPass123!"}) { accessToken tokenType } }'
    }
)
print("Email login response:", response_email.text)
print()

# Test login with username
print("Testing login with username...")
response_username = requests.post(
    'http://localhost:8000/graphql',
    json={
        "query": 'mutation { login(input: {username: "admin", password: "AdminPass123!"}) { accessToken tokenType } }'
    }
)
print("Username login response:", response_username.text)

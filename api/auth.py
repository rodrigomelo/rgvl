# Auth0 JWT Authentication
# RGVL Project

import os
import functools
import requests
from flask import request, jsonify, g
from jwt import PyJWKClient, PyJWKClientError

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'dev-4mhbzq6x4yvyckmt.us.auth0.com')
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE', 'http://localhost:5003')

# Cache JWKS client
_jwks_client = None

def get_jwks_client():
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'
        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client

def get_token_from_header():
    """Extract Bearer token from Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None

def verify_token(token):
    """Verify JWT token with Auth0"""
    try:
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # For Auth0 tokens, we need to verify differently
        # Auth0 tokens are RS256 signed
        import jwt
        from jwt import algorithms
        
        # Decode without verification first to get the header
        unverified = jwt.decode(token, options={"verify_signature": False})
        
        # Get the key from JWKS
        public_key = signing_key.key
        
        # Verify and decode
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=AUTH0_AUDIENCE,
            issuer=f'https://{AUTH0_DOMAIN}/'
        )
        
        return payload
    except PyJWKClientError as e:
        print(f'JWKS error: {e}')
        return None
    except Exception as e:
        print(f'Token verification error: {e}')
        return None

def require_auth(f):
    """Decorator to require authentication on endpoints"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        
        if not token:
            return jsonify({'error': 'Authorization required'}), 401
        
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Store user info in Flask's g object
        g.user = payload
        
        return f(*args, **kwargs)
    return decorated

def optional_auth(f):
    """Decorator for optional authentication - continues even if no token"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        
        if token:
            payload = verify_token(token)
            g.user = payload if payload else None
        else:
            g.user = None
        
        return f(*args, **kwargs)
    return decorated

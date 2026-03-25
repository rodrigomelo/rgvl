# Auth0 Authentication Spec

## Overview

RGVL uses Auth0 for authentication. All API endpoints are protected except `/api/health`, `/api/stats`, and `/api/search`.

## Architecture

```
Browser (SPA)
    │
    ├─ Login → Auth0 Universal Login
    │             ↓
    │         Return with token
    │             ↓
    └─ API Request (+ Bearer token)
              ↓
         Flask API validates via /userinfo
              ↓
         Return data or 401/403
```

## Files

| File | Purpose |
|------|---------|
| `web/auth.js` | Auth helpers (login, logout, callback) |
| `web/callback.html` | OAuth redirect handler |
| `web/index.html` | Login screen + user menu |
| `api/auth.py` | Token verification via Auth0 /userinfo |
| `api/main.py` | @before_request auth check |
| `.env.example` | Environment variables template |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `AUTH0_DOMAIN` | Auth0 tenant domain |
| `AUTH0_CLIENT_ID` | Auth0 application client ID |
| `AUTH0_AUDIENCE` | API identifier (optional) |
| `AUTH_DISABLED` | Set to `true` to bypass auth (dev only) |

## Auth0 Configuration

### Application Settings
- **Application Type:** Single Page App
- **Allowed Callback URLs:** 
  - `http://localhost:5002/callback`
  - `http://127.0.0.1:5002/callback`
  - `http://mac-mini-de-rodrigo:5002/callback`
  - (add production URL when deploying)
- **Allowed Logout URLs:**
  - `http://localhost:5002`
  - (add production URL when deploying)

### API Settings
- **Identifier:** `http://localhost:5003`

## User Management

Access is controlled via **Auth0 native user management**.

### Adding Users
1. Go to Auth0 Dashboard → Users
2. Click "Create User" or "Invite User"
3. User receives email → creates account → accesses portal

### Removing Users
1. Go to Auth0 Dashboard → Users
2. Find user → click "Actions" → "Block" or "Delete"

## Public Endpoints (No Auth Required)

- `GET /api/health` - Health check
- `GET /api/stats` - Public statistics
- `GET /api/search?q=...` - Public search

## User Info

After login, user info is stored in localStorage:
- `access_token` - JWT token
- `user` - JSON with name, email, picture

User menu shows logged-in user's name and logout button.

## Logout

Clicking "Sair" clears localStorage and redirects to home.

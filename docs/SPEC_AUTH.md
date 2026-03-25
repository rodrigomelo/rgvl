# SPEC_AUTH.md — Auth0 Authentication for RGVL Portal

**Author:** Athena (UX/UI Design)  
**Status:** Draft — awaiting Hermes approval → Hefesto implements  
**Date:** 2026-03-24

---

## 1. Overview

Add Auth0-based authentication to the RGVL family research portal. Only authenticated users may access data. Public endpoints (health, stats) remain open.

---

## 2. Visual Design

### 2.1 Design Language

**Inherits from existing portal palette:**

| Token | Hex | Usage |
|---|---|---|
| `--primary` | `#1E3A5F` | Headers, sidebar background, primary text |
| `--primary-light` | `#2C5282` | Secondary actions |
| `--secondary` | `#4A90A4` | Links, info states |
| `--accent` | `#E8B339` | Active nav, highlights, CTAs |
| `--success` | `#2E7D32` | Confirmation |
| `--danger` | `#C62828` | Error, logout |
| `--bg` | `#F5F7FA` | Page background |
| `--card-bg` | `#FFFFFF` | Cards, panels |
| `--text` | `#2D3748` | Body text |
| `--text-muted` | `#718096` | Secondary text |
| `--border` | `#E2E8F0` | Dividers, card borders |

**Typography:** `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` (system stack — no change needed)

**Spacing:** 8px base unit. Cards use 20px padding. Sections have 20px margins.

---

## 3. Pages & Components

### 3.1 Login Page (`web/login.html`)

**Purpose:** Gate the entire portal behind Auth0 authentication.

**Layout:**
- Full-page centered card, no sidebar, no header nav
- Portal logo/name: "🌳 RGVL" centered at top
- Subtitle: "Plataforma de Pesquisa Genealógica — Família Lanna"
- Auth0 login button (primary CTA)
- Footer: "Dados protegidos · Acesso restrito a membros autorizados"

**Visual specs:**
- Background: solid `--bg` (`#F5F7FA`)
- Card: `--card-bg`, border-radius 16px, box-shadow `0 8px 32px rgba(0,0,0,0.12)`, max-width 420px, padding 40px, centered vertically and horizontally
- Auth0 button: full-width, height 48px, background `--primary`, color white, border-radius 8px, font-size 16px, font-weight 600
- Button hover: background `--primary-light`
- Button text: "Entrar com Auth0"
- Below button: small muted text "Ao entrar, você concorda com os termos de uso."
- Error state: red card border + error message below button

**Behavior:**
- On page load: check for existing valid session token (see Session Handling)
  - If valid → redirect to `/` (dashboard)
  - If invalid/missing → show login page
- On button click → trigger Auth0 Universal Login (redirect flow)
- On auth callback → store tokens, redirect to `/`

**Redirect logic:**
```
/login               → always show login (unless authenticated)
/                    → authenticated → show dashboard | unauthenticated → redirect /login
```

---

### 3.2 Authenticated Header (`web/index.html` — modified)

**Add to existing `<header class="header">`:**

```
[existing: 🌳 RGVL title]     [User Menu Button 👤 + name]
```

**User Menu Button (right side of header):**
- Avatar circle: 32px diameter, background `--accent`, color white, font-size 14px, font-weight 700, contains first letter of user name
- Next to avatar: user name (truncate at 20 chars), down-arrow chevron (▼)
- Click → dropdown menu below button

**User Dropdown Menu:**
- Background: `--card-bg`, border 1px solid `--border`, border-radius 10px, box-shadow `0 4px 16px rgba(0,0,0,0.12)`
- Width: 200px
- Items:
  - "👤 Perfil" — disabled/grayed (future feature), font-size 13px, color `--text-muted`
  - Divider line
  - "🚪 Sair" — color `--danger`, font-size 13px
- Click on "Sair" → call `logout()` → redirect to `/login`

---

### 3.3 Protected Routes

All data-fetching sections of `index.html` are behind authentication:

| Route | Section | Protected? |
|---|---|---|
| `/` (index.html) | Full portal | ✅ Yes |
| `/login` | Login page | ❌ No (public) |

**API-level protection (port 5003):**

| Endpoint | Auth Required? |
|---|---|
| `GET /api/health` | ❌ No |
| `GET /api/stats` | ❌ No |
| `GET /` | ❌ No |
| `GET /api/family/*` | ✅ Yes |
| `GET /api/assets/*` | ✅ Yes |
| `GET /api/legal/*` | ✅ Yes |
| `GET /api/research/*` | ✅ Yes |
| `GET /api/sources/*` | ✅ Yes |
| `GET /api/search` | ✅ Yes |

**Behavior on unauthenticated API call:**
```json
HTTP 401
{ "error": "unauthorized", "message": "Token de autenticação inválido ou expirado" }
```

---

### 3.4 Session Handling

**Token Storage — Frontend (`index.html` / `login.html`):**
- Use `httpOnly: true, secure: true, sameSite: 'Lax'` cookies set by the API on login callback
- Access token stored in memory (JavaScript variable) for API calls
- Refresh token stored in `httpOnly` cookie (not accessible to JS)

**Token Storage — Backend (Flask API):**
- On successful Auth0 callback, exchange code for tokens
- Set `access_token` cookie: `httpOnly`, `secure` (in production), `sameSite: 'Lax'`
- Set `refresh_token` cookie: same flags
- Token lifetime: access token 1h, refresh token 7 days

**API calls from frontend:**
- Every `fetch()` to `/api/*` (except health) includes `Authorization: Bearer <access_token>` header
- If API returns 401 → attempt token refresh via `/api/auth/refresh`
  - If refresh succeeds → retry original request
  - If refresh fails → redirect to `/login`

**Session check on portal load:**
- `index.html` `load()` function: immediately call `GET /api/auth/me`
  - Returns 200 + user info → render dashboard
  - Returns 401/403 → redirect to `/login`

---

## 4. User Flow

```
┌─────────────┐
│  Visit /    │
└──────┬──────┘
       ▼
┌──────────────────┐   401    ┌─────────────┐
│ GET /api/auth/me │ ────────→│ Redirect to │
└──────────────────┘          │   /login    │
       │ 200 OK                └─────────────┘
       ▼
┌──────────────────────────────────┐
│  Render Dashboard (index.html)   │
└──────────────────────────────────┘

┌─────────────┐
│  Visit      │
│  /login     │
└──────┬──────┘
       ▼
┌────────────────────────┐
│  Show Login Page      │
│  (check: has session?)│
│  No → show login form  │
└──────────┬─────────────┘
           │ Click "Entrar com Auth0"
           ▼
┌────────────────────────────┐
│  Redirect to Auth0         │
│  Universal Login            │
└──────────┬─────────────────┘
           │ User authenticates
           ▼
┌────────────────────────────┐
│  Auth0 redirects to       │
│  /api/auth/callback?code=X│
└──────────┬─────────────────┘
           │ API exchanges code
           │ for tokens, sets
           │ httpOnly cookies
           ▼
┌────────────────────────────┐
│  Redirect to /             │
│  (dashboard)               │
└────────────────────────────┘

┌──────────────────────────┐
│  Click "Sair" (logout)   │
└──────────┬───────────────┘
           ▼
┌────────────────────────────┐
│  GET /api/auth/logout      │
│  Clear httpOnly cookies    │
│  Clear in-memory token     │
│  Redirect to /login        │
└────────────────────────────┘
```

---

## 5. Technical Implementation

### 5.1 Auth0 Application Setup (Manual — requires Rodrigo)

1. Go to [auth0.com](https://auth0.com) → Dashboard
2. Create Application → "Regular Web Applications" → Flask
3. Note down:
   - **Domain** (e.g., `your-tenant.auth0.com`)
   - **Client ID**
   - **Client Secret**
4. Allowed Callback URLs: `http://localhost:5003/api/auth/callback` (dev), `https://yourdomain.com/api/auth/callback` (prod)
5. Allowed Logout URLs: `http://localhost:5002/` (dev), production URL
6. Allowed Web Origins: `http://localhost:5003` (dev)
7. Advanced → Grant Types: enable "Authorization Code" (already default)

---

### 5.2 Environment Variables (`.env`)

**Create `/Users/rodrigomelo/.openclaw/workspace/projects/rgvl/.env`:**

```bash
# Auth0 Configuration
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your_client_id_here
AUTH0_CLIENT_SECRET=your_client_secret_here
AUTH0_CALLBACK_URL=http://localhost:5003/api/auth/callback
AUTH0_AUDIENCE=https://rgvl-api

# Flask
FLASK_SECRET_KEY=generate_a_long_random_string_here
PORT=5003

# CORS (comma-separated allowed origins)
ALLOWED_ORIGINS=http://localhost:5002,https://yourdomain.com

# Environment
FLASK_ENV=development
```

> ⚠️ **Security:** `AUTH0_CLIENT_SECRET` and `FLASK_SECRET_KEY` must never be committed to git. They must be in `.env` which is in `.gitignore`.

---

### 5.3 API Changes — `api/main.py`

**New imports:**
```python
from api.auth import auth_bp  # new blueprint
```

**Add after CORS setup:**
```python
app.register_blueprint(auth_bp)
```

**Update CORS configuration:**
```python
CORS(app, 
     origins=os.environ.get('ALLOWED_ORIGINS', 'http://localhost:5002').split(','),
     supports_credentials=True,  # required for httpOnly cookies
     expose_cookies=True)
```

**New file: `api/auth.py`** (full blueprint):

```
api/auth.py
├── GET  /api/auth/login         → redirect to Auth0 Universal Login
├── GET  /api/auth/callback      → exchange code for tokens, set cookies, redirect to /
├── GET  /api/auth/logout        → clear cookies, redirect to /login
├── GET  /api/auth/me            → return current user info (requires auth)
├── POST /api/auth/refresh       → refresh access token from refresh_token cookie
└── helper: validate_token()     → verify JWT signature against Auth0 /.well-known/jwks.json
```

**JWT Validation approach:**
- Use `authlib` or `PyJWT` + `requests` to fetch JWKS from `https://{AUTH0_DOMAIN}/.well-known/jwks.json`
- Validate `alg=RS256`, signature, `aud` (audience), `iss` (issuer), `exp` (expiry)
- No Auth0 SDK dependency — keeps it lightweight

**Decorator for protected routes:**
```python
from functools import wraps
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'unauthorized', 'message': 'Token de autenticação inválido ou expirado'}), 401
        payload = validate_token(token)
        if not payload:
            return jsonify({'error': 'unauthorized', 'message': 'Token de autenticação inválido ou expirado'}), 401
        request.user = payload
        return f(*args, **kwargs)
    return decorated
```

**Apply `require_auth` to all existing route blueprints** by wrapping each blueprint's `before_request` or individual routes. Simplest approach: add `require_auth` as a `before_request` function on each data blueprint, excluding `/api/health`.

---

### 5.4 Frontend Changes

#### `web/login.html` (new file)

Full login page as described in Section 3.1. Pure HTML/CSS/JS, no framework.

```html
<!-- Key structure -->
<body>
  <div class="login-container">
    <div class="login-card">
      <h1>🌳 RGVL</h1>
      <p class="login-subtitle">Plataforma de Pesquisa Genealógica — Família Lanna</p>
      <a href="/api/auth/login" class="btn-login">Entrar com Auth0</a>
      <p class="login-footer">Dados protegidos · Acesso restrito a membros autorizados</p>
    </div>
  </div>
</body>
```

#### `web/index.html` (modified)

**1. Add to `<head>` — inline style for login redirect overlay:**
```css
.auth-loading { display:flex; align-items:center; justify-content:center; height:100vh; flex-direction:column; gap:12px; color:var(--text-muted); }
```

**2. Add `<div id="auth-check" class="auth-loading">` as first child of `<body>`** (replaces entire body content during auth check):
```html
<div id="auth-check">
  <div class="spinner"></div>
  <p>Verificando sessão...</p>
</div>
```

**3. Add to `<header>` — user menu section:**
```html
<div id="user-menu" style="display:none;align-items:center;gap:8px;">
  <button id="user-menu-btn" style="background:none;border:none;color:white;display:flex;align-items:center;gap:8px;cursor:pointer;font-size:14px;">
    <span id="user-avatar" style="width:32px;height:32px;border-radius:50%;background:var(--accent);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;"></span>
    <span id="user-name" style="max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"></span>
    <span style="font-size:10px;">▼</span>
  </button>
  <div id="user-dropdown" style="position:absolute;top:50px;right:16px;background:white;border:1px solid var(--border);border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.12);width:200px;display:none;z-index:200;">
    <div style="padding:12px 16px;border-bottom:1px solid var(--border);">
      <div id="dropdown-email" style="font-size:12px;color:var(--text-muted);word-break:break-all;"></div>
    </div>
    <button onclick="logout()" style="width:100%;text-align:left;padding:12px 16px;background:none;border:none;cursor:pointer;color:var(--danger);font-size:13px;">🚪 Sair</button>
  </div>
</div>
```

**4. Add JavaScript constants and session state:**
```javascript
const API_BASE = await findAPI();
const ACCESS_TOKEN_KEY = '__rgvl_token';
let accessToken = sessionStorage.getItem(ACCESS_TOKEN_KEY) || null;

async function checkAuth() {
  const token = sessionStorage.getItem(ACCESS_TOKEN_KEY);
  if (!token) { redirectToLogin(); return false; }
  // Validate token with /api/auth/me
  try {
    const r = await fetch(API_BASE+'/auth/me', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    if (!r.ok) { redirectToLogin(); return false; }
    const user = await r.json();
    showUserMenu(user);
    return true;
  } catch(e) { redirectToLogin(); return false; }
}

function redirectToLogin() {
  window.location.href = '/login';
}

function showUserMenu(user) {
  document.getElementById('auth-check').style.display = 'none';
  const menu = document.getElementById('user-menu');
  menu.style.display = 'flex';
  menu.style.position = 'relative';
  document.getElementById('user-avatar').textContent = (user.name || user.email || '?')[0].toUpperCase();
  document.getElementById('user-name').textContent = user.name || user.email || '';
  document.getElementById('dropdown-email').textContent = user.email || '';
  // Attach dropdown toggle
  document.getElementById('user-menu-btn').addEventListener('click', () => {
    const dd = document.getElementById('user-dropdown');
    dd.style.display = dd.style.display === 'none' ? 'block' : 'none';
  });
}

function logout() {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  accessToken = null;
  fetch(API_BASE+'/auth/logout', { method: 'POST', credentials: 'include' })
    .finally(() => { window.location.href = '/login'; });
}
```

**5. Modify `load()` function:**
```javascript
async function load() {
  const token = sessionStorage.getItem(ACCESS_TOKEN_KEY);
  if (!token) { redirectToLogin(); return; }
  // Attach token to all API calls
  const headers = { 'Authorization': 'Bearer ' + token };
  
  const [tree, bisavos, /* ... rest unchanged ... */] = await Promise.all([
    fetch(api+'/family/person/'+PAI_ID+'/tree', { headers }).then(r=>r.ok?r.json():Promise.reject()).catch(()=>null),
    // ... all other fetch calls get { headers } added
  ]);
  // ... rest unchanged
}
```

**6. Click outside dropdown → close it:**
```javascript
document.addEventListener('click', e => {
  const dd = document.getElementById('user-dropdown');
  const btn = document.getElementById('user-menu-btn');
  if (dd && !btn.contains(e.target) && !dd.contains(e.target)) {
    dd.style.display = 'none';
  }
});
```

---

### 5.5 Rate Limiting

Add `flask-limiter` for login attempt protection:

```bash
# requirements.txt add:
flask-limiter>=3.5.0
```

Limits:
- `/api/auth/login` → 5 requests/minute per IP
- `/api/auth/callback` → 10 requests/minute per IP
- `/api/auth/refresh` → 10 requests/minute per IP
- All other protected endpoints → 100 requests/minute per token (user-level)

---

### 5.6 CORS Configuration

Current: `CORS(app)` — wide open.

New config:
```python
CORS(app,
     origins=os.environ.get('ALLOWED_ORIGINS', 'http://localhost:5002').split(','),
     supports_credentials=True,
     allow_headers=['Authorization', 'Content-Type'],
     expose_headers=['Authorization'])
```

---

## 6. Implementation Order (for Hefesto)

```
Step 1:  Create .env file with all required variables
Step 2:  Add flask-limiter to requirements.txt
Step 3:  Create api/auth.py (auth blueprint, JWT validation, routes)
Step 4:  Update api/main.py (register blueprint, update CORS)
Step 5:  Add require_auth decorator + apply to data blueprints
Step 6:  Create web/login.html (login page)
Step 7:  Modify web/index.html (auth check, user menu, token in headers)
Step 8:  Test: portal redirects unauthenticated → login
Step 9:  Test: login → auth0 → callback → dashboard
Step 10: Test: logout → login
Step 11: Test: API returns 401 for unauthenticated requests
Step 12: Test: /api/health remains accessible without auth
```

---

## 7. Security Checklist (Hades review)

- [ ] `AUTH0_CLIENT_SECRET` in `.env` only — never in code
- [ ] `FLASK_SECRET_KEY` is a strong random value (min 32 chars)
- [ ] Access tokens: RS256 validation (never HS256)
- [ ] `httpOnly` cookies prevent XSS token theft
- [ ] `sameSite: 'Lax'` prevents CSRF on logout
- [ ] `secure: true` cookie flag in production (HTTPS)
- [ ] Token expiry enforced (reject expired JWTs)
- [ ] `aud` (audience) claim validated against `AUTH0_AUDIENCE`
- [ ] `iss` (issuer) claim validated against `https://{AUTH0_DOMAIN}/`
- [ ] JWKS cached in-memory with TTL (don't fetch on every request)
- [ ] CORS origins explicitly whitelisted (no `*` with credentials)
- [ ] Rate limiting on auth endpoints
- [ ] No tokens in URL query strings (they appear in server logs)
- [ ] `.env` in `.gitignore`

---

## 8. File Inventory

| File | Action | Description |
|---|---|---|
| `docs/SPEC_AUTH.md` | **CREATE** | This spec |
| `.env` | **CREATE** | Environment variables |
| `requirements.txt` | **MODIFY** | Add `flask-limiter`, `PyJWT` (or `authlib`) |
| `api/auth.py` | **CREATE** | Auth blueprint: login, callback, logout, me, refresh, JWT validation |
| `api/main.py` | **MODIFY** | Register auth_bp, update CORS config |
| `api/routes/family.py` | **MODIFY** | Apply `require_auth` decorator |
| `api/routes/assets.py` | **MODIFY** | Apply `require_auth` decorator |
| `api/routes/legal.py` | **MODIFY** | Apply `require_auth` decorator |
| `api/routes/research.py` | **MODIFY** | Apply `require_auth` decorator |
| `api/routes/sources.py` | **MODIFY** | Apply `require_auth` decorator |
| `web/login.html` | **CREATE** | Standalone login page |
| `web/index.html` | **MODIFY** | Auth check on load, user menu in header, token in fetch headers |

---

## 9. Open Questions (for Hermes/Rodrigo)

1. **Auth0 account:** Does Rodrigo already have an Auth0 tenant set up, or does he need to create one?
2. **User model:** Should Auth0 users be matched to existing people in the database by email? Or is any Auth0 user allowed (family research portal, closed group)?
3. **Multi-user vs single user:** Is this portal for one person (Rodrigo only) or will there be multiple family members with separate logins?
4. **Production URL:** What domain will the portal run on in production?
5. **Existing users:** Are there existing hardcoded users or is this the first auth system?

## Access Control

Access is controlled via **Auth0 native user management**.

**Adding users:**
1. Go to Auth0 Dashboard → Users
2. Click "Create User" or "Invite User"
3. User receives email → creates account → accesses portal

**Removing users:**
1. Go to Auth0 Dashboard → Users
2. Find user → click "Actions" → "Block" or "Delete"

No configuration needed in the application - Auth0 handles everything.

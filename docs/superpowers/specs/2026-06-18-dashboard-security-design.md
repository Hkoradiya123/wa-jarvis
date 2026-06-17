# Design: Dashboard Security & Utility Modules

## Goals
1. Secure the dashboard with a password.
2. Implement the missing Reminders UI.
3. Implement a Direct Console for testing webhooks.

## Architecture

### Backend Security
- **Middleware**: A FastAPI `BaseHTTPMiddleware` will be added to `app/main.py`.
- **Logic**:
    - Protect paths starting with `/api/` and `/ws/`.
    - Validate `X-Password` header or `password` query parameter against `DASHBOARD_PASSWORD`.
    - Return `401` on failure.

### Frontend Security
- **Auth Guard**: `App.tsx` will manage the dashboard password state.
- **Persistence**: Store password in `localStorage`.
- **Integration**: All API requests will include the `X-Password` header.

### New Modules
- **Reminders**: A grid view fetching from `/api/reminders`.
- **Direct Console**: A text-based interface to trigger the `/webhook` endpoint with arbitrary payloads.

## Implementation Details

### Backend
```python
@app.middleware("http")
async def dashboard_security(request: Request, call_next):
    if request.url.path.startswith("/api/") or request.url.path.startswith("/ws/"):
        password = os.getenv("DASHBOARD_PASSWORD")
        if password:
            req_pass = request.headers.get("X-Password") or request.query_params.get("password")
            if req_pass != password:
                return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)
```

### Frontend
- Update `App.tsx` to handle password entry.
- Create `Reminders.tsx` and `DirectConsole.tsx`.
- Modify `MemoryVault.tsx` and `CommandCenter.tsx` to use the password header.

## Success Criteria
- Dashboard routes require a password if `DASHBOARD_PASSWORD` is set.
- Reminders are viewable in the UI.
- Webhook can be manually triggered from the UI.

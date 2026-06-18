# Multi-User Management System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Transition from a single-password system to a multi-user system with a dedicated management interface.

**Architecture:** 
- New `users` collection in MongoDB storing `{ username, password_hash, role }`.
- Backend middleware updated to verify credentials against the database.
- New `UserManagement.tsx` page for Admin users.
- Updated `LoginPage.tsx` to support Username/Password authentication.

**Tech Stack:** FastAPI, MongoDB, React, Tailwind, Lucide.

## Global Constraints
- Initial Admin Password: `Hkoradiya.jarvis`
- Role-based access: Only `admin` users can see the User Management page.

---

### Task 1: Database & Initial Admin Setup

**Files:**
- Modify: `app/database/mongodb.py`
- Modify: `.env`

- [x] **Step 1: Add user management functions to app/database/mongodb.py**
Implement `get_user(username)`, `create_user(username, password, role)`, and `list_users()`.
*Note: Use passlib or similar for password hashing.*

- [x] **Step 2: Set initial Admin password**
Update `.env` or implement a one-time setup script that creates the `admin` user with `Hkoradiya.jarvis`.

- [x] **Step 3: Commit**
```bash
git add app/database/mongodb.py
git commit -m "feat: add user management database layer"
```

---

### Task 2: Multi-User Security Middleware

**Files:**
- Modify: `app/main.py`

- [x] **Step 1: Update dashboard_security middleware**
Change from checking `X-Password` vs `ENV` to checking `X-Username` and `X-Password` (or an Auth token) against the MongoDB `users` collection.

- [x] **Step 2: Add User Management APIs**
`GET /api/users` (Admin only)
`POST /api/users` (Admin only)
`DELETE /api/users/{username}` (Admin only)

- [x] **Step 3: Commit**
```bash
git add app/main.py
git commit -m "feat: implement multi-user backend authentication"
```

---

### Task 3: Login Page Upgrade

**Files:**
- Modify: `frontend/src/pages/LoginPage.tsx`
- Modify: `frontend/src/App.tsx`

- [x] **Step 1: Update LoginPage.tsx UI**
Add a `Username` field to the terminal-themed login.

- [x] **Step 2: Update App.tsx session handling**
Store both `username` and `password` in `localStorage` and pass them to all API requests.

- [x] **Step 3: Commit**
```bash
git add frontend/src/
git commit -m "feat: upgrade login flow for multi-user support"
```

---

### Task 4: User Management Interface

**Files:**
- Create: `frontend/src/pages/UserManagement.tsx`
- Modify: `frontend/src/components/Sidebar.tsx`
- Modify: `frontend/src/App.tsx`

- [x] **Step 1: Create UserManagement.tsx**
A high-density table to list users, show roles, and a form to "Provision New User".

- [x] **Step 2: Update Sidebar.tsx**
Add the `USER_MANAGEMENT` icon/link.

- [x] **Step 3: Commit**
```bash
git add frontend/src/
git commit -m "feat: implement user management dashboard page"
```

---

### Task 5: Cleanup & Verification

- [x] **Step 1: Final build and test**
Verify that the `admin` / `Hkoradiya.jarvis` login works and can create new users.

- [x] **Step 2: Track plan in Git**
```bash
git add docs/superpowers/plans/2026-06-18-user-management.md
git commit -m "docs: plan for multi-user management system"
```

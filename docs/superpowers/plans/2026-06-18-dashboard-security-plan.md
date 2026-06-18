# Dashboard Security & Utility Modules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Secure the dashboard with a password and implement missing Reminders and Direct Console modules.

**Architecture:** 
- Backend security via FastAPI middleware checking paths starting with `/api/` or `/ws/`.
- Frontend password management in `App.tsx`, persisted in `localStorage`.
- All API calls updated to send `X-Password` header.

**Tech Stack:** FastAPI, React, TypeScript, Tailwind CSS, Lucide icons.

## Global Constraints
- Style: Utility / Dev-Tool (Monospace, dark mode, high density).
- Auth: Environment variable `DASHBOARD_PASSWORD`.

---

### Task 1: Backend Security Middleware

**Files:**
- Modify: `app/main.py`

**Interfaces:**
- Consumes: `os.getenv("DASHBOARD_PASSWORD")`
- Produces: Middleware that returns `401` for unauthorized `/api/` or `/ws/` requests.

- [x] **Step 1: Add JSONResponse import and middleware to app/main.py**

```python
from fastapi.responses import JSONResponse
# ... existing imports

@app.middleware("http")
async def dashboard_security(request: Request, call_next):
    # Skip security for static files and webhook
    path = request.url.path
    if path.startswith("/api/") or path.startswith("/ws/"):
        password = os.getenv("DASHBOARD_PASSWORD")
        if password:
            req_pass = request.headers.get("X-Password") or request.query_params.get("password")
            if req_pass != password:
                return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)
```

- [x] **Step 2: Test security with a temporary environment variable**

Run: `DASHBOARD_PASSWORD=test_pass python -m app.main`
Test with curl: `curl -I http://localhost:7860/api/memories`
Expected: `HTTP/1.1 401 Unauthorized`

- [x] **Step 3: Test security with correct password**

Run: `DASHBOARD_PASSWORD=test_pass python -m app.main`
Test with curl: `curl -I -H "X-Password: test_pass" http://localhost:7860/api/memories`
Expected: `HTTP/1.1 200 OK`

- [x] **Step 4: Commit**

```bash
git add app/main.py
git commit -m "feat: add dashboard security middleware"
```

---

### Task 2: Frontend Password Management

**Files:**
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Consumes: `localStorage`
- Produces: `password` state passed to components.

- [x] **Step 1: Implement password prompt and state in App.tsx**

```tsx
import React, { useState, useEffect } from 'react';
// ... existing imports

function App() {
  const [activeTab, setActiveTab] = useState('logs');
  const [password, setPassword] = useState<string | null>(localStorage.getItem('dashboard_password'));
  const [tempPass, setTempPass] = useState('');

  if (!password) {
    return (
      <div className="min-h-screen bg-[#0d1117] text-gray-300 flex items-center justify-center font-mono">
        <div className="border border-gray-800 p-8 rounded bg-[#161b22] w-96">
          <h1 className="text-blue-500 font-bold mb-4 tracking-widest">JARVIS_OS_LOGIN</h1>
          <input
            type="password"
            placeholder="ENTER_PASSWORD..."
            value={tempPass}
            onChange={(e) => setTempPass(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                localStorage.setItem('dashboard_password', tempPass);
                setPassword(tempPass);
              }
            }}
            className="w-full bg-black border border-gray-800 rounded px-3 py-2 text-xs focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={() => {
              localStorage.setItem('dashboard_password', tempPass);
              setPassword(tempPass);
            }}
            className="mt-4 w-full bg-blue-900/20 text-blue-500 border border-blue-900/50 py-2 text-[10px] hover:bg-blue-900/30"
          >
            ACCESS_SYSTEM
          </button>
        </div>
      </div>
    );
  }

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      <header className="mb-6 flex justify-between items-center">
        <h2 className="text-sm font-bold text-gray-500 uppercase tracking-tighter">
          Root / {activeTab}
        </h2>
        <button 
          onClick={() => { localStorage.removeItem('dashboard_password'); setPassword(null); }}
          className="text-[10px] text-gray-600 hover:text-red-500"
        >
          LOGOUT
        </button>
      </header>
      <div className="border border-gray-800 rounded bg-[#161b22] p-4 min-h-[400px]">
        {activeTab === 'logs' && <CommandCenter password={password} />}
        {activeTab === 'memory' && <MemoryVault password={password} />}
        {activeTab === 'reminders' && <Reminders password={password} />}
        {activeTab === 'console' && <DirectConsole password={password} />}
      </div>
    </Layout>
  );
}
```

- [x] **Step 2: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat: add frontend password guard"
```

---

### Task 3: Update Existing Pages for Security

**Files:**
- Modify: `frontend/src/pages/CommandCenter.tsx`
- Modify: `frontend/src/pages/MemoryVault.tsx`

- [x] **Step 1: Update MemoryVault.tsx to use password prop**

```tsx
export const MemoryVault = ({ password }: { password: string }) => {
  // ...
  const fetchMemories = async () => {
    const res = await fetch('/api/memories', {
      headers: { 'X-Password': password }
    });
    // ...
  };

  const deleteMemory = async (id: string) => {
    if (!confirm('Are you sure?')) return;
    await fetch(`/api/memories/${id}`, { 
      method: 'DELETE',
      headers: { 'X-Password': password }
    });
    fetchMemories();
  };
  // ...
}
```

- [x] **Step 2: Update CommandCenter.tsx (WebSockets)**

```tsx
// Find where WebSocket is initialized
const ws = new WebSocket(`ws://${window.location.host}/ws/logs?password=${password}`);
```

- [x] **Step 3: Commit**

```bash
git add frontend/src/pages/CommandCenter.tsx frontend/src/pages/MemoryVault.tsx
git commit -m "feat: integrate password header into existing pages"
```

---

### Task 4: Implement Reminders Page

**Files:**
- Create: `frontend/src/pages/Reminders.tsx`

- [x] **Step 1: Write Reminders.tsx**

```tsx
import React, { useEffect, useState } from 'react';
import { Clock, CheckCircle2 } from 'lucide-react';

export const Reminders = ({ password }: { password: string }) => {
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchReminders = async () => {
    try {
      const res = await fetch('/api/reminders', {
        headers: { 'X-Password': password }
      });
      const data = await res.json();
      setReminders(data);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { fetchReminders(); }, []);

  return (
    <div className="space-y-4 font-mono">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xs font-bold text-blue-500">ACTIVE_REMINDERS</h3>
        <button onClick={fetchReminders} className="text-[10px] text-blue-500 hover:underline">REFRESH_DATA</button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left border-collapse">
          <thead>
            <tr className="border-b border-gray-800 text-gray-500 uppercase text-[10px]">
              <th className="py-2 px-4">Task</th>
              <th className="py-2 px-4">Due_Date</th>
              <th className="py-2 px-4">Status</th>
            </tr>
          </thead>
          <tbody>
            {reminders.map((r: any) => (
              <tr key={r._id} className="border-b border-gray-900 hover:bg-gray-800/30 transition-colors">
                <td className="py-3 px-4 text-blue-400">{r.task}</td>
                <td className="py-3 px-4 text-gray-400">{new Date(r.due_date).toLocaleString()}</td>
                <td className="py-3 px-4">
                  <span className="px-2 py-0.5 rounded-full bg-blue-900/20 text-blue-500 border border-blue-900/50 text-[10px]">
                    PENDING
                  </span>
                </td>
              </tr>
            ))}
            {reminders.length === 0 && !loading && (
              <tr>
                <td colSpan={3} className="py-8 text-center text-gray-600">NO_ACTIVE_REMINDERS_FOUND</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
```

- [x] **Step 2: Commit**

```bash
git add frontend/src/pages/Reminders.tsx
git commit -m "feat: implement Reminders UI"
```

---

### Task 5: Implement Direct Console Page

**Files:**
- Create: `frontend/src/pages/DirectConsole.tsx`

- [x] **Step 1: Write DirectConsole.tsx**

```tsx
import React, { useState } from 'react';
import { Send, Terminal } from 'lucide-react';

export const DirectConsole = ({ password }: { password: string }) => {
  const [payload, setPayload] = useState(JSON.stringify({
    event: "message",
    data: {
      from: "user_test",
      body: "//jarvis help",
      fromMe: false
    }
  }, null, 2));
  const [status, setStatus] = useState<string | null>(null);

  const sendPayload = async () => {
    setStatus("SENDING...");
    try {
      const res = await fetch('/webhook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload
      });
      const data = await res.json();
      setStatus(`SUCCESS: ${JSON.stringify(data)}`);
    } catch (e: any) {
      setStatus(`ERROR: ${e.message}`);
    }
  };

  return (
    <div className="space-y-4 font-mono">
      <div className="flex items-center space-x-2 text-blue-500 mb-4">
        <Terminal size={14} />
        <h3 className="text-xs font-bold uppercase tracking-tighter">Webhook_Simulator</h3>
      </div>

      <div className="space-y-2">
        <label className="text-[10px] text-gray-500">JSON_PAYLOAD</label>
        <textarea
          value={payload}
          onChange={(e) => setPayload(e.target.value)}
          rows={12}
          className="w-full bg-black border border-gray-800 rounded p-4 text-xs text-green-500 focus:outline-none focus:border-blue-500 font-mono leading-relaxed"
        />
      </div>

      <div className="flex justify-between items-center">
        <div className="text-[10px] text-gray-600 truncate max-w-[70%]">
          {status && `> ${status}`}
        </div>
        <button
          onClick={sendPayload}
          className="flex items-center space-x-2 bg-blue-900/20 text-blue-500 border border-blue-900/50 px-4 py-2 text-[10px] hover:bg-blue-900/30 transition-all"
        >
          <Send size={12} />
          <span>EXECUTE_PAYLOAD</span>
        </button>
      </div>
    </div>
  );
};
```

- [x] **Step 2: Commit**

```bash
git add frontend/src/pages/DirectConsole.tsx
git commit -m "feat: implement Direct Console UI"
```

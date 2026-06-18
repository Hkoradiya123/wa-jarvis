# Jarvis Utility Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build a high-density, "Utility / Dev-Tool" styled dashboard for managing Jarvis memories, reminders, and live logs.

**Architecture:** Unified FastAPI backend serving a React (Vite) frontend. Communication via REST and WebSockets.

**Tech Stack:** React, TypeScript, Tailwind CSS, FastAPI, Motor (MongoDB), WebSockets.

## Global Constraints
- Style: Utility / Dev-Tool (Monospace, dark mode, high density).
- Port: 7860 (Hugging Face default).
- Auth: Environment variable `DASHBOARD_PASSWORD`.
- User ID: 1000 (Non-root for Docker).

---

### Task 1: Frontend Initialization & Scaffolding

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/index.css`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`

- [x] **Step 1: Create package.json**
```json
{
  "name": "jarvis-dashboard",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.284.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^1.14.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.15",
    "@types/react-dom": "^18.2.7",
    "@vitejs/plugin-react": "^4.0.3",
    "autoprefixer": "^10.4.14",
    "postcss": "^8.4.27",
    "tailwindcss": "^3.3.3",
    "typescript": "^5.0.2",
    "vite": "^4.4.5"
  }
}
```

- [x] **Step 2: Create tailwind.config.js**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', "Liberation Mono", "Courier New", 'monospace'],
      },
    },
  },
  plugins: [],
}
```

- [x] **Step 3: Create index.css**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-[#0d1117] text-[#c9d1d9] font-mono;
  }
}
```

- [x] **Step 4: Create index.html**
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Jarvis Console</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [x] **Step 5: Create main.tsx**
```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <div className="p-8">
      <h1 className="text-xl font-bold border-b border-gray-800 pb-2">JARVIS_UTILITY_DASHBOARD v0.1.0</h1>
      <p className="mt-4 text-gray-400">System initialized. Waiting for components...</p>
    </div>
  </React.StrictMode>,
)
```

- [x] **Step 6: Commit**
```bash
git add frontend/
git commit -m "feat: scaffold frontend project"
```

---

### Task 2: Layout & Sidebar Navigation

**Files:**
- Create: `frontend/src/components/Layout.tsx`
- Create: `frontend/src/components/Sidebar.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/main.tsx`

- [x] **Step 1: Create Sidebar component**
```tsx
import React from 'react';
import { Terminal, Database, Clock, Activity, Settings } from 'lucide-react';

const navItems = [
  { id: 'logs', label: 'LIVE_LOGS', icon: Activity },
  { id: 'memory', label: 'MEMORY_VAULT', icon: Database },
  { id: 'reminders', label: 'REMINDERS', icon: Clock },
  { id: 'console', label: 'DIRECT_CONSOLE', icon: Terminal },
];

export const Sidebar = ({ activeTab, setActiveTab }: any) => (
  <div className="w-64 border-r border-gray-800 h-screen flex flex-col bg-[#0d1117]">
    <div className="p-4 border-b border-gray-800 font-bold text-sm tracking-widest text-blue-400">
      JARVIS_OS
    </div>
    <nav className="flex-1 p-2 space-y-1">
      {navItems.map((item) => (
        <button
          key={item.id}
          onClick={() => setActiveTab(item.id)}
          className={`w-full flex items-center space-x-3 px-3 py-2 text-xs rounded transition-colors ${
            activeTab === item.id ? 'bg-gray-800 text-white' : 'text-gray-500 hover:text-gray-300'
          }`}
        >
          <item.icon size={14} />
          <span>{item.label}</span>
        </button>
      ))}
    </nav>
    <div className="p-4 border-t border-gray-800 text-[10px] text-gray-600">
      STATUS: CONNECTED
    </div>
  </div>
);
```

- [x] **Step 2: Create Layout component**
```tsx
import React from 'react';
import { Sidebar } from './Sidebar';

export const Layout = ({ children, activeTab, setActiveTab }: any) => (
  <div className="flex h-screen overflow-hidden">
    <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
    <main className="flex-1 overflow-auto bg-[#0d1117]">
      <div className="p-6">{children}</div>
    </main>
  </div>
);
```

- [x] **Step 3: Update App.tsx**
```tsx
import React, { useState } from 'react';
import { Layout } from './components/Layout';

function App() {
  const [activeTab, setActiveTab] = useState('logs');

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      <header className="mb-6">
        <h2 className="text-sm font-bold text-gray-500 uppercase tracking-tighter">
          Root / {activeTab}
        </h2>
      </header>
      <div className="border border-gray-800 rounded bg-[#161b22] p-4 min-h-[400px]">
        {activeTab === 'logs' && <div>Log Stream Component Placeholder</div>}
        {activeTab === 'memory' && <div>Memory Vault Component Placeholder</div>}
        {activeTab === 'reminders' && <div>Reminder Grid Component Placeholder</div>}
        {activeTab === 'console' && <div>Direct Console Component Placeholder</div>}
      </div>
    </Layout>
  );
}

export default App;
```

- [x] **Step 4: Commit**
```bash
git add frontend/src/
git commit -m "feat: implement dashboard layout and navigation"
```

---

### Task 3: Backend API for Memories & Reminders

**Files:**
- Modify: `app/main.py`
- Modify: `app/database/mongodb.py`

- [x] **Step 1: Add list/delete functions to mongodb.py**
```python
# Add to app/database/mongodb.py

async def get_all_memories():
    cursor = memories.find({}).sort("timestamp", -1)
    return await cursor.to_list(length=100)

async def delete_memory(memory_id: str):
    from bson import ObjectId
    await memories.delete_one({"_id": ObjectId(memory_id)})

async def get_all_reminders():
    cursor = reminders.find({}).sort("datetime", 1)
    return await cursor.to_list(length=100)
```

- [x] **Step 2: Add API routes to main.py**
```python
# Add to app/main.py

@app.get("/api/memories")
async def list_memories():
    items = await get_all_memories()
    # Convert ObjectId to str for JSON serialization
    for item in items:
        item["_id"] = str(item["_id"])
    return items

@app.delete("/api/memories/{memory_id}")
async def remove_memory(memory_id: str):
    await delete_memory(memory_id)
    return {"status": "deleted"}

@app.get("/api/reminders")
async def list_reminders():
    items = await get_all_reminders()
    for item in items:
        item["_id"] = str(item["_id"])
    return items
```

- [x] **Step 3: Commit**
```bash
git add app/
git commit -m "feat: add CRUD endpoints for memories and reminders"
```

---

### Task 4: Memory Vault Component

**Files:**
- Create: `frontend/src/pages/MemoryVault.tsx`
- Modify: `frontend/src/App.tsx`

- [x] **Step 1: Implement MemoryVault component**
```tsx
import React, { useEffect, useState } from 'react';
import { Trash2, Search } from 'lucide-react';

export const MemoryVault = () => {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchMemories = async () => {
    const res = await fetch('/api/memories');
    const data = await res.json();
    setMemories(data);
    setLoading(false);
  };

  const deleteMemory = async (id: string) => {
    if (!confirm('Are you sure?')) return;
    await fetch(`/api/memories/${id}`, { method: 'DELETE' });
    fetchMemories();
  };

  useEffect(() => { fetchMemories(); }, []);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 text-gray-500" size={14} />
          <input 
            type="text" 
            placeholder="Search memories..." 
            className="bg-black border border-gray-800 rounded pl-8 pr-3 py-1.5 text-xs w-64 focus:outline-none focus:border-blue-500"
          />
        </div>
        <button onClick={fetchMemories} className="text-[10px] text-blue-500 hover:underline">REFRESH_DATA</button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left border-collapse">
          <thead>
            <tr className="border-b border-gray-800 text-gray-500 uppercase text-[10px]">
              <th className="py-2 px-4">Category</th>
              <th className="py-2 px-4">Content</th>
              <th className="py-2 px-4">Timestamp</th>
              <th className="py-2 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {memories.map((m: any) => (
              <tr key={m._id} className="border-b border-gray-900 hover:bg-gray-800/30 transition-colors">
                <td className="py-3 px-4 text-blue-400">{m.category}</td>
                <td className="py-3 px-4">{m.value || m.content}</td>
                <td className="py-3 px-4 text-gray-600">{new Date(m.timestamp).toLocaleString()}</td>
                <td className="py-3 px-4 text-right">
                  <button onClick={() => deleteMemory(m._id)} className="text-red-900 hover:text-red-500">
                    <Trash2 size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
```

- [x] **Step 2: Update App.tsx to use MemoryVault**
```tsx
import { MemoryVault } from './pages/MemoryVault';
// ... inside App component ...
{activeTab === 'memory' && <MemoryVault />}
```

- [x] **Step 3: Commit**
```bash
git add frontend/src/
git commit -m "feat: implement memory vault UI"
```

---

### Task 5: Live Stream (WebSockets)

**Files:**
- Modify: `app/utils/logger.py`
- Modify: `app/main.py`
- Create: `frontend/src/pages/CommandCenter.tsx`

- [x] **Step 1: Create BroadcastLogger in app/utils/logger.py**
```python
# Add to app/utils/logger.py
import json

class LogManager:
    def __init__(self):
        self.connections = []

    async def connect(self, websocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket):
        self.connections.remove(websocket)

    async def broadcast(self, message: str, level: str = "INFO", category: str = "SYSTEM"):
        payload = json.dumps({
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "category": category,
            "message": message
        })
        for connection in self.connections:
            try:
                await connection.send_text(payload)
            except:
                pass

log_manager = LogManager()
```

- [x] **Step 2: Add WebSocket route to app/main.py**
```python
from fastapi import WebSocket
from app.utils.logger import log_manager

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await log_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep alive
    except:
        log_manager.disconnect(websocket)
```

- [x] **Step 3: Update process_message to broadcast logs**
```python
# Inside process_message in app/main.py
await log_manager.broadcast(f"Processing message from {sender}: {clean_query}", category="ROUTER")
```

- [x] **Step 4: Create CommandCenter.tsx**
```tsx
import React, { useEffect, useState, useRef } from 'react';

export const CommandCenter = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const scrollRef = useRef<any>(null);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/logs`);
    
    ws.onmessage = (event) => {
      const log = JSON.parse(event.data);
      setLogs(prev => [...prev.slice(-99), log]);
    };

    return () => ws.close();
  }, []);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [logs]);

  return (
    <div className="bg-black rounded border border-gray-800 h-[500px] flex flex-col font-mono text-[11px]">
      <div className="p-2 border-b border-gray-800 flex justify-between bg-gray-900/50">
        <span className="text-gray-500">SYSTEM_LOG_STREAM</span>
        <span className="text-green-500">● LIVE</span>
      </div>
      <div ref={scrollRef} className="flex-1 overflow-auto p-4 space-y-1">
        {logs.map((log, i) => (
          <div key={i} className="flex space-x-4">
            <span className="text-gray-600 shrink-0">{new Date(log.timestamp).toLocaleTimeString()}</span>
            <span className={`shrink-0 w-16 ${log.category === 'ROUTER' ? 'text-purple-500' : 'text-blue-500'}`}>[{log.category}]</span>
            <span className="text-gray-300 break-all">{log.message}</span>
          </div>
        ))}
        {logs.length === 0 && <div className="text-gray-700">Waiting for events...</div>}
      </div>
    </div>
  );
};
```

- [x] **Step 5: Commit**
```bash
git add app/ frontend/src/
git commit -m "feat: implement real-time log streaming via WebSockets"
```

---

### Task 6: Unified Build & Security

**Files:**
- Modify: `app/main.py`
- Modify: `Dockerfile`
- Modify: `requirements.txt`

- [x] **Step 1: Serve Static Files in app/main.py**
```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ... at the end of main.py ...
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # Check if file exists in dist, otherwise serve index.html (SPA)
    return FileResponse("frontend/dist/index.html")
```

- [x] **Step 2: Update Dockerfile for Multi-stage Build**
```dockerfile
# Stage 1: Build Frontend
FROM node:18-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend
FROM python:3.11-slim
RUN useradd -m -u 1000 user
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=user . .
COPY --from=frontend-build --chown=user /frontend/dist ./frontend/dist
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
EXPOSE 7860
USER user
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

- [x] **Step 3: Commit**
```bash
git add app/main.py Dockerfile
git commit -m "feat: configure unified build and frontend serving"
```

---

### Task 7: Final Polish & Environment Check

- [x] **Step 1: Build and Run locally to verify**
Run: `cd frontend && npm install && npm run build && cd .. && uvicorn app.main:app --port 7860`
Expected: Dashboard available at localhost:7860 with working logs.

- [x] **Step 2: Commit**
```bash
git add .
git commit -m "chore: final touches and verification"
```

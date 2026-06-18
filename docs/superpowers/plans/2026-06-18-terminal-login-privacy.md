# Terminal Login & Privacy Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Implement a professional terminal-themed login page and secure system logs to prevent data leakage in public environments.

**Architecture:** 
- New `LoginPage.tsx` for immersive authentication.
- Restrict sensitive console logging in `logger.py` while keeping WebSocket logs full.
- Update `App.tsx` for the new login flow.

**Tech Stack:** React, Tailwind CSS, Lucide icons, FastAPI.

## Global Constraints
- Style: Terminal / Cyberpunk / Monospace (JetBrains Mono).
- Visibility: All chat data MUST be restricted from stdout/stderr.

---

### Task 1: Immersive Terminal Login Page

**Files:**
- Create: `frontend/src/pages/LoginPage.tsx`

- [x] **Step 1: Implement LoginPage.tsx**

```tsx
import React, { useState, useEffect } from 'react';
import { Shield, Terminal, Lock, ChevronRight, Activity, Database, Cpu } from 'lucide-react';

export const LoginPage = ({ onLogin }: { onLogin: (pass: string) => void }) => {
  const [tempPass, setTempPass] = useState('');
  const [bootSequence, setBootSequence] = useState<string[]>([]);
  const [isReady, setIsReady] = useState(false);

  const lines = [
    "> INITIALIZING JARVIS_OS v2.0.4...",
    "> CONNECTING TO NEURAL_NET_GATEWAY... [OK]",
    "> SYNCING WITH MONGODB_ATLAS... [OK]",
    "> LOADING CORE_DIRECTIVES... [OK]",
    "> ENCRYPTING_SESSION_KEYS... [OK]",
    "> ACCESS_RESTRICTED: SYSTEM_IS_LOCKED."
  ];

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      if (i < lines.length) {
        setBootSequence((prev) => [...prev, lines[i]]);
        i++;
      } else {
        clearInterval(interval);
        setIsReady(true);
      }
    }, 400);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (tempPass) onLogin(tempPass);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-blue-500 font-mono flex items-center justify-center p-4 relative overflow-hidden">
      {/* Scanline Effect */}
      <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%] z-50"></div>
      
      <div className="w-full max-w-md bg-[#0d1117] border border-blue-900/30 p-8 rounded shadow-[0_0_50px_rgba(30,58,138,0.2)]">
        <div className="flex items-center space-x-3 mb-8 border-b border-blue-900/30 pb-4">
          <div className="p-2 bg-blue-900/20 rounded border border-blue-500/50">
            <Shield size={24} className="text-blue-400 animate-pulse" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-widest text-blue-400">JARVIS_OS</h1>
            <p className="text-[10px] text-blue-900 uppercase font-bold">Secure Access Terminal</p>
          </div>
        </div>

        <div className="space-y-2 mb-8 h-40 overflow-hidden text-[11px] leading-relaxed opacity-80">
          {bootSequence.map((line, idx) => (
            <div key={idx} className="flex items-center space-x-2">
              <ChevronRight size={10} className="text-blue-900" />
              <span>{line}</span>
            </div>
          ))}
          {!isReady && <div className="animate-pulse">_</div>}
        </div>

        {isReady && (
          <form onSubmit={handleSubmit} className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-1000">
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock size={14} className="text-blue-900 group-focus-within:text-blue-500 transition-colors" />
              </div>
              <input
                type="password"
                placeholder="ENTER_AUTHENTICATION_TOKEN..."
                value={tempPass}
                onChange={(e) => setTempPass(e.target.value)}
                autoFocus
                className="w-full bg-black/50 border border-blue-900/30 rounded pl-10 pr-4 py-3 text-sm focus:outline-none focus:border-blue-500/50 text-blue-100 placeholder:text-blue-900/50 transition-all"
              />
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 border border-blue-600/30 py-3 text-xs font-bold uppercase tracking-[0.2em] transition-all flex items-center justify-center space-x-2 group"
            >
              <Terminal size={14} className="group-hover:translate-x-1 transition-transform" />
              <span>Initiate_Handshake</span>
            </button>
          </form>
        )}

        <div className="mt-8 flex justify-between items-center text-[10px] text-blue-900/40 uppercase">
          <div className="flex items-center space-x-1">
            <Activity size={10} />
            <span>Encrypted_TLS_1.3</span>
          </div>
          <div className="flex items-center space-x-1">
            <Database size={10} />
            <span>Node_v20.x</span>
          </div>
        </div>
      </div>
    </div>
  );
};
```

- [x] **Step 2: Commit**

```bash
git add frontend/src/pages/LoginPage.tsx
git commit -m "feat: implement immersive terminal login page"
```

---

### Task 2: Integrate New Login Flow

**Files:**
- Modify: `frontend/src/App.tsx`

- [x] **Step 1: Update App.tsx to use LoginPage**

```tsx
import { LoginPage } from './pages/LoginPage';
// ... other imports

function App() {
  const [activeTab, setActiveTab] = useState('logs');
  const [password, setPassword] = useState<string | null>(localStorage.getItem('dashboard_password'));

  const handleLogin = (pass: string) => {
    localStorage.setItem('dashboard_password', pass);
    setPassword(pass);
  };

  if (!password) {
    return <LoginPage onLogin={handleLogin} />;
  }

  // ... rest of the App return
}
```

- [x] **Step 2: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat: integrate terminal login into main app flow"
```

---

### Task 3: Backend Privacy Guard (Silencing Logs)

**Files:**
- Modify: `app/utils/logger.py`
- Modify: `app/main.py`

**Goal:** Ensure that `print()` or standard `logger` calls in the cloud don't leak user chat data.

- [x] **Step 1: Update LogManager in app/utils/logger.py**

```python
# Add a way to broadcast without printing to terminal
async def broadcast(self, message: dict, console: bool = False):
    msg_str = json.dumps(message)
    
    # Only print to real terminal if requested (or for errors)
    if console or message.get("type") == "error":
        print(f"[{message.get('type', 'INFO')}] {message.get('content', '')}")

    # Always send to active dashboard users
    disconnected = []
    # ... rest of the loop ...
```

- [x] **Step 2: Update process_message in app/main.py**

Remove any `logger.info()` or `print()` calls that output the message body or AI thoughts. Keep only the `broadcast` calls.

Example:
```python
# Change from:
logger.info(f"User replied: {clean_query}") 
# To:
# (Nothing, just let the broadcast handle it for the dashboard)
```

- [x] **Step 3: Commit**

```bash
git add app/
git commit -m "fix: implement privacy guard to silence sensitive console logs"
```

---

### Task 4: Rebuild & Deploy

- [x] **Step 1: Rebuild frontend**
Run: `cd frontend && npm run build`

- [x] **Step 2: Final push**
Run: `git add . && git commit -m "chore: final polish and build for terminal login" && git push origin main && git push hf main:main`

# Developer & Debugging Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a suite of tools for real-time AI reasoning transparency, live prompt management, and system health monitoring.

**Architecture:** 
- Force structured LLM output (thought/answer) via system prompts.
- Move prompt storage from static files to a MongoDB collection (`prompts`).
- Add system health APIs to monitor infrastructure (DB, API Keys, Gateway).
- Update frontend with specialized pages for Prompts, System Status, and enhanced Log streaming.

**Tech Stack:** FastAPI, MongoDB, React, Tailwind, Lucide.

## Global Constraints
- Style: Utility / Dev-Tool (Monospace, dark mode, high density).
- Auth: Must respect `DASHBOARD_PASSWORD` (via `X-Password` header).
- Reliability: Prompts must have a hardcoded fallback if MongoDB is empty.

---

### Task 1: Prompt Collection & Dynamic Loading

**Files:**
- Modify: `app/database/mongodb.py`
- Modify: `app/agents/base.py`
- Modify: `app/agents/ai_agent.py`
- Modify: `app/agents/memory_agent.py`
- Modify: `app/agents/reminder_agent.py`
- Modify: `app/agents/planner_agent.py`
- Modify: `app/agents/summarizer_agent.py`
- Modify: `app/agents/router_agent.py`

**Interfaces:**
- Produces: `get_prompt(agent_name)` which fetches from MongoDB or returns the local hardcoded fallback.

- [ ] **Step 1: Add prompt fetching to app/database/mongodb.py**

```python
# Add to app/database/mongodb.py
prompts = db.prompts

async def get_db_prompt(name: str):
    doc = await prompts.find_one({"name": name})
    return doc.get("content") if doc else None

async def update_db_prompt(name: str, content: str):
    await prompts.update_one(
        {"name": name},
        {"$set": {"content": content, "updated_at": datetime.now()}},
        upsert=True
    )
```

- [ ] **Step 2: Update agents to use the dynamic fetcher**

Example for `app/agents/ai_agent.py`:
```python
from app.database.mongodb import get_db_prompt

AI_AGENT_PROMPT = """... existing ..."""

async def get_ai_prompt():
    db_prompt = await get_db_prompt("AI_AGENT")
    return db_prompt if db_prompt else AI_AGENT_PROMPT
```

Repeat for all agent files.

- [ ] **Step 3: Update GLOBAL_RULES for Reasoning**

Modify `app/agents/base.py`:
```python
GLOBAL_RULES = """
... existing ...
15. STRUCTURE: Your internal response MUST be formatted as:
<thought>
Write your internal reasoning here (how you are solving the task, what memory you are using, etc.)
</thought>
<answer>
Write your actual WhatsApp message here.
</answer>
"""
```

- [ ] **Step 4: Commit**

```bash
git add app/
git commit -m "feat: implement dynamic prompt loading and thought structure"
```

---

### Task 2: Thought Extraction & Broadcasting

**Files:**
- Modify: `app/main.py`
- Modify: `app/utils/logger.py`

- [ ] **Step 1: Update process_message to extract Thought/Answer**

```python
import re

# ... inside process_message in app/main.py ...

# After LLM call:
response_text = await call_llm(final_messages)

# Extract tags
thought_match = re.search(r'<thought>(.*?)</thought>', response_text, re.DOTALL)
answer_match = re.search(r'<answer>(.*?)</answer>', response_text, re.DOTALL)

thought = thought_match.group(1).strip() if thought_match else "No explicit reasoning provided."
clean_answer = answer_match.group(1).strip() if answer_match else response_text

# Broadcast thought to dashboard
await log_manager.broadcast({
    "type": "thought",
    "content": thought
})

# Send clean answer to WhatsApp
await send_whatsapp_message(sender, clean_answer)

# Save to history with thought
await save_message(sender, "assistant", clean_answer, thought=thought)
```

- [ ] **Step 2: Update save_message to handle thought field in app/database/mongodb.py**

```python
async def save_message(sender: str, role: str, content: str, thought: str = None):
    doc = {
        "sender": sender,
        "role": role,
        "content": content,
        "timestamp": datetime.now()
    }
    if thought:
        doc["thought"] = thought
    await messages.insert_one(doc)
```

- [ ] **Step 3: Commit**

```bash
git add app/
git commit -m "feat: extract and broadcast AI thoughts"
```

---

### Task 3: Prompt Manager & System Status APIs

**Files:**
- Modify: `app/main.py`

- [ ] **Step 1: Add APIs to main.py**

```python
from app.database.mongodb import get_db_prompt, update_db_prompt, prompts as prompts_col

@app.get("/api/prompts")
async def list_prompts():
    all_prompts = {}
    # Helper to get prompt with fallback
    from app.agents.ai_agent import AI_AGENT_PROMPT, get_ai_prompt
    # ... and others ...
    all_prompts["AI_AGENT"] = await get_ai_prompt()
    # ... repeat for all agents ...
    return all_prompts

@app.post("/api/prompts/{name}")
async def set_prompt(name: str, request: Request):
    data = await request.json()
    await update_db_prompt(name, data.get("content"))
    return {"status": "success"}

@app.get("/api/system/status")
async def get_system_status():
    status = {
        "mongodb": "online",
        "nvidia_api": "configured" if os.getenv("NVIDIA_API_KEY") else "missing",
        "openwa_gateway": "unknown"
    }
    # Check gateway
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(os.getenv("OPENWA_API_URL", "http://localhost:2785"))
            if res.status_code < 500: status["openwa_gateway"] = "online"
    except: status["openwa_gateway"] = "offline"
    
    return status
```

- [ ] **Step 2: Commit**

```bash
git add app/main.py
git commit -m "feat: add APIs for prompt management and system status"
```

---

### Task 4: UI Update - Sidebar & Thought Rendering

**Files:**
- Modify: `frontend/src/components/Sidebar.tsx`
- Modify: `frontend/src/pages/CommandCenter.tsx`
- Create: `frontend/src/pages/PromptManager.tsx`
- Create: `frontend/src/pages/SystemStatus.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Update Sidebar.tsx**

```tsx
const navItems = [
  { id: 'logs', label: 'LIVE_LOGS', icon: Activity },
  { id: 'memory', label: 'MEMORY_VAULT', icon: Database },
  { id: 'prompts', label: 'PROMPT_MANAGER', icon: Settings },
  { id: 'system', label: 'SYSTEM_STATUS', icon: Shield },
  { id: 'console', label: 'DIRECT_CONSOLE', icon: Terminal },
];
```

- [ ] **Step 2: Update CommandCenter.tsx for thought logs**

```tsx
case 'thought':
  return (
    <div key={index} className={`${baseStyle} bg-yellow-900/10 border-l-2 border-yellow-500/50 text-yellow-100/80 italic`}>
      <span className="text-yellow-600 font-bold not-italic">[{log.timestamp}] AI_THOUGHT_PROCESS</span>
      <div className="mt-1">{log.content}</div>
    </div>
  );
```

- [ ] **Step 3: Implement PromptManager.tsx (Basic)**

```tsx
import React, { useState, useEffect } from 'react';

export const PromptManager = ({ password }: { password: string }) => {
    const [prompts, setPrompts] = useState<any>({});
    
    useEffect(() => {
        fetch('/api/prompts', { headers: { 'X-Password': password } })
            .then(res => res.json())
            .then(setPrompts);
    }, []);

    const savePrompt = (name: str, content: str) => {
        fetch(`/api/prompts/${name}`, {
            method: 'POST',
            headers: { 'X-Password': password, 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
    };

    return (
        <div className="space-y-6">
            {Object.entries(prompts).map(([name, content]: any) => (
                <div key={name} className="space-y-2">
                    <label className="text-xs font-bold text-gray-500">{name}</label>
                    <textarea 
                        defaultValue={content}
                        className="w-full bg-black text-xs font-mono p-4 border border-gray-800 h-48"
                        onBlur={(e) => savePrompt(name, e.target.value)}
                    />
                </div>
            ))}
        </div>
    );
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: implement prompt manager and thought rendering UI"
```

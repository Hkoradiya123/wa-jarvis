# Design Spec: Jarvis Utility Dashboard
**Date:** 2026-06-17  
**Status:** Draft

## 1. Overview
A "Utility / Dev-Tool" styled dashboard for the WhatsApp Jarvis project, deployed as a unified FastAPI + React (Vite) application on Hugging Face Spaces. The UI will focus on transparency and control, avoiding traditional "Chatbot" aesthetics in favor of a high-density, functional layout.

## 2. Aesthetic & UX (Dev-Tool Style)
- **Theme:** Dark mode by default, high contrast.
- **Typography:** Monospace fonts for data (JetBrains Mono/Inter).
- **Layout:** Sidebar navigation with a multi-pane content area.
- **Visuals:** Subtle borders (1px solid), no gradients, clear status indicators (LED-style dots).

## 3. Core Features
### A. Command Center (Live Stream)
- Real-time websocket feed of system logs.
- Visual breakdown of Agent Routing decisions (e.g., `USER -> ROUTER -> MEMORY_AGENT`).
- LLM latency and token usage tracking per message.

### B. Memory Vault (Data Management)
- Table view of all entries in the `memories` and `conversations` collections.
- Ability to search, filter by category, and "Hard Delete" memories Jarvis has stored.

### C. Reminder Grid
- A functional list of upcoming tasks with a "Snooze" or "Complete" action.

### D. Direct Console
- A command-line style interface to send test messages to the backend without using WhatsApp.

## 4. Architecture
- **Frontend:** React + Tailwind CSS (Utility-first).
- **Backend:** FastAPI (Existing) serving static files from the build folder.
- **Communication:** REST API for data, WebSockets for live logging.
- **Deployment:** Single Docker container on Hugging Face (Port 7860).

## 5. Security
- Simple Password protection (Environment Variable: `DASHBOARD_PASSWORD`) to prevent public access to your personal data on Hugging Face.

## 6. Success Criteria
- Dashboard loads at the root `/` or `/dashboard` of the HF Space.
- Live logs accurately reflect WhatsApp traffic.
- Memory can be deleted via the UI and reflected in the MongoDB.

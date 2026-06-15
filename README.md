# WhatsApp Jarvis - Multi-Agent AI Assistant

WhatsApp Jarvis is a production-grade personal assistant powered by **NVIDIA NIM (Llama 3.1 8B)**, **FastAPI**, and **Open-WA**. It features a specialized agent architecture to handle general queries, memory, reminders, and daily planning with a natural conversational interface.

## 🚀 Key Features

- **Multi-Agent Routing:** Automatically detects user intent and routes requests to specialized agents (AI, Memory, Reminder, Planner).
- **Smart Context Memory:** Uses MongoDB to remember previous parts of the conversation.
- **Auto Context Compaction:** Automatically summarizes long conversations to maintain speed and focus while preserving "infinite" memory.
- **Reply Activation:** Simply reply to Jarvis's messages to continue the conversation without re-typing the trigger word.
- **WhatsApp Friendly:** Concise, well-formatted responses optimized for mobile reading.

---

## 🛠️ Architecture

```text
User ↔ WhatsApp ↔ Open-WA Gateway ↔ FastAPI (Jarvis) ↔ NVIDIA NIM (LLM)
                                      ↕
                                   MongoDB
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.9+
- MongoDB Atlas (or local MongoDB)
- [NVIDIA NIM API Key](https://build.nvidia.com/)
- [Open-WA REST API](https://github.com/open-wa/wa-automate-rest)

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
# NVIDIA NIM Settings
NVIDIA_API_KEY=your_nvidia_api_key
NVIDIA_MODEL=meta/llama-3.1-8b-instruct

# WhatsApp Gateway Settings
OPENWA_API_URL=http://localhost:2785
OPENWA_API_KEY=dev-admin-key
SESSION_ID=your_uuid_here
TRIGGER_WORD=//jarvis

# Database
DATABASE_URL=mongodb+srv://...
```

### 3. Local Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd wa-chatbot

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m app.main
```

### 4. Connect to WhatsApp
1. Start your Open-WA gateway.
2. Run the session discovery script to link your `.env`:
   ```bash
   python discover_session.py
   ```
3. Register the webhook (using your Ngrok URL if local):
   ```bash
   python setup_webhook.py
   ```

---

## 🐳 Docker Setup

You can run the entire stack using Docker Compose:

```bash
docker-compose up --build
```

---

## 🤖 Usage

- **Start Chatting:** Send `//jarvis hello!` to your WhatsApp number.
- **Conversational:** Once he replies, simply reply/swipe-right on his message to continue talking.
- **Memory:** `//jarvis remember my dog's name is Rex.`
- **Reminders:** `//jarvis remind me to drink water every hour.`

## 📂 Project Structure
- `app/agents/`: Specialized agent prompts and logic.
- `app/database/`: MongoDB connection and history management.
- `app/utils/`: LLM wrappers and logging utilities.
- `app/main.py`: FastAPI server and message routing logic.

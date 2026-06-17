# Design: Developer & Debugging Suite

## Goals
1. **AI Thought Process**: Visible "reasoning" for every AI response in the dashboard.
2. **Prompt Manager**: Live editing of system prompts via the UI.
3. **Variable Inspector**: Real-time status of environment variables and infrastructure.

## Architecture

### 1. AI Thought Process (Reasoning)
- **Prompt Update**: `GLOBAL_RULES` will be updated to force the model to wrap its internal reasoning in `<thought>` tags and its user-facing response in `<answer>` tags.
- **Parsing Logic**: The `call_llm` or `process_message` function will use regex to separate these components.
- **Broadcast**: The `thought` will be broadcasted to the frontend via WebSockets as a specialized log type.
- **Storage**: The `messages` collection in MongoDB will be updated to include a `thought` field for `assistant` messages.

### 2. Prompt Manager
- **Storage**: A new MongoDB collection `prompts` will store the text for each agent (AI, Memory, Reminder, Planner, Router).
- **Backend API**:
    - `GET /api/prompts`: Returns all current prompts.
    - `POST /api/prompts`: Updates a specific prompt.
- **Integration**: Agent files (e.g., `ai_agent.py`) will be updated to check the database first, falling back to hardcoded strings if the DB is empty.

### 3. Variable Inspector
- **Backend API**: `GET /api/system/status`.
- **Logic**: 
    - Check presence of `NVIDIA_API_KEY`, `OPENWA_API_KEY`, etc. (Values will be masked: `nvapi-****`).
    - MongoDB `ping` command to check DB health.
    - Check Open-WA connectivity via a simple `GET` to its base URL.
- **UI**: A "System" tab in the dashboard showing health cards for each component.

## UI Changes (Frontend)
- **Sidebar**: Add "PROMPTS" and "SYSTEM" items.
- **Prompts Page**: A vertical list of agents with expandable code editors for each.
- **System Page**: A grid of status cards with "Online/Offline" indicators and metadata.
- **Command Center**: Update to render `thought` logs with a distinct style (e.g., yellow-bordered "Reasoning" blocks).

## Success Criteria
- Live logs show what the AI is thinking before it replies.
- Editing a prompt in the UI immediately changes the bot's behavior on WhatsApp.
- System page accurately reports if MongoDB or the WhatsApp gateway is down.

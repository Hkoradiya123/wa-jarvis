# Design: Professional Terminal Login & Privacy Guard

## Goals
1.  **Terminal Login Page**: A professional, immersive "Jarvis OS" login experience.
2.  **Privacy Guard**: Prevent chat data and AI thoughts from appearing in Hugging Face's public system logs.
3.  **UI Access Control**: Maintain `DASHBOARD_PASSWORD` security with an upgraded interface.

## Architecture

### 1. Frontend: Terminal Login (`LoginPage.tsx`)
-   **Aesthetics**: Monospaced fonts, dark theme (#0d1117), scanline overlays, and "System Boot" text animations.
-   **Components**: 
    -   `LoginHeader`: Displays "JARVIS_OS v2.0.4 - SECURE_ACCESS".
    -   `SystemCheck`: Animated list of "services starting..." (DB_LINK, AI_CORE, GATEWAY_SYNC).
    -   `AuthForm`: Styled input and button for the password.
-   **State**: Once authorized, the password is saved to `localStorage` and the user is redirected to the dashboard.

### 2. Backend: Privacy Guard (`logger.py`)
-   **Log Filter**: Modify `LogManager.broadcast` and standard logging to distinguish between "System Logs" (safe for public) and "Data Logs" (private chat/thoughts).
-   **Standard Output**: Silence `INFO` level logs containing user messages in the Python console.
-   **WebSocket**: Continue sending all logs (including thoughts/messages) to the WebSocket, as these are protected by the dashboard login.

## Implementation Details

### Frontend Updates
-   Create `frontend/src/pages/LoginPage.tsx`.
-   Update `frontend/src/App.tsx` to conditional render the login page.

### Backend Updates
-   Modify `app/utils/logger.py` to add a `silence_console` flag or similar logic for sensitive data.
-   Update `app/main.py` to ensure the `process_message` broadcasts don't also print to stdout.

## Success Criteria
-   The dashboard shows a professional terminal login page.
-   The "Logs" tab on Hugging Face only shows technical startup info, not private chat data.
-   The Webhook remains fully functional and unaffected by the UI login.

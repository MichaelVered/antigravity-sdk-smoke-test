# Google Antigravity (AGY) SDK Verification & Multi-Agent Laboratory

A unified demonstration application built with the **Google Antigravity (AGY) SDK** (`google-antigravity`), showcasing native SDK verification audit, dynamic subagent minting, sandboxed in-memory Python code execution, and Orchestrator LLM feedback in a colored terminal interface.

---

## 🏗️ Architecture & Multi-Agent Flow

The application executes in two distinct phases:

```
                                ┌──────────────────────────────────┐
                                │             main.py              │
                                └────────────────┬─────────────────┘
                                                 │
                  ┌──────────────────────────────┴──────────────────────────────┐
                  ▼                                                             ▼
┌──────────────────────────────────┐                        ┌──────────────────────────────────┐
│  Phase 1: SDK Verification Audit │                        │ Phase 2: Interactive Math Lab    │
├──────────────────────────────────┤                        ├──────────────────────────────────┤
│ • Audits google.antigravity import│                        │ • Persistent Orchestrator Agent  │
│ • Validates site-packages origin │                        │   - Fresh LLM Welcome Greetings  │
│ • Loads API Key (No Fallbacks)   │                        │   - Dynamic LLM Feedback         │
│ • Tests Live Model IPC Ping      │                        │ • Minted Subagent Per Question   │
└──────────────────────────────────┘                        │   - Writes Code On-The-Fly       │
                                                            │   - Executes Code In-Memory      │
                                                            │   - Zero Files Saved to Disk     │
                                                            └──────────────────────────────────┘
```

---

## 📁 File Structure

```text
~/ADK/AGY_SDK/
├── main.py              # Unified Phase 1 Audit & Phase 2 Multi-Agent Lab Application
├── requirements.txt      # Project dependencies (google-antigravity, python-dotenv)
└── README.md            # Project documentation
```

> **Note on Storage**: Subagent code execution runs **100% in-memory** (`python3 -c "<code>"`). No ephemeral script files are written to or left on disk.

---

## ⚙️ Prerequisites & Environment Setup

1. **Python Environment**: Ensure Python 3.10+ is active.
2. **API Credentials**: Place your Gemini API key in `~/ADK/.env`:
   ```env
   GOOGLE_API_KEY="your-api-key-here"
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Running the Application

Execute the unified program using your active environment:

```bash
python3 main.py
```

### What Happens When Executed:

1. **Phase 1 (SDK Verification Audit)**:
   - Verifies that `google.antigravity` is imported natively from `site-packages`.
   - Confirms API key loading without fallback mocks.
   - Runs a live IPC test ping to the AGY backend.
   - Pauses for user confirmation before proceeding.

2. **Phase 2 (Interactive Multi-Agent Lab)**:
   - **Orchestrator Agent**: Greets you with a fresh LLM-generated welcoming message on every round.
   - **User Menu**: Select from Addition, Subtraction, Multiplication, or Division.
   - **Subagent Code Generation**: A brand-new AGY Subagent is minted, writes executable Python code to compute integer-constrained math logic, and runs it in-memory.
   - **Code Inspection**: The generated code is displayed in colored terminal text.
   - **Feedback**: The Orchestrator Agent crafts personalized, witty, encouraging feedback based on your answer.

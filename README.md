# 📧 Email Triage OpenEnv

An OpenEnv-compatible environment where an AI agent triages emails by deciding what to do with each one.

Built for the **OpenEnv Hackathon – Round 1**.

---

## 🌍 Environment Description

In a real workplace, people spend hours every day managing email. This environment simulates that task: the agent receives emails one at a time and must choose the correct action for each.

**Why email triage?**
- It's a task every professional does
- Actions have clear right/wrong answers
- Replies can be evaluated for quality
- Scales easily from simple to complex scenarios

---

## 🎮 Action Space

| Action | Description |
|--------|-------------|
| `reply` | Send a reply (must include `reply_text`) |
| `archive` | Save for reference, no action needed |
| `escalate` | Forward to management immediately |
| `delete` | Permanently delete the email |
| `spam` | Mark as spam |

```json
{"action_type": "reply", "reply_text": "Dear sender, thank you for reaching out..."}
{"action_type": "archive"}
{"action_type": "escalate"}
```

---

## 👁️ Observation Space

Each step returns an observation with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `email_id` | string | Unique ID for this email |
| `subject` | string | Email subject line |
| `sender` | string | Sender email address |
| `body` | string | Email body text |
| `success` | bool | Whether the last action was valid |
| `done` | bool | Whether the episode is finished |
| `reward` | float | Score for the last action (0.0–1.0) |
| `message` | string | Human-readable feedback |

---

## 📋 Tasks

| Task ID | Difficulty | Emails | Description |
|---------|-----------|--------|-------------|
| `easy` | ⭐ Easy | 3 | Clearly labelled spam and routine emails |
| `medium` | ⭐⭐ Medium | 4 | Mix of replies, escalations, and archives |
| `hard` | ⭐⭐⭐ Hard | 5 | Ambiguous emails requiring nuanced judgment |

---

## 🏆 Reward Function

- **1.0** — Correct action taken
- **0.6–1.0** — Correct reply with keyword quality scoring
- **0.5** — Correct action type (reply) but no reply text provided
- **0.3** — Partially correct (e.g. escalated instead of replied)
- **0.0** — Wrong action
- **-0.1** — Invalid action type

---

## 🚀 Setup & Usage

### Run locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app:app --host 0.0.0.0 --port 7860
```

### Run with Docker

```bash
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/reset?task_id=easy` | Start a new episode |
| POST | `/step` | Take one action |
| GET | `/state` | Get current state |

### Example usage

```python
import requests

BASE = "http://localhost:7860"

# Start easy task
obs = requests.post(f"{BASE}/reset", params={"task_id": "easy"}).json()
print(obs["subject"])  # "You won a prize!!!"

# Take action
result = requests.post(f"{BASE}/step", json={"action_type": "spam"}).json()
print(result["reward"])  # 1.0
```

---

## 🤖 Running the Baseline Inference

```bash
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="your-api-key"
export ENV_URL="http://localhost:7860"

python inference.py
```

### Baseline Scores (gpt-4o-mini)

| Task | Score |
|------|-------|
| easy | ~0.95 |
| medium | ~0.80 |
| hard | ~0.70 |
| **overall** | **~0.82** |

---

## 📁 Project Structure

```
email_triage_env/
├── app.py           # FastAPI server
├── environment.py   # Core environment logic
├── models.py        # Pydantic data models
├── tasks.py         # Task definitions and graders
├── inference.py     # Baseline inference script
├── openenv.yaml     # OpenEnv metadata
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 👥 Team

**VisionX** — OpenEnv Hackathon 2025

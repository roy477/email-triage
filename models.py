from pydantic import BaseModel
from typing import Optional, Dict, Any


class EmailObservation(BaseModel):
    """What the agent sees at each step."""
    email_id: str
    subject: str
    sender: str
    body: str
    success: bool
    done: bool
    reward: float
    message: str = ""


class EmailAction(BaseModel):
    """What the agent can do."""
    # One of: "reply", "archive", "escalate", "delete", "spam"
    action_type: str
    reply_text: Optional[str] = None  # Only used when action_type == "reply"


class EmailReward(BaseModel):
    """Reward details."""
    score: float
    reason: str


class EmailState(BaseModel):
    """Internal environment state."""
    episode_id: str
    step_count: int
    task_id: str
    current_email_index: int
    total_emails: int
    cumulative_score: float

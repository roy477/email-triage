from uuid import uuid4
from models import EmailObservation, EmailAction, EmailState
from tasks import TASKS, grade_action


class EmailTriageEnvironment:
    """
    Email Triage OpenEnv Environment.
    The agent reads emails one by one and decides what to do with each.
    Actions: reply, archive, escalate, delete, spam
    """

    VALID_ACTIONS = {"reply", "archive", "escalate", "delete", "spam"}

    def __init__(self):
        self._task_id = "easy"
        self._emails = []
        self._current_index = 0
        self._episode_id = str(uuid4())
        self._step_count = 0
        self._scores = []

    def reset(self, task_id: str = "easy") -> EmailObservation:
        """Start a new episode. task_id can be 'easy', 'medium', or 'hard'."""
        if task_id not in TASKS:
            task_id = "easy"

        self._task_id = task_id
        self._emails = TASKS[task_id]["emails"]
        self._current_index = 0
        self._episode_id = str(uuid4())
        self._step_count = 0
        self._scores = []

        return self._make_observation(reward=0.0, message=f"Task '{task_id}' started. {len(self._emails)} emails to triage.")

    def step(self, action: EmailAction) -> EmailObservation:
        """Process one action on the current email."""
        if self._current_index >= len(self._emails):
            return EmailObservation(
                email_id="done",
                subject="",
                sender="",
                body="",
                success=False,
                done=True,
                reward=0.0,
                message="Episode already finished. Call reset() to start again.",
            )

        if action.action_type not in self.VALID_ACTIONS:
            # Penalty for invalid action
            self._step_count += 1
            return self._make_observation(
                reward=-0.1,
                message=f"Invalid action '{action.action_type}'. Valid: {self.VALID_ACTIONS}",
            )

        current_email = self._emails[self._current_index]
        score = grade_action(current_email, action.action_type, action.reply_text)
        self._scores.append(score)
        self._step_count += 1
        self._current_index += 1

        done = self._current_index >= len(self._emails)
        avg_score = sum(self._scores) / len(self._scores)

        if done:
            message = f"Episode complete! Average score: {avg_score:.2f} over {len(self._scores)} emails."
        else:
            message = f"Email scored {score:.2f}. {len(self._emails) - self._current_index} emails remaining."

        return self._make_observation(reward=score, message=message, done=done)

    def state(self) -> EmailState:
        """Return the current internal state."""
        return EmailState(
            episode_id=self._episode_id,
            step_count=self._step_count,
            task_id=self._task_id,
            current_email_index=self._current_index,
            total_emails=len(self._emails),
            cumulative_score=sum(self._scores) / max(len(self._scores), 1),
        )

    def _make_observation(self, reward: float, message: str, done: bool = False) -> EmailObservation:
        """Helper to build an observation from the current email."""
        if self._current_index >= len(self._emails):
            return EmailObservation(
                email_id="done",
                subject="",
                sender="",
                body="",
                success=True,
                done=True,
                reward=reward,
                message=message,
            )
        email = self._emails[self._current_index]
        return EmailObservation(
            email_id=email["email_id"],
            subject=email["subject"],
            sender=email["sender"],
            body=email["body"],
            success=True,
            done=done,
            reward=reward,
            message=message,
        )

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from models import EmailAction, EmailObservation, EmailState
from environment import EmailTriageEnvironment

app = FastAPI(
    title="Email Triage OpenEnv",
    description="An OpenEnv-compatible environment for email triage tasks.",
    version="1.0.0",
)

# Single shared environment instance (stateful per server)
env = EmailTriageEnvironment()


@app.get("/")
def root():
    return {"status": "ok", "env": "EmailTriageEnv", "version": "1.0.0"}


@app.post("/reset")
def reset(task_id: str = "easy"):
    """Reset the environment and return the first observation."""
    obs = env.reset(task_id=task_id)
    return obs.model_dump()


@app.post("/step")
def step(action: EmailAction):
    """Take one step in the environment."""
    obs = env.step(action)
    return obs.model_dump()


@app.get("/state")
def state():
    """Get the current internal state of the environment."""
    s = env.state()
    return s.model_dump()


@app.get("/health")
def health():
    return {"status": "healthy"}

"""
Baseline inference script for Email Triage OpenEnv.
Uses the OpenAI client to run a model against the environment.

Required environment variables:
    API_BASE_URL  - The API endpoint for the LLM
    MODEL_NAME    - The model identifier
    HF_TOKEN      - Your Hugging Face / API key
"""

import os
import json
import requests
from openai import OpenAI

# ── Config ──────────────────────────────────────────────────────────────────
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN     = os.environ.get("HF_TOKEN", "")

ENV_URL = os.environ.get("ENV_URL", "http://localhost:7860")  # HF Space URL

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

SYSTEM_PROMPT = """You are an expert email triage assistant.
For each email you receive, decide the best action from:
- reply    : Send a reply (also provide reply_text)
- archive  : Save for reference, no action needed
- escalate : Forward to management immediately
- delete   : Permanently delete
- spam     : Mark as spam

Respond ONLY with a JSON object like:
{"action_type": "reply", "reply_text": "Dear sender, ..."}
or
{"action_type": "archive"}

No explanation, no markdown, just the JSON object."""


def call_llm(email_obs: dict) -> dict:
    """Ask the LLM what to do with this email."""
    user_message = f"""Email to triage:
Subject: {email_obs['subject']}
From: {email_obs['sender']}
Body: {email_obs['body']}

What action do you take?"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.0,
    )
    raw = response.choices[0].message.content.strip()

    # Parse JSON response
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: try to extract JSON from the response
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        # Default safe action
        return {"action_type": "archive"}


def run_task(task_id: str) -> float:
    """Run the agent on one task and return the average score."""
    print(f"\n{'='*50}")
    print(f"Running task: {task_id.upper()}")
    print('='*50)

    # Reset environment
    resp = requests.post(f"{ENV_URL}/reset", params={"task_id": task_id})
    obs = resp.json()
    print(f"Task started: {obs.get('message', '')}")

    scores = []
    step_num = 0

    while not obs.get("done", False):
        step_num += 1
        print(f"\nStep {step_num}: [{obs['email_id']}] {obs['subject']}")

        # Ask LLM for action
        action = call_llm(obs)
        print(f"  LLM action: {action.get('action_type')} ", end="")
        if action.get("reply_text"):
            print(f"(reply: {action['reply_text'][:60]}...)", end="")
        print()

        # Send action to environment
        resp = requests.post(f"{ENV_URL}/step", json=action)
        obs = resp.json()
        reward = obs.get("reward", 0.0)
        scores.append(reward)
        print(f"  Score: {reward:.2f} — {obs.get('message', '')}")

    avg = sum(scores) / len(scores) if scores else 0.0
    print(f"\nTask '{task_id}' complete. Average score: {avg:.2f}")
    return avg


def main():
    print("Email Triage OpenEnv — Baseline Inference")
    print(f"Model: {MODEL_NAME}")
    print(f"Environment URL: {ENV_URL}")

    results = {}
    for task in ["easy", "medium", "hard"]:
        results[task] = run_task(task)

    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    for task, score in results.items():
        print(f"  {task:8s}: {score:.2f}")
    overall = sum(results.values()) / len(results)
    print(f"  {'overall':8s}: {overall:.2f}")
    print("="*50)

    return results


if __name__ == "__main__":
    main()

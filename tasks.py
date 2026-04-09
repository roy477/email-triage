"""
3 Tasks for the Email Triage Environment.
Each task has a set of emails and a grader function.
Difficulty: easy -> medium -> hard
"""

TASKS = {
    "easy": {
        "description": "Triage clearly labelled spam and routine emails.",
        "emails": [
            {
                "email_id": "e1",
                "subject": "You won a prize!!!",
                "sender": "noreply@scam123.com",
                "body": "Congratulations! You have been selected to win $1,000,000. Click here now!",
                "correct_action": "spam",
            },
            {
                "email_id": "e2",
                "subject": "Team lunch tomorrow",
                "sender": "alice@company.com",
                "body": "Hey, just a reminder that we have team lunch tomorrow at noon. See you there!",
                "correct_action": "archive",
            },
            {
                "email_id": "e3",
                "subject": "Free iPhone giveaway",
                "sender": "deals@fakeoffers.net",
                "body": "Act now! Limited time offer. Get a free iPhone by filling out this form.",
                "correct_action": "spam",
            },
        ],
    },
    "medium": {
        "description": "Triage a mix of emails that require replying, archiving, or escalating.",
        "emails": [
            {
                "email_id": "m1",
                "subject": "Question about invoice #4521",
                "sender": "client@bigcorp.com",
                "body": "Hi, could you please clarify the charges on invoice #4521?",
                "correct_action": "reply",
                "reply_keywords": ["invoice", "clarif", "apologize", "sorry", "explain", "charge"],
            },
            {
                "email_id": "m2",
                "subject": "Server is down!",
                "sender": "ops@company.com",
                "body": "URGENT: The production server has been down for 10 minutes.",
                "correct_action": "escalate",
            },
            {
                "email_id": "m3",
                "subject": "Monthly newsletter",
                "sender": "newsletter@industry.com",
                "body": "Here is your monthly industry digest.",
                "correct_action": "archive",
            },
            {
                "email_id": "m4",
                "subject": "Complaint: order not delivered",
                "sender": "angry.customer@email.com",
                "body": "My order hasn't arrived.",
                "correct_action": "reply",
                "reply_keywords": ["sorry", "apologize", "refund", "order", "resolve", "help"],
            },
        ],
    },
    "hard": {
        "description": "Triage ambiguous emails requiring careful judgment.",
        "emails": [
            {
                "email_id": "h1",
                "subject": "Follow up on our conversation",
                "sender": "unknown.person@gmail.com",
                "body": "Following up on last week.",
                "correct_action": "reply",
                "reply_keywords": ["clarif", "remind", "context", "which", "meeting", "discuss"],
            },
            {
                "email_id": "h2",
                "subject": "Urgent: Legal matter",
                "sender": "legal@partnerlaw.com",
                "body": "Contract clause risk.",
                "correct_action": "escalate",
            },
            {
                "email_id": "h3",
                "subject": "Re: Project proposal",
                "sender": "ceo@potentialclient.com",
                "body": "Questions about pricing.",
                "correct_action": "reply",
                "reply_keywords": ["pricing", "detail", "model", "happy", "glad", "provide", "send"],
            },
            {
                "email_id": "h4",
                "subject": "System maintenance window",
                "sender": "it@company.com",
                "body": "Maintenance Saturday.",
                "correct_action": "archive",
            },
            {
                "email_id": "h5",
                "subject": "Unsubscribe request",
                "sender": "customer@email.com",
                "body": "Please unsubscribe me.",
                "correct_action": "reply",
                "reply_keywords": ["unsubscribe", "removed", "list", "confirm", "sorry", "done"],
            },
        ],
    },
}


def clamp_score(score: float) -> float:
    """Ensure score always stays strictly between (0,1)."""
    return max(0.01, min(score, 0.99))


def grade_action(email: dict, action_type: str, reply_text: str = None) -> float:

    correct = email["correct_action"]

    if action_type != correct:
        partial_credit_pairs = {("reply", "escalate"), ("escalate", "reply")}

        if (action_type, correct) in partial_credit_pairs or (correct, action_type) in partial_credit_pairs:
            return clamp_score(0.3)

        return clamp_score(0.01)

    if correct == "reply":

        if not reply_text:
            return clamp_score(0.5)

        reply_lower = reply_text.lower()
        keywords = email.get("reply_keywords", [])

        if not keywords:
            return clamp_score(0.9)

        matched = sum(1 for kw in keywords if kw in reply_lower)
        keyword_score = matched / len(keywords)

        score = 0.6 + 0.4 * keyword_score
        return clamp_score(round(score, 2))

    return clamp_score(0.9)

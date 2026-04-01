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
                "body": "Hi, could you please clarify the charges on invoice #4521? I see an unexpected line item.",
                "correct_action": "reply",
                "reply_keywords": ["invoice", "clarif", "apologize", "sorry", "explain", "charge"],
            },
            {
                "email_id": "m2",
                "subject": "Server is down!",
                "sender": "ops@company.com",
                "body": "URGENT: The production server has been down for 10 minutes. Customers are affected!",
                "correct_action": "escalate",
            },
            {
                "email_id": "m3",
                "subject": "Monthly newsletter",
                "sender": "newsletter@industry.com",
                "body": "Here is your monthly industry digest. Top stories: AI advances, market updates...",
                "correct_action": "archive",
            },
            {
                "email_id": "m4",
                "subject": "Complaint: order not delivered",
                "sender": "angry.customer@email.com",
                "body": "I placed an order 3 weeks ago and it has not arrived. This is unacceptable. I want a refund.",
                "correct_action": "reply",
                "reply_keywords": ["sorry", "apologize", "refund", "order", "resolve", "help"],
            },
        ],
    },
    "hard": {
        "description": "Triage ambiguous emails with nuanced context requiring careful judgment.",
        "emails": [
            {
                "email_id": "h1",
                "subject": "Follow up on our conversation",
                "sender": "unknown.person@gmail.com",
                "body": "Hey, following up on what we discussed last week. Let me know your thoughts.",
                "correct_action": "reply",
                "reply_keywords": ["clarif", "remind", "context", "which", "meeting", "discuss"],
            },
            {
                "email_id": "h2",
                "subject": "Urgent: Legal matter",
                "sender": "legal@partnerlaw.com",
                "body": "Dear team, we need your immediate attention on a contract clause that may expose the company to liability. Please escalate to management.",
                "correct_action": "escalate",
            },
            {
                "email_id": "h3",
                "subject": "Re: Project proposal",
                "sender": "ceo@potentialclient.com",
                "body": "We reviewed your proposal and have a few questions before we can proceed. Can you send more details about your pricing model?",
                "correct_action": "reply",
                "reply_keywords": ["pricing", "detail", "model", "happy", "glad", "provide", "send"],
            },
            {
                "email_id": "h4",
                "subject": "System maintenance window",
                "sender": "it@company.com",
                "body": "Scheduled maintenance this Saturday 2am-4am. Please save your work before end of day Friday.",
                "correct_action": "archive",
            },
            {
                "email_id": "h5",
                "subject": "Unsubscribe request",
                "sender": "customer@email.com",
                "body": "I would like to unsubscribe from all your marketing emails immediately.",
                "correct_action": "reply",
                "reply_keywords": ["unsubscribe", "removed", "list", "confirm", "sorry", "done"],
            },
        ],
    },
}


def grade_action(email: dict, action_type: str, reply_text: str = None) -> float:
    """
    Grade a single action on a single email.
    Returns a score between 0.0 and 1.0.
    """
    correct = email["correct_action"]

    if action_type != correct:
        # Partial credit: escalating when reply was needed (or vice versa) is less wrong than spam/delete
        partial_credit_pairs = {("reply", "escalate"), ("escalate", "reply")}
        if (action_type, correct) in partial_credit_pairs or (correct, action_type) in partial_credit_pairs:
            return 0.3
        return 0.0

    # Correct action type — now check quality if it's a reply
    if correct == "reply":
        if not reply_text:
            return 0.5  # Right action but no reply text = partial credit
        reply_lower = reply_text.lower()
        keywords = email.get("reply_keywords", [])
        if not keywords:
            return 1.0
        matched = sum(1 for kw in keywords if kw in reply_lower)
        keyword_score = matched / len(keywords)
        # At least 0.6 for correct action, scaled up to 1.0 by keyword quality
        return round(0.6 + 0.4 * keyword_score, 2)

    return 1.0  # Perfect score for correct non-reply action

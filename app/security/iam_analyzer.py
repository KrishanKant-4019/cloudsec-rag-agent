import json


def analyze_iam_policy(policy_str):
    """
    Analyze IAM policy and detect risks.
    """

    try:
        policy = json.loads(policy_str)
    except Exception:
        return (
            "IAM Policy Analysis\n\n"
            "Risk Level: UNKNOWN\n\n"
            "Issues:\n\n"
            "- Invalid JSON policy\n\n"
            "Recommendations:\n\n"
            "- Provide valid IAM policy JSON"
        )

    risks = []

    for stmt in policy.get("Statement", []):
        action = stmt.get("Action", [])
        resource = stmt.get("Resource", [])
        effect = stmt.get("Effect")

        if isinstance(action, str):
            action = [action]
        if isinstance(resource, str):
            resource = [resource]

        if "*" in action:
            risks.append("Wildcard action '*' allows all operations")

        if "*" in resource:
            risks.append("Wildcard resource '*' allows access to all resources")

        if effect == "Allow" and "*" in action and "*" in resource:
            risks.append("Full administrative access detected")

    if len(risks) == 0:
        level = "LOW"
    elif len(risks) == 1:
        level = "MEDIUM"
    else:
        level = "HIGH"

    issues_text = "\n".join(f"- {risk}" for risk in risks) if risks else "- No major issues found"

    return (
        "IAM Policy Analysis\n\n"
        f"Risk Level: {level}\n\n"
        "Issues:\n\n"
        f"{issues_text}\n\n"
        "Recommendations:\n\n"
        "- Follow least privilege\n"
        "- Avoid wildcard '*'\n"
        "- Use role-based access"
    )

def detect_misconfig(text):
    """
    Detect cloud misconfigurations from text.
    """

    if not text:
        return (
            "Misconfiguration Analysis\n\n"
            "Risk Level: UNKNOWN\n\n"
            "Issues:\n- Empty input\n\n"
            "Recommendations:\n"
            "- Provide configuration details for analysis"
        )

    issues = []
    text_lower = text.lower()

    if "public" in text_lower:
        issues.append("Resource is publicly accessible")

    if "no encryption" in text_lower:
        issues.append("Encryption is not enabled")

    if "0.0.0.0/0" in text_lower:
        issues.append("Open access to all IPs (0.0.0.0/0)")

    if len(issues) == 0:
        level = "LOW"
    elif len(issues) == 1:
        level = "MEDIUM"
    else:
        level = "HIGH"

    issues_text = "\n".join(f"- {issue}" for issue in issues) if issues else "- No misconfigurations found"

    return (
        "Misconfiguration Analysis\n\n"
        f"Risk Level: {level}\n\n"
        "Issues:\n"
        f"{issues_text}\n\n"
        "Recommendations:\n"
        "- Disable public access\n"
        "- Enable encryption\n"
        "- Restrict network access (avoid 0.0.0.0/0)"
    )

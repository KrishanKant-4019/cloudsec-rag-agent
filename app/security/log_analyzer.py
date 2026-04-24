def analyze_log(log_text):
    """
    Analyze cloud logs for suspicious activity.
    """

    if not log_text:
        return (
            "Log Security Analysis\n\n"
            "Risk Level: UNKNOWN\n\n"
            "Issues:\n- Empty log input\n\n"
            "Recommendations:\n"
            "- Provide a cloud log excerpt for analysis"
        )

    risks = []
    log_lower = log_text.lower()

    if "delete" in log_lower:
        risks.append("Destructive action detected (delete operation)")

    if "0.0.0.0" in log_lower:
        risks.append("Access from public/unrestricted IP")

    if "sensitive" in log_lower:
        risks.append("Sensitive resource accessed")

    if len(risks) == 0:
        level = "LOW"
    elif len(risks) == 1:
        level = "MEDIUM"
    else:
        level = "HIGH"

    issues_text = "\n".join(f"- {risk}" for risk in risks) if risks else "- No issues detected"

    return (
        "Log Security Analysis\n\n"
        f"Risk Level: {level}\n\n"
        "Issues:\n"
        f"{issues_text}\n\n"
        "Recommendations:\n"
        "- Restrict IP access\n"
        "- Enable monitoring and alerts\n"
        "- Audit destructive actions"
    )

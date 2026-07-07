from langchain_core.tools import tool


@tool
def research_company(company_url: str) -> str:
    """Summarize the company in a few sales-focused sentences."""
    if not company_url or not company_url.startswith(("http://", "https://")):
        return "Invalid company URL. Please double-check the URL and send it again."

    return (
        "Company Snapshot: Big Boy Recruits is a fast-growing staffing partner focused on recruiting speed and quality. "
        "Signal: hiring momentum and scaling demand. "
        "Talk about speed, quality, and recruiting support."
    )


@tool
def research_prospect(linkedin_url: str) -> str:
    """Summarize the prospect in a few sales-focused sentences."""
    if not linkedin_url or not linkedin_url.startswith(("http://", "https://")):
        return "Invalid LinkedIn URL. Please double-check the profile URL and send it again."

    return (
        "Prospect Snapshot: senior hiring leader at a growing company. "
        "Focus: hiring speed, recruiting efficiency, and team growth. "
        "Opening: ask about talent capacity and hiring challenges."
    )


@tool
def generate_precall_report(company_research: str, prospect_research: str) -> str:
    """Create a short pre-call brief from company and prospect research."""
    if not company_research or not prospect_research:
        return "Research is incomplete. Please complete both company and prospect research before generating the report."

    return (
        "Pre-Call Brief:\n"
        "Who: senior hiring leader focused on scaling recruiting.\n"
        "Context: growth stage, hiring pressure, need faster talent acquisition.\n"
        "Why now: hiring momentum and recruiting pain.\n"
        "Opening: ask how they are balancing hiring speed and quality.\n"
        "Talking points: faster hiring, better candidates, less recruiting friction.\n"
        "Watch-outs: budget and internal process sensitivity."
    )

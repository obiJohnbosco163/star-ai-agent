from langchain_core.tools import tool


@tool
def research_company(company_url: str) -> str:
    """Research a company from a public URL and return a concise, sales-relevant summary."""
    if not company_url or not company_url.startswith(("http://", "https://")):
        return "Invalid company URL. Please double-check the URL and send it again."

    return (
        "Company Snapshot: Big Boy Recruits is a recruiting and staffing-focused business helping clients hire faster and scale teams. "
        "The company operates in the talent acquisition space and is positioned as a growth-oriented recruiting partner.\n"
        "Recent Developments: Recent hiring momentum, expansion into new client segments, and a stronger emphasis on recruiting operations.\n"
        "Sales-Relevant Signals: The company appears to be scaling and likely needs flexible recruiting support as headcount grows. "
        "They may also need help improving hiring speed and candidate quality.\n"
        "Notable Talking Points: Their growth stage and hiring focus make them a strong fit for a consultative recruiting partnership."
    )


@tool
def research_prospect(linkedin_url: str) -> str:
    """Research a prospect from a LinkedIn URL and return a concise, sales-relevant summary."""
    if not linkedin_url or not linkedin_url.startswith(("http://", "https://")):
        return "Invalid LinkedIn URL. Please double-check the profile URL and send it again."

    return (
        "Prospect Snapshot: The prospect is a senior hiring or talent leader at a growing company, likely responsible for recruiting strategy and team scaling.\n"
        "Background: Their experience suggests strong exposure to hiring operations, team growth, and recruiting bottlenecks.\n"
        "Likely Priorities: Improving hiring speed, reducing recruiting friction, and building a reliable talent pipeline.\n"
        "Conversation Openers: Reference their current growth priorities and ask how they are balancing speed with quality in hiring."
    )


@tool
def generate_precall_report(company_research: str, prospect_research: str) -> str:
    """Generate a concise pre-call report from completed company and prospect research."""
    if not company_research or not prospect_research:
        return "Research is incomplete. Please complete both company and prospect research before generating the report."

    return (
        "Prospect @ Company — Pre-Call Brief\n"
        "1. Who You're Talking To: A senior hiring leader focused on scaling recruiting efficiently and improving team performance.\n"
        "2. Company Context: The company is growing, hiring-focused, and likely experiencing pressure to expand talent acquisition capacity.\n"
        "3. Why Now: Hiring velocity and recruiting consistency appear to be the strongest signals that a staffing partner could add value right now.\n"
        "4. Suggested Opening: I noticed your team is expanding and I wanted to understand how you're thinking about hiring capacity and speed.\n"
        "5. Key Talking Points: Emphasize faster hiring support, access to qualified candidates, and reduced recruiting friction.\n"
        "6. Watch Out For: Budget sensitivity and internal priorities around hiring efficiency should be handled carefully."
    )

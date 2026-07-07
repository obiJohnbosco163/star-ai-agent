from main import map_sales_research_response_to_precall_report


def test_maps_sales_research_response_to_precall_report():
    payload = {
        "company_name": "Big Boy Recruits",
        "prospect_name": "Avery Chen",
        "who_you_are_talking_to": "A senior talent leader responsible for hiring strategy.",
        "company_context": "The company is expanding and scaling recruiting capacity.",
        "why_now": "Hiring velocity and recruiting efficiency appear to be the strongest signals for support right now.",
        "suggested_opening": "I noticed your team is expanding and wanted to understand how you're thinking about hiring capacity.",
        "key_talking_points": ["Faster hiring support", "Better candidate quality"],
        "watch_out_for": ["Budget sensitivity"],
    }

    report = map_sales_research_response_to_precall_report(payload)

    assert report["whoYoureTalkingTo"] == "A senior talent leader responsible for hiring strategy."
    assert report["companyContext"] == "The company is expanding and scaling recruiting capacity."
    assert report["whyNow"] == "Hiring velocity and recruiting efficiency appear to be the strongest signals for support right now."
    assert report["suggestedOpening"] == "I noticed your team is expanding and wanted to understand how you're thinking about hiring capacity."
    assert report["keyTalkingPoints"] == ["Faster hiring support", "Better candidate quality"]
    assert report["watchOutFor"] == ["Budget sensitivity"]

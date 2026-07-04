import unittest

from agent.state import AgentState, SalesResearchResponse


class SalesResearchResponseTests(unittest.TestCase):
    def test_model_can_be_stored_in_agent_state(self):
        payload = SalesResearchResponse(
            company_name="Big Boy Recruits",
            prospect_name="Avery Chen",
            who_you_are_talking_to="A senior talent leader responsible for hiring strategy.",
            company_context="The company is expanding and scaling recruiting capacity.",
            why_now="Hiring velocity and recruiting efficiency appear to be the strongest signals for support right now.",
            suggested_opening="I noticed your team is expanding and wanted to understand how you're thinking about hiring capacity.",
            key_talking_points=["Faster hiring support", "Better candidate quality", "Flexible recruiting coverage"],
            watch_out_for=["Budget sensitivity", "Internal hiring priorities"],
        )

        state = AgentState(messages=[], sales_research_response=payload)

        self.assertEqual(state["sales_research_response"], payload)
        self.assertEqual(state["sales_research_response"].company_name, "Big Boy Recruits")


if __name__ == "__main__":
    unittest.main()

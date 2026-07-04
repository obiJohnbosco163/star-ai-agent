# S.T.A.R. — Sales Targeting & Readiness Assistant

An AI-powered sales research copilot built for **Big Boy Recruits** that helps sales representatives walk into every call fully prepared. S.T.A.R. automates company and prospect research, then synthesizes both into a single, actionable pre-call brief — turning 15–20 minutes of manual prep into a minutes-long automated workflow.

---

## What It Does

Give S.T.A.R. a company URL and a prospect's LinkedIn URL, and it will:

1. Research the company (business, size, recent news, sales-relevant signals)
2. Research the prospect (role, background, likely priorities, conversation openers)
3. Synthesize both into one structured **Pre-Call Brief** — ready to scan in under a minute before a call

If only one input is provided, S.T.A.R. proactively asks for the missing piece rather than generating an incomplete report.

---

## Architecture

S.T.A.R. is built as one orchestrating agent that calls three sub-tools in sequence:

```
Rep provides company URL + LinkedIn URL
              │
              ▼
   ┌─────────────────────┐
   │   Orchestrator       │  (Sales Research Assistant)
   │   — collects inputs  │
   │   — routes to tools  │
   │   — presents report  │
   └─────────┬────────────┘
             │
   ┌─────────┼─────────────┐
   ▼                       ▼
RESEARCH_COMPANY      RESEARCH_PROSPECT
(company URL)         (LinkedIn URL)
   │                       │
   └───────────┬───────────┘
               ▼
     GENERATE_PRECALL_REPORT
     (synthesizes both into
      one structured brief)
               │
               ▼
     Pre-Call Brief delivered
     to the rep in chat
```

### Components

| Component | Role | Input | Output |
|---|---|---|---|
| **Orchestrator** (Sales Research Assistant) | Manages the conversation, collects missing inputs, routes to tools, presents the final report | Rep's message | Routed tool calls + final formatted report |
| **RESEARCH_COMPANY** | Investigates the prospect's company | Company URL | Company snapshot, recent developments, sales-relevant signals, talking points |
| **RESEARCH_PROSPECT** | Investigates the individual prospect | LinkedIn URL | Prospect snapshot, background, likely priorities, conversation openers |
| **GENERATE_PRECALL_REPORT** | Synthesizes both research outputs | Company + prospect research | Structured Pre-Call Brief (~300 words) |

---

## Pre-Call Brief Structure

Every report follows this format:

1. **Who You're Talking To** — role, tenure, background
2. **Company Context** — what they do, size, recent developments
3. **Why Now** — the strongest signal(s) suggesting they need Big Boy Recruits' services
4. **Suggested Opening** — a natural, specific conversation starter
5. **Key Talking Points** — how Big Boy Recruits' offering maps to their likely needs
6. **Watch Out For** — potential objections or sensitivities (layoffs, leadership change, etc.)

---

## How to Use

1. Open S.T.A.R. in your chat/agent interface
2. Provide a **company URL** and a **LinkedIn profile URL** for the prospect you're calling
   - If you only have one, S.T.A.R. will ask for the other before generating a report
3. Wait for the three research/synthesis steps to complete
4. Review your Pre-Call Brief before the call
5. Optionally, ask S.T.A.R. to dig deeper into any section (e.g. "tell me more about their recent funding" or "look into their competitors")

**Example prompt:**
```
Company: https://example-company.com
Prospect: https://linkedin.com/in/prospect-name
```

---

## Requirements

- Access to the underlying LLM/agent platform, this is deployed and listed on https://croo.network as an AI Agent.
- **Web search / browsing tool access** — all three research tools depend on live web lookups
- No CRM, database, or additional accounts required for the MVP

---

## Scope

### In Scope (MVP)
- Company research from a URL
- Prospect research from a LinkedIn URL
- Synthesized pre-call report generation
- Proactive prompting for missing inputs
- Follow-up deep-dive requests on specific report sections

### Out of Scope (MVP)
- CRM integration (Salesforce, HubSpot, etc.)
- Call recording or transcription
- Automated follow-up email drafting
- Historical report storage / report history
- Multi-user permissions or team dashboards
- Bulk/batch research across multiple prospects at once

These are natural candidates for a future phase but are intentionally excluded to keep the MVP lean and fast to ship.

---

## Design Principles

- **Never guess.** If research is incomplete or a URL is invalid, the tool says so clearly rather than fabricating details.
- **Always require both inputs.** A pre-call report is only generated once both company and prospect research are complete, unless the rep explicitly asks for one in isolation.
- **Built for speed, not depth.** Every report is capped at ~300 words — designed to be read in under a minute, right before a call.
- **Tone: confident, sharp, no fluff.** Like a well-prepared research analyst handing a rep exactly what they need, nothing they don't.

---

## Tech Notes

This build is implemented as a set of system prompts (one orchestrator + three tool-specific prompts) rather than custom application code. To deploy it:

1. Set the orchestrator prompt as the main agent's system prompt
2. Register `RESEARCH_COMPANY`, `RESEARCH_PROSPECT`, and `GENERATE_PRECALL_REPORT` as callable tools/functions, each using its respective prompt as its instruction set
3. Ensure the agent platform has web search/browsing capability wired into the two research tools

If porting this to a code-based agent framework (e.g. LangChain, an OpenAI/Anthropic function-calling setup), each tool prompt above maps directly to a tool definition with its own system instructions.

---

## Status

MVP complete — prompts finalized for orchestrator and all three tools. Ready for deployment/testing on your chosen agent platform.

## Contact

Email: star.ai.agent163@gmail.com · X-handle: @star_ai_agent

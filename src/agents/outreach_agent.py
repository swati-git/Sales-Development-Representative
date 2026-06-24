
from typing import Annotated
from agent_framework.foundry import  FoundryChatClient
from agent_framework import  Agent, tool
from qualification_agent import get_lead

@tool
def fetch_engagement_history(
    lead_id: Annotated[str, "The lead's unique id"],
) -> dict:
    """Past email opens, clicks, meetings, and site visits for the lead."""
    ...  # call your CRM / engagement store
    return {"opens": 0, "clicks": 0, "last_touch": None}
 
@tool
def fetch_company_signals(
    company: Annotated[str, "The prospect's company name"],
) -> dict:
    """Recent news, funding, hiring signals, tech stack — personalization fuel."""
    ...  # call your enrichment / news source
    return {"recent_news": [], "hiring": [], "tech": []}
 
 
@tool
def draft_outreach_email(
    lead_id: Annotated[str, "The lead's unique id"],
    angle: Annotated[str, "The personalization angle to lead with"],
    subject: Annotated[str, "Proposed subject line"],
    body: Annotated[str, "Proposed email body"],
) -> dict:
    """Persist a DRAFT (no send). Returns the stored draft for review."""
    ...  # save draft to your outreach store
    return {"status": "draft_saved", "lead_id": lead_id, "subject": subject}
 
@tool(approval_mode="always_require")   # ApprovalMode = Literal["always_require","never_require"]
def send_outreach_email(
    draft_id: Annotated[str, "Id of the approved draft to send"],
) -> dict:
    """Send a previously-approved draft."""
    ...  # call your email/ESP send API
    return {"status": "sent", "draft_id": draft_id}
 
 
OUTREACH_INSTRUCTIONS = """\
You are the Activate Outreach Agent. You receive a QUALIFIED lead and craft a
highly personalized, engaging outreach email.
 
Process:
1. Pull the lead profile (get_lead), engagement history
   (fetch_engagement_history), and company signals (fetch_company_signals).
2. Choose a single specific personalization angle grounded in that data — never
   generic. Reference a concrete signal (a recent hire, funding, a prior click).
3. Produce ONE subject line and a concise body (under ~120 words), then call
   draft_outreach_email. Do NOT send.
Output the draft and the angle you chose so a human can review.
"""
 
 
def build_outreach_agent(client: FoundryChatClient) -> Agent:
    return Agent(
        client=client,
        instructions=OUTREACH_INSTRUCTIONS,
        tools=[
            get_lead,                  # reused from the scoring agent's toolset
            fetch_engagement_history,
            fetch_company_signals,
            draft_outreach_email,
            send_outreach_email,     # add with approval_mode="always_require"
        ],
    )
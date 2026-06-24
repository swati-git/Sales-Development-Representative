# Score first; only if the lead is qualified, hand off to outreach. The gate is
# deterministic Python, not left to the model. The functional workflow API
# (plain async + native if/else) fits this cleanly; sketch:
#

from typing import Annotated, Optional

from agent_framework import Agent, tool
from agent_framework_foundry_hosting import ResponsesHostServer
from agents.outreach_agent import build_outreach_agent
from agents.qualification_agent import build_qualification_agent
from foundry_chat_client.client import make_client
from input_output_objects.qualificationresult import QualificationResult

def is_qualified(qualification: Optional[QualificationResult]) -> bool:
    """Deterministic gate: only if the lead is qualified do we proceed to outreach."""
    return qualification is not None and qualification.icp_fit_score >= 70

async def _run_pipeline(lead_id: str) -> dict:
    client = make_client()
    
    scoring = build_qualification_agent(client)
    result = await scoring.run(
        f"Qualify lead {lead_id}",
         options={"response_format": QualificationResult})
    
    q = result.value  # parsed QualificationResult, or None on parse failure
    if not isinstance(q, QualificationResult):
        return {"lead_id": lead_id, "qualified": False,
                "reason": "scoring output did not parse to QualificationResult"}
 
    if not is_qualified(q):
        return {"lead_id": lead_id, "qualified": False,
                "icp_fit_score": q.icp_fit_score, "reasons": q.reasons}

   
    outreach = build_outreach_agent(client)
    draft = await outreach.run(f"Craft outreach for qualified lead {lead_id}")
    return {
        "lead_id": lead_id,
        "qualified": True,
        "icp_fit_score": q.icp_fit_score,
        "outreach_draft": draft.text,
    }


@tool
async def process_lead(lead_id: Annotated[str, "The lead id to process"]) -> dict:
    """Score a lead and, only if qualified, draft personalized outreach."""
    return await _run_pipeline(lead_id)

def build_host_agent() -> Agent:
    return Agent(
        client=make_client(),
        instructions="For each lead id, call process_lead and return its result.",
        tools=[process_lead],
    )

if __name__ == "__main__":
    server = ResponsesHostServer(build_host_agent())  # build_host_agent() is a SupportsAgentRun
    server.run()
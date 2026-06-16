"""
SDR Qualification Agent — a hosted agent for Foundry.

Role: given a lead, the agent reasons through qualification using a ReAct loop:
fetch the lead from CRM -> enrich missing data -> score against the ICP ->
write the verdict back to CRM. The model decides which tool to call and when;
the @tool functions below are the "Act" half of Reason+Act.

All tool bodies are STUBS returning mock data. Each marks where a real
integration goes (CRM is provider-agnostic; enrichment is Breeze/Apollo-shaped).
Swap the bodies later without changing the agent or the tool signatures.
"""

import os
from dotenv import load_dotenv
load_dotenv()
from typing import Annotated

from agent_framework import Agent, tool
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import AzureCliCredential

#

# --- Tools (the "Act" half of the ReAct loop) -----------------------------
# The @tool decorator inspects each signature + Annotated descriptions and
# builds the JSON schema the model uses to decide when/how to call the tool.

@tool
def get_lead(
    lead_id: Annotated[str, "The CRM record ID of the lead to qualify."],
) -> dict:
    """Fetch a lead's current fields from the CRM by record ID."""
    # TODO: replace with real CRM read (CRM not yet chosen — keep this
    # interface stable; implement against Salesforce/HubSpot/etc. later).
    return {
        "lead_id": lead_id,
        "full_name": "Jordan Rivera",
        "email": "jordan.rivera@acme-logistics.com",
        "company": "Acme Logistics",
        "title": "VP of Operations",
        "company_domain": "acme-logistics.com",
        "employee_count": None,   # missing -> agent should enrich
        "industry": None,         # missing -> agent should enrich
        "annual_revenue": None,   # missing -> agent should enrich
        "lead_source": "Webinar: Q2 Supply Chain Trends",
    }


@tool
def enrich_contact(
    email: Annotated[str, "Work email of the contact to enrich."],
    company_domain: Annotated[str, "Company domain, e.g. 'acme-logistics.com'."],
) -> dict:
    """Fill in missing firmographic/contact data from an enrichment provider."""
    # TODO: bind to a real provider. Clearbit's standalone API is sunset
    # (now HubSpot Breeze Intelligence); use Breeze if on HubSpot, else
    # Apollo/ZoomInfo. Return shape below is provider-agnostic.
    return {
        "email": email,
        "company_domain": company_domain,
        "employee_count": 850,
        "industry": "Transportation & Logistics",
        "annual_revenue": "120M",
        "seniority": "VP",
        "technologies": ["SAP", "Salesforce", "Snowflake"],
        "confidence": 0.86,
    }


@tool
def compute_icp_fit(
    industry: Annotated[str, "Lead's industry."],
    employee_count: Annotated[int, "Number of employees at the company."],
    seniority: Annotated[str, "Seniority of the contact (e.g. VP, Director, C-level)."],
) -> dict:
    """Score a lead 0-100 against the Ideal Customer Profile using fixed rules."""
    # Deterministic so scores are reproducible and auditable. Tune to your ICP.
    score = 0
    reasons = []

    target_industries = {"Transportation & Logistics", "Manufacturing", "Retail"}
    if industry in target_industries:
        score += 40
        reasons.append(f"Industry '{industry}' is in target set (+40).")
    else:
        reasons.append(f"Industry '{industry}' outside target set (+0).")

    if employee_count >= 500:
        score += 35
        reasons.append("Company size >= 500 employees (+35).")
    elif employee_count >= 100:
        score += 20
        reasons.append("Company size 100-499 (+20).")
    else:
        reasons.append("Company size < 100 (+0).")

    if seniority.upper() in {"VP", "C-LEVEL", "CXO", "DIRECTOR"}:
        score += 25
        reasons.append(f"Decision-maker seniority '{seniority}' (+25).")
    else:
        reasons.append(f"Seniority '{seniority}' is non-decision-maker (+0).")

    tier = "A" if score >= 80 else "B" if score >= 55 else "C"
    return {"score": score, "tier": tier, "reasons": reasons}


@tool
def update_lead_qualification(
    lead_id: Annotated[str, "CRM record ID to update."],
    status: Annotated[str, "Qualification status, e.g. 'Qualified' or 'Disqualified'."],
    score: Annotated[int, "ICP fit score 0-100."],
    notes: Annotated[str, "Short rationale for the verdict, for the AE to read."],
) -> dict:
    """Write the qualification verdict back to the CRM lead record."""
    # TODO: replace with real CRM write once the CRM is chosen.
    return {"lead_id": lead_id, "status": status, "score": score,
            "notes": notes, "written": True}


# --- The agent (the "Reason" half — the model orchestrates the tools) ------

INSTRUCTIONS = """\
You are an SDR qualification assistant. Given a lead (by ID or details), decide
whether it is worth an Account Executive's time.

Process:
1. Use get_lead to load the record if you were given an ID.
2. If industry, employee_count, or revenue are missing, call enrich_contact.
3. Call compute_icp_fit with the resolved industry, employee_count, seniority.
4. Decide: tier A/B -> 'Qualified', tier C -> 'Disqualified'.
5. Call update_lead_qualification to record the verdict.

Then reply with: the verdict, the score and tier, the top 2-3 reasons, and one
suggested next action for the AE. Be concise and specific."""


def build_agent() -> Agent:
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=AzureCliCredential(),
    )
    return Agent(
        client=client,
        instructions=INSTRUCTIONS,
        tools=[get_lead, enrich_contact, compute_icp_fit, update_lead_qualification],
    )


if __name__ == "__main__":
    server = ResponsesHostServer(build_agent())
    server.run()
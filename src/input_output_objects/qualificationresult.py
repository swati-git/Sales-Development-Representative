from pydantic import BaseModel, Field

class QualificationResult(BaseModel):
    """Structured result emitted by the lead-scoring agent."""
    lead_id: str
    icp_fit_score: int = Field(ge=0, le=100, description="0-100 ICP fit score")
    qualified: bool = Field(description="Model's qualification call")
    reasons: list[str] = Field(default_factory=list, description="Evidence for the decision")
    recommended_next_step: str | None = None
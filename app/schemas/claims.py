from pydantic import BaseModel, Field
from enum import Enum
class ExtractClaim(BaseModel):
    claim_text:str=Field(description="one shot factual statement that can be checked.")
    evidence_quote:str=Field(description="the exact sentence from the source that supports claim.")
    source_index:int=Field(description="the nubmber in the square brackets of the source this claim came from.")

class ClaimList(BaseModel):
    claims:list[ExtractClaim]

class VerificationStatus(str,Enum):
    VERIFIED="verified"
    CONFLICTING="conflicting"
    INSUFFICIENT_EVIDENCE="insufficient_evidence"

class ClaimVerdict(BaseModel):
    status:VerificationStatus=Field(description="verified if sources support the claim and none contradict it;"
                                    "conflict if some support and some contradict it;"
                                    "insufficient_evidence if no source clearly addressess it;"
                                    )
    confidence:float=Field(description="A number from 0.0 to 1.0 for how sure you are")
    reasoning:str=Field(description="one or two sentences explaining the decision")
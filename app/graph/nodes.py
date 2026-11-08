from app.graph.state import ResearchAgentState
from app.llm import generate_structured
from app.schemas.research import ResearchPlan
from app.tools.web_search import search_web
from app.tools.qdrant_search import search_qdrant
from app.schemas.claims import ClaimList, ClaimVerdict
from app.llm import generate_structured,generate_text

def planner_node(state:ResearchAgentState):
    prompt=f"""
you are a research planner.
Break the following research request into a clear objective and 3 to 5 specific,
searchable sub-questions. Each must be searchable with the web search.
research request: {state['user_query']}
"""
    plan=generate_structured(prompt, ResearchPlan)
    return{
        "plan":plan.sub_questions,
        "step_count":state["step_count"]+1,
    }

def researcher_node(state:ResearchAgentState)->dict:
    new_results=[]
    seen_urls={r["url"] for r in state["search_results"] if r.get("url")}
    for question in state["plan"]:
        for item in search_qdrant(question):
            new_results.append({
                "sub_question":question,
                "origin":"knowledge_docs",
                "title":item["title"],
                "url":item["url"],
                "content":item["content"],
            })
        for item in search_web(question, max_results=3):
            if item["url"] in seen_urls:
                continue
            seen_urls.add(item["url"])
            new_results.append({
                "sub_question":question,
                "origin":"web",
                "title":item["title"],
                "url":item["url"],
                "content":item["content"],
            })
    return{
        "search_results":new_results,
        "step_count":state["step_count"]+1,
    }


from app.schemas.claims import ClaimList

def claim_extractor_node(state: ResearchAgentState):
    results=state["search_results"]
    sources_text="\n\n".join(
        f"[{i}] {r["title"]} \n {r["content"][:500]}"
        for i, r in enumerate(results)
    )
    prompt=f"""
you are a carerful research analyst.
Research question: {state["user_query"]}
Below are the numbered sources. Extract the important factual claims that help answer the question.
Rules:
Each claim must be short, specific and checkable.
Use only information that appears in the sources . Do not add outside knowledge.
For each claim copy the exact supporting sentence from the source as the evidence quote.
set source_index to the answer in the square brackets of that source.
Extract at most 10 claims.
sources: {sources_text}
"""
    extracted=generate_structured(prompt,ClaimList)
    claims=[]
    for c in extracted.claims:
        if not (0 <= c.source_index < len(results)):
            continue
        source= results[c.source_index]
        claims.append({
            "claim_text":c.claim_text,
            "evidence_quote":c.evidence_quote,
            "source_title":source["title"],
            "source_url":source["url"],
            "origin":source["origin"],
            "verification_status":"unverified",
            "confidence":0,
        })
    return {
        "claims": claims,
        "step_count":state["step_count"]+1,

    }


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def verifier_node(state: ResearchAgentState) -> dict:
    results = state["search_results"]

    sources_text = "\n\n".join(
        f"[{i}] {r['title']}\n{r['content'][:800]}"
        for i, r in enumerate(results)
    )

    verified_claims = []

    for claim in state["claims"]:
        updated = dict(claim)

        # Step 2a: kya evidence quote sach mein apne source mein hai?
        own_sources = [
            r for r in results
            if r["title"] == claim["source_title"] and r["url"] == claim["source_url"]
        ]
        source_text = _normalize(own_sources[0]["content"]) if own_sources else ""

        if _normalize(claim["evidence_quote"]) not in source_text:
            updated["verification_status"] = "insufficient_evidence"
            updated["confidence"] = 0.0
            updated["reasoning"] = "Evidence quote not found in the cited source."
            verified_claims.append(updated)
            continue

        # Step 2b, 2c: LLM se faisla
        prompt = f"""
You are a strict fact-checker.

Claim: {claim["claim_text"]}

Check this claim ONLY against the numbered sources below.
For each source, decide mentally whether it supports the claim, contradicts it, or does not address it.
Then give one final status:
- verified: at least one source clearly supports the claim and none contradict it
- conflicting: some sources support it and some contradict it
- insufficient_evidence: no source clearly addresses the claim

Do not use outside knowledge.

Sources:
{sources_text}
"""
        # Step 2d: status aur confidence claim mein likho
        try:
            verdict = generate_structured(prompt, ClaimVerdict)
            updated["verification_status"] = verdict.status.value
            updated["confidence"] = max(0.0, min(1.0, verdict.confidence))
            updated["reasoning"] = verdict.reasoning
        except Exception as e:
            print(f"Verifier error for claim '{claim['claim_text'][:50]}': {e}")
            updated["reasoning"] = "Verification failed; needs review."

        verified_claims.append(updated)

    # Step 3: state mein wapas
    return {
        "claims": verified_claims,
        "step_count": state["step_count"] + 1,
    }


def human_review_node(state: ResearchAgentState) -> dict:
    return {
        "human_feedback": state["human_feedback"].strip(),
        "step_count": state["step_count"] + 1,
    }


def synthesizer_node(state: ResearchAgentState) -> dict:
    # 1. Har alag source ko ek number do: [1], [2], ...
    source_numbers = {}
    for claim in state["claims"]:
        key = (claim["source_title"], claim["source_url"])
        if key not in source_numbers:
            source_numbers[key] = len(source_numbers) + 1

    # 2. Claims ko LLM ke liye text banao
    claims_text = "\n".join(
        f"- [{source_numbers[(c['source_title'], c['source_url'])]}] "
        f"({c['verification_status']}) {c['claim_text']}"
        for c in state["claims"]
    )

    feedback = state["human_feedback"] or "None"

    prompt = f"""
You are writing a research report.

Research question: {state["user_query"]}

Claims found (each has a source number and a verification status):
{claims_text}

Human reviewer feedback: {feedback}

Write the report in markdown with these sections:
## Executive Summary
## Key Findings
## Conflicting or Uncertain Information
## Limitations

Rules:
- Use only the claims above. Do not add outside facts.
- Put verified claims in Key Findings.
- Put conflicting claims in the Conflicting section and say clearly that sources disagree.
- Do not state insufficient_evidence claims as facts. Mention them only in Limitations.
- After each statement, cite its source number like [1].
- Follow the human reviewer feedback. If it says to exclude something, leave it out.
- Do not write a Sources section. It will be added automatically.
"""
    body = generate_text(prompt)

    # 3. Sources ki list Python banata hai (LLM nahi)
    sources_section = "\n".join(
        f"[{number}] {title} - {url or 'internal knowledge base'}"
        for (title, url), number in source_numbers.items()
    )

    final_report = f"{body}\n\n## Sources\n{sources_section}"

    return {
        "final_report": final_report,
        "step_count": state["step_count"] + 1,
    }
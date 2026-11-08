from sqlalchemy.orm import Session

from app.database.models import ResearchRun, Source, Claim, HumanFeedback


def create_run(db: Session, user_query: str) -> ResearchRun:
    run = ResearchRun(user_query=user_query, status="running")
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_run(db: Session, run_id: int):
    return db.query(ResearchRun).filter(ResearchRun.id == run_id).first()


def update_status(db: Session, run_id: int, status: str):
    run = get_run(db, run_id)
    if run:
        run.status = status
        db.commit()


def save_sources(db: Session, run_id: int, search_results: list[dict]):
    for r in search_results:
        db.add(Source(
            research_run_id=run_id,
            url=r["url"],
            title=r["title"],
            content_snippet=r["content"][:500],
        ))
    db.commit()


def save_claims(db: Session, run_id: int, claims: list[dict]):
    for c in claims:
        db.add(Claim(
            research_run_id=run_id,
            claim_text=c["claim_text"],
            verification_status=c["verification_status"],
            confidence_score=c["confidence"],
        ))
    db.commit()


def save_feedback(db: Session, run_id: int, feedback_text: str):
    db.add(HumanFeedback(research_run_id=run_id, feedback_text=feedback_text))
    db.commit()


def save_report(db: Session, run_id: int, report: str):
    run = get_run(db, run_id)
    if run:
        run.final_report = report
        run.status = "completed"
        db.commit()
from app.database.connection import SessionLocal
from app.database import repository as repo
from app.graph.workflow import research_graph, make_initial_state


def _config(run_id: int) -> dict:
    return {"configurable": {"thread_id": str(run_id)}}


def _save_outcome(db, run_id: int):
    snapshot = research_graph.get_state(_config(run_id))

    if snapshot.next:
        repo.update_status(db, run_id, "awaiting_review")
    else:
        repo.save_report(db, run_id, snapshot.values["final_report"])


def run_research(run_id: int, query: str):
    db = SessionLocal()
    try:
        research_graph.invoke(make_initial_state(query), _config(run_id))

        values = research_graph.get_state(_config(run_id)).values
        repo.save_sources(db, run_id, values["search_results"])
        repo.save_claims(db, run_id, values["claims"])

        _save_outcome(db, run_id)
    except Exception as e:
        print(f"Research {run_id} failed: {e}")
        db.rollback()
        repo.update_status(db, run_id, "failed")
    finally:
        db.close()


def resume_research(run_id: int, feedback: str):
    db = SessionLocal()
    try:
        repo.save_feedback(db, run_id, feedback)
        repo.update_status(db, run_id, "running")

        research_graph.update_state(_config(run_id), {"human_feedback": feedback})
        research_graph.invoke(None, _config(run_id))

        _save_outcome(db, run_id)
    except Exception as e:
        print(f"Resume {run_id} failed: {e}")
        db.rollback()
        repo.update_status(db, run_id, "failed")
    finally:
        db.close()
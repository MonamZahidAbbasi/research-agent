from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ResearchRun(Base):
    __tablename__ = "research_runs"

    id = Column(Integer, primary_key=True)
    user_query = Column(Text)
    status= Column(String(50), default="pending")
    final_report=Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    research_run_id = Column(Integer, ForeignKey("research_runs.id"))
    url = Column(String, nullable=True)
    title = Column(String, nullable=True)
    content_snippet = Column(Text, nullable=True)

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True)
    research_run_id = Column(Integer, ForeignKey("research_runs.id"))
    claim_text = Column(Text)
    verfication_status = Column(String(50), default="unverified")
    confidence_score = Column(Float, nullable=True)

class HumanFeedback(Base):
    __tablename__ = "human_feedback"

    id = Column(Integer, primary_key=True)
    research_run_id = Column(Integer, ForeignKey("research_runs.id"))
    feedback_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Asset(Base):
    __tablename__ = "assets"
    symbol: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    asset_class: Mapped[str] = mapped_column(String)

class Venue(Base):
    __tablename__ = "venues"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    venue_type: Mapped[str] = mapped_column(String)

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    venue: Mapped[str] = mapped_column(String)

class PositionSnapshot(Base):
    __tablename__ = "position_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset: Mapped[str] = mapped_column(String)
    quantity: Mapped[float] = mapped_column(Float)
    usd_value: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String)
    account: Mapped[str] = mapped_column(String)
    venue: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    raw_data: Mapped[dict] = mapped_column(JSON)

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String, index=True)
    asset: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
    direction: Mapped[str] = mapped_column(String)
    transaction_type: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)
    venue: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String)

class ReconciliationRun(Base):
    __tablename__ = "reconciliation_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String, default="COMPLETED")
    matched_count: Mapped[int] = mapped_column(Integer, default=0)

class ReconciliationItem(Base):
    __tablename__ = "reconciliation_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("reconciliation_runs.id"))
    asset: Mapped[str] = mapped_column(String)
    internal_quantity: Mapped[float] = mapped_column(Float)
    external_quantity: Mapped[float] = mapped_column(Float)
    difference: Mapped[float] = mapped_column(Float)
    usd_impact: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String)
    venue: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    evidence: Mapped[dict] = mapped_column(JSON)

class Exception(Base):
    __tablename__ = "exceptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    reconciliation_item_id: Mapped[int | None] = mapped_column(ForeignKey("reconciliation_items.id"), nullable=True)
    type: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="OPEN")
    title: Mapped[str] = mapped_column(String)
    summary: Mapped[str] = mapped_column(Text)
    usd_impact: Mapped[float] = mapped_column(Float)
    asset: Mapped[str] = mapped_column(String)
    source_records: Mapped[dict] = mapped_column(JSON)
    detected_at: Mapped[datetime] = mapped_column(DateTime)
    assigned_analyst: Mapped[str | None] = mapped_column(String, nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    severity_reason: Mapped[str] = mapped_column(Text)

class ExceptionComment(Base):
    __tablename__ = "exception_comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    exception_id: Mapped[int] = mapped_column(ForeignKey("exceptions.id"))
    author: Mapped[str] = mapped_column(String)
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String)
    entity_type: Mapped[str] = mapped_column(String)
    entity_id: Mapped[str] = mapped_column(String)
    actor: Mapped[str] = mapped_column(String)
    detail: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

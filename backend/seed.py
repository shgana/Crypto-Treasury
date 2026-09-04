"""Repeatable synthetic demo data. Safe to run repeatedly."""
import random
from datetime import datetime, timedelta
from .database import Base, engine, SessionLocal
from .models import Asset, Venue, Account, PositionSnapshot, Transaction, ReconciliationRun, ReconciliationItem, Exception, AuditEvent
from .reconciliation import severity

NOW = datetime(2026, 9, 4, 14, 15)
PRICES = {"BTC": 108000, "ETH": 4300, "XRP": 2.5, "SOL": 205, "USDC": 1, "USDT": 1, "USD": 1}
ASSETS = [("BTC", "Bitcoin", "digital_asset"), ("ETH", "Ethereum", "digital_asset"), ("XRP", "XRP", "digital_asset"), ("SOL", "Solana", "digital_asset"), ("USDC", "USD Coin", "stablecoin"), ("USDT", "Tether", "stablecoin"), ("USD", "US Dollar", "cash")]

def audit(db, action, entity_type, entity_id, detail, actor="System"):
    db.add(AuditEvent(action=action, entity_type=entity_type, entity_id=str(entity_id), detail=detail, actor=actor, created_at=NOW))

def add_exception(db, item, kind, title, summary, impact, asset, pct=0, stale=0):
    sev, reason = severity(impact, pct, stale)
    e = Exception(reconciliation_item_id=item.id if item else None, type=kind, severity=sev, status="OPEN", title=title, summary=summary, usd_impact=impact, asset=asset, source_records=item.evidence if item else {"source": "synthetic seed"}, detected_at=NOW, severity_reason=reason)
    db.add(e); db.flush(); audit(db, "EXCEPTION_CREATED", "Exception", e.id, f"{kind} detected by deterministic reconciliation")
    return e

def seed():
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
    db = SessionLocal(); random.seed(42)
    try:
        db.add_all([Asset(symbol=s, name=n, asset_class=c) for s,n,c in ASSETS])
        db.add_all([Venue(name=n, venue_type=t) for n,t in [("Internal Ledger","internal"),("Exchange A","exchange"),("Exchange B","exchange"),("Custodian A","custodian"),("Custodian B","custodian"),("On-chain Treasury Wallet","wallet"),("On-chain Settlement Wallet","wallet")]])
        db.add_all([Account(id="TREASURY",name="Treasury Master",venue="Internal Ledger"),Account(id="EXA-01",name="Prime Account",venue="Exchange A"),Account(id="CUST-A",name="Safekeeping",venue="Custodian A")])
        quantities = {"BTC":105, "ETH":1700, "XRP":1550000, "SOL":12000, "USDC":3000000, "USDT":2000000, "USD":1250000}
        # Canonical source snapshots produce a ~$25m portfolio and source evidence.
        for asset, qty in quantities.items():
            for source, account, venue, multiplier in [("Internal Ledger","TREASURY","Internal Ledger",1), ("Exchange A","EXA-01","Exchange A",0.34), ("Custodian A","CUST-A","Custodian A",0.48), ("On-chain Wallet","0xTREASURY","On-chain Treasury Wallet",0.18)]:
                q = qty * multiplier
                db.add(PositionSnapshot(asset=asset, quantity=q, usd_value=q*PRICES[asset], source=source, account=account, venue=venue, timestamp=NOW - timedelta(minutes=10), raw_data={"synthetic":True,"feed":source}))
        run = ReconciliationRun(created_at=NOW, status="COMPLETED", matched_count=412); db.add(run); db.flush()
        # 412 successful reconciliations make the dashboard credible without cluttering source records.
        for i in range(420):
            asset = list(PRICES)[i % 7]; q = round(random.uniform(0.1, 25), 5)
            status = "EXACT_MATCH" if i < 395 else "MATCH_WITHIN_TOLERANCE"
            db.add(ReconciliationItem(run_id=run.id, asset=asset, internal_quantity=q, external_quantity=q if status == "EXACT_MATCH" else q-.005, difference=0 if status == "EXACT_MATCH" else .005, usd_impact=0 if status == "EXACT_MATCH" else 4.5, source="Internal Ledger ↔ External", venue="Exchange A" if i%3 else "Custodian A", status=status, timestamp=NOW-timedelta(minutes=i%30), evidence={"internal_record":f"OMS-{i:04d}","external_record":f"EXT-{i:04d}","rule":status}))
        breaks = [
          ("USDC", 200000, "MISSING_EXTERNAL", "Custodian A", "Missing USDC settlement", "Internal records show a 200,000 USDC withdrawal at 14:02 UTC. Custodian balance has not reflected the transfer as of the 14:15 UTC snapshot.", 10),
          ("BTC", 216000, "BREAK", "Exchange A", "BTC quantity mismatch", "Internal Ledger is 2.000 BTC higher than Exchange A after the configured matching window.", 0),
          ("ETH", 86000, "DUPLICATE", "Exchange B", "Duplicate ETH transaction", "Two Exchange B records share external ID EXB-ETH-7741 with the same amount and timestamp.", 0),
          ("SOL", 61500, "STALE_DATA", "On-chain Treasury Wallet", "Stale wallet snapshot", "Treasury wallet snapshot is 3 hours old; the maximum permitted age is 60 minutes.", 3),
          ("XRP", 38750, "PRICE_MISMATCH", "Custodian A", "XRP mark discrepancy", "Custodian A mark differs by 62 bps from the approved synthetic reference mark.", 0),
          ("USDT", 75000, "TIMING_DIFFERENCE", "Exchange B", "Settlement timing difference", "Exchange B transfer remains pending beyond the 30-minute timestamp tolerance.", 0),
          ("USDC", 120000, "MISSING_INTERNAL", "Exchange A", "Missing exchange withdrawal", "Exchange A reports a completed USDC withdrawal with no corresponding internal ledger transaction.", 0),
        ]
        for idx,(asset,impact,status,venue,title,summary,stale) in enumerate(breaks):
            diff=impact/PRICES[asset]; item=ReconciliationItem(run_id=run.id,asset=asset,internal_quantity=0 if status=="MISSING_INTERNAL" else diff,external_quantity=diff if status=="MISSING_INTERNAL" else 0,difference=diff,usd_impact=impact,source="Internal Ledger ↔ "+venue,venue=venue,status=status,timestamp=NOW-timedelta(hours=stale),evidence={"internal_record":f"OMS-BREAK-{idx}","external_record":f"{venue[:3].upper()}-BREAK-{idx}","matching_rule":status,"tolerance":"quantity 0.01; USD $100; timestamp 30m"});db.add(item);db.flush();add_exception(db,item,status,title,summary,impact,asset, pct=2.1 if status=="BREAK" else 0, stale=stale)
        for i in range(30):
            external_id = "EXB-ETH-7741" if i in (5,6) else f"TX-{i:03d}"
            db.add(Transaction(external_id=external_id,asset="ETH" if i<10 else "USDC",amount=round(random.uniform(100,5000),2),direction="OUT" if i%2 else "IN",transaction_type="TRANSFER",source="Exchange B",venue="Exchange B",timestamp=NOW-timedelta(minutes=i*5),status="SETTLED"))
        audit(db,"RECONCILIATION_EXECUTED","ReconciliationRun",run.id,"419 matched or within tolerance; 7 exceptions surfaced")
        db.commit()
    finally: db.close()

if __name__ == "__main__": seed()

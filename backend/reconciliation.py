from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Tolerances:
    quantity: float = 0.01
    usd_value: float = 100.0
    price_bps: float = 25.0
    timestamp_minutes: int = 30

def reconcile_position(internal, external, tol=Tolerances()):
    if external is None: return "MISSING_EXTERNAL"
    if internal is None: return "MISSING_INTERNAL"
    difference = internal.quantity - external.quantity
    if abs(difference) < 1e-10: return "EXACT_MATCH"
    if abs(difference) <= tol.quantity: return "MATCH_WITHIN_TOLERANCE"
    return "BREAK"

def transaction_status(tx, seen_ids, now):
    if tx.external_id in seen_ids: return "DUPLICATE"
    if tx.status == "PENDING" and now - tx.timestamp > timedelta(minutes=30): return "TIMING_DIFFERENCE"
    return "EXACT_MATCH"

def severity(usd_impact, pct_difference=0, stale_hours=0, concentration=False):
    reasons = []
    score = 0
    if usd_impact >= 100000: score += 3; reasons.append(f"${usd_impact:,.0f} impact exceeds $100k")
    elif usd_impact >= 25000: score += 2; reasons.append(f"${usd_impact:,.0f} impact exceeds $25k")
    else: score += 1; reasons.append(f"${usd_impact:,.0f} impact")
    if pct_difference >= 2: score += 1; reasons.append(f"{pct_difference:.1f}% variance")
    if stale_hours >= 2: score += 1; reasons.append(f"snapshot is {stale_hours:.1f}h stale")
    if concentration: score += 1; reasons.append("concentration threshold breached")
    return ("CRITICAL" if score >= 4 else "HIGH" if score >= 3 else "MEDIUM" if score >= 2 else "LOW", "; ".join(reasons))

def is_stale(timestamp, now, max_age_minutes=60): return now - timestamp > timedelta(minutes=max_age_minutes)

def concentration_warning(venue_value, nav, threshold=0.30):
    ratio = venue_value / nav if nav else 0
    return ratio > threshold, ratio

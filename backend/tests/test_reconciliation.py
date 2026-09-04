from datetime import datetime, timedelta
from types import SimpleNamespace
from backend.reconciliation import Tolerances, concentration_warning, is_stale, reconcile_position, severity, transaction_status

def p(q): return SimpleNamespace(quantity=q)
def test_exact_and_tolerance_reconciliation():
    assert reconcile_position(p(10),p(10)) == "EXACT_MATCH"
    assert reconcile_position(p(10),p(9.995),Tolerances(quantity=.01)) == "MATCH_WITHIN_TOLERANCE"
def test_missing_positions():
    assert reconcile_position(p(1),None) == "MISSING_EXTERNAL"
    assert reconcile_position(None,p(1)) == "MISSING_INTERNAL"
def test_break(): assert reconcile_position(p(10),p(8)) == "BREAK"
def test_duplicate_transaction():
    tx=SimpleNamespace(external_id="dup",status="SETTLED",timestamp=datetime.now())
    assert transaction_status(tx,{"dup"},datetime.now()) == "DUPLICATE"
def test_stale_snapshot(): assert is_stale(datetime.now()-timedelta(hours=2),datetime.now())
def test_severity_explains_reason():
    level,reason=severity(200000,2.5,3); assert level == "CRITICAL" and "impact" in reason and "stale" in reason
def test_concentration_warning():
    warning,ratio=concentration_warning(34,100,.30); assert warning and ratio == .34

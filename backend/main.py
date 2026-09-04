from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from .database import get_db
from .models import PositionSnapshot, ReconciliationItem, Exception, ExceptionComment, AuditEvent
from .seed import audit

app = FastAPI(title="LedgerOps API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])

def event_dict(e): return {"id":e.id,"action":e.action,"entity_type":e.entity_type,"entity_id":e.entity_id,"actor":e.actor,"detail":e.detail,"created_at":e.created_at}
def exception_dict(e, db):
    d={c.name:getattr(e,c.name) for c in e.__table__.columns}; d["comments"]= [{"id":c.id,"author":c.author,"body":c.body,"created_at":c.created_at} for c in db.query(ExceptionComment).filter_by(exception_id=e.id).all()]; return d

@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/overview")
def overview(db: Session=Depends(get_db)):
    positions=db.query(PositionSnapshot).filter(PositionSnapshot.source=="Internal Ledger").all(); nav=sum(p.usd_value for p in positions); ex=db.query(Exception).all(); items=db.query(ReconciliationItem).all()
    by_asset=[{"name":p.asset,"value":round(p.usd_value)} for p in positions]
    by_venue=[{"name":"Exchange A","value":round(nav*.34)},{"name":"Custodian A","value":round(nav*.48)},{"name":"On-chain Wallet","value":round(nav*.18)}]
    critical=sum(e.severity in ("CRITICAL","HIGH") and e.status!="RESOLVED" for e in ex)
    return {"nav":round(nav),"gross_exposure":round(nav-1250000),"stablecoin":round(sum(p.usd_value for p in positions if p.asset in ("USDC","USDT"))),"cash":1250000,"open_exceptions":sum(e.status != "RESOLVED" for e in ex),"priority_exceptions":critical,"unsettled_transfers":2,"reconciliation_rate":round(100*sum(i.status in ("EXACT_MATCH","MATCH_WITHIN_TOLERANCE") for i in items)/len(items),1),"by_asset":by_asset,"by_venue":by_venue,"severity_counts":[{"name":s,"value":sum(e.severity==s for e in ex)} for s in ["CRITICAL","HIGH","MEDIUM","LOW"]],"concentration_warning":{"venue":"Exchange A","ratio":34,"threshold":30,"message":"Exchange A holds 34% of total NAV, above the configured 30% concentration threshold."}}

@app.get("/reconciliation-items")
def reconciliation_items(status:str|None=None,asset:str|None=None,venue:str|None=None,db:Session=Depends(get_db)):
    q=db.query(ReconciliationItem)
    if status:q=q.filter_by(status=status)
    if asset:q=q.filter_by(asset=asset)
    if venue:q=q.filter_by(venue=venue)
    return [{c.name:getattr(x,c.name) for c in x.__table__.columns} for x in q.order_by(ReconciliationItem.usd_impact.desc()).limit(100).all()]

@app.get("/exceptions")
def exceptions(db:Session=Depends(get_db)):
    return [exception_dict(e,db) for e in db.query(Exception).order_by(Exception.usd_impact.desc()).all()]
@app.get("/exceptions/{exception_id}")
def exception_detail(exception_id:int,db:Session=Depends(get_db)):
    e=db.get(Exception,exception_id)
    if not e: raise HTTPException(404,"Exception not found")
    d=exception_dict(e,db); item=db.get(ReconciliationItem,e.reconciliation_item_id) if e.reconciliation_item_id else None;d["evidence"]=item.evidence if item else e.source_records;d["audit"]= [event_dict(x) for x in db.query(AuditEvent).filter_by(entity_id=str(e.id)).order_by(AuditEvent.created_at).all()];return d
class Update(BaseModel): status:str|None=None; assigned_analyst:str|None=None; resolution_notes:str|None=None; actor:str="Avery Chen"
@app.patch("/exceptions/{exception_id}")
def update_exception(exception_id:int, u:Update, db:Session=Depends(get_db)):
    e=db.get(Exception,exception_id)
    if not e: raise HTTPException(404,"Exception not found")
    if u.status: e.status=u.status; audit(db,"STATUS_CHANGED","Exception",e.id,f"Status changed to {u.status}",u.actor)
    if u.assigned_analyst: e.assigned_analyst=u.assigned_analyst;audit(db,"ASSIGNED","Exception",e.id,f"Assigned to {u.assigned_analyst}",u.actor)
    if u.resolution_notes: e.resolution_notes=u.resolution_notes
    if u.status=="RESOLVED":e.resolved_at=datetime.utcnow();audit(db,"RESOLVED","Exception",e.id,"Resolution recorded",u.actor)
    db.commit();return exception_dict(e,db)
class CommentIn(BaseModel): author:str="Avery Chen"; body:str
@app.post("/exceptions/{exception_id}/comments")
def add_comment(exception_id:int, c:CommentIn,db:Session=Depends(get_db)):
    if not db.get(Exception,exception_id):raise HTTPException(404,"Exception not found")
    comment=ExceptionComment(exception_id=exception_id,author=c.author,body=c.body);db.add(comment);audit(db,"COMMENT_ADDED","Exception",exception_id,"Analyst comment added",c.author);db.commit();return {"id":comment.id}
@app.get("/activity")
def activity(db:Session=Depends(get_db)): return [event_dict(e) for e in db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(100).all()]
@app.get("/settings")
def settings():return {"quantity_tolerance":0.01,"usd_value_tolerance":100,"price_tolerance_bps":25,"timestamp_tolerance_minutes":30,"concentration_threshold":30}

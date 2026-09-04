"use client";
export default function ErrorState({reset}:{reset:()=>void}){return <div className="page-state"><p className="eyebrow">DATA CONNECTION UNAVAILABLE</p><h2>We couldn’t load the operations workspace.</h2><p>Check that the LedgerOps API is running, then retry.</p><button className="primary" onClick={reset}>Retry connection</button></div>}

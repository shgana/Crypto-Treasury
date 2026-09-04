import "./globals.css";
import "./polish.css";
import "./final-polish.css";
import Link from "next/link";
export const metadata={title:"LedgerOps | Digital Asset Operations",description:"Institutional reconciliation console"};
const links=[["Overview","/overview"],["Reconciliation","/reconciliation"],["Exceptions","/exceptions"],["Activity","/activity"],["Settings","/settings"]];
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><body><aside><div className="brand"><span className="brandmark">L</span><span>Ledger<span>Ops</span></span></div><div className="workspace">TREASURY OPERATIONS</div><nav>{links.map(([label,href])=><Link key={href} href={href}>{label}</Link>)}</nav><div className="analyst"><div className="avatar">AC</div><div><b>Avery Chen</b><small>Operations Analyst</small></div></div></aside><main>{children}</main></body></html>}

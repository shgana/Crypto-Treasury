"""Source-specific parsing lives only here; the rest of the app consumes CanonicalPosition."""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CanonicalPosition:
    asset: str; quantity: float; usd_value: float; source: str; account: str; venue: str; timestamp: datetime; raw_data: dict

class SourceAdapter:
    def normalize(self, record: dict) -> CanonicalPosition: raise NotImplementedError

class InternalLedgerAdapter(SourceAdapter):
    def normalize(self, r): return CanonicalPosition(r["symbol"], r["qty"], r["qty"] * r["book_price"], "Internal Ledger", r["account_id"], "Internal Ledger", r["as_of"], r)
class ExchangeAdapter(SourceAdapter):
    def normalize(self, r):
        qty = r["available_balance"] + r["locked_balance"]
        return CanonicalPosition(r["currency"], qty, qty * r["mark_price"], r["exchange"], r["account"], r["exchange"], r["as_of"], r)
class CustodianAdapter(SourceAdapter):
    def normalize(self, r): return CanonicalPosition(r["asset_code"], r["position_quantity"], r["usd_value"], "Custodian A", r["account"], "Custodian A", r["as_of"], r)
class WalletAdapter(SourceAdapter):
    def normalize(self, r): return CanonicalPosition(r["token"], r["balance"], r["balance"] * r["mark_price"], "On-chain Wallet", r["wallet_address"], r["chain"], r["snapshot_time"], r)

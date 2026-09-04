from datetime import datetime
from backend.adapters import InternalLedgerAdapter, ExchangeAdapter, CustodianAdapter, WalletAdapter

NOW=datetime(2026,1,1)
def test_each_source_normalizes_to_canonical_shape():
    records=[
      (InternalLedgerAdapter(),{"symbol":"BTC","qty":2,"book_price":100,"account_id":"a","as_of":NOW}),
      (ExchangeAdapter(),{"currency":"ETH","available_balance":2,"locked_balance":1,"mark_price":100,"exchange":"Exchange A","account":"a","as_of":NOW}),
      (CustodianAdapter(),{"asset_code":"USDC","position_quantity":2,"usd_value":2,"account":"a","as_of":NOW}),
      (WalletAdapter(),{"token":"SOL","balance":2,"mark_price":100,"chain":"Solana","wallet_address":"0x1","snapshot_time":NOW}),
    ]
    for adapter,record in records:
        p=adapter.normalize(record); assert p.asset and p.quantity > 0 and p.usd_value > 0 and p.raw_data == record

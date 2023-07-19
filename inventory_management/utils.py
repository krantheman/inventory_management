import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum


@frappe.whitelist()
def get_item_stock(item, warehouse):
    StockLedgerEntry = DocType("Stock Ledger Entry")
    item_stock = (
        frappe.qb.from_(StockLedgerEntry)
        .where(
            (StockLedgerEntry.item == item) & (StockLedgerEntry.warehouse == warehouse)
        )
        .select(Sum(StockLedgerEntry.qty_change).as_("value"))
    ).run(as_dict=True)
    return item_stock[0].value or 0


@frappe.whitelist()
def get_valuation_rate(item, warehouse):
    entries = frappe.db.get_list(
        "Stock Ledger Entry",
        fields=["valuation_rate", "qty_change"],
        filters={
            "item": item,
            "warehouse": warehouse,
            "qty_change": [">", "0"],
        },
    )
    if len(entries) == 0:
        return None
    numerator = denominator = 0
    for entry in entries:
        numerator += entry.qty_change * entry.valuation_rate
        denominator += entry.qty_change
    return numerator / denominator

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


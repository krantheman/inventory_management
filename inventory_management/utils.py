import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum


@frappe.whitelist()
def get_item_stock(item, warehouse):
    SLE = DocType("Stock Ledger Entry")
    item_stock = (
        frappe.qb.from_(SLE)
        .where((SLE.item == item) & (SLE.warehouse == warehouse))
        .select(Sum(SLE.qty_change))
    ).run()
    return item_stock[0][0] or 0


@frappe.whitelist()
def get_valuation_rate(item, warehouse):
    doc = frappe.get_last_doc(
        "Stock Ledger Entry", filters={"item": item, "warehouse": warehouse}
    )
    return doc.valuation_rate if doc else 0


@frappe.whitelist()
def get_default_warehouse(item):
    return frappe.db.get_value("Item", item, "default_warehouse")

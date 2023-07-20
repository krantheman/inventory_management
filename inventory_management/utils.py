import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum


SLE = DocType("Stock Ledger Entry")


@frappe.whitelist()
def get_item_stock(item, warehouse):
    item_stock = (
        frappe.qb.from_(SLE)
        .where((SLE.item == item) & (SLE.warehouse == warehouse))
        .select(Sum(SLE.qty_change))
    ).run()
    return item_stock[0][0] or 0


@frappe.whitelist()
def get_valuation_rate(item, warehouse):
    valuation_rate = (
        frappe.qb.from_(SLE)
        .where((SLE.item == item) & (SLE.warehouse == warehouse) & (SLE.qty_change > 0))
        .select((Sum(SLE.qty_change * SLE.valuation_rate) / Sum(SLE.qty_change)))
    ).run()
    return valuation_rate[0][0]

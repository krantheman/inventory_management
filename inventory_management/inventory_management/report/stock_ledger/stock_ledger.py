# Copyright (c) 2023, krantheman and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns = [
        {
            "fieldname": "date",
            "label": "Posting Date",
            "fieldtype": "date",
            "options": "Posting Date",
        },
        {
            "fieldname": "time",
            "label": "Posting Time",
            "fieldtype": "time",
            "options": "Posting Time",
        },
        {"fieldname": "item", "label": "Item", "fieldtype": "Link", "options": "Item"},
        {
            "fieldname": "warehouse",
            "label": "Warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
        },
        {
            "fieldname": "qty_in",
            "label": "Quantity In",
            "fieldtype": "int",
            "options": "Quantity In",
        },
        {
            "fieldname": "qty_out",
            "label": "Quantity Out",
            "fieldtype": "int",
            "options": "Quantity Out",
        },
        {
            "fieldname": "balance_qty",
            "label": "Balance Quantity",
            "fieldtype": "int",
            "options": "Balance Quantity",
        },
        {
            "fieldname": "valuation_rate",
            "label": "Valuation Rate",
            "fieldtype": "float",
            "options": "Valuation Rate",
        },
        {
            "fieldname": "value_change",
            "label": "Value Change",
            "fieldtype": "float",
            "options": "Value Change",
        },
        {
            "fieldname": "balance_value",
            "label": "Balance Value",
            "fieldtype": "float",
            "options": "Balance Value",
        },
    ]

    entries = frappe.db.get_all(
        "Stock Ledger Entry",
        ["date", "time", "item", "warehouse", "qty_change", "valuation_rate"],
        filters,
        order_by="date",
    )
    update_entries(entries)

    return map(lambda x: {**x, "width": 120}, columns), entries


def update_entries(entries):
    balance_qty = {}
    balance_value = {}
    for entry in entries:
        entry.time = str(entry.time).split(".")[0]
        entry.qty_in = entry.qty_change if entry.qty_change > 0 else 0
        entry.qty_out = entry.qty_change if entry.qty_change < 0 else 0
        entry.value_change = entry.qty_change * entry.valuation_rate
        key = f"{entry.item}-{entry.warehouse}"
        if key in balance_qty:
            balance_qty[key] += entry.qty_change
            balance_value[key] += entry.value_change
        else:
            balance_qty[key] = entry.qty_change
            balance_value[key] = entry.value_change
        entry.balance_qty = balance_qty[key]
        entry.balance_value = balance_value[key]
        entry.valuation_rate = "{:.2f}".format(entry.valuation_rate)
        entry.value_change = "{:.2f}".format(entry.value_change)
        entry.balance_value = "{:.2f}".format(entry.balance_value)

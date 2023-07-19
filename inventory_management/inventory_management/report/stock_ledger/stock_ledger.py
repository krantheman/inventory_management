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
            "fieldname": "qty_change",
            "label": "Quantity Change",
            "fieldtype": "int",
            "options": "Quantity Change",
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

    data = frappe.db.get_all(
        "Stock Ledger Entry",
        ["date", "time", "item", "warehouse", "qty_change", "valuation_rate"],
        order_by="date",
        filters=format_filters(filters),
    )
    format_data(data)

    return map(lambda x: {**x, "width": 134}, columns), data


def format_data(data):
    balance_qty = {}
    balance_value = {}
    for row in data:
        row.time = str(row.time).split(".")[0]  # remove milliseconds
        row.value_change = row.qty_change * row.valuation_rate
        key = f"{row.item}-{row.warehouse}"
        if key in balance_qty:
            balance_qty[key] += row.qty_change
            balance_value[key] += row.value_change
        else:
            balance_qty[key] = row.qty_change
            balance_value[key] = row.value_change
        row.balance_qty = balance_qty[key]
        row.balance_value = balance_value[key]
        # Format to two decimal places
        row.valuation_rate = "{:.2f}".format(row.valuation_rate)
        row.value_change = "{:.2f}".format(row.value_change)
        row.balance_value = "{:.2f}".format(row.balance_value)


def format_filters(filters):
    from_date = "1900-01-01"
    to_date = "2100-01-01"
    applied_filters = {}
    if filters.from_date:
        from_date = filters.from_date
    if filters.to_date:
        to_date = filters.to_date
    applied_filters["date"] = ["between", [from_date, to_date]]
    if filters.item:
        applied_filters["item"] = filters.item
    if filters.warehouse:
        applied_filters["warehouse"] = filters.warehouse
    if filters.type == "Incoming":
        applied_filters["qty_change"] = [">", 0]
    elif filters.type == "Outgoing":
        applied_filters["qty_change"] = ["<", 0]
    return applied_filters

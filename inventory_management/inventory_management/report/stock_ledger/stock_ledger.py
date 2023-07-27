# Copyright (c) 2023, krantheman and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt


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
            "fieldname": "in_out_rate",
            "label": "In/Out Rate",
            "fieldtype": "float",
            "options": "In/Out Rate",
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
        [
            "date",
            "time",
            "item",
            "warehouse",
            "qty_change",
            "in_out_rate",
            "valuation_rate",
            "stock_entry",
        ],
        order_by="creation",
        filters=format_filters(filters),
    )
    format_data(data)

    return map(lambda x: {**x, "width": 121}, columns), data


def format_data(data):
    balance_qty = {}
    balance_value = {}
    for row in data:
        format_time(row)
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
        format_decimals(row)


def format_filters(filters):
    applied_filters = {}
    add_date_filter(applied_filters, filters)
    add_item_filter(applied_filters, filters)
    add_warehouse_filter(applied_filters, filters)
    add_type_filter(applied_filters, filters)
    add_stock_entry_filter(applied_filters, filters)
    return applied_filters


def add_date_filter(applied_filters, filters):
    from_date = "1900-01-01"
    to_date = "2100-01-01"
    if filters.from_date:
        from_date = filters.from_date
    if filters.to_date:
        to_date = filters.to_date
    applied_filters["date"] = ["between", [from_date, to_date]]


def add_item_filter(applied_filters, filters):
    if filters.item:
        applied_filters["item"] = filters.item


def add_warehouse_filter(applied_filters, filters):
    if filters.warehouse:
        applied_filters["warehouse"] = filters.warehouse


def add_type_filter(applied_filters, filters):
    if filters.type == "Incoming":
        applied_filters["qty_change"] = [">", 0]
    elif filters.type == "Outgoing":
        applied_filters["qty_change"] = ["<", 0]


def add_stock_entry_filter(applied_filters, filters):
    if filters.stock_entry:
        applied_filters["stock_entry"] = filters.stock_entry


def format_time(entry):
    entry.time = str(entry.time).split(".")[0]  # remove milliseconds


def format_decimals(entry):
    entry.valuation_rate = flt(entry.valuation_rate, 2)
    entry.value_change = flt(entry.value_change, 2)
    entry.balance_value = flt(entry.balance_value, 2)

# Copyright (c) 2023, krantheman and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Max, Concat
from pypika.terms import Case


SLE = DocType("Stock Ledger Entry")


def execute(filters=None):
    columns = [
        {"fieldname": "item", "label": "Item", "fieldtype": "Link", "options": "Item"},
        {
            "fieldname": "warehouse",
            "label": "Warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
        },
        {
            "fieldname": "balance_qty",
            "label": "Balance Quantity",
            "fieldtype": "int",
            "options": "Balance Quantity",
        },
        {
            "fieldname": "balance_value",
            "label": "Balance Value",
            "fieldtype": "float",
            "options": "Balance Value",
        },
        {
            "fieldname": "in_qty",
            "label": "In Quantity",
            "fieldtype": "int",
            "options": "In Quantity",
        },
        {
            "fieldname": "in_value",
            "label": "In Value",
            "fieldtype": "float",
            "options": "In Value",
        },
        {
            "fieldname": "out_qty",
            "label": "Out Quantity",
            "fieldtype": "int",
            "options": "Out Quantity",
        },
        {
            "fieldname": "out_value",
            "label": "Out Value",
            "fieldtype": "float",
            "options": "Out Value",
        },
        {
            "fieldname": "valuation_rate",
            "label": "Valuation Rate",
            "fieldtype": "float",
            "options": "Valuation Rate",
        },
    ]

    query = frappe.qb.from_(SLE)
    query = add_filters(query, filters)
    query = update_query(query)
    data = query.run(as_dict=True)
    format_data(data)

    return map(lambda x: {**x, "width": 134}, columns), data


def add_filters(query, filters):
    if filters.from_date:
        query = query.where(SLE.date >= filters.from_date)
    if filters.to_date:
        query = query.where(SLE.date <= filters.to_date)
    if filters.item:
        query = query.where(SLE.item == filters.item)
    if filters.warehouse:
        query = query.where(SLE.warehouse == filters.warehouse)
    return query


def update_query(query):
    latest_date_query = (
        frappe.qb.from_(SLE)
        .select(
            SLE.item,
            SLE.warehouse,
            Max(Concat(SLE.date, " ", SLE.time)).as_("date_time"),
        )
        .groupby(SLE.item, SLE.warehouse)
    )

    latest_valuation_rate_query = (
        frappe.qb.from_(SLE)
        .inner_join(latest_date_query)
        .on(
            SLE.item == latest_date_query.item
            and SLE.warehouse == latest_date_query.warehouse
            and Concat(SLE.date, " ", SLE.time) == latest_date_query.date_time
        )
        .select(SLE.item, SLE.warehouse, SLE.valuation_rate)
    )

    return (
        query.groupby(SLE.item, SLE.warehouse)
        .left_join(latest_valuation_rate_query)
        .on_field("item", "warehouse")
        .select(
            SLE.item,
            SLE.warehouse,
            Sum(SLE.qty_change).as_("balance_qty"),
            Sum(SLE.qty_change * SLE.valuation_rate).as_("balance_value"),
            Sum(in_qty()).as_("in_qty"),
            Sum(in_value()).as_("in_value"),
            Sum(out_qty()).as_("out_qty"),
            Sum(out_value()).as_("out_value"),
            latest_valuation_rate_query.valuation_rate,
        )
    )


def in_qty():
    return Case().when(SLE.qty_change > 0, SLE.qty_change).else_(0)


def out_qty():
    return Case().when(SLE.qty_change < 0, SLE.qty_change).else_(0)


def in_value():
    return (
        Case()
        .when(
            SLE.qty_change > 0,
            SLE.qty_change * SLE.valuation_rate,
        )
        .else_(0)
    )


def out_value():
    return (
        Case()
        .when(
            SLE.qty_change < 0,
            SLE.qty_change * SLE.valuation_rate,
        )
        .else_(0)
    )


def format_data(data):
    for row in data:
        # Format to two decimal places
        row.balance_value = "{:.2f}".format(row.balance_value)
        row.in_value = "{:.2f}".format(row.in_value)
        row.out_value = "{:.2f}".format(row.out_value)
        row.valuation_rate = "{:.2f}".format(row.valuation_rate)
# Copyright (c) 2023, krantheman and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum
from frappe.model.document import Document
from inventory_management.utils import get_item_stock


class StockEntry(Document):
    def on_submit(self):
        if self.type == "Transfer":
            self.submit_transfer()
        elif self.type == "Consume":
            self.submit_consume()
        else:
            self.submit_receipt()

    def on_cancel(self):
        if self.type == "Transfer":
            self.cancel_transfer()
        elif self.type == "Consume":
            self.cancel_consume()
        else:
            self.cancel_receipt()

    def submit_transfer(self):
        self.validate_item_stock()
        for d in self.items:
            validate_transfer(d)
            validate_value(d.qty, "Quantity")
            validate_value(d.rate, "Rate")
            create_stock_ledger_entry(
                self.name, d.item, d.rate, d.src_warehouse, -abs(d.qty)
            )
            create_stock_ledger_entry(self.name, d.item, d.rate, d.tgt_warehouse, d.qty)

    def submit_consume(self):
        self.validate_item_stock()
        for d in self.items:
            validate_consume(d)
            validate_value(d.qty, "Quantity")
            validate_value(d.rate, "Rate")
            d.tgt_warehouse = None
            create_stock_ledger_entry(
                self.name, d.item, d.rate, d.src_warehouse, -abs(d.qty)
            )

    def submit_receipt(self):
        for d in self.items:
            validate_receipt(d)
            validate_value(d.qty, "Quantity")
            validate_value(d.rate, "Rate")
            d.src_warehouse = None
            create_stock_ledger_entry(self.name, d.item, d.rate, d.tgt_warehouse, d.qty)

    def cancel_transfer(self):
        self.validate_item_stock(is_cancel=True)
        delete_stock_ledger_entries(self.name)
        # for d in self.items:
        #     create_stock_ledger_entry(
        #         self.name, d.item, d.rate, d.tgt_warehouse, -abs(d.qty)
        #     )
        #     create_stock_ledger_entry(self.name, d.item, d.rate, d.src_warehouse, d.qty)

    def cancel_consume(self):
        delete_stock_ledger_entries(self.name)
        # for d in self.items:
        #     create_stock_ledger_entry(self.name, d.item, d.rate, d.src_warehouse, d.qty)

    def cancel_receipt(self):
        self.validate_item_stock(is_cancel=True)
        delete_stock_ledger_entries(self.name)
        # for d in self.items:
        #     create_stock_ledger_entry(
        #         self.name, d.item, d.rate, d.tgt_warehouse, -abs(d.qty)
        #     )

    def group_items_by_warehouse(self, is_tgt_warehouse):
        grouped = {}
        for d in self.items:
            warehouse = d.tgt_warehouse if is_tgt_warehouse else d.src_warehouse
            key = f"{d.item}-{warehouse}"
            if key not in grouped:
                grouped[key] = {
                    "item": d.item,
                    "warehouse": warehouse,
                    "qty": 0,
                }
            grouped[key]["qty"] += d.qty
        return list(grouped.values())

    def validate_item_stock(self, is_cancel=False):
        is_tgt_warehouse = True if is_cancel else False
        grouped_items = self.group_items_by_warehouse(is_tgt_warehouse)
        for d in grouped_items:
            item_stock = get_item_stock(d["item"], d["warehouse"])
            if item_stock < d["qty"]:
                frappe.throw_(
                    "There is not enough stock of item {0} available at {1} for this operation".format(
                        d["item"], d["warehouse"]
                    )
                )


def create_stock_ledger_entry(stock_entry, item, rate, warehouse, qty_change):
    stock_ledger_entry = frappe.get_doc(
        {
            "doctype": "Stock Ledger Entry",
            "item": item,
            "warehouse": warehouse,
            "qty_change": qty_change,
            "in_out_rate": rate,
            "valuation_rate": calculate_valuation_rate(
                item, rate, warehouse, qty_change
            ),
            "stock_entry": stock_entry,
        }
    )
    stock_ledger_entry.insert()


def delete_stock_ledger_entries(stock_entry):
    sles = frappe.db.get_list(
        "Stock Ledger Entry",
        filters={"stock_entry": stock_entry},
    )
    for sle in sles:
        frappe.delete_doc("Stock Ledger Entry", sle.name)


def validate_transfer(item):
    if not (item.src_warehouse and item.tgt_warehouse):
        frappe.throw_(
            "Source warehouse as well as target warehouse required in stock entries of type Transfer"
        )
    if item.src_warehouse == item.tgt_warehouse:
        frappe.throw_("Source and target warehouse cannot be the same")


def validate_consume(item):
    if not item.src_warehouse:
        frappe.throw_("Source warehouse required in stock entries of type Consume")


def validate_receipt(item):
    if not item.tgt_warehouse:
        frappe.throw_("Target warehouse required in stock entries of type Receipt")


def validate_value(value, text):
    if value <= 0:
        frappe.throw_("{0} must be greater than zero".format(text))


def calculate_valuation_rate(item, rate, warehouse, qty_change):
    SLE = DocType("Stock Ledger Entry")
    old_valuation_rate = (
        frappe.qb.from_(SLE)
        .where((SLE.item == item) & (SLE.warehouse == warehouse))
        .select(
            Sum(SLE.qty_change * SLE.in_out_rate).as_("balance_value"),
            Sum(SLE.qty_change).as_("total_qty_change"),
        )
    ).run(as_dict=True)[0]
    if not old_valuation_rate.balance_value:
        old_valuation_rate.balance_value = 0
        old_valuation_rate.total_qty_change = 0
    numerator = old_valuation_rate.balance_value + rate * qty_change
    denominator = old_valuation_rate.total_qty_change + qty_change
    new_valuation_rate = numerator / denominator if denominator else 0
    return new_valuation_rate

# Copyright (c) 2023, krantheman and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Item(Document):
    def before_save(self):
        if self.is_receipt():
            self.validate_receipt()

    def after_insert(self):
        if self.is_receipt():
            self.create_stock_ledger_entry()

    def is_receipt(self):
        return self.opening_warehouse or self.opening_rate or self.opening_qty

    def validate_receipt(self):
        self.validate_field(self.opening_warehouse, "warehouse")
        self.validate_field(self.opening_qty, "quantity")
        self.validate_field(self.opening_rate, "valuation rate")

    def validate_field(self, field, str_field):
        if not field:
            frappe.throw(
                "Enter valid opening {} for receipt stock entry".format(str_field)
            )

    def create_stock_ledger_entry(self):
        stock_ledger_entry = frappe.get_doc(
            {
                "doctype": "Stock Ledger Entry",
                "item": self.name,
                "warehouse": self.opening_warehouse,
                "qty_change": self.opening_qty,
                "valuation_rate": self.opening_rate,
            }
        )
        stock_ledger_entry.insert()

# Copyright (c) 2023, krantheman and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StockEntry(Document):
    def validate(self):
        if self.type == "Receipt":
            self.validate_receipt()
        elif self.type == "Consume":
            self.validate_consume()
        if self.type == "Transfer":
            self.validate_transfer()

    def validate_receipt(self):
        for item in self.items:
            if item.src_warehouse:
                frappe.throw("Receipt entry cannot have source warehouse")

    def validate_consume(self):
        for item in self.items:
            if item.tgt_warehouse:
                frappe.throw("Consume entry cannot have target warehouse")

    def validate_transfer(self):
        for item in self.items:
            if not (item.src_warehouse and item.tgt_warehouse):
                frappe.throw(
                    "Transfer entry must have source as well as target warehouse"
                )
            if item.src_warehouse == item.tgt_warehouse:
                frappe.throw("Source and target warehouse cannot be the same")

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

    def before_save(self):
        print(self.items)
        for item in self.items:
            if item.src_warehouse:
                item_stock = item.get_stock()
                if not item_stock:
                    frappe.throw(
                        "There is not enough stock of {} available at {} for this operation".format(
                            item.item, item.src_warehouse
                        )
                    )

    def on_submit(self):
        for item in self.items:
            if item.src_warehouse:
                item_stock = item.get_stock()
                if not item_stock:
                    frappe.throw(
                        "There is not enough stock of {} available at {} for this operation".format(
                            item.item, item.src_warehouse
                        )
                    )
                # item.create_stock_ledger_entry(is_tgt_warehouse=False)
            if item.tgt_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=True)

    def on_cancel(self):
        for item in self.items:
            if item.tgt_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=True, is_cancel=True)
            if item.src_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=False, is_cancel=True)

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

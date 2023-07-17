# Copyright (c) 2023, krantheman and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StockEntry(Document):
    def on_submit(self):
        for item in self.items:
            if item.src_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=False)
            if item.tgt_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=True)

    def on_cancel(self):
        for item in self.items:
            if item.tgt_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=True, is_cancel=True)
            if item.src_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=False, is_cancel=True)

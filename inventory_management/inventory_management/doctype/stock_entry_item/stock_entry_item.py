# Copyright (c) 2023, krantheman and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StockEntryItem(Document):
    def create_stock_ledger_entry(self, is_tgt_warehouse, is_cancel=False):
    # param is_tgt_warehouse: true if target warehouse, false if source warehouse
    # param is_cancel: true while cancelling form, false while submitting form
        if not is_cancel:
            if is_tgt_warehouse:
                self._create_stock_ledger_entry(self.tgt_warehouse, self.qty)
            else:
                self._create_stock_ledger_entry(self.src_warehouse, -abs(self.qty))
        else:
            if is_tgt_warehouse:
                self._create_stock_ledger_entry(self.tgt_warehouse, -abs(self.qty))
            else:
                self._create_stock_ledger_entry(self.src_warehouse, self.qty)

    def _create_stock_ledger_entry(self, warehouse, qty_change):
        ledger_entry = frappe.get_doc(
            {
                "doctype": "Stock Ledger Entry",
                "item": self.item,
                "warehouse": warehouse,
                "qty_change": qty_change,
                "valuation_rate": self.rate,
            }
        )
        ledger_entry.insert()

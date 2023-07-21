# Copyright (c) 2023, krantheman and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum


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
        stock_ledger_entry = frappe.get_doc(
            {
                "doctype": "Stock Ledger Entry",
                "item": self.item,
                "warehouse": warehouse,
                "qty_change": qty_change,
                "valuation_rate": self.rate,
            }
        )
        stock_ledger_entry.insert()

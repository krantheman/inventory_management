# Copyright (c) 2023, krantheman and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from inventory_management.utils import get_item_stock


class StockEntry(Document):
    def on_submit(self):
        if self.type == "Consume" or self.type == "Transfer":
            self.validate_item_stock()
        for d in self.items:
            if d.src_warehouse:
                d.create_stock_ledger_entry(is_tgt_warehouse=False)
            if d.tgt_warehouse:
                d.create_stock_ledger_entry(is_tgt_warehouse=True)

    def on_cancel(self):
        if self.type == "Receipt" or self.type == "Transfer":
            self.validate_item_stock(is_cancel=True)
        for d in self.items:
            if d.tgt_warehouse:
                d.create_stock_ledger_entry(is_tgt_warehouse=True, is_cancel=True)
            if d.src_warehouse:
                d.create_stock_ledger_entry(is_tgt_warehouse=False, is_cancel=True)

    def validate_item_stock(self, is_cancel=False):
        is_tgt_warehouse = True if is_cancel else False
        grouped_items = self.group_items_by_warehouse(is_tgt_warehouse)
        for d in grouped_items:
            item_stock = get_item_stock(d["item"], d["warehouse"])
            if item_stock < d["qty"]:
                frappe.throw(
                    f"There is not enough stock of item {d['item']} available at {d['warehouse']} for this operation"
                )

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

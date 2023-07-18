# Copyright (c) 2023, krantheman and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from inventory_management.inventory_management.utils import validate_item_stock


class StockEntry(Document):
    def on_submit(self):
        for item in self.items:
            if item.src_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=False)
            if item.tgt_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=True)

    def on_cancel(self):
        grouped_items = self.group_items_by_tgt_warehouse()
        validate_item_stock(grouped_items)
        for item in self.items:
            if item.tgt_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=True, is_cancel=True)
            if item.src_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=False, is_cancel=True)

    def group_items_by_tgt_warehouse(self):
        grouped = {}
        for obj in self.items:
            key = f"{obj.item}-{obj.tgt_warehouse}"
            if key not in grouped:
                grouped[key] = {
                    "item": obj.item,
                    "warehouse": obj.tgt_warehouse,
                    "qty": 0,
                }
            grouped[key]["qty"] += obj.qty
        return list(grouped.values())

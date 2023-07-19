# Copyright (c) 2023, krantheman and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from inventory_management.utils import get_item_stock


class StockEntry(Document):
    def on_submit(self):
        if self.type == "Consume" or self.type == "Transfer":
            self.validate_item_stock()
        for item in self.items:
            if item.src_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=False)
            if item.tgt_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=True)

    def on_cancel(self):
        if self.type == "Receipt" or self.type == "Transfer":
            self.validate_item_stock(is_cancel=True)
        for item in self.items:
            if item.tgt_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=True, is_cancel=True)
            if item.src_warehouse:
                item.create_stock_ledger_entry(is_tgt_warehouse=False, is_cancel=True)

    def validate_item_stock(self, is_cancel=False):
        is_tgt_warehouse = True if is_cancel else False
        grouped_items = self.group_items_by_warehouse(is_tgt_warehouse)
        for obj in grouped_items:
            item_stock = get_item_stock(obj["item"], obj["warehouse"])
            if item_stock < obj["qty"]:
                frappe.throw(
                    f"There is not enough stock of item {obj['item']} available at {obj['warehouse']} for this operation"
                )

    def group_items_by_warehouse(self, is_tgt_warehouse):
        grouped = {}
        for obj in self.items:
            warehouse = obj.tgt_warehouse if is_tgt_warehouse else obj.src_warehouse
            key = f"{obj.item}-{warehouse}"
            if key not in grouped:
                grouped[key] = {
                    "item": obj.item,
                    "warehouse": warehouse,
                    "qty": 0,
                }
            grouped[key]["qty"] += obj.qty
        return list(grouped.values())

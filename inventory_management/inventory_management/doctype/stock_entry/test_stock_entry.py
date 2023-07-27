# Copyright (c) 2023, krantheman and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from inventory_management.utils import get_valuation_rate


def create_warehouses():
    if frappe.flags.test_warehouses_created:
        return
    frappe.get_doc(
        {
            "doctype": "Warehouse",
            "title": "Warehouse A",
        }
    ).insert()

    frappe.get_doc(
        {
            "doctype": "Warehouse",
            "title": "Warehouse B",
        }
    ).insert()

    frappe.flags.test_warehouses_created = True


def create_items():
    if frappe.flags.test_items_created:
        return
    frappe.get_doc(
        {
            "doctype": "Item",
            "code": "IA",
            "title": "Item A",
            "opening_warehouse": "Warehouse A",
            "opening_qty": 5,
            "opening_rate": 50,
        }
    ).insert()
    frappe.flags.test_items_created = True


def submit_receipt(qty, rate):
    stock_entry = frappe.get_doc(
        {
            "doctype": "Stock Entry",
            "type": "Receipt",
            "items": [
                {
                    "item": "IA",
                    "tgt_warehouse": "Warehouse A",
                    "qty": qty,
                    "rate": rate,
                },
            ],
        }
    )
    stock_entry.insert()
    stock_entry.submit()
    return stock_entry


def submit_consume(qty):
    stock_entry = frappe.get_doc(
        {
            "doctype": "Stock Entry",
            "type": "Consume",
            "items": [
                {
                    "item": "IA",
                    "src_warehouse": "Warehouse A",
                    "qty": qty,
                    "rate": get_valuation_rate("IA", "Warehouse A"),
                },
            ],
        }
    )
    stock_entry.insert()
    stock_entry.submit()
    return stock_entry


def submit_transfer(qty):
    stock_entry = frappe.get_doc(
        {
            "doctype": "Stock Entry",
            "type": "Transfer",
            "items": [
                {
                    "item": "IA",
                    "src_warehouse": "Warehouse A",
                    "tgt_warehouse": "Warehouse B",
                    "qty": qty,
                    "rate": get_valuation_rate("IA", "Warehouse A"),
                },
            ],
        }
    )
    stock_entry.insert()
    stock_entry.submit()
    return stock_entry


class TestStockEntry(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        create_warehouses()
        create_items()

    def tearDown(self):
        frappe.set_user("Administrator")

    def test_stock_entry(self):
        receipt_entry = submit_receipt(5, 40)
        sle = frappe.get_last_doc(
            "Stock Ledger Entry", filters={"stock_entry": receipt_entry.name}
        )
        self.assertEqual(sle.valuation_rate, 45)
        self.assertEqual(sle.qty_change, 5)

        consume_entry = submit_consume(2)
        sle = frappe.get_last_doc(
            "Stock Ledger Entry", filters={"stock_entry": consume_entry.name}
        )
        self.assertEqual(sle.valuation_rate, 45)
        self.assertEqual(sle.qty_change, -2)

        receipt_entry = submit_receipt(2, 60)
        sle = frappe.get_last_doc(
            "Stock Ledger Entry", filters={"stock_entry": receipt_entry.name}
        )
        self.assertEqual(sle.valuation_rate, 48)
        self.assertEqual(sle.qty_change, 2)

        transfer_entry = submit_transfer(3)
        sle = frappe.get_list(
            "Stock Ledger Entry",
            fields=["valuation_rate", "qty_change"],
            filters={"stock_entry": transfer_entry.name},
        )
        self.assertEqual(sle[0].valuation_rate, 48)
        self.assertEqual(sle[0].qty_change, 3)
        self.assertEqual(sle[1].valuation_rate, 48)
        self.assertEqual(sle[1].qty_change, -3)

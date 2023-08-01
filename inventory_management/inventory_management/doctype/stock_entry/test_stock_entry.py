# Copyright (c) 2023, krantheman and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from inventory_management.utils import get_valuation_rate


class TestStockEntry(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        create_warehouses()
        create_items()

    def tearDown(self):
        frappe.set_user("Administrator")

    def test_stock_entry(self):
        (
            first_receipt_entry,
            consume_entry,
            second_receipt_entry,
            transfer_entry,
        ) = self.stock_entry_submission()
        self.stock_entry_cancellation(
            transfer_entry, second_receipt_entry, consume_entry, first_receipt_entry
        )

    def stock_entry_submission(self):
        first_receipt_entry = submit_receipt(5, 40)
        valuation_rate, qty_change = get_valuation_rate_and_qty_change(
            first_receipt_entry.name
        )
        # Opening Rate = 50 | Opening Qty = 5 | Original Valuation Rate = 50
        self.assertEqual(valuation_rate, 45)
        self.assertEqual(qty_change, 5)

        consume_entry = submit_consume(2)
        valuation_rate, qty_change = get_valuation_rate_and_qty_change(
            consume_entry.name
        )
        self.assertEqual(valuation_rate, 45)
        self.assertEqual(qty_change, -2)

        second_receipt_entry = submit_receipt(2, 60)
        valuation_rate, qty_change = get_valuation_rate_and_qty_change(
            second_receipt_entry.name
        )
        self.assertEqual(valuation_rate, 48)
        self.assertEqual(qty_change, 2)

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

        return first_receipt_entry, consume_entry, second_receipt_entry, transfer_entry

    def stock_entry_cancellation(
        self, transfer_entry, second_receipt_entry, consume_entry, first_receipt_entry
    ):
        transfer_entry.cancel()
        valuation_rate, qty_change = get_valuation_rate_and_qty_change(
            transfer_entry.name
        )
        self.assertEqual(valuation_rate, 48)
        self.assertEqual(qty_change, 3)

        second_receipt_entry.cancel()
        valuation_rate, qty_change = get_valuation_rate_and_qty_change(
            second_receipt_entry.name
        )
        self.assertEqual(valuation_rate, 45)
        self.assertEqual(qty_change, -2)

        consume_entry.cancel()
        valuation_rate, qty_change = get_valuation_rate_and_qty_change(
            consume_entry.name
        )
        self.assertEqual(valuation_rate, 45)
        self.assertEqual(qty_change, 2)

        first_receipt_entry.cancel()
        valuation_rate, qty_change = get_valuation_rate_and_qty_change(
            first_receipt_entry.name
        )
        self.assertEqual(valuation_rate, 50)
        self.assertEqual(qty_change, -5)


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


def get_valuation_rate_and_qty_change(stock_entry_name):
    return frappe.db.get_value(
        "Stock Ledger Entry",
        {"stock_entry": stock_entry_name},
        ["valuation_rate", "qty_change"],
    )

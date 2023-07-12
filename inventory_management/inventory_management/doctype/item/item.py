# Copyright (c) 2023, krantheman and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Item(Document):
    def before_save(self):
        receipt = self.opening_warehouse or self.opening_rate or self.opening_qty
        if receipt:
            self.validate_receipt()

    def validate_receipt(self):
        self.validate_field(self.opening_warehouse, "warehouse")
        self.validate_field(self.opening_qty, "quantity")
        self.validate_field(self.opening_rate, "valuation rate")

    def validate_field(self, field, str_field):
        if not field:
            frappe.throw("Enter valid opening {} for receipt".format(str_field))

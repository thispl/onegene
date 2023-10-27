# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

class OpenOrder(Document):
    def on_update(self):
        order_open = frappe.get_doc("Open Order",{"sales_order_number":self.sales_order_number})
        from erpnext.controllers.accounts_controller import update_child_qty_rate
        get_so_qty = []
        for i in order_open.open_order_table:
            get_so_qty.append(frappe._dict({"item_code":i.item_code,"qty":i.qty,"warehouse":i.warehouse,"item_name":i.item_name,"rate":i.rate,"amount":i.amount}))
        json_data = json.dumps(get_so_qty)
        update_child_qty_rate("Sales Order", json_data, order_open.sales_order_number)

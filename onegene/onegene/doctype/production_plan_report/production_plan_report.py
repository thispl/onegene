# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.model.document import Document
import frappe
import requests
from datetime import date
import erpnext
import json
from frappe.utils import now
from frappe import throw,_
from frappe.utils import flt
from frappe.utils import (
    add_days,
    ceil,
    cint,
    comma_and,
    flt,
    get_link_to_form,
    getdate,
    now_datetime,
    datetime,get_first_day,get_last_day,
    nowdate,
    today,
)
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days,date_diff
from datetime import date, datetime, timedelta
import datetime as dt
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Union

class ProductionPlanReport(Document):
	@frappe.whitelist()
	def create_mr(self):
		data = []
		bom_list = []
		bom = frappe.db.get_value("BOM", {'item': self.item}, ['name'])
		bom_list.append(frappe._dict({"bom": bom, "qty": self.today_prod_plan}))
		for k in bom_list:
			self.get_exploded_items(k["bom"], data, k["qty"], bom_list)
		unique_items = {}
		for item in data:
			item_code = item['item_code']
			qty = item['qty']
			if item_code in unique_items:
				unique_items[item_code]['qty'] += qty
			else:
				unique_items[item_code] = item
			combined_items_list = list(unique_items.values())
		if not frappe.db.exists("Material Request",{'custom_production_plan':self.name,'docstatus': ["in", ["Draft", "Submitted"]]}):
			doc = frappe.new_doc("Material Request")
			doc.material_request_type = "Material Transfer"
			doc.transaction_date = self.date
			doc.schedule_date = self.date
			doc.custom_production_plan = self.name
			doc.set_from_warehouse = "PPS Store - O"
			doc.set_warehouse = "Stores - O"
			pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse != 'Stores - O' """%('RAT0TB1588124STR'),as_dict=1)[0].qty or 0
			sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse = 'Stores - O' """%('RAT0TB1588124STR'),as_dict=1)[0].qty or 0
			for h in combined_items_list:
				doc.append("items",{
					'item_code':h["item_code"],
					'schedule_date':self.date,
					'qty':ceil(h["qty"]),
					'custom_current_req_qty':ceil(h["qty"]),
					'custom_req_per_qty':(h["qty"]/self.today_prod_plan),
					'custom_stock_qty_copy':pps,
					'custom_shop_floor_stock':sfs,
					'uom': "Nos"
				})
			doc.save()
			name = [
				"""<a href="/app/Form/Material Request/{0}">{1}</a>""".format(doc.name,doc.name)
			]
			frappe.msgprint(_("Material Request - {0} created").format(comma_and(name)))
		else:
			frappe.msgprint("Material Request already Exists")
			

	def get_exploded_items(self, bom, data, qty, skip_list):
		exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no", "item_code", "item_name", "description", "uom"])
		for item in exploded_items:
			item_code = item['item_code']
			if item_code in skip_list:
				continue
			item_qty = frappe.utils.flt(item['qty']) * qty
			stock = frappe.db.get_value("Bin", {'item_code': item_code}, ['actual_qty']) or 0
			to_order = item_qty - stock
			if to_order < 0:
				to_order = 0
			data.append(
                {
                    "item_code": item_code,
                    # "item_name": item['item_name'],
                    # "bom": item['bom_no'],
                    # "uom": item['uom'],
                    "qty": item_qty,
                    # "stock_qty": frappe.db.get_value("Bin", {'item_code': item_code}, ['actual_qty']) or 0,
                    # "qty_to_order": to_order,
                    # "description": item['description'],
                }
            )
			if item['bom_no']:
				self.get_exploded_items(item['bom_no'], data, qty=item_qty, skip_list=skip_list)

@frappe.whitelist()
def create_mrr(name):
    doc_list = []
    consolidated_items = {}
    doc_name = json.loads(name)

    for doc_nam in doc_name:
        self = frappe.get_doc("Production Plan Report", doc_nam)
        data = []
        bom_list = []

        bom = frappe.db.get_value("BOM", {'item': self.item}, ['name'])
        bom_list.append(frappe._dict({"bom": bom, "qty": self.required_plan}))

        for k in bom_list:
            get_exploded_items(k["bom"], data, k["qty"], bom_list)

        unique_items = {}
        for item in data:
            item_code = item['item_code']
            qty = item['qty']
            if item_code in unique_items:
                unique_items[item_code]['qty'] += qty
            else:
                unique_items[item_code] = item
        combined_items_list = list(unique_items.values())
        doc_list.append(combined_items_list)

    for i in doc_list:
        for h in i:
            item_code = h["item_code"]
            qty = h["qty"]
            if item_code in consolidated_items:
                consolidated_items[item_code] += qty
            else:
                consolidated_items[item_code] = qty

    doc = frappe.new_doc("Material Request")
    doc.material_request_type = "Material Transfer"
    doc.transaction_date = frappe.utils.today()
    doc.schedule_date = frappe.utils.today()
    doc.set_from_warehouse = "PPS Store - O"
    doc.set_warehouse = "SFS Store - O"

    for item_code, qty in consolidated_items.items():
        uom = frappe.db.get_value("Item",item_code,'stock_uom')
        pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
                               where item_code = %s and warehouse != 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0
        sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin`
                               where item_code = %s and warehouse = 'SFS Store - O' """, (item_code), as_dict=1)[0].qty or 0

        sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
                              left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                              where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
                              and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
        today_req = sf[0].qty if sf else 0

        stock = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s """, (item_code), as_dict=1)[0].qty or 0
        req = qty - stock if stock else qty
        cur_req = req - sfs
        cal = sfs + today_req if today_req else 0

        req_qty = req - cal if cal <= req else 0
        if ceil(req) > 0:
            doc.append("items", {
                'item_code': item_code,
                'schedule_date': frappe.utils.today(),
                'qty': ceil(req),
                'custom_mr_qty': ceil(req),
                'custom_total_req_qty': ceil(qty),
                'custom_current_req_qty': ceil(cur_req),
                'custom_stock_qty_copy': pps,
                'custom_shop_floor_stock': sfs,
                'custom_requesting_qty': req_qty,
                'custom_today_req_qty': today_req,
                'uom': uom
            })
    doc.save()
    name = [
        """<a href="/app/Form/Material Request/{0}">{1}</a>""".format(doc.name, doc.name)
    ]
    frappe.msgprint(_("Material Request - {0} created").format(", ".join(name)))

def get_exploded_items(bom, data, qty, skip_list):
    exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},
                                    fields=["qty", "bom_no", "item_code", "item_name", "description", "uom"])
    for item in exploded_items:
        item_code = item['item_code']
        if item_code in skip_list:
            continue
        item_qty = frappe.utils.flt(item['qty']) * qty
        stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - O"},
                                    ['actual_qty']) or 0
        to_order = item_qty - stock if item_qty > stock else 0
        data.append({
            "item_code": item_code,
            "qty": item_qty,
        })
        if item['bom_no']:
            self.get_exploded_items(item['bom_no'], data, qty=item_qty, skip_list=skip_list)


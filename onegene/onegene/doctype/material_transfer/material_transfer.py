# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, getdate, add_days
from onegene.onegene.custom import get_year_code
from datetime import datetime, time


class MaterialTransfer(Document):
    def before_insert(self):
        self.fiscal_year = get_year_code()
        
    def validate(self):
        if not self.item:
            return

        zero_count = 0
        all_issued = True
        rows_to_remove = []

        for row in self.item:
            issued_qty = row.issued_qty or 0
            requested_qty = row.requested_qty or 0

            if issued_qty == 0:
                zero_count += 1
                rows_to_remove.append(row)

            if issued_qty < requested_qty:
                all_issued = False

        # if all rows are zero
        if zero_count == len(self.item):
            frappe.throw("Issued Qty cannot be zero for all rows")

        # remove rows where issued qty = 0
        for row in rows_to_remove:
            self.remove(row)


        # set status
        self.status = "Issued" if all_issued else "Partially Issued"

        user_roles = frappe.get_roles(frappe.session.user)
        material_request_owner = frappe.db.get_value("Material Request", self.material_request, "owner")
        if (frappe.session.user == material_request_owner):
            if "System Manager" not in user_roles:
                frappe.throw(f"Cannot transfer material against your own request <b>{self.material_request}</b>", title="Not Permitted")
                frappe.throw(f"உங்கள் சொந்த கோரிக்கைக்கு (<b>{self.material_request}</b>) எதிராக material transfer செய்ய முடியாது.", title="Not Permitted")


    def on_submit(self):
        self.custom_issued_by_on = now_datetime()
        
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = "Material Transfer"
        stock_entry.posting_date = self.posting_date
        stock_entry.from_warehouse = self.default_source_warehouse
        stock_entry.to_warehouse = self.default_target_warehouse
        stock_entry.material_request = self.material_request
        stock_entry.custom_material_transfer = self.name
        stock_entry.company = "WONJIN AUTOPARTS INDIA PVT.LTD."

        for item in self.item:
            stock_entry.append("items", {
                "item_code": item.item_code,
                "qty": item.issued_qty,
                "uom": item.uom,
                "s_warehouse": self.default_source_warehouse,
                "t_warehouse": item.target_warehouse,
                "material_request": self.material_request,
                "material_request_item": item.material_request_item,   # ✅ fixed here
                "custom_requesting_qty": item.requested_qty,
                "valuation_rate": 12,
                "allow_zero_valuation_rate": 1,
            })

        stock_entry.insert(ignore_permissions=True)
        stock_entry.submit()

        # update Material Request quantities
        from erpnext.stock.doctype.material_request.material_request import update_completed_and_requested_qty
        update_completed_and_requested_qty(stock_entry, "on_submit")
        
        frappe.db.sql("""
            UPDATE `tabMaterial Request`
            SET workflow_state = CASE
                WHEN status = 'Partially Received' THEN 'Partially Received'
                WHEN status = 'Transferred' THEN 'Received'
                ELSE 'Material Pending'
                END
            """)

    def on_cancel(self):
        stock_entry = frappe.db.get_value(
            "Stock Entry",
            {"custom_material_transfer": self.name, "docstatus": 1},  
        )
        
        if stock_entry:
            se = frappe.get_doc("Stock Entry", stock_entry)
            se.cancel()

        frappe.db.sql("""
            UPDATE `tabMaterial Request`
            SET workflow_state = CASE
                WHEN status = 'Partially Ordered' THEN 'Partially Received'
                WHEN status = 'Transferred' THEN 'Received'
                ELSE 'Material Pending'
                END
            """)
  

        
             
    


from frappe import _

@frappe.whitelist()
def make_material_transfer(material_request):
    material_request = frappe.get_doc("Material Request", material_request)

    total_requested_qty = sum([d.custom_requesting_qty for d in material_request.items])
    issued_qty = 0

    transfers = frappe.get_all(
        "Material Transfer",
        filters={"material_request": material_request.name, "docstatus": ["!=", "2"]},
        fields=["name"]
    )

    for t in transfers:
        transfer_doc = frappe.get_doc("Material Transfer", t.name)
        for d in transfer_doc.item:
            issued_qty += d.issued_qty or 0
    if issued_qty >= total_requested_qty:
        frappe.throw(_("You have already issued full quantity for this Material Request. Cannot create another Material Transfer."))
        frappe.throw(_("இந்த Material Request-க்கான முழு அளவையும் நீங்கள் ஏற்கனவே வழங்கிவிட்டீர்கள். மற்றொரு Material Transfer உருவாக்க முடியாது."))


    mt = frappe.new_doc("Material Transfer")
    mt.material_request = material_request.name
    mt.default_source_warehouse = material_request.set_from_warehouse
    mt.default_target_warehouse = "Shop Floor - WAIP"
    mt.requested_by = material_request.custom_requested_by
    mt.requester_name = material_request.custom_requester_name
    mt.requested_department = material_request.custom_department

    for row in material_request.items:
        already_issued = get_already_issued_qty(row.item_code)
        remaining_qty = (row.custom_requesting_qty or 0) - already_issued

    
        if remaining_qty <= 0:
            continue

        if remaining_qty < 0:
            frappe.throw(_(
                f"Item {row.item_code}: Already issued more than requested quantity."
            ))
            frappe.throw(_(
                f"Item {row.item_code}: கோரப்பட்ட அளவிற்கு மேல் ஏற்கனவே வழங்கப்பட்டுள்ளது."
            ))


        stock_qty = frappe.db.get_value("Bin", {"warehouse": material_request.set_from_warehouse, "item_code": row.item_code}, "actual_qty")
        child = mt.append("item", {})
        child.item_code = row.item_code
        child.item_name = row.item_name
        child.uom = row.uom
        child.stock_qty = stock_qty
        child.requested_qty = remaining_qty   
        child.source_warehouse = material_request.set_from_warehouse
        child.target_warehouse = "Shop Floor - WAIP"
        child.material_request = material_request.name
        child.material_request_item = row.name
        child.pack_size = row.custom_pack_size
        child.parent_bom = row.custom_parent_bom

    return mt


def get_already_issued_qty(material_request_item):
    issued = 0
    transfers = frappe.get_all(
        "Material Transfer",
        filters={"docstatus": ["!=", "2"]},
        fields=["name"]
    )
    for t in transfers:
        transfer_doc = frappe.get_doc("Material Transfer", t.name)
        for d in transfer_doc.item:
            if d.item_code == material_request_item:
                issued += d.issued_qty or 0
    return issued

@frappe.whitelist()
def check_material_request_status(material_request):
    material_request = frappe.get_doc("Material Request", material_request)
    total_requested_qty = sum([d.custom_requesting_qty for d in material_request.items])
    issued_qty = 0

    transfers = frappe.get_all(
        "Material Transfer",
        filters={"material_request": material_request.name, "docstatus": ["!=", "2"]},
        fields=["name"]
    )

    for t in transfers:
        transfer_doc = frappe.get_doc("Material Transfer", t.name)
        for d in transfer_doc.item:
            issued_qty += d.issued_qty or 0

    return issued_qty >= total_requested_qty


@frappe.whitelist()
def get_mt_table(name, source_warehouse):
    # Validate material request
    now = now_datetime()
    today = getdate()

    # Define 8:30 AM cutoff
    today_830 = datetime.combine(today, time(8, 30, 0))

    current_time = now
    cutoff_time = today_830

    if current_time > cutoff_time:
        # Current time is AFTER today's 8:30 AM
        start_datetime = f"{today} 08:31:00"
        end_datetime = f"{add_days(today, 1)} 08:30:00"
    else:
        # Current time is BEFORE today's 8:30 AM
        start_datetime = f"{add_days(today, -1)} 08:31:00"
        end_datetime = f"{today} 08:30:00"
        
    if frappe.db.exists("Material Request", 
        {
            "docstatus": 1,
            "material_request_type": "Material Transfer",
            "status": ["not in", ["Transferred", "Issued", "Cancelled", "Stopped"]],
            "creation": ["between", [start_datetime, end_datetime]],
            "name": name
        }):
        

        items = frappe.get_all(
            "Material Request Item",
            filters={"parent": name},
            fields=["name", "item_code", "item_name", "qty", "stock_uom", "parent", "custom_parent_bom", "ordered_qty"]
        )
        for item in items:
            stock_qty = frappe.db.get_value("Bin", {"warehouse": source_warehouse, "item_code": item.item_code}, "actual_qty")
            item["stock_qty"] = stock_qty
        return {"items": items}

def test_check():
    items = frappe.db.get_all("Item", {"custom_warehouse": "PPS Store - WAIP", "is_stock_item": 1}, "name")
    count = 0
    for item in items:
        stock = frappe.db.get_value("Bin", {"item_code": item.name, "warehouse": "PPS Store - WAIP"}, "actual_qty")
        if not stock:
            frappe.errprint(item.name)
            count += 1
    frappe.errprint(count)


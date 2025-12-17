import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Store Receipt"), "fieldtype": "HTML", "options": "Store Receipt", "fieldname": "store_receipt", "width": 200},
        {"label": _("Date"), "fieldtype": "HTML", "fieldname": "date", "width": 120},
        {"label": _("Quality Inspection"), "fieldtype": "Data", "options": "Quality Inspection", "fieldname": "quality_inspection", "width": 200},
        {"label": _("Inspection Date"), "fieldtype": "Date", "fieldname": "inspection_date", "width": 150, "inspection_date": 1},
        {"label": _("Item Group"), "fieldtype": "Data", "fieldname": "item_group", "width": 150},
        {"label": _("Item Code"), "fieldtype": "Data", "options": "Item", "fieldname": "item_code", "width": 150},
        {"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 250},
        {"label": _("QID"), "fieldtype": "Data", "fieldname": "qid", "width": 120},
    ]


def get_data(filters):
    data = []

    # parent filters
    parent_conditions = {"docstatus":"1"}
    if filters.get("store_receipt"):
        parent_conditions["name"] = filters.get("store_receipt")
    if filters.get("date"):
        parent_conditions["date"] = filters.get("date")

    store_receipts = frappe.get_all("Store Receipt", filters=parent_conditions, fields=["name", "date"])
    last_store_receipt = None

    for store in store_receipts:
        doc = frappe.get_doc("Store Receipt", store.name)

        
        matching_items = []
        for itm in doc.item:  
            item_group = frappe.db.get_value("Item", itm.item_code, "item_group")

            # --- child filter check ---
            if filters.get("item_code") and filters.get("item_code") != itm.item_code:
                continue
            if filters.get("item_group") and filters.get("item_group") != item_group:
                continue

            quality_inspection_date = None
            
            
            if itm.quality_inspection:
                quality_inspection_date = frappe.db.get_value("Quality Inspection", itm.quality_inspection, "report_date")
                
            show_store_info = store.name != last_store_receipt
            last_store_receipt = store.name    
                
            data.append({
                
                "store_receipt": f"""<a href="/app/store-receipt/{store.name}"><p style='font-weight:bold; color:#842A3B; '>{store.name}</p></a>""" if show_store_info else "",                
                "date": f"""<p>{frappe.format(store.date,{"fieldtype":"Date"})}</p>"""if show_store_info else "",
                "quality_inspection": itm.quality_inspection,
                "inspection_date": quality_inspection_date,
                "item_group": item_group,
                "item_code": itm.item_code,
                "item_name": itm.item_name,
                "qid": itm.qid,
                "previous":store.name
				
			})    

        #     matching_items.append({
        #         "quality_inspection": itm.quality_inspection,
        #         "inspection_date": quality_inspection_date,
        #         "item_group": item_group,
        #         "item_code": itm.item_code,
        #         "item_name": itm.item_name,
        #         "qid": itm.qid,
        #         "indent": 1
        #     })

        # # only add parent row if child rows exist OR no child filter applied
        # if matching_items or not (filters.get("item_code") or filters.get("item_group")):
        #     data.append({
        #         "store_receipt": f"""<a href="https://dev.onegeneindia.in/app/store-receipt/{store.name}"><p style='font-weight:bold;'>{store.name}</p></a>""",
        #         "date": f"""<p style="font-weight:bold;">{frappe.format(store.date,{"fieldtype":"Date"})}</p>""",
        #         "indent": 0
        #     })
        #     data.extend(matching_items)

    return data

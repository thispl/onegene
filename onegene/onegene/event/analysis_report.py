# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe,json

def execute(filters=None):
    if isinstance(filters, str):
        filters = json.loads(filters) 
    filters = frappe._dict(filters or {})
    

    report_name = filters.get("report_name")
    report_for = filters.get("report_for")
    sorting = filters.get("sorting")
    summary = filters.get("summary")
 
    columns = get_columns(report_name, report_for, summary, sorting)
    data = get_data(filters, report_name, report_for, summary, sorting)

    return columns, data

# Report columns
def get_columns(report_name, report_for, summary,sorting=None):
    columns = []

    if report_for == "Purchase Order":
        columns.extend(get_purchase_order_columns(report_name, summary, sorting))
    if report_for == "Job Order":
        columns.extend(get_job_order_columns(report_name, summary, sorting))
    if report_for == "Production":
        columns.extend(get_production_columns(report_name, summary, sorting))
    if report_for == "Customer Return":
        columns.extend(get_customer_return_columns(report_name, summary, sorting))
    if report_for == "All":
        columns.extend(get_all_columns(report_name, summary, sorting))

    return columns

def get_purchase_order_columns(report_name, summary, sorting=None):
    return []

def get_job_order_columns(report_name, summary, sorting=None):
    return []

def get_production_columns(report_name, summary, sorting=None):
    if report_name == "Rejection":
        qty_fieldname = "rejected_qty"
        qty_label = "Rejection Qty"
        percentage_fieldname = "rejection_percentage"
        percentage_label = "Rejection (%s)"
        category_fieldname = "rejection_category"
        category_label = "Rejection Category"
        reason_fieldname = "rejection_reason"
        reason_label = "Rejection Reason"

    else:
        qty_fieldname = "rework_qty"
        qty_label = "Rework Qty"
        percentage_fieldname = "rework_percentage"
        percentage_label = "Rework (%s)"
        category_fieldname = "rework_category"
        category_label = "Rework Category"
        reason_fieldname = "rework_reason"
        reason_label = "Rework Reason"
    
    if summary:
        if sorting == "Item Wise":
            return [
                {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Data", "width": 200, "align": "left"},
                {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 300, "align": "left"},
                {"fieldname": "processed_qty", "label": "Processed Qty", "fieldtype": "Data", "width": 130, "align": "right"},
                {"fieldname": "accepted_qty", "label": "Accepted Qty", "fieldtype": "Float", "width": 130, "align": "right"},
                {"fieldname": qty_fieldname, "label": qty_label, "fieldtype": "Data", "width": 120, "align": "right"},
                {"fieldname": percentage_fieldname, "label": percentage_label, "fieldtype": "Data", "width": 120, "align": "right"},
            ]
        elif sorting == "Item Group Wise":
            return [
                {"fieldname": "item_group", "label": "Item Group", "fieldtype": "Data", "width": 200, "align": "left"},
                {"fieldname": "processed_qty", "label": "Processed Qty", "fieldtype": "Data", "width": 130, "align": "right"},
                {"fieldname": "accepted_qty", "label": "Accepted Qty", "fieldtype": "Float", "width": 130, "align": "right"},
                {"fieldname": qty_fieldname, "label": qty_label, "fieldtype": "Data", "width": 120, "align": "right"},
                {"fieldname": percentage_fieldname, "label": percentage_label, "fieldtype": "Data", "width": 120, "align": "right"},
            ]
        elif sorting in ["Rework Wise", "Rejection Wise"]:
            return [
                {"fieldname": reason_fieldname, "label": reason_label, "fieldtype": "data", "width": 200, "align": "left"},
                {"fieldname": "processed_qty", "label": "Processed Qty", "fieldtype": "Data", "width": 130, "align": "right"},
                {"fieldname": "accepted_qty", "label": "Accepted Qty", "fieldtype": "Float", "width": 130, "align": "right"},
                {"fieldname": qty_fieldname, "label": qty_label, "fieldtype": "Data", "width": 120, "align": "right"},
                {"fieldname": percentage_fieldname, "label": percentage_label, "fieldtype": "Data", "width": 120, "align": "right"},
            ]
        elif sorting == "Operation Wise":
            return [
                {"fieldname": "operation", "label": "Operation", "fieldtype": "Data", "width": 150, "align": "left"},
                {"fieldname": "processed_qty", "label": "Processed Qty", "fieldtype": "Data", "width": 130, "align": "right"},
                {"fieldname": "accepted_qty", "label": "Accepted Qty", "fieldtype": "Float", "width": 130, "align": "right"},
                {"fieldname": qty_fieldname, "label": qty_label, "fieldtype": "Data", "width": 120, "align": "right"},
                {"fieldname": percentage_fieldname, "label": percentage_label, "fieldtype": "Data", "width": 120, "align": "right"},
            ]
        elif sorting == "Operator Wise":
            return [
                {"fieldname": "operator", "label": "Operator", "fieldtype": "Data", "width": 150, "align": "left"},
                {"fieldname": "operator_name", "label": "Operator Name", "fieldtype": "Data", "width": 250, "align": "left"},
                {"fieldname": "processed_qty", "label": "Processed Qty", "fieldtype": "Data", "width": 130, "align": "right"},
                {"fieldname": "accepted_qty", "label": "Accepted Qty", "fieldtype": "Float", "width": 130, "align": "right"},
                {"fieldname": qty_fieldname, "label": qty_label, "fieldtype": "Data", "width": 120, "align": "right"},
                {"fieldname": percentage_fieldname, "label": percentage_label, "fieldtype": "Data", "width": 120, "align": "right"},
            ]
        elif sorting == "Workstation Wise":
            return [
                {"fieldname": "workstation", "label": "Workstation", "fieldtype": "data", "width": 300, "align": "left"},
                {"fieldname": "processed_qty", "label": "Processed Qty", "fieldtype": "Data", "width": 130, "align": "right"},
                {"fieldname": "accepted_qty", "label": "Accepted Qty", "fieldtype": "Float", "width": 130, "align": "right"},
                {"fieldname": qty_fieldname, "label": qty_label, "fieldtype": "Data", "width": 120, "align": "right"},
                {"fieldname": percentage_fieldname, "label": percentage_label, "fieldtype": "Data", "width": 120, "align": "right"},
            ]
        elif sorting == "Month Wise":
            return [
                {"fieldname": "month_name", "label": "Month", "fieldtype": "data", "width": 300, "align": "left"},
                {"fieldname": "processed_qty", "label": "Processed Qty", "fieldtype": "Data", "width": 130, "align": "right"},
                {"fieldname": "accepted_qty", "label": "Accepted Qty", "fieldtype": "Float", "width": 130, "align": "right"},
                {"fieldname": qty_fieldname, "label": qty_label, "fieldtype": "Data", "width": 120, "align": "right"},
                {"fieldname": percentage_fieldname, "label": percentage_label, "fieldtype": "Data", "width": 120, "align": "right"},
            ]
        else:
            return [
                {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Data", "width": 200, "align": "left"},
                {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 300, "align": "left"},
                {"fieldname": "datetime", "label": "Date Time", "fieldtype": "Data", "width": 200, "align": "left"},
                {"fieldname": "processed_qty", "label": "Processed Qty", "fieldtype": "Data", "width": 130, "align": "right"},
                {"fieldname": "accepted_qty", "label": "Accepted Qty", "fieldtype": "Float", "width": 130, "align": "right"},
                {"fieldname": qty_fieldname, "label": qty_label, "fieldtype": "Data", "width": 120, "align": "right"},
                {"fieldname": percentage_fieldname, "label": percentage_label, "fieldtype": "Data", "width": 120, "align": "right"},
                {"fieldname": category_fieldname, "label": category_label, "fieldtype": "data", "width": 160, "align": "left"},
                {"fieldname": reason_fieldname, "label": reason_label, "fieldtype": "data", "width": 200, "align": "left"},
                {"fieldname": "job_card", "label": "Job Card", "fieldtype": "Data", "width": 150, "align": "left"},
                {"fieldname": "job_card_entry", "label": "Job Card Entry", "fieldtype": "Data", "width": 150, "align": "left"},
                {"fieldname": "entry_type", "label": "Entry Type", "fieldtype": "Data", "width": 150, "align": "left"},
                {"fieldname": "operation", "label": "Operation", "fieldtype": "Data", "width": 150, "align": "left"},
                {"fieldname": "operator", "label": "Operator", "fieldtype": "Data", "width": 150, "align": "left"},
                {"fieldname": "workstation", "label": "Workstation", "fieldtype": "data", "width": 300, "align": "left"},
                
            ]
    else:
        return [
            {"fieldname": "item_code", "label": "Item Code", "fieldtype": "Data", "width": 200, "align": "left"},
            {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "width": 300, "align": "left"},
            {"fieldname": "datetime", "label": "Date Time", "fieldtype": "Data", "width": 200, "align": "left"},
            {"fieldname": "processed_qty", "label": "Processed Qty", "fieldtype": "Data", "width": 130, "align": "right"},
            {"fieldname": "accepted_qty", "label": "Accepted Qty", "fieldtype": "Float", "width": 130, "align": "right"},
            {"fieldname": qty_fieldname, "label": qty_label, "fieldtype": "Data", "width": 120, "align": "right"},
            {"fieldname": percentage_fieldname, "label": percentage_label, "fieldtype": "Data", "width": 120, "align": "right"},
            {"fieldname": category_fieldname, "label": category_label, "fieldtype": "data", "width": 160, "align": "left"},
            {"fieldname": reason_fieldname, "label": reason_label, "fieldtype": "data", "width": 200, "align": "left"},
            {"fieldname": "job_card", "label": "Job Card", "fieldtype": "Data", "width": 150, "align": "left"},
            {"fieldname": "job_card_entry", "label": "Job Card Entry", "fieldtype": "Data", "width": 150, "align": "left"},
            {"fieldname": "entry_type", "label": "Entry Type", "fieldtype": "Data", "width": 150, "align": "left"},
            {"fieldname": "operation", "label": "Operation", "fieldtype": "Data", "width": 150, "align": "left"},
            {"fieldname": "operator", "label": "Operator", "fieldtype": "Data", "width": 150, "align": "left"},
            {"fieldname": "workstation", "label": "Workstation", "fieldtype": "data", "width": 300, "align": "left"},
        ]
  
def get_customer_return_columns(report_name, summary,sorting=None):
    return []

def get_all_columns(report_name, summary,sorting=None):
    return []

# Report Data  
def get_data(filters, report_name, report_for, summary, sorting):
    data = []

    if report_for == "Purchase Order":
        data.extend(get_purchase_order_data(filters, report_name, sorting))
    if report_for == "Job Order":
        data.extend(get_job_order_data(filters, report_name, sorting))
    if report_for == "Production":
        data.extend(get_production_data(filters, report_name, summary,sorting))
    if report_for == "Customer Return":
        data.extend(get_customer_return_data(filters, report_name, sorting))
    if report_for == "All":
        data.extend(get_all_data(filters, report_name, sorting))
  
    return data

def get_purchase_order_data(filters, report_name, sorting):
    return []

def get_job_order_data(filters, report_name, sorting):
    return []

def get_production_data(filters, report_name, summary,sorting):
    start_datetime = f"{filters.from_date} 00:00:00"
    end_datetime = f"{filters.to_date} 23:59:59"
    
    order_by = ""
    if sorting == "Item Wise":
        order_by = "`tabJob Card`.production_item, `tabJob Card Time Log`.custom_entry_time"
        group_field = "item_code"
  
    elif sorting == "Item Group Wise":
        order_by = "`tabItem`.item_group, `tabJob Card Time Log`.custom_entry_time"
        group_field = "item_group"
  
    elif sorting == "Rejection Wise":
        order_by = "`tabJob Card Time Log`.custom_rejection_reason, `tabJob Card Time Log`.custom_entry_time"
        group_field = "rejection_reason"
  
    elif sorting == "Rework Wise":
        order_by = "`tabJob Card Time Log`.custom_rework_reason, `tabJob Card Time Log`.custom_entry_time"
        group_field = "rework_reason"
  
    elif sorting == "Operation Wise":
        order_by = "`tabJob Card`.operation, `tabJob Card Time Log`.custom_entry_time"
        group_field = "operation"
  
    elif sorting == "Operator Wise":
        order_by = "`tabJob Card Time Log`.employee, `tabJob Card Time Log`.custom_entry_time"
        group_field = "operator"
    
    elif sorting == "Workstation Wise":
        order_by = "`tabJob Card`.workstation, `tabJob Card Time Log`.custom_entry_time"
        group_field = "workstation"
    
    elif sorting == "Month Wise":
        order_by = "month_key, `tabJob Card Time Log`.custom_entry_time"
        group_field = "month_name"
  
    else:
        order_by = "`tabJob Card Time Log`.custom_entry_time"
        group_field = None
  
    analysis_data = frappe.db.sql(f"""
        SELECT
            `tabJob Card`.production_item as item_code,
            `tabJob Card`.item_name,
            `tabJob Card`.operation,
            `tabJob Card`.name as job_card,
            `tabJob Card`.workstation,
            
   
            `tabItem`.item_group,
   
            `tabJob Card Time Log`.employee as operator,
            `tabJob Card Time Log`.completed_qty as accepted_qty,
            `tabJob Card Time Log`.custom_docname as job_card_entry,
            `tabJob Card Time Log`.custom_entry_type as entry_type,
            `tabJob Card Time Log`.custom_shift_type,
            `tabJob Card Time Log`.custom_item_group,
   
            DATE_FORMAT(`tabJob Card Time Log`.custom_entry_time, '%%Y-%%m-%%d %%H:%%i:%%s') as datetime,
            DATE_FORMAT(`tabJob Card Time Log`.custom_entry_time, '%%Y-%%m') as month_key,
            DATE_FORMAT(`tabJob Card Time Log`.custom_entry_time, '%%b %%Y') as month_name,
   
            `tabJob Card Time Log`.custom_rejected_qty as rejected_qty,
            `tabJob Card Time Log`.custom_rejection_category as rejection_category,
            `tabJob Card Time Log`.custom_rejection_reason as rejection_reason,
   
            `tabJob Card Time Log`.custom_rework_qty as rework_qty,
            `tabJob Card Time Log`.custom_rework_category as rework_category,
            `tabJob Card Time Log`.custom_rework_reason as rework_reason,
   
            (`tabJob Card Time Log`.completed_qty +
             `tabJob Card Time Log`.custom_rejected_qty +
             `tabJob Card Time Log`.custom_rework_qty) as processed_qty,
            CASE 
                WHEN (`tabJob Card Time Log`.completed_qty +
                      `tabJob Card Time Log`.custom_rejected_qty +
                      `tabJob Card Time Log`.custom_rework_qty) > 0
                THEN (`tabJob Card Time Log`.custom_rejected_qty /
                     (`tabJob Card Time Log`.completed_qty +
                      `tabJob Card Time Log`.custom_rejected_qty +
                      `tabJob Card Time Log`.custom_rework_qty)) * 100
                ELSE 0
            END as rejection_percentage,

            (`tabJob Card Time Log`.completed_qty +
             `tabJob Card Time Log`.custom_rejected_qty +
             `tabJob Card Time Log`.custom_rework_qty) as processed_qty,
            CASE 
                WHEN (`tabJob Card Time Log`.completed_qty +
                      `tabJob Card Time Log`.custom_rejected_qty +
                      `tabJob Card Time Log`.custom_rework_qty) > 0
                THEN (`tabJob Card Time Log`.custom_rework_qty /
                     (`tabJob Card Time Log`.completed_qty +
                      `tabJob Card Time Log`.custom_rejected_qty +
                      `tabJob Card Time Log`.custom_rework_qty)) * 100
                ELSE 0
            END as rework_percentage

        FROM `tabJob Card`
  
        INNER JOIN `tabJob Card Time Log`
            ON `tabJob Card Time Log`.parent = `tabJob Card`.name
   
        INNER JOIN `tabItem`
            ON `tabJob Card`.production_item = `tabItem`.name
   
        WHERE 
            `tabJob Card Time Log`.custom_docname IS NOT NULL AND
            `tabJob Card Time Log`.custom_entry_time BETWEEN %s AND %s
        ORDER BY {order_by}
    """, (start_datetime, end_datetime), as_dict=True)
    # frappe.errprint(analysis_data)
    data = []
    current_group = None
 
    if not summary:
        for row in analysis_data:

            # Report Data
            if row.rejected_qty > 0 and report_name == "Rejection":
                if group_field:
                    group_value = row.get(group_field)
                    if current_group != group_value:
                        if sorting == "Item Wise":
                            data.append({
                                "item_code": f"<b>{row.item_code}</b>",
                                "item_name": f"<b>{row.item_name}</b>"
                            })
                        elif sorting == "Operator Wise":
                            employee_name = frappe.db.get_value("Employee", group_value, "employee_name")
                            data.append({
                                "item_code": f"<b>{group_value}</b>",
                                "item_name": f"<b>{employee_name}</b>"
                            })
                        else:
                            data.append({
                                "item_code": f"<b>{group_value}</b>",
                            })
                        
                        current_group = group_value
                data.append({
                    "datetime": row.datetime,
                    "item_code": row.item_code,
                    "item_name": row.item_name,
                    "operation": row.operation,
                    "job_card": row.job_card,
                    "workstation": row.workstation,
                    "job_card_entry": row.job_card_entry,
                    "entry_type": row.entry_type,
                    "operator": row.operator,
                    "processed_qty": row.processed_qty,
                    "custom_shift_type":row.custom_shift_type,
                    "custom_item_group":row.custom_item_group,
                    "rejected_qty": row.rejected_qty,
                    "rejection_category": row.rejection_category,
                    "rejection_reason": row.rejection_reason,
                    "rejection_percentage": row.rejection_percentage,
                    "accepted_qty":row.accepted_qty,
                })
            if row.rework_qty > 0 and report_name == "Rework":
                if group_field:
                    group_value = row.get(group_field)
                    if current_group != group_value:
                        if sorting == "Item Wise":
                            data.append({
                                "item_code": f"<b>{row.item_code}</b>",
                                "item_name": f"<b>{row.item_name}</b>"
                            })
                        elif sorting == "Operator Wise":
                            employee_name = frappe.db.get_value("Employee", group_value, "employee_name")
                            data.append({
                                "item_code": f"<b>{group_value}</b>",
                                "item_name": f"<b>{employee_name}</b>"
                            })
                        else:
                            data.append({
                                "item_code": f"<b>{group_value}</b>",
                            })
                        
                        current_group = group_value
                data.append({
                    "datetime": row.datetime,
                    "item_code": row.item_code,
                    "item_name": row.item_name,
                    "operation": row.operation,
                    "job_card": row.job_card,
                    "workstation": row.workstation,
                    "job_card_entry": row.job_card_entry,
                    "entry_type": row.entry_type,
                    "operator": row.operator,
                    "custom_shift_type":row.custom_shift_type,
                    "custom_item_group":row.custom_item_group,
                    "processed_qty": row.processed_qty,
                    "rework_qty": row.rework_qty,
                    "rework_category": row.rework_category,
                    "rework_reason": row.rework_reason,
                    "rework_percentage": row.rework_percentage,
                    "accepted_qty":row.accepted_qty,
                })
    else:
        grouped_data = {}
        for row in analysis_data:
            # Skip irrelevant rows
            if report_name == "Rejection" and row.rejected_qty <= 0:
                continue
            if report_name == "Rework" and row.rework_qty <= 0:
                continue

            key = row.get(group_field) if group_field else "Total"

            if key not in grouped_data:
                
                grouped_data[key] = {
                    "processed_qty": 0,
                    "rejected_qty": 0,
                    "accepted_qty":0,
                    "rework_qty": 0,
                }

            grouped_data[key]["processed_qty"] += row.processed_qty
            grouped_data[key]["rejected_qty"] += row.rejected_qty
            grouped_data[key]["rework_qty"] += row.rework_qty
            grouped_data[key]["accepted_qty"] += row.accepted_qty

        # Build final summary rows
        for key, value in grouped_data.items():

            processed = value["processed_qty"]
            accepted_qty=value['accepted_qty']

            if report_name == "Rejection":
                qty = value["rejected_qty"]
            else:
                qty = value["rework_qty"]

            percentage = round((qty / processed * 100),2) if processed else 0
            
            if sorting == "Operator Wise":
                data.append({
                    group_field if group_field else "item_code": f"<b>{key}</b>",
                    "operator_name": f'<b>{frappe.db.get_value("Employee", key, "employee_name")}</b>',
                    "processed_qty": processed,
                    "accepted_qty":accepted_qty,
                    "rework_qty": value["rework_qty"] if report_name == "Rework" else None,
                    "rejected_qty": value["rejected_qty"] if report_name == "Rejection" else None,
                    "rework_percentage": percentage if report_name == "Rework" else None,
                    "rejection_percentage": percentage if report_name == "Rejection" else None,
                })
            elif sorting == "Item Wise":
                data.append({
                    group_field if group_field else "item_code": f"<b>{key}</b>",
                    "item_name": f'<b>{frappe.db.get_value("Item", key, "item_name")}</b>',
                    "processed_qty": processed,
                    "accepted_qty":accepted_qty,
                    "rework_qty": value["rework_qty"] if report_name == "Rework" else None,
                    "rejected_qty": value["rejected_qty"] if report_name == "Rejection" else None,
                    "rework_percentage": percentage if report_name == "Rework" else None,
                    "rejection_percentage": percentage if report_name == "Rejection" else None,
                })
            else:
                data.append({
                    group_field if group_field else "item_code": f"<b>{key}</b>",
                    "processed_qty": processed,
                    "accepted_qty":accepted_qty,
                    "rework_qty": value["rework_qty"] if report_name == "Rework" else None,
                    "rejected_qty": value["rejected_qty"] if report_name == "Rejection" else None,
                    "rework_percentage": percentage if report_name == "Rework" else None,
                    "rejection_percentage": percentage if report_name == "Rejection" else None,
                })
    return data



def get_customer_return_data(filters, report_name, sorting):
    return []

def get_all_data(filters, report_name, sorting):	
    return []
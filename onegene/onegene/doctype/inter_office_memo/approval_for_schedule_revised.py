import frappe
from collections import defaultdict
from datetime import datetime
from frappe.utils import now
import textwrap

@frappe.whitelist()
def revise_schedule(docname):
    iom = frappe.get_doc("Inter Office Memo", docname)
    new_count = 0
    update_count = 0
    skipped_count = 0
    
    # SALES ORDER SCHEDULE
    if iom.approval_schdule_increase:
        sales_orders = frappe.db.sql(
            """SELECT DISTINCT sales_order 
               FROM `tabApproval for Schedule Increase`
               WHERE parent = %s""",
            (docname,),
            as_dict=True
        )

        for so in sales_orders:
            sales_order = so["sales_order"]  # extract string from dict
            if frappe.db.exists("Open Order", {"sales_order_number": sales_order}):
                open_order = frappe.get_doc("Open Order", {"sales_order_number": sales_order})
                for iom_row in iom.approval_schdule_increase:
                    if sales_order == iom_row.sales_order:
                        for op_row in open_order.open_order_table:
                            if iom_row.part_no == op_row.item_code:
                                qty = iom_row.revised_schedule_value
                                total_qty = frappe.db.sql("""
                                    SELECT SUM(qty)
                                    FROM `tabSales Order Schedule`
                                    WHERE sales_order_number = %s AND item_code = %s AND schedule_month != %s AND schedule_year = %s AND docstatus = 1
                                """, (sales_order, iom_row.part_no, iom.schedule_month, iom.schedule_year), as_dict=False)[0][0] or 0
                                total_qty += iom_row.revised_schedule_value
                                op_row.qty = total_qty if total_qty > 0 else 1
                                if not frappe.db.exists("Sales Order Schedule", {
                                    'sales_order_number': sales_order,
                                    'schedule_month': iom.schedule_month,
                                    "schedule_year": iom.schedule_year,
                                    'item_code': iom_row.part_no,
                                    'docstatus': 1,
                                    'qty': iom_row.revised_schedule_value
                                }):
                                    sos = frappe.db.get_value(
                                        "Sales Order Schedule",
                                        {"sales_order_number": sales_order, "schedule_month": iom.schedule_month, "schedule_year": iom.schedule_year, "item_code": iom_row.part_no},
                                        ["name", "qty", "delivered_qty", "order_rate", "order_rate_inr"],
                                        as_dict=True
                                    )

                                    if sos:
                                        pending_qty = qty - sos.delivered_qty
                                        schedule_amount = qty * sos.order_rate
                                        pending_amount = pending_qty * sos.order_rate
                                        schedule_amount_inr = qty * sos.order_rate_inr
                                        pending_amount_inr = pending_qty * sos.order_rate_inr

                                        update_vals = {
                                            "qty": qty,
                                            "pending_qty": pending_qty,
                                            "schedule_amount": schedule_amount,
                                            "schedule_amount_inr": schedule_amount_inr,
                                            "pending_amount": pending_amount,
                                            "pending_amount_inr": pending_amount_inr
                                        }
                                        
                                        next_idx = frappe.db.count("Sales Order Schedule Revision", {"parent": sos.name}) + 1
                                        log = frappe.new_doc("Sales Order Schedule Revision")
                                        log.parent = sos.name
                                        log.parenttype = "Sales Order Schedule"
                                        log.parentfield = "revision"
                                        log.idx = next_idx  # <-- IMPORTANT
                                        log.revised_on = now()
                                        log.schedule_qty = sos.qty
                                        log.revised_schedule_qty = qty
                                        log.revised_by = iom.owner
                                        log.remarks = f"Revised from IOM - {iom.name}"
                                        log.insert(ignore_permissions=True)
                                        
                                        frappe.db.set_value("Sales Order Schedule", sos.name, update_vals)
                                        update_count += 1
                                    else:
                                        current_year = datetime.now().year
                                        schedule_month = iom.schedule_month
                                        schedule_year = iom.schedule_year
                                        schedule_date = datetime.strptime(f"01-{schedule_month}-{current_year}", "%d-%b-%Y")
                                        
                                        order_rate = frappe.db.get_value("Sales Order Item", {"parent":sales_order, "item_code":iom_row.part_no}, "rate")
                                        order_rate_inr = frappe.db.get_value("Sales Order Item", {"parent":sales_order, "item_code":iom_row.part_no}, "base_rate")
                                        currency = frappe.db.get_value("Sales Order", sales_order, "currency")
                                        exchange_rate = frappe.db.get_value("Sales Order", sales_order, "conversion_rate")
                                        
                                        sos = frappe.get_doc({
                                            "doctype": "Sales Order Schedule",
                                            "customer_code": iom_row.customer_code,
                                            "customer_name": iom_row.customer,
                                            "customer_group": iom_row.customer_type,
                                            "item_group": iom_row.item_group,
                                            "item_name":iom_row.part_name,
                                            "sales_order_number": sales_order,
                                            "item_code": iom_row.part_no,
                                            "schedule_date": schedule_date,
                                            "qty": qty,
                                            "schedule_month": schedule_month,
                                            "schedule_year": schedule_year,
                                            "pending_qty": qty,
                                            "tentative_plan_1": 0,
                                            "tentative_plan_2": 0,
                                            "disable_update_items": 1,
                                            "order_rate": order_rate,
                                            "currency": currency,
                                            "schedule_amount": qty * order_rate,
                                            "pending_amount": qty * order_rate,
                                            "schedule_amount_inr": qty * order_rate_inr,
                                            "pending_amount_inr": qty * order_rate_inr,
                                            "order_rate_inr": order_rate_inr,
                                            "exchange_rate": exchange_rate
                                        })

                                        sos.db_insert()

                                        child = frappe.get_doc({
                                            "doctype": "Sales Order Schedule Revision",
                                            "parent": sos.name,
                                            "parenttype": "Sales Order Schedule",
                                            "parentfield": "revision",
                                            "revised_on": now(),
                                            "schedule_qty": 0,
                                            "revised_schedule_qty": qty,
                                            "revised_by": iom.owner,
                                            "remarks": f"Created from IOM - {iom.name}"
                                        })
                                        child.db_insert()
                                        
                                        frappe.db.set_value("Sales Order Schedule", sos.name, "docstatus", 1)
                                        new_count += 1
                                else:
                                    skipped_count += 1
                                break

                # Save Open Order
                open_order.disable_update_items = 0
                open_order.save(ignore_permissions=True)

        response_data = f"""
            <div style="max-width: 420px;
                margin: 20px auto;
                background: #ffffff;
                border-radius: 12px;
                padding: 20px 24px;
                box-shadow: 0 4px 14px rgba(0,0,0,0.08);
                font-family: Inter, sans-serif;
                border: 1px solid #e7e7e7;">
                <div style="font-size: 18px; font-weight: 600; color: #333;">
                    Last Updated On
                </div>

                <div style="margin-top: 6px; font-size: 13px; color: #666;">
                    {now()}
                </div>

                <hr style="margin: 12px 0; border: 0; border-top: 1px solid #eee;">

                <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                    <li style="color:#4caf50;">New documents created: {new_count}</li>
                    <li style="color:#2196f3;">Updated in existing document: {update_count}</li>
                    <li style="color:#999;">Skipped documents: {skipped_count}</li>
                </ul>
            </div>
        """
        clean_html = textwrap.dedent(response_data).strip()
        frappe.db.set_value("Inter Office Memo", docname, "response_data", clean_html)
        frappe.db.set_value("Inter Office Memo", docname, "item_Schedule_revised", 1)
        frappe.db.commit()

        return True
    
    # PURCHASE ORDER SCHEDULE
    if iom.schedule_revised:
        purchase_orders = frappe.db.sql(
            """SELECT DISTINCT purchase_order
               FROM `tabApproval for Schedule Revised`
               WHERE parent = %s""",
            (docname,),
            as_dict=True
        )
        for po in purchase_orders:
            purchase_order = po["purchase_order"]  # extract string from dict
            if frappe.db.exists("Purchase Open Order", {"purchase_order": purchase_order}):
                open_order = frappe.get_doc("Purchase Open Order", {"purchase_order": purchase_order})
                for iom_row in iom.schedule_revised:
                    if purchase_order == iom_row.purchase_order:
                        for op_row in open_order.open_order_table:
                            if iom_row.part_no == op_row.item_code:
                                qty = iom_row.revised_schedule_value
                                total_qty = frappe.db.sql("""
                                    SELECT SUM(qty)
                                    FROM `tabPurchase Order Schedule`
                                    WHERE purchase_order_number = %s AND item_code = %s AND schedule_month != %s AND schedule_year = %s AND docstatus = 1
                                """, (purchase_order, iom_row.part_no, iom.schedule_month, iom.schedule_year), as_dict=False)[0][0] or 0
                                total_qty += iom_row.revised_schedule_value
                                op_row.qty = total_qty if total_qty > 0 else 1
                                if not frappe.db.exists("Purchase Order Schedule", {
                                    'purchase_order_number': purchase_order,
                                    'schedule_month': iom.schedule_month,
                                    "schedule_year": iom.schedule_year,
                                    'item_code': iom_row.part_no,
                                    'docstatus': 1,
                                    'qty': iom_row.revised_schedule_value
                                }):
                                    pos = frappe.db.get_value(
                                        "Purchase Order Schedule",
                                        {"purchase_order_number": purchase_order, "schedule_month": iom.schedule_month, "schedule_year": iom.schedule_year, "item_code": iom_row.part_no},
                                        ["name", "qty", "received_qty", "order_rate", "order_rate_inr"],
                                        as_dict=True
                                    )

                                    if pos:
                                        pending_qty = qty - pos.received_qty
                                        schedule_amount = qty * pos.order_rate
                                        pending_amount = pending_qty * pos.order_rate
                                        schedule_amount_inr = qty * pos.order_rate_inr
                                        pending_amount_inr = pending_qty * pos.order_rate_inr

                                        update_vals = {
                                            "qty": qty,
                                            "pending_qty": pending_qty,
                                            "schedule_amount": schedule_amount,
                                            "schedule_amount_inr": schedule_amount_inr,
                                            "pending_amount": pending_amount,
                                            "pending_amount_inr": pending_amount_inr
                                        }
                                        
                                        next_idx = frappe.db.count("Purchase Order Schedule Revision", {"parent": pos.name}) + 1
                                        log = frappe.new_doc("Purchase Order Schedule Revision")
                                        log.parent = pos.name
                                        log.parenttype = "Purchase Order Schedule"
                                        log.parentfield = "revision"
                                        log.idx = next_idx  # <-- IMPORTANT
                                        log.revised_on = now()
                                        log.schedule_qty = pos.qty
                                        log.revised_schedule_qty = qty
                                        log.revised_by = iom.owner
                                        log.remarks = f"Revised from IOM - {iom.name}"
                                        log.insert(ignore_permissions=True)
                                        
                                        frappe.db.set_value("Purchase Order Schedule", pos.name, update_vals)
                                        update_count += 1
                                    else:
                                        current_year = datetime.now().year
                                        schedule_month = iom.schedule_month
                                        schedule_year = iom.schedule_year
                                        schedule_date = datetime.strptime(f"01-{schedule_month}-{current_year}", "%d-%b-%Y")
                                        
                                        order_rate = frappe.db.get_value("Purchase Order Item", {"parent":purchase_order, "item_code":iom_row.part_no}, "rate")
                                        order_rate_inr = frappe.db.get_value("Purchase Order Item", {"parent":purchase_order, "item_code":iom_row.part_no}, "base_rate")
                                        currency = frappe.db.get_value("Purchase Order", purchase_order, "currency")
                                        exchange_rate = frappe.db.get_value("Purchase Order", purchase_order, "conversion_rate")
                                        
                                        
                                        po_type = frappe.db.get_value("Purchase Order",{"name":purchase_order},"custom_po_type")
                                        pos = frappe.get_doc({
                                            "doctype": "Purchase Order Schedule",
                                            "supplier_code": iom_row.supplier_code,
                                            "purchase_order_number": purchase_order,
                                            "supplier_name": iom_row.supplier,
                                            "supplier_group": iom_row.supplier_type,
                                            "item_group": iom_row.item_group,
                                            "item_name":iom_row.part_name,
                                            "item_code": iom_row.part_no,
                                            "schedule_date": schedule_date,
                                            "qty": qty,
                                            "schedule_month": schedule_month,
                                            "schedule_year": schedule_year,
                                            "pending_qty": qty,
                                            "tentative_plan_1": 0,
                                            "tentative_plan_2": 0,
                                            "disable_update_items": 1,
                                            "order_rate": order_rate,
                                            "currency": currency,
                                            "schedule_amount": qty * order_rate,
                                            "pending_amount": qty * order_rate,
                                            "schedule_amount_inr": qty * order_rate_inr,
                                            "pending_amount_inr": qty * order_rate_inr,
                                            "order_rate_inr": order_rate_inr,
                                            "exchange_rate": exchange_rate,
                                            "po_type": po_type
                                        })

                                        pos.db_insert()

                                        child = frappe.get_doc({
                                            "doctype": "Purchase Order Schedule Revision",
                                            "parent": pos.name,
                                            "parenttype": "Purchase Order Schedule",
                                            "parentfield": "revision",
                                            "revised_on": now(),
                                            "schedule_qty": 0,
                                            "revised_schedule_qty": qty,
                                            "revised_by": iom.owner,
                                            "remarks": f"Created from IOM - {iom.name}"
                                        })
                                        child.db_insert()
                                        
                                        frappe.db.set_value("Purchase Order Schedule", pos.name, "docstatus", 1)
                                        new_count += 1
                                else:
                                    skipped_count += 1
                                break

                # Save Purchase Open Order
                open_order.disable_update_items = 0
                open_order.save(ignore_permissions=True)

        response_data = f"""
            <div style="max-width: 420px;
                margin: 20px auto;
                background: #ffffff;
                border-radius: 12px;
                padding: 20px 24px;
                box-shadow: 0 4px 14px rgba(0,0,0,0.08);
                font-family: Inter, sans-serif;
                border: 1px solid #e7e7e7;">
                <div style="font-size: 18px; font-weight: 600; color: #333;">
                    Last Updated On
                </div>

                <div style="margin-top: 6px; font-size: 13px; color: #666;">
                    {now()}
                </div>

                <hr style="margin: 12px 0; border: 0; border-top: 1px solid #eee;">

                <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                    <li style="color:#4caf50;">New documents created: {new_count}</li>
                    <li style="color:#2196f3;">Updated in existing document: {update_count}</li>
                    <li style="color:#999;">Skipped documents: {skipped_count}</li>
                </ul>
            </div>
        """
        clean_html = textwrap.dedent(response_data).strip()
        frappe.db.set_value("Inter Office Memo", docname, "response_data", clean_html)
        frappe.db.set_value("Inter Office Memo", docname, "item_Schedule_revised", 1)
        frappe.db.commit()

    return True
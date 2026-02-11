import frappe
from frappe.utils import cstr
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

@frappe.whitelist()
def update_lr_status(doc, method):
	if doc.custom_invoice_type=='Export Invoice':
		try:
			lr=frappe.get_doc('Logistics Request',{'order_no':doc.name})
			if lr.status=='LR Approved':
				lr.status='Ready to Ship'
				lr.save(ignore_permissions=True)
				frappe.log_error(f"status update ok {lr.name}")
		except Exception as e:
				frappe.log_error(f"status update failed {doc.name}: {str(e)}")

@frappe.whitelist()
def packing_list(sales_invoice):
    data = frappe.db.sql("""
        SELECT 
            si.custom_exporter_iec, si.custom_gstin,
            sii.custom_pallet, sii.custom_pallet_length,
            sii.custom_pallet_breadth, sii.custom_pallet_height,
            SUM(sii.total_weight) as net_weight,
            SUM(sii.custom_gross_weight) as gross_weight,
            SUM(sii.custom_no_of_boxes) as total_boxes,
            SUM(sii.custom_no_of_pallets) as total_pallets,
            sii.item_code, sii.description, SUM(sii.qty) as qty
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE si.name = %s
        GROUP BY sii.custom_pallet, sii.item_code
        ORDER BY sii.custom_pallet
    """, (sales_invoice,), as_dict=True)

    if not data:
        return "<p>No packing list data available.</p>"

    iec = data[0].custom_exporter_iec or ''
    gstin = data[0].custom_gstin or ''

    # Group by pallet
    pallet_map = {}
    for row in data:
        pallet_map.setdefault(row.custom_pallet, []).append(row)

    # Header and first table
    html = f"""
    <h3 class="text-center">Packing List</h3>
    <p style="margin-left: 70%;">Exporter IEC: <span style="font-weight: 100;">{iec}</span></p>
    <p style="margin-left: 70%;">GSTIN: <span style="font-weight: 100;">{gstin}</span></p>
    <table class="mt-2" border="1" cellspacing="0" cellpadding="4">
        <tr>
            <td class="background text-center">Pallet</td>
            <td class="background text-center">Item</td>
            <td class="background text-center">Description</td>
            <td class="background text-center">Qty (Nos)</td>
            <td class="background text-center">No. of Boxes (Nos)</td>
            <td class="background text-center">No. of Pallets (Nos)</td>
        </tr>
    """
    total_qty = 0
    total_boxes = 0
    total_pallets = 0
    for pallet, items in pallet_map.items():
        rowspan = len(items)
        for idx, i in enumerate(items):
            html += "<tr>"
            if idx == 0:
                html += f'<td rowspan="{rowspan}">{pallet or ""}</td>'
            total_qty += int(round(i.qty or 0))
            total_boxes += int(round(i.total_boxes or 0))
            total_pallets += int(round(i.total_pallets or 0))
            html += f"""
                <td>{i.item_code}</td>
                <td>{i.description}</td>
                <td class="text-right">{int(round(i.qty or 0))}</td>
                <td class="text-right">{int(round(i.total_boxes or 0))}</td>
                <td class="text-right">{int(round(i.total_pallets or 0))}</td>
            </tr>
            """
    html += f"""
            <tr>
                <td colspan=3 class="text-right"><b>Total</b></td>
                <td class="text-right"><b>{total_qty}</b></td>
                <td class="text-right"><b>{total_boxes}</b></td>
                <td class="text-right"><b>{total_pallets}</b></td>
            </tr>"""
    html += "</table>"

    # Second table: Pallet summary
    html += f"""
    <div style="width: 70%;">
    <table class="mt-5" border="1" cellspacing="0" cellpadding="4" width=60%>
        <tr>
            <td rowspan="2" class="background text-center">Pallet</td>
            <td colspan="3" class="background text-center">Dimensions (mm)</td>
            <td colspan="2" class="background text-center">Weight (kg)</td>
        </tr>
        <tr>
            <td class="background text-center">L</td>
            <td class="background text-center">B</td>
            <td class="background text-center">H</td>
            <td class="background text-center">Net</td>
            <td class="background text-center">Gross</td>
        </tr>
    """

    total_net = 0
    total_gross = 0

    for pallet, items in pallet_map.items():
        first = items[0]
        length = int(round(first.custom_pallet_length or 0))
        breadth = int(round(first.custom_pallet_breadth or 0))
        height = int(round(first.custom_pallet_height or 0))
        net_weight = int(round(first.net_weight or 0))
        gross_weight = int(round(first.gross_weight or 0))

        html += f"""
        <tr>
            <td class="text-left">{pallet or ""}</td>
            <td class="text-right">{length}</td>
            <td class="text-right">{breadth}</td>
            <td class="text-right">{height}</td>
            <td class="text-right">{net_weight}</td>
            <td class="text-right">{gross_weight}</td>
        </tr>
        """
        total_net += net_weight
        total_gross += gross_weight

    html += f"""
        <tr>
            <td colspan="4" class="text-right"><b>Total</b></td>
            <td class="text-right"><b>{total_net}</b></td>
            <td class="text-right"><b>{total_gross}</b></td>
        </tr>
        """

    html += "</table></div>"
    return html

from onegene.onegene.custom import validate_stock_qty
@frappe.whitelist()
def validate_qty(doc,method):
    if doc.stock_entry_type == "Material Transfer":
        for i, d in enumerate(doc.items):
            if d.s_warehouse or d.t_warehouse:
                actual_qty = validate_stock_qty(
                    item_code=d.item_code,
                    warehouse=d.s_warehouse or d.t_warehouse,
                    posting_date=doc.posting_date,
                    posting_time=doc.posting_time,
                    qty=d.qty,
                    idx=d.idx
                )
                if actual_qty<d.qty:
                    d.qty = actual_qty

@frappe.whitelist()
def explode_bom(bom):
    bom_qty = frappe.db.get_value("BOM", bom, "quantity") or 1
    bom_items = frappe.get_all("BOM Item", filters={"parent": bom}, fields=["item_code", "qty", "bom_no"])
    exploded_items = []

    for item in bom_items:
        exploded_items.append({
            "item_code": item["item_code"],
            "qty": (item["qty"] * bom_qty) or 0
        })
        # if item.get("bom_no"):
        # 	# Recursively add sub-assembly items
        # 	child_items = explode_bom(item["bom_no"])
        # 	exploded_items.extend(child_items)

    return exploded_items

@frappe.whitelist()
def explode_and_update_bom_in_mri(bom, source_warehouse):
    from frappe.utils import today, add_days

    start_datetime = f"{today()} 08:31:00"
    end_datetime = f"{add_days(today(), 1)} 08:30:00"

    start_datetime = frappe.utils.get_datetime(start_datetime)
    end_datetime = frappe.utils.get_datetime(end_datetime)

    result = frappe.db.sql("""
        SELECT name FROM `tabProduction Material Request`
        WHERE creation BETWEEN %s AND %s
    """, (start_datetime, end_datetime))

    if not result:
        frappe.throw("No Production Material Request found in the given time range.")
        frappe.throw("கொடுக்கப்பட்ட காலப்பகுதியில் எந்த Production Material Request -ம் கண்டுபிடிக்கப்படவில்லை.")


    pmr = result[0][0]

    data = []
    exploded_items = explode_bom(bom)

    for row in exploded_items:
        item_code = row["item_code"]
        if frappe.db.exists("Sub Assembly Item", {"item_code": item_code, "parent": pmr, "warehouse": source_warehouse}) or frappe.db.exists("Raw Materials", {"item_code": item_code, "parent": pmr, "warehouse": source_warehouse}):
            data.append({"item_code": item_code})
    return data

@frappe.whitelist()
def get_bom_from_pmr(doctype, txt, searchfield, start, page_len, filters):
    from frappe.utils import today, add_days

    start_datetime = f"{today()} 08:31:00"
    end_datetime = f"{add_days(today(), 1)} 08:30:00"

    start_datetime = frappe.utils.get_datetime(start_datetime)
    end_datetime = frappe.utils.get_datetime(end_datetime)

    result = frappe.db.sql("""
        SELECT name FROM `tabProduction Material Request`
        WHERE creation BETWEEN %s AND %s
    """, (start_datetime, end_datetime))

    if not result:
        frappe.throw("No Production Material Request found in the given time range.")

    pmr = result[0][0]
    
    return frappe.db.sql("""
        SELECT DISTINCT b.name AS bom, ai.item_name
        FROM `tabAssembly Item` ai
        INNER JOIN `tabBOM` b ON b.item = ai.item_code
        WHERE ai.parent = %s AND ai.item_code LIKE %s
        LIMIT %s OFFSET %s
    """, (pmr, f"%{txt}%", page_len, start))

@frappe.whitelist()
def mr_required_from_pmr(bom):
    item_code = frappe.db.get_value("BOM", bom, "item")
    from frappe.utils import today, add_days

    start_datetime = f"{today()} 08:31:00"
    end_datetime = f"{add_days(today(), 1)} 08:30:00"

    start_datetime = frappe.utils.get_datetime(start_datetime)
    end_datetime = frappe.utils.get_datetime(end_datetime)

    result = frappe.db.sql("""
        SELECT name FROM `tabProduction Material Request`
        WHERE creation BETWEEN %s AND %s
    """, (start_datetime, end_datetime))

    if not result:
        frappe.throw("No Production Material Request found in the given time range.")
        frappe.throw("கொடுக்கப்பட்ட காலப்பகுதியில் எந்த Production Material Request -ம் கண்டுபிடிக்கப்படவில்லை.")


    pmr = result[0][0]
    total_required_plan = frappe.db.sql("""
        SELECT
            COALESCE((SELECT SUM(required_plan) FROM `tabAssembly Item` 
                    WHERE parent = %s AND item_code = %s), 0) +
            COALESCE((SELECT SUM(required_plan) FROM `tabSub Assembly Item` 
                    WHERE parent = %s AND item_code = %s), 0) AS total
    """, (pmr, item_code, pmr, item_code))[0][0]
    return total_required_plan


import re

def update_si_name(doc,method):
    if not doc.amended_from:
        if doc.custom_invoice_type in ['Scrap Invoice', 'Tooling Invoice']:
            invoice_type = doc.custom_invoice_type
            short_code = 'SCRP' if invoice_type == 'Scrap Invoice' else 'T'
            si_list = frappe.db.get_all("Sales Invoice", {'custom_invoice_type': invoice_type,'amended_from':''}, ['name'])

            pattern = re.compile(rf"^{short_code}(\d+)$")
            max_num = 0
            for reg in si_list:
                si_number = reg['name']
                match = pattern.match(si_number)
                if match:
                    num_part = int(match.group(1))
                    if num_part > max_num:
                        max_num = num_part
            if invoice_type == 'Tooling Invoice' and max_num < 10:
                max_num = 10
            next_num = max_num + 1
            next_reg_number = f'{short_code}0{str(next_num).zfill(4)}'
            # print(next_reg_number)
        
        elif doc.custom_invoice_type in ['Export Invoice', 'Supplementary Invoice', 'Non Commercial Invoice','Domestic Invoice', 'Tax Invoice']:
            invoice_type = doc.custom_invoice_type
            
            if invoice_type == 'Export Invoice':
                short_code = 'E'
                min_start = 314
            elif invoice_type == 'Non Commercial Invoice':
                short_code = 'NI'
                min_start = 1 
            elif invoice_type=='Supplementary Invoice':
                short_code = 'SI'
                min_start = 6 
            else:
                short_code = 'D'
                min_start = 5567
            today = datetime.today()
            year = today.year
            month = today.month
            if month >= 4:
                fy_start = year
                fy_end = year + 1
            else:
                fy_start = year - 1
                fy_end = year
            fin_year = f"{str(fy_start)[-2:]}{str(fy_end)[-2:]}"  
            short_code_with_year = f"{short_code}{fin_year}"
            si_list = frappe.db.get_all("Sales Invoice", {'custom_invoice_type': invoice_type,'amended_from':''}, ['name'])
            pattern = re.compile(rf"^{short_code_with_year}(\d+)$")
            max_num = 0
            for reg in si_list:
                si_number = reg['name']
                match = pattern.match(si_number)
                if match:
                    num_part = int(match.group(1))
                    if num_part > max_num:
                        max_num = num_part
            if max_num < (min_start - 1):
                max_num = min_start - 1

            next_num = max_num + 1
            next_reg_number = f'{short_code_with_year}0{str(next_num).zfill(4)}'

        else:
            today = datetime.today()
            year_suffix = str(today.year)[-2:] 
            short_code = f"SI-{year_suffix}-"

            invoice_type = doc.custom_invoice_type
            si_list = frappe.db.get_all("Sales Invoice", {'name': ['!=',doc.name]}, ['name'])
            pattern = re.compile(rf"^{short_code}(\d+)$")
            max_num = 0
            for reg in si_list:
                si_number = reg['name']
                match = pattern.match(si_number)
                if match:
                    num_part = int(match.group(1))
                    if num_part > max_num:
                        max_num = num_part

            next_num = max_num + 1
            next_reg_number = f'{short_code}0{str(next_num).zfill(5)}'
        doc.custom_si_code=next_reg_number

            
@frappe.whitelist()
def del_glentry():
    gl_entry=frappe.db.get_all('GL Entry',{"voucher_type":"Sales Invoice",'is_cancelled':1},['name'])
    for g in gl_entry:
        gl=frappe.get_doc('GL Entry',g.name)
        gl.cancel()
        # gl.delete()


import frappe

@frappe.whitelist()
def get_customer_and_company_state(customer, company):
    customer_state = None
    company_state = None

    # Get default customer address
    cust_addr = frappe.db.get_value("Dynamic Link",
        {"link_doctype": "Customer", "link_name": customer, "parenttype": "Address"},
        "parent"
    )
    if cust_addr:
        customer_state = frappe.db.get_value("Address", cust_addr, "state")

    # Get default company address
    comp_addr = frappe.db.get_value("Dynamic Link",
        {"link_doctype": "Company", "link_name": company, "parenttype": "Address"},
        "parent"
    )
    if comp_addr:
        company_state = frappe.db.get_value("Address", comp_addr, "state")

    return {
        "customer_state": customer_state,
        "company_state": company_state
    }

import frappe

@frappe.whitelist()
def get_item_tax_and_sales_template(hsn_code, customer, company):
    # Step 1: Get states
    customer_state, company_state = None, None

    cust_addr = frappe.db.get_value("Dynamic Link",
        {"link_doctype": "Customer", "link_name": customer, "parenttype": "Address"},
        "parent"
    )
    if cust_addr:
        customer_state = frappe.db.get_value("Address", cust_addr, "state")

    comp_addr = frappe.db.get_value("Dynamic Link",
        {"link_doctype": "Company", "link_name": company, "parenttype": "Address"},
        "parent"
    )
    if comp_addr:
        company_state = frappe.db.get_value("Address", comp_addr, "state")

    if not (customer_state and company_state):
        return {}

    # Step 2: Decide state type (In-State / Out-State)
    state_type = "In-State" if customer_state == company_state else "Out-State"

    # Step 3: Get HSN-based item tax template row
    if not hsn_code:
        return {}

    row = frappe.db.sql("""
        SELECT it.item_tax_template, it.tax_category
        FROM `tabItem Tax` it
        WHERE it.parent = %s AND it.tax_category = %s
        LIMIT 1
    """, (hsn_code, state_type), as_dict=True)

    if not row:
        return {}

    # Step 4: Extract % from Item Tax Template name (ex: "28%")
    rate = None
    if row[0].item_tax_template:
        if "28" in row[0].item_tax_template:
            rate = "28%"
        elif "18" in row[0].item_tax_template:
            rate = "18%"

    if not rate:
        return {}

    # Step 5: Build Sales Taxes & Charges Template name
    # (Ex: "GST 28% In-State - WAIP")
    sales_tax_template_name = f"GST {rate} {state_type} - WAIP"

    # Step 6: Validate it exists
    exists = frappe.db.exists("Sales Taxes and Charges Template", sales_tax_template_name)
    if not exists:
        return {}

    return {
        "item_tax_template": row[0].item_tax_template,
        "tax_category": state_type,
        "sales_taxes_and_charges_template": sales_tax_template_name
    }

@frappe.whitelist()
def get_item_tax_and_sales_template_for_tad(hsn_code, supplier, company):
    # Step 1: Get states
    supplier_state, company_state = None, None

    supp_addr = frappe.db.get_value("Dynamic Link",
        {"link_doctype": "Supplier", "link_name": supplier, "parenttype": "Address"},
        "parent"
    )
    if supp_addr:
        supplier_state = frappe.db.get_value("Address", supp_addr, "state")

    comp_addr = frappe.db.get_value("Dynamic Link",
        {"link_doctype": "Company", "link_name": company, "parenttype": "Address"},
        "parent"
    )
    if comp_addr:
        company_state = frappe.db.get_value("Address", comp_addr, "state")

    if not (supplier_state and company_state):
        return {}

    # Step 2: Decide state type (In-State / Out-State)
    state_type = "In-State" if supplier_state == company_state else "Out-State"

    # Step 3: Get HSN-based item tax template row
    if not hsn_code:
        return {}

    row = frappe.db.sql("""
        SELECT it.item_tax_template, it.tax_category
        FROM `tabItem Tax` it
        WHERE it.parent = %s AND it.tax_category = %s
        LIMIT 1
    """, (hsn_code, state_type), as_dict=True)

    if not row:
        return {}

    # Step 4: Extract % from Item Tax Template name (ex: "28%")
    rate = None
    if row[0].item_tax_template:
        if "28" in row[0].item_tax_template:
            rate = "28%"
        elif "18" in row[0].item_tax_template:
            rate = "18%"

    if not rate:
        return {}

    # Step 5: Build Sales Taxes & Charges Template name
    # (Ex: "GST 28% In-State - WAIP")
    sales_tax_template_name = f"GST {rate} {state_type} - WAIP"

    # Step 6: Validate it exists
    exists = frappe.db.exists("Sales Taxes and Charges Template", sales_tax_template_name)
    if not exists:
        return {}

    return {
        "item_tax_template": row[0].item_tax_template,
        "tax_category": state_type,
        "sales_taxes_and_charges_template": sales_tax_template_name
    }


# @frappe.whitelist()
# def get_gate_items(entry_document, entry_id):
#     entry_doc = frappe.get_doc(entry_document, entry_id)
    
#     html = f"""
#     <table style="width:100%; border-collapse: collapse;" border="1">
#         <tr style="background-color: #f7941d; font-weight: bold;">
#             <td>Sr No</td>
#             <td>Item Code</td>
#             <td>Item Name</td>
#             <td>Qty</td>
#             <td>UOM</td>
#             <td>Rate</td>
#             <td>Amount</td>
#         </tr>
#     """
#     sr_no = 1
#     for e in entry_doc.items:
#         html += f"""
#         <tr>
#             <td>{sr_no}</td>
#             <td>{e.item_code}</td>
#             <td>{e.item_name}</td>
#             <td>{e.qty}</td>
#             <td>{e.uom}</td>
#             <td>{e.rate}</td>
#             <td>{e.amount}</td>
#         </tr>
#         """
#         sr_no += 1

#     html += "</table>"
#     return html


@frappe.whitelist()
def get_gate_items_geu(entry_document, entry_id):
    entry_doc = frappe.get_doc(entry_document, entry_id)
    items = []
    scrap_items =[]
    si_no = 0
    ref_no=''
    security_name=''
    vehicle_number=''
    driver_name=''
    if entry_document=='General DC' and entry_doc.is_return==1:
        party_type=entry_doc.party_type
        party=entry_doc.party
        company=entry_doc.company
        for e in entry_doc.items_:
            si_no = si_no +1
            items.append({
                "item_code": e.item_code,
                "item_name": e.item_name,
                "qty": e.qty,
                "uom": e.uom,
                'box':e.box,
                "pallet":0,
                
            })
    elif entry_document=='Advance Shipping Note':
        party_type="Supplier"
        party=entry_doc.supplier
        ref_no=entry_doc.confirm_supplier_dn
        security_name=entry_doc.security_name
        vehicle_number=entry_doc.vehicle_no
        driver_name=entry_doc.security_name
        company=entry_doc.company
        for e in entry_doc.item_table:
            si_no = si_no +1
        
            items.append({
                "item_code": e.item_code,
                "item_name": e.item_name,
                "qty": e.dis_qty,
                "uom": e.uom,
                'box':int(e.no_of_bins) or 0,
                "pallet":0,

                
            })
        for s in entry_doc.end_bit_scrap:
            scrap_items.append({
                "item_name": s.item_name,
                "qty": s.qty,
                "uom": s.uom,
                'actual_qty':s.actual_qty,
            })
    else:
        for e in entry_doc.items:
            si_no = si_no +1
            if entry_document=='Sales Invoice':
                party_type="Customer"
                party=entry_doc.customer
                company=entry_doc.company
                items.append({
                    "item_code": e.item_code,
                    "item_name": e.item_name,
                    "qty": e.qty,
                    "uom": e.uom,
                    'box':int(e.custom_no_of_boxes) or 0,
                    'pallet':int(e.custom_no_of_pallets) or 0,

                    
                })
            else:
                party_type=entry_doc.party_type
                party=entry_doc.party
                company=entry_doc.company
                items.append({
                    "item_code": e.item_code,
                    "item_name": e.item_name,
                    "qty": e.qty,
                    "uom": e.uom,
                    'box':e.box,
                    'pallet':0
                    
                })
        # frappe.log_error(message=str(si_no),title="si_no")    

    return {
        "items": items,
        "party_type": party_type,
        "party": party,
        "ref_no":ref_no,
        "security_name":security_name,
        "vehicle_number":vehicle_number,
        "driver_name":driver_name,
        "scrap_items":scrap_items,
        "company":company
        
    }



@frappe.whitelist()
def create_gate_entry(doc,method):
	ge=frappe.new_doc('Gate Entry')
	ge.entry_type='Outward'
	ge.entry_against='Sales Invoice'
	ge.ref_no=doc.name
	ge.save(ignore_permissions=True)

@frappe.whitelist()
def delete_gate_entry(doc,method):
	if frappe.db.exists('Gate Entry',{'ref_no':doc.name}):
		ge=frappe.get_doc('Gate Entry',{'ref_no':doc.name})
		ge.delete()
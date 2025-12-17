import frappe
import time
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.model.workflow import apply_workflow
from erpnext.accounts.doctype.tax_withholding_category.tax_withholding_category import get_party_tax_withholding_details
from datetime import datetime
from collections import defaultdict
from frappe.utils.jinja import render_template

from frappe.utils import now_datetime
@frappe.whitelist()
def get_schedule_increase_delivery_html(doc):
    doc = frappe.parse_json(doc)

    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""

        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Production Manager",
            "Pending for PPC",
            "Pending for Material Manager",
            "Pending for Plant Head",
            "Pending for BMD",
            "Approved",
            "Rejected",
            "None"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    schedule_month = doc.get("schedule_month")
    schedule_sums = frappe.db.sql("""
        SELECT customer_code, SUM(schedule_amount_inr) AS total_schedule
        FROM `tabSales Order Schedule`
        WHERE schedule_month = %s
        GROUP BY customer_code
    """, (schedule_month,), as_dict=True)

    # Convert results to dict for fast lookup
    schedule_totals = {d.customer_code: d.total_schedule for d in schedule_sums}
    schedule_sums_item = frappe.db.sql("""
        SELECT item_group, SUM(schedule_amount_inr) AS total_schedule_item
        FROM `tabSales Order Schedule`
        WHERE schedule_month = %s
        GROUP BY item_group
    """, (schedule_month,), as_dict=True)
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    ppc_signature = frappe.db.get_value("Employee", {"user_id": doc.get("ppc")}, "custom_digital_signature")
    # Step 2: Convert result to dictionary for lookup in Jinja
    schedule_totals_item = {d.item_group: d.total_schedule_item for d in schedule_sums_item}
    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>


    <div class="iom-wrapper">
        <table >
    <tr>
        <td style="width: 15%;text-align:center;border-right:hidden;border-bottom:none"><div style="padding-top:8px;border-bottom:none"><img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;"></div></td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:hidden;border-bottom:none" class="header-title" nowrap><div style="padding-top:10px;">INTER OFFICE MEMO (I O M)</div></td>
    <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
        <div style="padding-top:13px;border-bottom:none;">
            <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
                ✔
            </span>
            {{ doc.priority }}
        </div>
    </td>


    </tr>
    
   
    </table>
    {% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

    <table style="width:100%; border-collapse: collapse; margin-top:-1px;">
        <tr>
        <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
            <p style="line-height:1.1">
        <span style="display:inline-block; width:100px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
        <span style="display:inline-block; width:100px;">Dept.To </span>:&nbsp;{{ doc.department_to or '' }}<br><br>

        <span style="display:inline-block; width:100px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
    
    </p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
        <span style="display:inline-block; width:90px;white-space:nowrap">Requested By&nbsp</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;border-right:hidden;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;
            <span style="display: inline-block; width: 70%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>

</table>

        <br>
     {% set label_width = "140px" %} <!-- adjust as needed -->

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Revision Level</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.revision_level or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Schedule Month</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.schedule_month or 'NA' }}</span>
</div>


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason For Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
</div>

        <br>
 {% set grouped = {} %}

{# --- Group by customer_code and sum revised/difference values --- #}
{% for row in doc.approval_schdule_increase %}
    {% set code = row.customer_code %}
    {% if code not in grouped %}
        {% set _ = grouped.update({code: {
            "customer_type": row.customer_type,
            "current_schedule_value": (schedule_totals.get(code) or 0) | float,
            "increase_value": (row.difference_value or 0) | float
        }}) %}
    {% else %}
        {% set _ = grouped[code].update({
            "increase_value": (grouped[code].increase_value or 0) + (row.difference_value or 0)
        }) %}
    {% endif %}
{% endfor %}

<table style="width:100%;border-collapse:collapse;" border="1">
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Customer Type</td>
        <td style="background-color:#fec76f;text-align:center;">Customer Code</td>
        <td style="background-color:#fec76f;text-align:center;">Current Schedule Value</td>
        <td style="background-color:#fec76f;text-align:center;">Revised Schedule Value</td>
        <td style="background-color:#fec76f;text-align:center;">Difference Value</td>
    </tr>

    {% set ns = namespace(total_difference=0) %}
    {% if doc.customer_wise_schedule %}
        {% for row in doc.customer_wise_schedule %}
            {% set ns.total_difference = ns.total_difference + row.difference_value %}
            {# Set up/down arrow #}
            {% if row.difference_value > 0 %}
                {% set arrow = '<span style="color:green;">&#9650;</span>' %} {# ▲ Up arrow (green) #}
            {% elif row.difference_value < 0 %}
                {% set arrow = '<span style="color:red;">&#9660;</span>' %} {# ▼ Down arrow (red) #}
            {% else %}
                {% set arrow = '' %}
            {% endif %}
            <tr>
                <td style="text-align:center;">{{ loop.index }}</td>
                <td style="text-align:left;">{{ row.customer_type or '' }}</td>
                <td style="text-align:left;">{{ row.customer_code }}</td>
                <td style="text-align:right;">{{ frappe.utils.fmt_money(row.current_schedule_value, 1, currency="INR") }}</td>
                <td style="text-align:right;">{{ frappe.utils.fmt_money(row.revised_schedule_value, 1, currency="INR") }}</td>
                <td style="text-align:right;">
                    {{ frappe.utils.fmt_money(row.difference_value, 1, currency="INR") }} {{ arrow | safe }}
                </td>
            </tr>
        {% endfor %}
    {% else %}
    {% for code, data in grouped.items() %}
        {% set current_val = (data.current_schedule_value or 0) | float %}
        {% set increase_val = (data.increase_value or 0) | float %}
        {% set revised_val = current_val + increase_val %}
        {% set diff_val = revised_val - current_val %}
        {% set ns.total_difference = ns.total_difference + diff_val %}

        {# Set up/down arrow #}
        {% if diff_val > 0 %}
            {% set arrow = '<span style="color:green;">&#9650;</span>' %} {# ▲ Up arrow (green) #}
        {% elif diff_val < 0 %}
            {% set arrow = '<span style="color:red;">&#9660;</span>' %} {# ▼ Down arrow (red) #}
        {% else %}
            {% set arrow = '' %}
        {% endif %}

        <tr>
            <td style="text-align:center;">{{ loop.index }}</td>
            <td style="text-align:left;">{{ data.customer_type or '' }}</td>
            <td style="text-align:left;">{{ code }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(current_val, 1, currency="INR") }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(revised_val, 1, currency="INR") }}</td>
            <td style="text-align:right;">
                {{ frappe.utils.fmt_money(diff_val, 1, currency="INR") }} {{ arrow | safe }}
            </td>
        </tr>
    {% endfor %}
    
    {% endif %}
    <tr>
        <td colspan="5" style="text-align:center;font-size:13px;font-weight:bold;">Total</td>
        <td style="text-align:right;font-size:13px;font-weight:bold;">
            {{ frappe.utils.fmt_money(ns.total_difference, 1, currency="INR") }}
        </td>
    </tr>
    
</table>

    <br>
   {% set grouped = {} %}

{# 1. Group and sum by item_group from doc.approval_schdule_increase #}
{% for row in doc.approval_schdule_increase %}
    {% set group = row.item_group %}
    {% if group not in grouped %}
        {% set _ = grouped.update({group: {
            "increase_value": (row.difference_value or 0) | float
        }}) %}
    {% else %}
        {% set _ = grouped[group].update({
            "increase_value": (grouped[group].increase_value or 0) + (row.difference_value or 0)
        }) %}
    {% endif %}
{% endfor %}

<table style="width:100%;border-collapse:collapse;" border="1">
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Group</td>
        <td style="background-color:#fec76f;text-align:center;">Current Schedule Value</td>
        <td style="background-color:#fec76f;text-align:center;">Revised Schedule Value</td>
        <td style="background-color:#fec76f;text-align:center;">Difference Value</td>
    </tr>

    {% set ns = namespace(total_difference1=0) %}

    {% if doc.item_group_wise_schedule %}
    {% for row in doc.item_group_wise_schedule %}
        {% set ns.total_difference1 = ns.total_difference1 + row.difference_value %}
        {% if row.difference_value > 0 %}
            {% set arrow = '<span style="color:green;">&#9650;</span>' %} {# ▲ Up arrow #}
        {% elif row.difference_value < 0 %}
            {% set arrow = '<span style="color:red;">&#9660;</span>' %} {# ▼ Down arrow #}
        {% else %}
            {% set arrow = '' %}
        {% endif %}
        <tr>
            <td style="text-align:center;">{{ loop.index }}</td>
            <td style="text-align:left;">{{ row.item_group }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(row.current_schedule_value, 1,currency="INR") }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(row.revised_schedule_value, 1,currency="INR") }}</td>
            <td style="text-align:right;">
                {{ frappe.utils.fmt_money(row.difference_value, 1,currency="INR") }} {{ arrow | safe }}
            </td>
        </tr>
    {% endfor %}
    {% else %}
    {% for group, data in grouped.items() %}
        {% set current_val = (schedule_totals_item.get(group.strip()) or 0) | float %}
        {% set increase_val = (data.increase_value or 0) | float %}
        {% set revised_val = current_val + increase_val %}
        {% set diff_val = revised_val - current_val %}
        {% set ns.total_difference1 = ns.total_difference1 + diff_val %}

        {% if diff_val > 0 %}
            {% set arrow = '<span style="color:green;">&#9650;</span>' %} {# ▲ Up arrow #}
        {% elif diff_val < 0 %}
            {% set arrow = '<span style="color:red;">&#9660;</span>' %} {# ▼ Down arrow #}
        {% else %}
            {% set arrow = '' %}
        {% endif %}

        <tr>
            <td style="text-align:center;">{{ loop.index }}</td>
            <td style="text-align:left;">{{ group }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(current_val, 1,currency="INR") }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(revised_val, 1,currency="INR") }}</td>
            <td style="text-align:right;">
                {{ frappe.utils.fmt_money(diff_val, 1,currency="INR") }} {{ arrow | safe }}
            </td>
        </tr>
    {% endfor %}
    {% endif %}

    <tr>
        <td colspan="4" style="text-align:center;font-size:13px;font-weight:bold;">Total</td>
        <td style="text-align:right;font-size:13px;font-weight:bold;">
            {{ frappe.utils.fmt_money(ns.total_difference1, 1,currency="INR") }}
        </td>
    </tr>
    
</table>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Total Sales Plan</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ frappe.utils.fmt_money(doc.total_sales_plan, 1,currency="INR") }}</span>
</div>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
    <br>
   
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

   
    {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    {% if signature %}
                        <img src="{{ signature }}" style="height:50px;"><br>
                    {% else %}
                        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;"><br>
                    {% endif %}
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}

        <table>
            <tr>
                <td style="text-align:center;font-weight:bold;font-size:15px;width:12.5%;background-color:#a5a3ac">Prepared</td>
                <td style="text-align:center;font-weight:bold;font-size:15px;width:12.5%;background-color:#a5a3ac">HOD</td>
                <td style="text-align:center;font-weight:bold;font-size:15px;width:12.5%;background-color:#a5a3ac">ERP</td>
                <td style="text-align:center;font-weight:bold;font-size:15px;width:12.5%;background-color:#a5a3ac">Production HOD</td>
                <td style="text-align:center;font-weight:bold;font-size:15px;width:12.5%;background-color:#a5a3ac">PPC</td>
                <td style="text-align:center;font-weight:bold;font-size:15px;width:12.5%;background-color:#a5a3ac">Material Manager</td>
                <td style="text-align:center;font-weight:bold;font-size:15px;width:12.5%;background-color:#a5a3ac">Plant Head</td>
                <td style="text-align:center;font-weight:bold;font-size:15px;width:12.5%;background-color:#a5a3ac">BMD</td>
            </tr>

            <tr style="height:80px;">
                <td style="text-align:center;">
                    {% if py.show_till("Draft") %}
                        {{ show_signature(prepared_signature, doc.date_time, 'Draft', doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
                <td style="text-align:center;">
                    {% if py.show_till("Pending For HOD") %}
                        {{ show_signature(hod_signature, doc.hod_approved_on, 'Pending For HOD', doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
                <td style="text-align:center;">
                    {% if py.show_till("Pending for ERP Team") %}
                        {{ show_signature(erp_signature, doc.erp_team_approved_on, 'Pending for ERP Team', doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
                <td style="text-align:center;">
                    {% if py.show_till("Pending for Production Manager") %}
                        {{ show_signature(pm_signature, doc.production_manager_approved_on, 'Pending for Production Manager', doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
                <td style="text-align:center;">
                    {% if py.show_till("Pending for PPC") %}
                        {{ show_signature(ppc_signature, doc.ppc_approved_on, 'Pending for PPC', doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
                <td style="text-align:center;">
                    {% if py.show_till("Pending for Material Manager") %}
                        {{ show_signature(material_signature, doc.material_manager_approved_on, 'Pending for Material Manager', doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
                <td style="text-align:center;">
                    {% if py.show_till("Pending for Plant Head") %}
                        {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
                <td style="text-align:center;">
                    {% if py.show_till("Pending for BMD") %}
                        {{ show_signature(bmd_signature, doc.bmd_approved_on, 'Pending for BMD', doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
            </tr>
        </table>

        <div style="text-align:left; font-size:12px; margin-top:5px;">
            Note: This document is Digitally Signed
        </div>
    </div>
    """

    # --- 6. Render final HTML ---
    html = render_template(template, {
        "doc": doc,
        "emp_name": emp_name,
        "schedule_totals": schedule_totals,
        "stop_state": stop_state,
        "prepared_signature":prepared_signature,
        "hod_signature" : hod_signature,
        "erp_signature" : erp_signature,
        "material_signature" : material_signature,
        "plant_signature" : plant_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "ppc_signature":ppc_signature,
        "schedule_totals_item": schedule_totals_item,
        "py": {"show_till": show_till}
    })

    return {"html": html}




@frappe.whitelist()
def get_schedule_revise_delivery_html(doc):
    doc = frappe.parse_json(doc)

    # --- 1. Handle rejection remarks ---
    remarks = doc.get("rejection_remarks", [])
    stop_state = None
    if remarks:
        last_remark = remarks[-1]
        stop_state = last_remark.get("previous_workflow_state")
        if last_remark.get("revised_iom")==0:
            stop_state = last_remark.get("previous_workflow_state")
        else:
            stop_state=doc.get("workflow_state")
    else:
        stop_state=doc.get("workflow_state")

    # --- 2. Define Python helper used in Jinja ---
    def show_till(state_name):
        """Return True if signature for this level should be visible."""

        workflow_order = [
            "Draft",
            "Pending For HOD",
            "Pending for ERP Team",
            "Pending for Plant Head",
            "Pending for Finance",
            "Pending for CMD",
            "Approved",
            "Rejected",
            "None"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
        

    # --- 3. Fetch Schedule Totals ---
    schedule_month = doc.get("schedule_month")
    schedule_sums = frappe.db.sql("""
        SELECT supplier_code, SUM(schedule_amount_inr) AS total_schedule
        FROM `tabPurchase Order Schedule`
        WHERE schedule_month = %s
        GROUP BY supplier_code
    """, (schedule_month,), as_dict=True)

    # Convert results to dict for fast lookup
    schedule_totals = {d.supplier_code: d.total_schedule for d in schedule_sums}
    # --- 4. Get Employee Signatures ---
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")

    # --- 5. Jinja Template ---
    template = """
    <style>
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid black; padding: 4px; }
    .header-title { font-size: 18px; font-weight: bold; }
    .iom-wrapper {
        border: 2px solid black;
        padding: 15px;
        margin: 5px;
        border-radius: 8px;
    }
    </style>


    <div class="iom-wrapper">
        <table >
    <tr>
        <td style="width: 15%;text-align:center;border-right:hidden;border-bottom:none"><div style="padding-top:8px;border-bottom:none"><img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;"></div></td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:hidden;border-bottom:none" class="header-title" nowrap><div style="padding-top:10px;">INTER OFFICE MEMO (I O M)</div></td>
<td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:13px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>


    </tr>
    
   
</table>
{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
<table style="width:100%; border-collapse: collapse; margin-top:-1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:100px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:100px;">Requested By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>
    <span style="display:inline-block; width:100px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
</p>

       </td>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-left:none;">
           <p style="line-height:1.1">
            <span style="display:inline-block; width:90px;">Date & Time</span>: {{ frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Doc.No</span>: {{ doc.name }}<br><br>
    <span style="display:inline-block; width:90px;">Instructed By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>

       </p></td>
   </tr>
    
</table>
<table style="margin-top:-30px; width: 100%;">
    <tr>
        <td colspan="6" style="font-weight:bold;font-size:17px;border-right:hidden;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;&nbsp;
            <span style="display: inline-block; width: 70%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>

</table>

        <br>
     {% set label_width = "140px" %} <!-- adjust as needed -->

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Revision Level</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.revision_level or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Schedule Month</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.schedule_month or 'NA' }}</span>
</div>


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason For Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.schedule_revised[0].reason_for_request if doc.schedule_revised and doc.schedule_revised[0].reason_for_request else 'NA' }}</span>
</div>

        <br>
    
{% set grouped = {} %}

{# --- Group by supplier_code and sum revised values --- #}
{% for row in doc.schedule_revised %}
    {% set code = row.supplier_code %}
    {% if code not in grouped %}
        {% set _ = grouped.update({code: {
            "supplier_type": row.supplier_type,
            "supplier_name": row.supplier_name,
            "revised_schedule_valueinr": row.revised_schedule_valueinr or 0
        }}) %}
    {% else %}
        {% set _ = grouped[code].update({
            "revised_schedule_valueinr": (grouped[code].revised_schedule_valueinr or 0) + (row.revised_schedule_valueinr or 0)
        }) %}
    {% endif %}
{% endfor %}

<table style="width:100%;border-collapse:collapse;" border="1">
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Supplier Type</td>
        <td style="background-color:#fec76f;text-align:center;">Supplier Name</td>
        <td style="background-color:#fec76f;text-align:center;">Current Schedule Value</td>
        <td style="background-color:#fec76f;text-align:center;">Revised Schedule Value</td>
        <td style="background-color:#fec76f;text-align:center;">Difference Value</td>
    </tr>

    {% set ns = namespace(total_difference=0) %}
    {% if doc.supplier_wise_schedule %}
        {% for row in doc.supplier_wise_schedule %}
            {% set ns.total_difference = ns.total_difference + row.difference_value %}
            {# Set up/down arrow #}
            {% if row.difference_value > 0 %}
                {% set arrow = '<span style="color:green;">&#9650;</span>' %} {# ▲ Up arrow (green) #}
            {% elif row.difference_value < 0 %}
                {% set arrow = '<span style="color:red;">&#9660;</span>' %} {# ▼ Down arrow (red) #}
            {% else %}
                {% set arrow = '' %}
            {% endif %}
            {%set supplier_name=frappe.db.get_value("Supplier",{"supplier_code":row.supplier_code},"supplier_name")%}
            <tr>
                <td style="text-align:center;">{{ loop.index }}</td>
                <td style="text-align:left;">{{ row.supplier_type or '' }}</td>
                <td style="text-align:left;">{{ supplier_name or '' }}</td>
                <td style="text-align:right;">{{ frappe.utils.fmt_money(row.current_schedule_value, 1, currency="INR") }}</td>
                <td style="text-align:right;">{{ frappe.utils.fmt_money(row.revised_schedule_value, 1, currency="INR") }}</td>
                <td style="text-align:right;">
                    {{ frappe.utils.fmt_money(row.difference_value, 1, currency="INR") }} {{ arrow | safe }}
                </td>
            </tr>
        {% endfor %}
    {% else %}
   
    {% for code, data in grouped.items() %}
        {% set current_val = (schedule_totals.get(code) if schedule_totals else 0) | float %}
        {% set increase_val = (data.increase_value or 0) | float %}
        {% set revise_diff_val = current_val - increase_val %}
        {% set revised_val = current_val + revise_diff_val %}
        {% set diff_val = revised_val - current_val %}
        {% set ns.total_difference = ns.total_difference + diff_val %}

        {# Up/down arrow #}
        {% if diff_val > 0 %}
            {% set arrow = '<span style="color:green;">&#9650;</span>' %}
        {% elif diff_val < 0 %}
            {% set arrow = '<span style="color:red;">&#9660;</span>' %}
        {% else %}
            {% set arrow = '' %}
        {% endif %}

        <tr>
            <td style="text-align:center;">{{ ns.counter }}</td>
            <td style="text-align:left;">{{ data.supplier_type or '' }}</td>
            <td style="text-align:left;">{{ data.supplier_name or '' }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(current_val, 1, currency="INR") }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(revised_val, 1, currency="INR") }}</td>
            <td style="text-align:right;">
                {{ frappe.utils.fmt_money(diff_val, 1, currency="INR") }} {{ arrow | safe }}
            </td>
        </tr>
        {% set ns.counter = ns.counter + 1 %}
    {% endfor %}
    {%endif%}
    <tr>
        <td colspan="5" style="text-align:center;font-size:13px;font-weight:bold;">Total</td>
        <td style="text-align:right;font-size:13px;font-weight:bold;">
            {{ frappe.utils.fmt_money(ns.total_difference, 1, currency="INR") }}
        </td>
    </tr>
</table>
<div style="width:100%; margin-top:10px; display:flex; justify-content:space-between; gap:20px;">

    {% if doc.approval_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#008000; text-decoration: underline;">Approved Remarks</b>
        <br><br>
        {% for r in doc.approval_remarks %}
        {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}
            ● <b>{{ user_full_name or r.user }}</b> -{{ r.remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

    {% if doc.rejection_remarks %}
    <div style="
        width:50%;
        padding:10px;
        border:1px solid #000;
        box-sizing:border-box;
    ">
        <b style="color:#FF0000; text-decoration: underline;">Rejected Remarks</b>
        <br><br>
        {% for r in doc.rejection_remarks %}
                {% set user_full_name = frappe.db.get_value("Employee",{ "user_id":r.user}, "employee_name") %}

            ●<b>{{ user_full_name or r.user }}</b> : {{ r.rejection_remarks or '' }}
            {% if not loop.last %}<br>{% endif %}
        {% endfor %}
    </div>
    {% endif %}

</div>
<br>

        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
        {# ---- SIGNATURE SECTION ---- #}
        {% macro show_signature(signature, date_field, workflow_state, current_workflow_state, stop_state) %}
            {% if date_field %}
                {% if current_workflow_state == 'Rejected' and workflow_state == stop_state %}
                    <img src="/files/Rejected.jpg" style="height:50px;"><br>
                {% else %}
                    <img src="{{ signature or '/files/Screenshot 2025-09-22 141452.png' }}" style="height:50px;"><br>
                {% endif %}
                {% set formatted_date = frappe.utils.format_datetime(date_field, "dd-MM-yyyy HH:mm:ss") %}
                <span style="white-space:nowrap; font-size:9px;">{{ formatted_date }}</span>
            {% endif %}
        {% endmacro %}

        <table>
            <tr>
                <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Prepared</td>
                <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">HOD</td>
                <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">ERP Team</td>
                <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Plant Head</td>
                <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Finance</td>
                <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">CMD</td>
            </tr>

            <tr style="height:80px;">
                <td style="text-align:center;">
                    {% if py.show_till("Draft") %}
                        {{ show_signature(prepared_signature, doc.date_time, "Draft", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
                <td style="text-align:center;">
                    {% if py.show_till("Pending For HOD") %}
                        {{ show_signature(hod_signature, doc.hod_approved_on, "Pending For HOD", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
                <td style="text-align:center;">
                    {% if py.show_till("Pending for ERP Team") %}
                        {{ show_signature(erp_signature, doc.erp_team_approved_on, "Pending for ERP Team", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
                
                <td style="text-align:center;">
                    {% if py.show_till("Pending for Plant Head") %}
                        {{ show_signature(plant_signature, doc.plant_head_approved_on, "Pending for Plant Head", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
                <td style="text-align:center;">
                    {% if py.show_till("Pending for Finance") %}
                        {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
                <td style="text-align:center;">
                    {% if py.show_till("Pending for CMD") %}
                        {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
                    {% endif %}
                </td>
            </tr>
        </table>

        <div style="text-align:left; font-size:12px; margin-top:5px;">
            Note: This document is Digitally Signed
        </div>

    </div>
    """

    # --- 6. Render final HTML ---
    html = render_template(template, {
        "doc": doc,
        "emp_name": emp_name,
        "schedule_totals": schedule_totals,
        "stop_state": stop_state,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "py": {"show_till": show_till}
    })

    return {"html": html}

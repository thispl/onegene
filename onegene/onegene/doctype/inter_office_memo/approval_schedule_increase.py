import frappe
from frappe.utils.jinja import render_template
@frappe.whitelist()
def get_schedule_increase_delivery_html(doc):
    doc = frappe.parse_json(doc)
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
            <td style="text-align:right;">{{ frappe.utils.fmt_money(current_val, 2, currency="INR") }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(revised_val, 2, currency="INR") }}</td>
            <td style="text-align:right;">
                {{ frappe.utils.fmt_money(diff_val, 2, currency="INR") }} {{ arrow | safe }}
            </td>
        </tr>
    {% endfor %}

    <tr>
        <td colspan="5" style="text-align:center;font-size:13px;font-weight:bold;">Total</td>
        <td style="text-align:right;font-size:13px;font-weight:bold;">
            {{ frappe.utils.fmt_money(ns.total_difference, 2, currency="INR") }}
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
            <td style="text-align:right;">{{ frappe.utils.fmt_money(current_val, 2,currency="INR") }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(revised_val, 2,currency="INR") }}</td>
            <td style="text-align:right;">
                {{ frappe.utils.fmt_money(diff_val, 2,currency="INR") }} {{ arrow | safe }}
            </td>
        </tr>
    {% endfor %}

    <tr>
        <td colspan="4" style="text-align:center;font-size:13px;font-weight:bold;">Total</td>
        <td style="text-align:right;font-size:13px;font-weight:bold;">
            {{ frappe.utils.fmt_money(ns.total_difference1, 2,currency="INR") }}
        </td>
    </tr>
    
</table>

    <br>
    
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
    <table>
  <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">HOD</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">ERP</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Material Manager</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Plant Head</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">BMD</td>

</tr>


    <tr style="height: 80px;">
     {% set erp_signature = frappe.db.get_value("Employee", {"user_id":doc.erp_team}, "custom_digital_signature") %}
     {% set prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.owner}, "custom_digital_signature") %}
       {% set hod_signature = frappe.db.get_value("Employee", {"name": doc.reports_to}, "custom_digital_signature") %}
       {% set bmd_signature = frappe.db.get_value("Employee", {"name":"BMD01"}, "custom_digital_signature") %}
       {% set plant_signature = frappe.db.get_value("Employee", {"name":"S0004"}, "custom_digital_signature") %}
       {% set material_signature = frappe.db.get_value("Employee", {"name":"S0004"}, "custom_digital_signature") %}
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state == "Draft" or "Pending For HOD"  or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Approved" or doc.workflow_state=="Pending for Material Manager"%}
           {% if prepared_signature %}
        <img src="{{ prepared_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
     {% if doc.date_time %}
{% set formatted_date = frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state=="Pending for Plant Head" or doc.workflow_state=="Pending for ERP Team" or doc.workflow_state == "Approved" or doc.workflow_state == "Pending for BMD" or doc.workflow_state=="Pending for Material Manager"%}
            {% if hod_signature %}
        <img src="{{ hod_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
    {% if doc.hod_approved_on %}
{% set formatted_date = frappe.utils.format_datetime(doc.hod_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state=="Pending for Plant Head" or doc.workflow_state == "Approved" or doc.workflow_state == "Pending for BMD" or doc.workflow_state=="Pending for Material Manager"%}
            {% if erp_signature %}
        <img src="{{ erp_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
    {% if doc.erp_team_approved_on %}
        {% set formatted_date = frappe.utils.format_datetime(doc.erp_team_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>

    {% endif %}
    {% endif %}
    </td>
    
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state == "Approved" or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state == "Pending for BMD" %}
            {% if material_signature %}
        <img src="{{ material_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
    {% if doc.material_manager_approved_on %}
                {% set formatted_date = frappe.utils.format_datetime(doc.material_manager_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>

    {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state == "Approved" or doc.workflow_state == "Pending for BMD" %}
            {% if plant_signature %}
        <img src="{{ plant_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
    {% if doc.plant_head_approved_on %}
{% set formatted_date = frappe.utils.format_datetime(doc.plant_head_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>

    {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state == "Approved"%}
            {% if bmd_signature %}
        <img src="{{ bmd_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">


    {% endif %}
    <br>
    {% if doc.bmd_approved_on %}
{% set formatted_date = frappe.utils.format_datetime(doc.bmd_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    
</tr>

</table>
<div style="text-align:left; font-size:12px;margin-top:5px;">
    Note: This document is Digitally Signed
</div>

    </div>
    """
    html = render_template(template, {
    "doc": doc,
    "schedule_totals": schedule_totals,
    "schedule_totals_item": schedule_totals_item
})

    # html = render_template(template, {"doc": doc, "schedule_totals": schedule_totals})

    # html = render_template(template, {"doc": doc})
    return {"html": html}

@frappe.whitelist()
def get_air_shipment_material_html(doc):
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
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Pending for SMD",
            "Approved",
            "Rejected",
            "None"]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")

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
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
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
 {% set label_width = "130px" %} <!-- adjust as needed -->
 <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier_group or 'NA' }}</span>
</div>
{% set supplier_name=frappe.db.get_value("Supplier",{"name":doc.supplier},"supplier_name") %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ supplier_name or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
{% set forwarder_name=frappe.db.get_value("Supplier",{"name":doc.forwarder_name},"supplier_name") %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Forwarder Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{forwarder_name or 'NA' }}</span>

</div>

<br>

<br>
<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>

        </tr>
    {% for i in doc.approval_shipment_materail%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap">{{i.part_no or ''}}</td>
        <td style="text-align:left;">{{i.part_name or '' }}</td>
        <td style="text-align:center;white-space:nowrap">{{i.qty or '' }}</td>

    </tr>
    {%endfor%}
   </table>
    <br>
    <table>
    <tr>
    <td style="text-align:center">Fright cost if sea({{doc.currency or 'NA'}})<br><b>{{frappe.utils.fmt_money(doc.fright_cost_if_sea_inr  or 0 , currency="INR")}}</b></td>
    <td style="text-align:center">Fright cost if air({{doc.currency or 'NA'}})<br><b>{{frappe.utils.fmt_money(doc.fright_cost_if_air_inr  or 0 , currency="INR")}}</b></td>
    <td style="text-align:center">Loss Cost(INR)<br><b>{{frappe.utils.fmt_money(doc.total_loss_value  or 0 , currency="INR")}}</b></td>

    </tr>
    </table>
    <br>
        <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Remarks</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
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
    <table>
     <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">GM</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">Finance</td>
    <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">BMD</td>
    <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">CMD</td>
    <td style="text-align:center; font-weight:bold; font-size:15px; width:12.5%;background-color:#a5a3ac">SMD</td>

</tr>

     <tr style="height: 80px;">
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
     
    <td style="text-align:center;font-size:15px;">
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
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for SMD") %}
            {{ show_signature(smd_signature, doc.smd_approved_on, "Pending for SMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}




@frappe.whitelist()
def get_new_business_jo_html(doc):
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
            "Pending for Marketing Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")
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
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>

{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
<table style="width:100%; border-collapse: collapse; margin-top:1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
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
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "140px" %} <!-- adjust as needed -->

{% set supplier_name=frappe.db.get_value("Supplier",{"name":doc.supplier},"supplier_name") %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{supplier_name or 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">PO No & PO Date</span>
    <span>
        :&nbsp;&nbsp;&nbsp;&nbsp;
        {{doc.po_no or 'NA'}}/{{frappe.utils.formatdate(doc.po_date, "dd-MM-yyyy") or 'NA'}}
    </span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.new_business_jo[0].hsn_code if doc.new_business_jo and doc.new_business_jo[0].hsn_code else 'NA' }}</span>
</div>


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Order Type</span>
    <span>:&nbsp;&nbsp;&nbsp;
        {{doc.order_type or 'NA' }}
    </span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason For Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{doc.subject or 'NA'}}</span>
</div>

<br>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">UOM</td>
        <td style="background-color:#fec76f;text-align:center;">Operation</td>
        <td style="background-color:#fec76f;text-align:center;">Qty</td>
        <td style="background-color:#fec76f;text-align:center;">PO Price({{doc.currency or ''}})</td>
        <td style="background-color:#fec76f;text-align:center;">Value({{doc.currency or ''}})</td>

        </tr>
    {% for i in doc.new_business_jo%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.item_code or ''}}</td>
        <td style="text-align:left;">{{i.item_name or ''}}</td>
        <td style="text-align:center;white-space:nowrap;">{{i.uom or ''}}</td>
        <td style="text-align:left;">{{i.operation_data or ''}}</td>
        <td style="text-align:center;white-space:nowrap;">{{i.qty or ''}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.po_price or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.value or 0 , currency=doc.currency)}}</td>

    </tr>
    {%endfor%}
    <tr><td colspan=7 style="text-align:center;font-weight:bold">Total PO Value</td>
    <td colspan=1 style="text-align:right;font-weight:bold">{{frappe.utils.fmt_money(doc.total_po_value or 0 , currency=doc.currency) }}</td></tr>
    </table>
<br>
    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:50%;font-weight:bold;">TERMS & CONDITIONS</span>
</div><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Payment Terms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Incoterms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Duties and Taxes</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.duties_and_taxes or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Freight</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.freight or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Scrap</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.scrap or 'NA' }}</span>
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
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Marketing HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
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
     
    <td style="text-align:center;font-size:15px;">
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
        {% if py.show_till("Pending for Marketing Manager") %}
            {{ show_signature(mm_signature, doc.marketing_manager_approved_on, 'Pending for Marketing Manager', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def get_price_revision_jo_html(doc):
    doc = frappe.parse_json(doc)
    
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
       <table>
    <tr>
        <td style="width: 15%;text-align:center;border-right:none;border-bottom:none;border-bottom:bold">
            <div style="padding-top:8px;">
                <img src="/files/ci_img.png" alt="Logo" style="max-width: 60%;">
            </div>
        </td>
        <td style="width:30%;font-size:20px;text-align:center;border-right:none;border-bottom:none;padding-top:14px" nowrap>
            <div class="header-title" style="padding-top:8px">INTER OFFICE MEMO (I O M)</div>         </td>
        <td style="width:15%;white-space:nowrap;border-bottom:none;font-weight:bold;">
    <div style="padding-top:10px;border-bottom:none;">
        <span style="border: 2px solid black; width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; margin-right: 5px;">
            ✔
        </span>
        {{ doc.priority }}
    </div>
</td>



    </tr>
</table>

{% set emp_name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
<table style="width:100%; border-collapse: collapse; margin-top:1px;">
    <tr>
       <td style="width:50%; border:1px solid black; vertical-align:top; padding:5px; border-bottom:none;border-right:none;">
           <p style="line-height:1.1">
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
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
        <td colspan="6" style="font-weight:bold;font-size:17px;">
            SUBJECT&nbsp;&nbsp;&nbsp;:&nbsp;
            <span style="display: inline-block; width: 60%; text-align: center;">
                {{ doc.iom_type or 'NA' }}
            </span>
        </td>
    </tr>
</table><br>


{% set label_width = "140px" %} <!-- adjust as needed -->
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier_group or 'NA' }}</span>
</div>
{% set supplier_name=frappe.db.get_value("Supplier",{"name":doc.supplier},"supplier_name") %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ supplier_name or 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">PO No & PO Date</span>
    <span>
        :&nbsp;&nbsp;&nbsp;&nbsp;
        {% if doc.price_revision_jo and doc.price_revision_jo[0] %}
            {{ 
                doc.price_revision_jo[0].po_no 
                if doc.price_revision_jo[0].po_no 
                else 'NA'
            }}
            &nbsp;/&nbsp;
            {{ frappe.utils.formatdate(doc.price_revision_jo[0].date, "dd-MM-yyyy") if doc.price_revision_jo[0].date else 'NA' }}
        {% else %}
            NA / NA
        {% endif %}
    </span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.price_revision_jo[0].hsn_code if doc.price_revision_jo and doc.price_revision_jo[0].hsn_code else 'NA' }}</span>
</div>


<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason For Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.price_revision_jo[0].reason_for_request if doc.price_revision_jo and doc.price_revision_jo[0].reason_for_request else 'NA' }}</span>
</div>

<br>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">UOM</td>
        <td style="background-color:#fec76f;text-align:center;">Operation</td>
        <td style="background-color:#fec76f;text-align:center;">Current Price ({{doc.currency or ''}})</td>
        <td style="background-color:#fec76f;text-align:center;">Revised Price({{doc.currency or ''}})</td>
        <td style="background-color:#fec76f;text-align:center;">Diff({{doc.currency or ''}})</td>

        </tr>
    {% for i in doc.price_revision_jo%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.part_no or ''}}</td>
        <td style="text-align:left;">{{i.part_name or ''}}</td>
        <td style="text-align:center;white-space:nowrap;">{{i.uom or ''}}</td>
        <td style="text-align:left;">{{i.operation_data or ''}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.po_price or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.new_price or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.increase_price or 0 , currency=doc.currency)}}</td>

    </tr>
    {%endfor%}
    </table>
<br>
    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:50%;font-weight:bold;">TERMS & CONDITIONS</span>
</div><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Payment Terms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Incoterms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Duties and Taxes</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.duties_and_taxes or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Freight</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.freight or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Scrap</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.scrap or 'NA' }}</span>
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
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Marketing HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">CMD</td>
</tr>


    <tr style="height: 80px;">
    {% set prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.owner}, "custom_digital_signature") %}
       {% set hod_signature = frappe.db.get_value("Employee", {"name": doc.reports_to}, "custom_digital_signature") %}
       {% set erp_signature = frappe.db.get_value("Employee", {"name":"S0330"}, "custom_digital_signature") %}
       {% set plant_signature = frappe.db.get_value("Employee", {"name":"S0004"}, "custom_digital_signature") %}
       {% set gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature") %}
       {% set marketing_signature = frappe.db.get_value("Employee", {"name":"S0116"}, "custom_digital_signature") %}
        {% set finance_signature = frappe.db.get_value("Employee", {"name":"S0189"}, "custom_digital_signature") %}
        {% set bmd_signature = frappe.db.get_value("Employee", {"name":"BMD01"}, "custom_digital_signature") %}
        {% set cmd_signature = frappe.db.get_value("Employee", {"name":"CMD01"}, "custom_digital_signature") %}
    <td style="text-align:center;font-size:15px;">
        {% if doc.workflow_state=="Draft" or doc.workflow_state=="Pending for Marketing Manager" or doc.workflow_state == "Pending For HOD" or doc.workflow_state=="Pending for BMD" or doc.workflow_state=="Pending for Finance" or doc.workflow_state=="Pending for GM" or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state=="Pending for CMD" or doc.workflow_state == "Pending for ERP Team" or doc.workflow_state == "Approved"%}
             {% if prepared_signature %}
        <img src="{{ prepared_signature }}" style="height:50px;">
          {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">
    {% endif %}
    {% if doc.date_time %}
        {% set formatted_date = frappe.utils.formatdate(doc.date_time, "dd-MM-yyyy") %}
        {% set formatted_time = frappe.utils.format_datetime(doc.date_time, "HH:mm:ss") %}
          <span style="font-size:9px; line-height:1;white-space:nowrap">{{ formatted_date }}&nbsp;{{ formatted_time }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
        {% if doc.workflow_state=="Pending for BMD" or doc.workflow_state=="Pending for Marketing Manager" or doc.workflow_state=="Pending for Finance" or doc.workflow_state=="Pending for GM" or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state=="Pending for CMD" or doc.workflow_state == "Pending for ERP Team" or doc.workflow_state == "Approved"%}
             {% if hod_signature %}
        <img src="{{ hod_signature }}" style="height:50px;">
          {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">
    {% endif %}
    <br>
     {% if doc.hod_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.hod_approved_on, "dd-MM-yyyy") %}
        {% set formatted_time = frappe.utils.format_datetime(doc.hod_approved_on, "HH:mm:ss") %}
          <span style="font-size:9px; line-height:1;white-space:nowrap">{{ formatted_date }}&nbsp;{{ formatted_time }}</span>

            {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
        {% if doc.workflow_state == "Pending for Plant Head" or doc.workflow_state=="Pending for Marketing Manager" or doc.workflow_state == "Pending for GM" or doc.workflow_state == "Pending for Finance" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
            {% if erp_signature %}
        <img src="{{ erp_signature }}" style="height:50px;">
          {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">
    {% endif %}
    <br>
     {% if doc.erp_team_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.erp_team_approved_on, "dd-MM-yyyy") %}
        {% set formatted_time = frappe.utils.format_datetime(doc.erp_team_approved_on, "HH:mm:ss") %}
          <span style="font-size:9px; line-height:1;white-space:nowrap">{{ formatted_date }}&nbsp;{{ formatted_time }}</span>

            {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
        {% if doc.workflow_state == "Pending for Plant Head" or doc.workflow_state == "Pending for GM" or doc.workflow_state == "Pending for Finance" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
            {% if marketing_signature %}
        <img src="{{ marketing_signature }}" style="height:50px;">
          {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">
    {% endif %}
    <br>
     {% if doc.marketing_manager_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.marketing_manager_approved_on, "dd-MM-yyyy") %}
        {% set formatted_time = frappe.utils.format_datetime(doc.marketing_manager_approved_on, "HH:mm:ss") %}
          <span style="font-size:9px; line-height:1;white-space:nowrap">{{ formatted_date }}&nbsp;{{ formatted_time }}</span>

            {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
        {% if doc.workflow_state == "Pending for GM"  or doc.workflow_state == "Pending for Finance" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
            {% if plant_signature %}
        <img src="{{ plant_signature }}" style="height:50px;">
          {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">
    {% endif %}
    <br>
    {% if doc.plant_head_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.plant_head_approved_on, "dd-MM-yyyy") %}
        {% set formatted_time = frappe.utils.format_datetime(doc.plant_head_approved_on, "HH:mm:ss") %}
          <span style="font-size:9px; line-height:1;white-space:nowrap">{{ formatted_date }}&nbsp;{{ formatted_time }}</span>

            {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
        {% if doc.workflow_state == "Pending for Finance" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
             {% if gm_signature %}
        <img src="{{ gm_signature }}" style="height:50px;">
          {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">
    {% endif %}
    <br>
      {% if doc.gm_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.gm_approved_on, "dd-MM-yyyy") %}
        {% set formatted_time = frappe.utils.format_datetime(doc.gm_approved_on, "HH:mm:ss") %}
          <span style="font-size:9px; line-height:1;white-space:nowrap">{{ formatted_date }}&nbsp;{{ formatted_time }}</span>

    {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
        {% if doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
             {% if finance_signature %}
        <img src="{{ finance_signature }}" style="height:50px;">
          {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">
    {% endif %}
    <br>
    {% if doc.finance_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.finance_approved_on, "dd-MM-yyyy") %}
        {% set formatted_time = frappe.utils.format_datetime(doc.finance_approved_on, "HH:mm:ss") %}
          <span style="font-size:9px; line-height:1;white-space:nowrap">{{ formatted_date }}&nbsp;{{ formatted_time }}</span>

    {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
        {% if doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved"%}
             {% if bmd_signature %}
        <img src="{{ bmd_signature }}" style="height:50px;">
          {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">
    {% endif %}
    <br>
   {% if doc.bmd_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.bmd_approved_on, "dd-MM-yyyy") %}
        {% set formatted_time = frappe.utils.format_datetime(doc.bmd_approved_on, "HH:mm:ss") %}
          <span style="font-size:9px; line-height:1;white-space:nowrap">{{ formatted_date }}&nbsp;{{ formatted_time }}</span>

    {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
        {% if doc.workflow_state == "Approved" %}
           {% if cmd_signature %}
        <img src="{{ cmd_signature }}" style="height:50px;">
          {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">
    {% endif %}
    <br>
     {% if doc.cmd_approved_on %}
        {% set formatted_date = frappe.utils.formatdate(doc.cmd_approved_on, "dd-MM-yyyy") %}
        {% set formatted_time = frappe.utils.format_datetime(doc.cmd_approved_on, "HH:mm:ss") %}
          <span style="font-size:9px; line-height:1;white-space:nowrap">{{ formatted_date }}&nbsp;{{ formatted_time }}</span>

    {% endif %}
        {% endif %}
    </td>
</tr>

</table>
<div style="text-align:left; font-size:12px;margin-top:5px;">
    Note: This document is Digitally Signed
</div>
    </div>
    """

    html = render_template(template, {"doc": doc})
    return {"html": html}

@frappe.whitelist()
def get_schedule_revise_delivery_html(doc):
    doc = frappe.parse_json(doc)
    schedule_month = doc.get("schedule_month")
    schedule_sums = frappe.db.sql("""
        SELECT supplier_code, SUM(schedule_amount_inr) AS total_schedule
        FROM `tabPurchase Order Schedule`
        WHERE schedule_month = %s
        GROUP BY supplier_code
    """, (schedule_month,), as_dict=True)

    # Convert results to dict for fast lookup
    schedule_totals = {d.supplier_code: d.total_schedule for d in schedule_sums}
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

    {% set ns = namespace(counter=1, total_difference=0) %}

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
            <td style="text-align:right;">{{ frappe.utils.fmt_money(current_val, 2, currency="INR") }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(revised_val, 2, currency="INR") }}</td>
            <td style="text-align:right;">
                {{ frappe.utils.fmt_money(diff_val, 2, currency="INR") }} {{ arrow | safe }}
            </td>
        </tr>
        {% set ns.counter = ns.counter + 1 %}
    {% endfor %}

    <tr>
        <td colspan="5" style="text-align:center;font-size:13px;font-weight:bold;">Total</td>
        <td style="text-align:right;font-size:13px;font-weight:bold;">
            {{ frappe.utils.fmt_money(ns.total_difference, 2, currency="INR") }}
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
    <table>
  <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">HOD</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Finance</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">CMD</td>

</tr>


    <tr style="height: 80px;">
     {% set erp_signature = frappe.db.get_value("Employee", {"name":"S0330"}, "custom_digital_signature") %}
     {% set prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.owner}, "custom_digital_signature") %}
       {% set hod_signature = frappe.db.get_value("Employee", {"name": doc.reports_to}, "custom_digital_signature") %}
       {% set bmd_signature = frappe.db.get_value("Employee", {"name":"BMD01"}, "custom_digital_signature") %}
       {% set plant_signature = frappe.db.get_value("Employee", {"name":"S0004"}, "custom_digital_signature") %}
              {% set finance_signature = frappe.db.get_value("Employee", {"name":"S0189"}, "custom_digital_signature") %}
        {% set cmd_signature = frappe.db.get_value("Employee", {"name":"CMD01"}, "custom_digital_signature") %}

        {% set material_signature = frappe.db.get_value("Employee", {"name":"S0004"}, "custom_digital_signature") %}
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state == "Draft" or "Pending For HOD"  or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state == "Pending for CMD" or doc.workflow_state == "Approved" or doc.workflow_state=="Pending for ERP Team" or doc.workflow_state=="Pending for Finance"%}
           {% if prepared_signature %}
        <img src="{{ prepared_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
     {% if doc.date_time %}
{% set formatted_date = frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state=="Pending for Plant Head" or doc.workflow_state=="Pending for ERP Team" or doc.workflow_state == "Approved" or doc.workflow_state == "Pending for CMD" or doc.workflow_state=="Pending for Finance"%}
            {% if hod_signature %}
        <img src="{{ hod_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
    {% if doc.hod_approved_on %}
{% set formatted_date = frappe.utils.format_datetime(doc.hod_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state=="Pending for Plant Head" or doc.workflow_state == "Approved" or doc.workflow_state == "Pending for CMD" or doc.workflow_state=="Pending for Finance"%}
            {% if erp_signature %}
        <img src="{{ erp_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
    {% if doc.erp_team_approved_on %}
        {% set formatted_date = frappe.utils.format_datetime(doc.erp_team_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>

    {% endif %}
    {% endif %}
    </td>
    
       <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state == "Approved" or doc.workflow_state == "Pending for CMD" or doc.workflow_state=="Pending for Finance" %}
            {% if plant_signature %}
        <img src="{{ plant_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
    {% if doc.plant_head_approved_on %}
{% set formatted_date = frappe.utils.format_datetime(doc.plant_head_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>

    {% endif %}
        {% endif %}
    </td>
     <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state == "Approved" or doc.workflow_state == "Pending for CMD" %}
            {% if finance_signature %}
        <img src="{{ finance_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
    {% if doc.finance_approved_on %}
                {% set formatted_date = frappe.utils.format_datetime(doc.finance_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>

    {% endif %}
        {% endif %}
    </td>

    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state == "Approved"%}
            {% if cmd_signature %}
        <img src="{{ cmd_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">


    {% endif %}
    <br>
    {% if doc.cmd_approved_on %}
{% set formatted_date = frappe.utils.format_datetime(doc.cmd_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    
</tr>

</table>
<div style="text-align:left; font-size:12px;margin-top:5px;">
    Note: This document is Digitally Signed
</div>

    </div>
    """
    html = render_template(template, {"doc": doc, "schedule_totals": schedule_totals})

    # html = render_template(template, {"doc": doc})
    return {"html": html}

@frappe.whitelist()
def get_product_conversion_material_html(doc):
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
            "Pending for Marketing Manager",
            "Pending for Quality Team",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")
    quality_signature = frappe.db.get_value("Employee", {"user_id": doc.get("quality_manager")}, "custom_digital_signature")
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
    <span style="display:inline-block; width:90px;">Requested By</span>: &nbsp;{{ doc.employee_name or '' }}<br><br>
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



<div style="margin-bottom:2px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;"><u>Input Details</u></span>
</div>

    <table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
    <td style="background-color:#fec76f;text-align:center;">UOM</td>
        <td style="background-color:#fec76f;text-align:center;">Warehouse</td>
        <td style="background-color:#fec76f;text-align:center;">Stock Qty</td>

        <td style="background-color:#fec76f;text-align:center;">Input Qty</td>
        </tr>
    {% for i in doc.product_convertion%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.part_nofrom or ''}}</td>
        <td style="text-align:left">{{i.part_namefrom or '' }}</td>
         <td style="text-align:center;white-space:nowrap;">{{i.uom or ''}}</td>
        <td style="text-align:center;">{{i.warehouse_from or '' }}</td>
        <td style="text-align:center;">{{i.stock_qty or '0' }}</td>

        <td style="text-align:center;">{{i.qtyfrom or '' }}</td>

    </tr>
    {%endfor%}
    </table>
    <br>
    <div style="margin-bottom: 2px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;"><u>Converted Products</u></span>
</div>
    <table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
         <td style="background-color:#fec76f;text-align:center;">UOM</td>
        <td style="background-color:#fec76f;text-align:center;">Warehouse</td>
                <td style="background-color:#fec76f;text-align:center;">Stock Qty</td>
        <td style="background-color:#fec76f;text-align:center;">Converted Qty</td>
        </tr>
    {% for i in doc.table_mugs%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left">{{i.part_nofrom or ''}}</td>
        <td style="text-align:left">{{i.part_namefrom or '' }}</td>
          <td style="text-align:center;white-space:nowrap;">{{i.uom or ''}}</td>
        <td style="text-align:center;">{{i.warehouse_from or '' }}</td>
                <td style="text-align:center;">{{i.stock_qty or '0' }}</td>

        <td style="text-align:center;">{{i.qtyfrom or '' }}</td>

    </tr>
    {%endfor%}
    </table><br>
    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:160px;font-weight:bold;white-space:nowrap">Reason For Conversion</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
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
    <table>
  <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">HOD</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">ERP Team</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Quality</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">BMD</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">CMD</td>

</tr>


    <tr style="height: 80px;">
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
     
    <td style="text-align:center;font-size:15px;">
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
        {% if py.show_till("Pending for Quality Team") %}
            {{ show_signature(quality_signature, doc.quality_team_approved_on, 'Pending for Quality Team', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "quality_signature":quality_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def get_proto_sample_material_html(doc):
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
            "Pending for Marketing Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")
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
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
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
        <br><br>
     {% set label_width = "140px" %} <!-- adjust as needed -->

     <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier_group or 'NA' }}</span>
</div>
{% set supplier_name=frappe.db.get_value("Supplier",{"name":doc.supplier},"supplier_name") %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ supplier_name or 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Quotation No & Date</span>
        {% if doc.table_cpri%}
    <span>
        :&nbsp;&nbsp;&nbsp;&nbsp;
        {% if doc.table_cpri and doc.table_cpri[0] %}
            {{ 
               doc.table_cpri[0].po_no_new if doc.table_cpri[0].po_no_new else 'NA'
            }}
            &nbsp;/&nbsp;
            {{ frappe.utils.formatdate(doc.table_cpri[0].po_date, "dd-MM-yyyy") if doc.table_cpri[0].po_date else 'NA' }}
        {% else %}
            NA / NA
        {% endif %}
    </span>
    {%else%}
    <span>
        :&nbsp;&nbsp;&nbsp;&nbsp;
        {% if doc.proto_sample_existing and doc.proto_sample_existing[0] %}
            {{ 
               doc.proto_sample_existing[0].po_no_new if doc.proto_sample_existing[0].po_no_new else 'NA'
            }}
            &nbsp;/&nbsp;
            {{ frappe.utils.formatdate(doc.proto_sample_existing[0].po_date, "dd-MM-yyyy") if doc.proto_sample_existing[0].po_date else 'NA' }}
        {% else %}
            NA / NA
        {% endif %}
    </span>
    {% endif %}
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
        {% if doc.table_cpri%}
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.table_cpri[0].hsn_code if doc.table_cpri and doc.table_cpri[0].hsn_code else 'NA' }}</span>
{%else%}
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.proto_sample_existing[0].hsn_code if doc.proto_sample_existing and doc.proto_sample_existing[0].hsn_code else 'NA' }}</span>

    {% endif %}
    </div>
{% set ns = namespace(gst_rates=[]) %}  
{% if doc.taxes %}
    {% for t in doc.taxes %}
        {% if t.rate %}
            {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
        {% endif %}
    {% endfor %}
{%if doc.supplier_group!="Importer"%}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">GST Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') or '' }}</span>
</div>
{% endif %}

{% endif %}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Valid From</span>
        {% if doc.table_cpri%}
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ frappe.utils.formatdate(doc.table_cpri[0].valid_from, "dd-MM-yyyy") if doc.table_cpri[0].valid_from else 'NA' }}
</span>
{%else%}
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ frappe.utils.formatdate(doc.proto_sample_existing[0].valid_from, "dd-MM-yyyy") if doc.proto_sample_existing[0].valid_from else 'NA' }}
</span>
{% endif %}

</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Valid To</span>
        {% if doc.table_cpri%}

    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ frappe.utils.formatdate(doc.table_cpri[0].valid_to, "dd-MM-yyyy") if doc.table_cpri[0].valid_to else 'NA' }}
</span>
{%else%}
<span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ frappe.utils.formatdate(doc.proto_sample_existing[0].valid_to, "dd-MM-yyyy") if doc.proto_sample_existing[0].valid_to else 'NA' }}
</span>
{% endif %}

</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason For Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
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

{% set ns = namespace(counter=1) %}
<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;">Item Name</td>
        <td style="background-color:#fec76f;text-align:center;">Fixed Qty</td>
        <td style="background-color:#fec76f;text-align:center;">PO Price ({{doc.currency or ''}})</td>
        <td style="background-color:#fec76f;text-align:center;">Value({{doc.currency or ''}})</td>
    </tr>

    {% for i in doc.table_cpri %}
    <tr>
        <td>{{ ns.counter }}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.item_code_new or ''}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.item_name_new or ''}}</td>
        <td style="text-align:center;white-space:nowrap;">{{i.qty_new or 0}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.po_price_new or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.value or 0 , currency=doc.currency)}}</td>
    </tr>
    {% set ns.counter = ns.counter + 1 %}
    {% endfor %}

    {% for i in doc.proto_sample_existing %}
    <tr>
        <td>{{ ns.counter }}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.item_code_new or ''}}</td>
        <td style="text-align:left;white-space:nowrap;">{{i.item_name_new or ''}}</td>
        <td style="text-align:center;white-space:nowrap;">{{i.qty_new or 0}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.po_price_new or 0 , currency=doc.currency)}}</td>
        <td style="text-align:right;white-space:nowrap;">{{frappe.utils.fmt_money(i.value or 0 , currency=doc.currency)}}</td>
    </tr>
    {% set ns.counter = ns.counter + 1 %}
    {% endfor %}

    <tr>
        <td colspan=5 style="text-align:center;font-weight:bold">Total Value({{doc.currency or ''}})</td>
        <td colspan=1 style="text-align:right;font-weight:bold">{{frappe.utils.fmt_money(doc.total_po_value or 0 , currency=doc.currency)}}</td>
    </tr>
</table>

<br>
    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:50%;font-weight:bold;">TERMS & CONDITIONS</span>
</div><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Payment Terms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Incoterms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Mode Of Dispatch</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.mode_of_dispatch or 'NA' }}</span>
</div>



        <br>
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
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Marketing Manager</td>

  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">CMD</td>
</tr>

     <tr style="height: 80px;">
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
     
    <td style="text-align:center;font-size:15px;">
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
        {% if py.show_till("Pending for Marketing Manager") %}
            {{ show_signature(mm_signature, doc.marketing_manager_approved_on, 'Pending for Marketing Manager', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def get_debit_material_html(doc):
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
            "Pending for Marketing Manager",
            "Pending for Plant Head",
            "Pending for GM",
            "Pending for Finance",
            "Pending for BMD",
            "Pending for CMD",
            "Approved",
            "Rejected"
        ]
        if (stop_state is not None and workflow_order.index(state_name) < workflow_order.index(stop_state)) or (state_name == stop_state and doc.get("workflow_state") in ["Rejected","Draft"]):
            return True
        try:
            return workflow_order.index(state_name) < workflow_order.index(stop_state)
        except ValueError:
            return False
    emp_name = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "employee_name")
    prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.get("owner")}, "custom_digital_signature")
    hod_signature = frappe.db.get_value("Employee", {"name": doc.get("reports_to")}, "custom_digital_signature")
    erp_signature = frappe.db.get_value("Employee", {"user_id": doc.get("erp_team")}, "custom_digital_signature")
    material_signature = frappe.db.get_value("Employee", {"user_id": doc.get("material_manager")}, "custom_digital_signature")
    plant_signature = frappe.db.get_value("Employee", {"user_id": doc.get("plant_head")}, "custom_digital_signature")
    bmd_signature = frappe.db.get_value("Employee", {"name": 'BMD01'}, "custom_digital_signature")
    pm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("production_manager")}, "custom_digital_signature")
    finance_signature = frappe.db.get_value("Employee", {"user_id": doc.get("finance")}, "custom_digital_signature")
    cmd_signature = frappe.db.get_value("Employee", {"name": "CMD01"}, "custom_digital_signature")
    smd_signature = frappe.db.get_value("Employee", {"name": "SMD01"}, "custom_digital_signature")
    gm_signature = frappe.db.get_value("Employee", {"name":"KR002"}, "custom_digital_signature")
    mm_signature = frappe.db.get_value("Employee", {"user_id": doc.get("marketing_manager")}, "custom_digital_signature")
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
    <span style="display:inline-block; width:90px;">Dept.From </span>:&nbsp;{{ doc.department_from or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Dept.To</span>:&nbsp; {{ doc.department_to or '' }}<br><br>
    <span style="display:inline-block; width:90px;">Created By</span>: &nbsp;{{emp_name or '' }}<br><br>
   
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
        <br><br>
     {% set label_width = "140px" %} <!-- adjust as needed -->

     <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Group</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.supplier_group or 'NA' }}</span>
</div>
{% set supplier_name=frappe.db.get_value("Supplier",{"name":doc.supplier},"supplier_name") %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Name</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ supplier_name or 'NA' }}</span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Currency</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.currency or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Supplier Invoice No</span>
    <span>
        :&nbsp;&nbsp;&nbsp;&nbsp;
       {{doc.supplier_invoice_number or 'NA'}}
    </span>
</div>

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">HSN Code</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_debit_note_material[0].hsn_code if doc.approval_debit_note_material and doc.approval_debit_note_material[0].hsn_code else 'NA' }}</span>
</div>
{% if doc.supplier_group=="Local Purchase"%}
{% set ns = namespace(gst_rates=[]) %}  
{% if doc.taxes %}
    {% for t in doc.taxes %}
        {% if t.rate %}
            {% set ns.gst_rates = ns.gst_rates + [t.rate|string + '%'] %}
        {% endif %}
    {% endfor %}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">GST Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;{{ ns.gst_rates | join(' + ') or '' }}</span>
</div>
{% endif %}
{% endif%}
{%if doc.supplier_group=="Importer"%}
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Exchange Rate</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{doc.exchange_rate or 'NA' }}
</span>
</div>
{%endif%}

<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Reason For Update</span>
    <span>:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.approval_debit_note_material[0].reason_for_request if doc.approval_debit_note_material and doc.approval_debit_note_material[0].reason_for_request else 'NA' }}</span>
</div>

<br>
{% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}

<table>
    <tr>
        <td style="background-color:#fec76f;text-align:center;font-size:12px;">S.No</td>
        <td style="background-color:#fec76f;text-align:center;font-size:12px;">Item Code</td>
        <td style="background-color:#fec76f;text-align:center;font-size:12px;">Item Name</td>
         <td style="background-color:#fec76f;text-align:center;font-size:12px;">UOM</td>
        <td style="background-color:#fec76f;text-align:center;font-size:12px;">PO Price ({{doc.currency or ''}})</td>

        <td style="background-color:#fec76f;text-align:center;font-size:12px;">Qty</td>
        <td style="background-color:#fec76f;text-align:center;font-size:12px;">Total DN Value ({{doc.currency or ''}})</td>

        </tr>
    {% for i in doc.approval_debit_note_material%}
    <tr>
        <td>{{loop.index}}</td>
        <td style="text-align:left;white-space:nowrap;font-size:12px;">{{i.part_no or ''}}</td>
        <td style="text-align:left;white-space:nowrap;font-size:12px;">{{i.part_name or ''}}</td>
         <td style="text-align:center;white-space:nowrap;font-size:12px;">{{i.uom or ''}}</td>
        <td style="text-align:right;white-space:nowrap;font-size:12px;">{{frappe.utils.fmt_money(i.pojo_price or 0 , currency=doc.currency)}}</td>
         <td style="text-align:center;white-space:nowrap;font-size:12px;">{{i.qty or 0}}</td>
      
        <td style="text-align:right;white-space:nowrap;font-size:12px;">{{frappe.utils.fmt_money(i.dn_amount or 0 , currency=doc.currency)}}</td>

    </tr>
    {%endfor%}
    <tr>
        <td colspan=6 style="text-align:center;font-weight:bold">Total DN Value({{doc.currency or ''}})</td>
        <td colspan=1 style="text-align:right;font-weight:bold">{{frappe.utils.fmt_money(doc.total_dn_value or 0 , currency=doc.currency)}}</td>
    </tr>
      </table>
<br>
    <div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:50%;font-weight:bold;">TERMS & CONDITIONS</span>
</div><br>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Payment Terms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.payment_terms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Incoterms</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.wonjin_incoterms or 'NA' }}</span>
</div>
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;">Remarks</span>
    <span >:&nbsp;&nbsp;&nbsp;&nbsp;{{ doc.subject or 'NA' }}</span>
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
    <table>
   <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">HOD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">ERP Team</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Plant Head</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">GM</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">Finance</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">BMD</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:11.11%;background-color:#a5a3ac">CMD</td>
</tr>

     <tr style="height: 80px;">
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
     
    <td style="text-align:center;font-size:15px;">
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
        {% if py.show_till("Pending for Plant Head") %}
            {{ show_signature(plant_signature, doc.plant_head_approved_on, 'Pending for Plant Head', doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for GM") %}
            {{ show_signature(gm_signature, doc.gm_approved_on, "Pending for GM", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for Finance") %}
            {{ show_signature(finance_signature, doc.finance_approved_on, "Pending for Finance", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for BMD") %}
            {{ show_signature(bmd_signature, doc.bmd_approved_on, "Pending for BMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
    <td style="text-align:center;">
        {% if py.show_till("Pending for CMD") %}
            {{ show_signature(cmd_signature, doc.cmd_approved_on, "Pending for CMD", doc.workflow_state, stop_state) }}
        {% endif %}
    </td>
 

</tr>

</table>

    <div style="text-align:left; font-size:12px;margin-top:5px;">
        Note: This document is Digitally Signed
    </div>
    </div>
    """

    html = render_template(template, {"doc": doc,
        "prepared_signature": prepared_signature,
        "hod_signature": hod_signature,
        "erp_signature": erp_signature,
        "finance_signature": finance_signature,
        "plant_signature": plant_signature,
        "cmd_signature": cmd_signature,
        "material_signature":material_signature,
        "bmd_signature":bmd_signature,
        "pm_signature":pm_signature,
        "smd_signature":smd_signature,
        "gm_signature":gm_signature,
        "mm_signature":mm_signature,
        "stop_state":stop_state,
        "py": {"show_till": show_till}
    })
    return {"html": html}

@frappe.whitelist()
def amar_karthick(doc):
    doc = frappe.parse_json(doc)
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
            <td style="text-align:right;">{{ frappe.utils.fmt_money(current_val, 2, currency="INR") }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(revised_val, 2, currency="INR") }}</td>
            <td style="text-align:right;">
                {{ frappe.utils.fmt_money(diff_val, 2, currency="INR") }} {{ arrow | safe }}
            </td>
        </tr>
    {% endfor %}

    <tr>
        <td colspan="5" style="text-align:center;font-size:13px;font-weight:bold;">Total</td>
        <td style="text-align:right;font-size:13px;font-weight:bold;">
            {{ frappe.utils.fmt_money(ns.total_difference, 2, currency="INR") }}
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
            <td style="text-align:right;">{{ frappe.utils.fmt_money(current_val, 2,currency="INR") }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(revised_val, 2,currency="INR") }}</td>
            <td style="text-align:right;">
                {{ frappe.utils.fmt_money(diff_val, 2,currency="INR") }} {{ arrow | safe }}
            </td>
        </tr>
    {% endfor %}

    <tr>
        <td colspan="4" style="text-align:center;font-size:13px;font-weight:bold;">Total</td>
        <td style="text-align:right;font-size:13px;font-weight:bold;">
            {{ frappe.utils.fmt_money(ns.total_difference1, 2,currency="INR") }}
        </td>
    </tr>
</table>

    <br>
    
   

        <br>
        {% set name=frappe.db.get_value("Employee",{"user_id":doc.owner},"employee_name") %}
    <table>
  <tr>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Prepared</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">HOD</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">ERP</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Material Manager</td>
  <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Plant Head</td>
   <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">BMD</td>

</tr>


    <tr style="height: 80px;">
     {% set erp_signature = frappe.db.get_value("Employee", {"user_id":doc.erp_team}, "custom_digital_signature") %}
     {% set prepared_signature = frappe.db.get_value("Employee", {"user_id": doc.owner}, "custom_digital_signature") %}
       {% set hod_signature = frappe.db.get_value("Employee", {"name": doc.reports_to}, "custom_digital_signature") %}
       {% set bmd_signature = frappe.db.get_value("Employee", {"name":"BMD01"}, "custom_digital_signature") %}
       {% set plant_signature = frappe.db.get_value("Employee", {"name":"S0004"}, "custom_digital_signature") %}
       {% set material_signature = frappe.db.get_value("Employee", {"name":"S0004"}, "custom_digital_signature") %}
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state == "Draft" or "Pending For HOD"  or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Approved" or doc.workflow_state=="Pending for Material Manager"%}
           {% if prepared_signature %}
        <img src="{{ prepared_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
     {% if doc.date_time %}
{% set formatted_date = frappe.utils.format_datetime(doc.date_time, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state=="Pending for Plant Head" or doc.workflow_state=="Pending for ERP Team" or doc.workflow_state == "Approved" or doc.workflow_state == "Pending for BMD" or doc.workflow_state=="Pending for Material Manager"%}
            {% if hod_signature %}
        <img src="{{ hod_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
    {% if doc.hod_approved_on %}
{% set formatted_date = frappe.utils.format_datetime(doc.hod_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state=="Pending for Plant Head" or doc.workflow_state == "Approved" or doc.workflow_state == "Pending for BMD" or doc.workflow_state=="Pending for Material Manager"%}
            {% if erp_signature %}
        <img src="{{ erp_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
    {% if doc.erp_team_approved_on %}
        {% set formatted_date = frappe.utils.format_datetime(doc.erp_team_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>

    {% endif %}
    {% endif %}
    </td>
    
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state == "Approved" or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state == "Pending for BMD" %}
            {% if material_signature %}
        <img src="{{ material_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
    {% if doc.material_manager_approved_on %}
                {% set formatted_date = frappe.utils.format_datetime(doc.material_manager_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>

    {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state == "Approved" or doc.workflow_state == "Pending for BMD" %}
            {% if plant_signature %}
        <img src="{{ plant_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
    {% if doc.plant_head_approved_on %}
{% set formatted_date = frappe.utils.format_datetime(doc.plant_head_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>

    {% endif %}
        {% endif %}
    </td>
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state == "Approved"%}
            {% if bmd_signature %}
        <img src="{{ bmd_signature }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">


    {% endif %}
    <br>
    {% if doc.bmd_approved_on %}
{% set formatted_date = frappe.utils.format_datetime(doc.bmd_approved_on, "dd-MM-yyyy HH:mm:ss") %}
        <span style="white-space:nowrap;font-size:9px;">{{ formatted_date }}</span>
    {% endif %}
        {% endif %}
    </td>
    
</tr>

</table>
<div style="text-align:left; font-size:12px;margin-top:5px;">
    Note: This document is Digitally Signed
</div>

    </div>
    """
    html = render_template(template, {
    "doc": doc,
    "schedule_totals": schedule_totals,
    "schedule_totals_item": schedule_totals_item
})

    # html = render_template(template, {"doc": doc, "schedule_totals": schedule_totals})

    # html = render_template(template, {"doc": doc})
    return {"html": html}

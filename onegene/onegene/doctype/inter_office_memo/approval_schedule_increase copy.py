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
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;text-decoration: underline;">Customer Wise</span>
</div>

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
                <td style="text-align:right;">{{ frappe.utils.fmt_money(row.current_schedule_value, 2, currency="INR") }}</td>
                <td style="text-align:right;">{{ frappe.utils.fmt_money(row.revised_schedule_value, 2, currency="INR") }}</td>
                <td style="text-align:right;">
                    {{ frappe.utils.fmt_money(row.difference_value, 2, currency="INR") }} {{ arrow | safe }}
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
            <td style="text-align:right;">{{ frappe.utils.fmt_money(current_val, 2, currency="INR") }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(revised_val, 2, currency="INR") }}</td>
            <td style="text-align:right;">
                {{ frappe.utils.fmt_money(diff_val, 2, currency="INR") }} {{ arrow | safe }}
            </td>
        </tr>
    {% endfor %}
    
    {% endif %}
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
<div style="margin-bottom: 4px;">
    <span style="display:inline-block;width:{{ label_width }};font-weight:bold;text-decoration: underline;">Department Wise</span>
</div>
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
            <td style="text-align:right;">{{ frappe.utils.fmt_money(row.current_schedule_value, 2,currency="INR") }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(row.revised_schedule_value, 2,currency="INR") }}</td>
            <td style="text-align:right;">
                {{ frappe.utils.fmt_money(row.difference_value, 2,currency="INR") }} {{ arrow | safe }}
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
            <td style="text-align:right;">{{ frappe.utils.fmt_money(current_val, 2,currency="INR") }}</td>
            <td style="text-align:right;">{{ frappe.utils.fmt_money(revised_val, 2,currency="INR") }}</td>
            <td style="text-align:right;">
                {{ frappe.utils.fmt_money(diff_val, 2,currency="INR") }} {{ arrow | safe }}
            </td>
        </tr>
    {% endfor %}
    {% endif %}

    <tr>
        <td colspan="4" style="text-align:center;font-size:13px;font-weight:bold;">Total</td>
        <td style="text-align:right;font-size:13px;font-weight:bold;">
            {{ frappe.utils.fmt_money(ns.total_difference1, 2,currency="INR") }}
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
   <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">ERP</td>
    <td style="text-align:center; font-weight:bold; font-size:15px; width:14.28%;background-color:#a5a3ac">Production HOD</td>
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
       {% set production_hod=frappe.db.get_value("Employee", {"user_id":doc.production_manager}, "custom_digital_signature")%}
    <td style="text-align:center;font-size:15px;">
       <br>
        {% if doc.workflow_state == "Draft" or doc.workflow_state=="Pending for Production Manager" or "Pending For HOD"  or doc.workflow_state=="Pending for Plant Head" or doc.workflow_state == "Pending for BMD" or doc.workflow_state == "Approved" or doc.workflow_state=="Pending for Material Manager"%}
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
        {% if doc.workflow_state=="Pending for Plant Head" or doc.workflow_state=="Pending for Production Manager" or doc.workflow_state == "Approved" or doc.workflow_state == "Pending for BMD" or doc.workflow_state=="Pending for Material Manager"%}
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
        {% if doc.workflow_state=="Pending for Plant Head" or doc.workflow_state == "Approved" or doc.workflow_state == "Pending for BMD" or doc.workflow_state=="Pending for Material Manager"%}
            {% if production_hod %}
        <img src="{{ production_hod }}" style="max-height:50px;">
         {%else%}
        <img src="/files/Screenshot 2025-09-22 141452.png" style="height:50px;">

    {% endif %}
    <br>
    {% if doc.production_manager_approved_on %}
        {% set formatted_date = frappe.utils.format_datetime(doc.production_manager_approved_on, "dd-MM-yyyy HH:mm:ss") %}
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

from __future__ import unicode_literals
import frappe
from frappe.utils import today,flt,cint, getdate, get_datetime
from datetime import timedelta,datetime
from datetime import datetime, timedelta
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
import frappe
from frappe.utils import today, flt, cint, getdate, get_datetime, add_days, ceil, comma_and, get_link_to_form, get_first_day, get_last_day, nowdate
from datetime import datetime, timedelta

no_cache = 1
def get_context(context):
	context.att_data = get_att_data()
def get_att_data():
    from datetime import datetime, timedelta
    import frappe
    now = datetime.now()
    two_days_ago = now - timedelta(days=1)
    yesterday = two_days_ago.strftime('%Y-%m-%d')    
    formatted = two_days_ago.strftime('%d-%m-%Y')
    all_data = []
    ec_count = frappe.get_all("Employee Category", {'name': ('not in', ['Sub Staff', 'Director', 'Staff'])}, ['name'])
    departments = frappe.get_all("Department", {'disabled': ('!=', 1), "parent_department": "All Departments", "name": ('not in', ['PPS - WAIP','IT - WAIP','Finance - WAIP','HR - WAIP','Management - WAIP','Safety - WAIP','AUDITOR - WAIP'])}, ['name'])
    parent_summary = {}
    for d in departments:
        linked_departments = frappe.get_all("Department", {'disabled': ('!=', 1), "parent_department": d.name}, ['name'])
        table_data = '<table width=100% border="1" style="border-collapse:collapse;font-size: 16px;text-align:center;line-height:0.5" cellspacing="0" cellpadding="5">'
        table_data += '<tr style="background-color:#f0e29c;"><td colspan="1" style="border-right:hidden;"><img src="https://erp.onegeneindia.in/files/ci_img.png" width="190" height="100" style="float:left"></td><td colspan="5" style="padding-right:250px;font-size: 20px;"><b>Over Time Report ({})</b></td></tr>'.format(formatted)
        table_data += "<tr style='border: 1px solid black;background-color:#a3d696;font-weight:bold;text-align:center'><td width=28%>Parent Department</td>"
        table_data += '<td width=29%>Department</td><td width=12%>Apprentice</td><td width=12%>Operator</td><td width=12%>Contractor</td>'
        table_data += '<td width=12%>Total</td></tr>'
        parent_ot_data = frappe.db.sql(""" 
            SELECT custom_employee_category, COALESCE(SUM(custom_overtime_hours), 0) AS count
            FROM `tabAttendance`
            WHERE attendance_date = %s
            AND department = %s
            GROUP BY custom_employee_category
        """, (yesterday, d.name), as_dict=True)
        parent_ot_count = {ec.get('name'): 0 for ec in ec_count}
        for row in parent_ot_data:
            category = row.get('custom_employee_category')
            if category in parent_ot_count:
                parent_ot_count[category] = row.get('count')
        total_parent_ot = (
            parent_ot_count.get('Apprentice', 0) +
            parent_ot_count.get('Operator', 0) +
            parent_ot_count.get('Contractor', 0)
        )
        table_data += '<tr>'
        table_data += '<td rowspan={0} style="vertical-align:text-top;"><b><center>{1}</center></td></b>'.format(len(linked_departments)+1, d.name)
        table_data += '<td></td><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td>'.format(
            parent_ot_count.get('Apprentice', 0),
            parent_ot_count.get('Operator', 0),
            parent_ot_count.get('Contractor', 0),
            total_parent_ot
        )
        table_data += '</tr>'        
        sub_totals = {ec.get('name'): 0 for ec in ec_count}
        for dep in linked_departments:
            sub_ot_data = frappe.db.sql(""" 
                SELECT custom_employee_category, COALESCE(SUM(custom_overtime_hours), 0) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND department = %s
                GROUP BY custom_employee_category
            """, (yesterday, dep.name), as_dict=True)
            
            sub_ot_count = {ec.get('name'): 0 for ec in ec_count}
            for row in sub_ot_data:
                category = row.get('custom_employee_category')
                if category in sub_ot_count:
                    sub_ot_count[category] = row.get('count')
                if category in sub_totals:
                    sub_totals[category] += sub_ot_count[category]
            total_sub_ot = (
                sub_ot_count.get('Apprentice', 0) +
                sub_ot_count.get('Operator', 0) +
                sub_ot_count.get('Contractor', 0)
            ) 
            table_data += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>'.format(
                dep.name,
                sub_ot_count.get('Apprentice', 0),
                sub_ot_count.get('Operator', 0),
                sub_ot_count.get('Contractor', 0),
                total_sub_ot
            )
            table_data += '</tr>'
        total_all_ot = total_parent_ot + sum(sub_totals.values())
        table_data += "<tr style='border: 1px solid black;background-color:#96cfd6;font-weight:bold;color:red;text-align:center;font-size: 15px;'><td></td><td><strong>Total</strong></td>"
        table_data += '<td>{}</td><td>{}</td><td>{}</td><td>{}</td>'.format(
            sub_totals.get('Apprentice', 0) + parent_ot_count.get('Apprentice', 0),
            sub_totals.get('Operator', 0) + parent_ot_count.get('Operator', 0),
            sub_totals.get('Contractor', 0) + parent_ot_count.get('Contractor', 0),
            total_all_ot
        )
        table_data += '</tr>' 
        table_data += '</table><br>'
        all_data.append(table_data)
        parent_summary[d.name] = {
            'Apprentice': parent_ot_count.get('Apprentice', 0) + sub_totals.get('Apprentice', 0),
            'Operator': parent_ot_count.get('Operator', 0) + sub_totals.get('Operator', 0),
            'Contractor': parent_ot_count.get('Contractor', 0) + sub_totals.get('Contractor', 0),
            'Total': total_all_ot
        }
        tot_emp_app=0
        tot_emp_cont=0
        tot_emp_oper=0
        tot_emp_tot=0
        for dept, counts in parent_summary.items():
            tot_emp_app+=counts['Apprentice']
            tot_emp_cont+=counts['Contractor']
            tot_emp_oper+=counts['Operator']
            tot_emp_tot+=counts['Total']
    summary_table = '<table width=100% border="1" style="border-collapse:collapse;font-size: 12px;text-align:center" cellspacing="0" cellpadding="5">'
    summary_table += '<tr style="background-color:#f0e29c;"><td colspan="1" style="border-right:hidden;"><img src="https://erp.onegeneindia.in/files/ci_img.png" width="190" height="100" style="float:left"></td><td colspan="4" style="padding-right:290px;font-size: 20px;"><b>Over Time Report ({})</b></td></tr>'.format(formatted)
    summary_table += "<tr style='border: 1px solid black;background-color:#a3d696;font-weight:bold;text-align:center'><td width=25%>Parent Department</td>"
    summary_table += '<td width=15%>Apprentice</td><td width=15%>Operator</td><td width=15%>Contractor</td><td width=15%>Total</td></tr>'
    for dept, counts in parent_summary.items():
        summary_table += '<tr style="font-size: 15px;"><b><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</b></td>'.format(
            dept,
            counts['Apprentice'],
            counts['Operator'],
            counts['Contractor'],
            counts['Total']
        )
        summary_table += '</tr>'
    summary_table += '<tr style="border: 1px solid black;background-color:#96cfd6;font-weight:bold;color:red;text-align:center;font-size: 15px;"><b><td>Total</td><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</b></td>'.format(tot_emp_app,tot_emp_oper,tot_emp_cont,tot_emp_tot)   
    summary_table += '</table>'
    all_data.append(summary_table)
    
    return all_data

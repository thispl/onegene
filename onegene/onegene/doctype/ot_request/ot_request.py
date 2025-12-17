# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from time import strptime
from datetime import date, timedelta,time
from frappe.utils import today,get_first_day, get_last_day, add_days

class OTRequest(Document):
    # Update the OT hours in attendance and OT hours in OT Balance

    def on_submit(self):    
        if self.workflow_state=='Approved':
            for i in self.employee_details:
                month_start=get_first_day(self.ot_requested_date)
                month_end=get_last_day(self.ot_requested_date)
                name = frappe.db.get_value("Attendance",{"attendance_date":self.ot_requested_date,"docstatus":("!=",2),"employee":i.employee_code,"custom_ot_balance_updated":0},["name"])
                if name:
                    att = frappe.get_doc("Attendance",name)
                    if int(att.custom_extra_hours) >=2:
                        if int(att.custom_extra_hours) >= int(i.requested_ot_hours):
                            ot_hours = time(int(i.requested_ot_hours),0,0)
                        else:
                            ot_hours = time(int(att.custom_extra_hours),0,0)			
                        ftr = [3600,60,1]
                        hr = sum([a*b for a,b in zip(ftr, map(int,str(ot_hours).split(':')))])
                        ot_hr = round(hr/3600,1)
                        frappe.db.set_value('Attendance',name,'custom_total_overtime_hours',ot_hours)
                        frappe.db.set_value('Attendance',name,'custom_overtime_hours',ot_hr)
                        frappe.db.set_value('OT Request',self.name,'ot_updated',True)
                        frappe.db.set_value('Attendance',name,'custom_ot_updated',True)
                        if not frappe.db.exists("OT Balance",{'employee':i.employee_code,'from_date':month_start,'to_date':month_end}):
                            otb=frappe.new_doc("OT Balance")
                            otb.employee=i.employee_code
                            otb.from_date=month_start
                            otb.to_date=month_end
                            otb.total_ot_hours = ot_hr
                            draft=frappe.db.count("Leave Application",{'employee':i.employee_code,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Draft','custom_select_leave_type':'Comp-off from OT','docstatus':('!=',2)})
                            approved=frappe.db.count("Leave Application",{'employee':i.employee_code,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','custom_select_leave_type':'Comp-off from OT','docstatus':('!=',2)})
                            otb.comp_off_pending_for_approval = draft
                            otb.comp_off_used = approved
                            otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
                            otb.save(ignore_permissions=True)
                        else:
                            otb=frappe.get_doc("OT Balance",{'employee':i.employee_code,'from_date':month_start,'to_date':month_end})
                            otb.total_ot_hours += ot_hr
                            draft=frappe.db.count("Leave Application",{'employee':i.employee_code,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Draft','custom_select_leave_type':'Comp-off from OT','docstatus':('!=',2)})
                            approved=frappe.db.count("Leave Application",{'employee':i.employee_code,'from_date':('between',[month_start,month_end]),'to_date':('between',[month_start,month_end]),'workflow_state':'Approved','custom_select_leave_type':'Comp-off from OT','docstatus':('!=',2)})
                            otb.comp_off_pending_for_approval = draft
                            otb.comp_off_used = approved
                            otb.ot_balance = otb.total_ot_hours - ((draft * 8)+(approved * 8))
                            otb.save(ignore_permissions=True)
                        frappe.db.set_value('Attendance',name,'custom_ot_balance_updated',True)
                        frappe.db.set_value('OT Request',self.name,'ot_balance',True)

    def on_trash(self):
        if "System Manager" not in frappe.get_roles(frappe.session.user):
            if self.workflow_state and self.workflow_state not in ["Draft", "Cancelled"]:
                if self.docstatus == 0:
                    frappe.throw(
                        "Cannot delete this document as the workflow has moved to the next level.",
                        title="Not Permitted"
                    )

# Return Employees based on the Department selected
@frappe.whitelist()
def get_employees(dept=None,category=None):
    emp_list = []
    if category and dept:
        employees = frappe.db.sql("""
            SELECT name, employee_name, designation
            FROM `tabEmployee` 
            WHERE `status` = 'Active' 
            AND `department` = %s 
            AND `employee_category` = %s
            AND `employee_category` NOT IN ('Staff', 'Sub Staff')
        """, (dept,category), as_dict=1)
        for emp in employees:
            emp_list.append({
                'name': emp.name,
                'employee_name': emp.employee_name,
                'designation': emp.designation
            })
    elif dept and not category:
        employees = frappe.db.sql("""
            SELECT name, employee_name, designation
            FROM `tabEmployee` 
            WHERE `status` = 'Active' 
            AND `department` = %s 
            AND `employee_category` NOT IN ('Staff', 'Sub Staff')
        """, (dept,), as_dict=1)
        for emp in employees:
            emp_list.append({
                'name': emp.name,
                'employee_name': emp.employee_name,
                'designation': emp.designation
            })
    
    return emp_list
@frappe.whitelist()
#Return the Employee Name and Designation by passing the Employee Code
def get_details(name,dep=None, ot_requested_date=None):
    if not ot_requested_date:
        frappe.throw("OT Requested Date not found")
        return
        
    dept=frappe.db.get_value("Employee", {'name': name}, ['department'])
    if dep:
        dept=frappe.db.get_value("Employee", {'name': name}, ['department'])
        if dept!=dep:
            return 'ok'
    if name:
        category=frappe.db.get_value("Employee", {'name': name}, ['employee_category'])
        if category=='Staff' or category=='Sub Staff':
            # frappe.throw("Staff category not allowed for OT request")
            return 'OK'
        else:
            emp = frappe.db.get_value("Employee", {'name': name}, ['employee_name', 'designation', 'employee_category'], as_dict=1)
            ot_limit_details = frappe.db.get_value("Employee Category", emp.employee_category, ['custom_limit_ot', 'custom_ot_limit'], as_dict=1)
            total_ot = get_total_ot(name, ot_requested_date)
            return {
                "employee_name": emp.employee_name,
                "designation": emp.designation,
                "employee_category": emp.employee_category,
                "limit_ot": ot_limit_details.custom_limit_ot,
                "ot_limit": ot_limit_details.custom_ot_limit,
                "total_ot": total_ot,
            }

@frappe.whitelist()
def get_total_requested_ot(department, ot_date, shift, exclude_doc=None):
    total = 0
    filters = {
        "department": department,
        "ot_requested_date": ot_date,
        "docstatus": ["!=", 2]  
    }
    if exclude_doc:
        filters["name"] = ["!=", exclude_doc]
    ot_requests = frappe.get_all("OT Request", filters=filters, fields=["name"])

    for ot in ot_requests:
        child_rows = frappe.get_all("OT Request Child", 
            filters={"parent": ot.name, "shift": shift},
            fields=["requested_ot_hours"]
        )
        total += sum([int(row.requested_ot_hours) for row in child_rows if row.requested_ot_hours])


    return total


@frappe.whitelist()
def make_ot_table(department):
    dept = frappe.get_doc('Department', department)
    orange_color = '#f57c00'
    data = f'''
        <div style="text-align: center;">
            <table class="table table-bordered" style="border-collapse: collapse; width: 60%; margin: auto;">
                <tr>
                    <td colspan="3" style="text-align: center; font-weight: bold; border: 1px solid black;">Allowed OT for {department}</td>
                </tr>
                <tr style="background-color:{orange_color}; color:white;">
                    <td style="padding:0px; border: 1px solid black; width: 10%;"><b>Sr No</b></td>
                    <td style="padding:0px; border: 1px solid black; width: 45%;"><b>Shift</b></td>
                    <td style="padding:0px; border: 1px solid black; width: 45%;"><b>Allowed Hours</b></td>
                </tr>
    '''
    sr_no = 1
    if dept.custom_ot_details:
        for d in dept.custom_ot_details:
            data += f'''
                <tr>
                    <td style="padding:0px; border: 1px solid black; width: 10%;">{sr_no}</td>
                    <td style="padding:0px; border: 1px solid black; width: 45%;">{d.shift}</td>
                    <td style="padding:0px; border: 1px solid black; width: 45%;">{int(d.allowed_ot)}</td>
                </tr>
            '''
            sr_no += 1
    else:
        shift_list = frappe.get_all("Shift Type",{"custom_disabled": 0},["name"])
        if shift_list:
            for shift in shift_list:
                data += f'''
                    <tr>
                        <td style="padding:0px; border: 1px solid black; width: 10%;">{sr_no}</td>
                        <td style="padding:0px; border: 1px solid black; width: 45%;">{shift.name}</td>
                        <td style="padding:0px; border: 1px solid black; width: 45%;">0</td>
                    </tr>
                '''
                sr_no += 1
        else:
            data += '''
                <tr>
                    <td colspan="3" style="text-align: center; border: 1px solid black;">No shift data available.</td>
                </tr>
            '''
    data += '''
            </table>
        </div>
    '''
    return data

def get_total_ot(name, ot_requested_date):
    month_start_date = get_month_start(ot_requested_date)
    total_ot = frappe.db.sql("""
            SELECT SUM(otc.requested_ot_hours) as total_ot_requested
            FROM `tabOT Request` ot
            INNER JOIN `tabOT Request Child` otc 
                ON ot.name = otc.parent
            WHERE 
                (ot.docstatus != 2 OR ot.workflow_state NOT IN ('Rejected', 'Cancelled'))
                AND otc.employee_code = %s AND ot.ot_requested_date BETWEEN %s AND %s
            """, (name, month_start_date, ot_requested_date), as_dict=1)[0]['total_ot_requested'] or 0
    return total_ot

def get_month_start(date_value):
    from datetime import datetime

    if isinstance(date_value, str):
        date_value = datetime.strptime(date_value, "%Y-%m-%d")
    return date_value.replace(day=1).date()

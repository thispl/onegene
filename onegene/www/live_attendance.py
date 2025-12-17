from __future__ import unicode_literals
import frappe
from frappe.utils import today,flt,cint, getdate, get_datetime
from datetime import timedelta,datetime
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

no_cache = 1

def get_context(context):
	context.att_data = get_att_data()

@frappe.whitelist(allow_guest=True)
def get_att_data():
    date = nowdate()
    from datetime import datetime
    # now = datetime.now()
    now = datetime.now()
    date_now = now.strftime("%d/%m/%Y")
    time_now = now.strftime("%H:%M:%S")
    time_now_combined = f"{date_now} {time_now}"
    shift = frappe.get_all("Shift Type",{'name':('!=',"4")}, ['*'], order_by='name ASC')
    ec_count = frappe.get_all("Employee Category", {'name': ('not in', ['Sub Staff', 'Director'])}, ['*'])
    shift_count = len(shift)
    ec_count_length = len(ec_count)
    def generate_table_rows(departments):
        data = ""
        for d in departments:
            length = 2
            department1 = frappe.get_all("Department", {'disabled': ('!=', 1), "parent_department": d.name}, ['name'])
            length += len(department1)
            parent_dep = d.name
            total_pre, total_cl, total_trainee, total_ops, trainee_tr, total_staff, totl_ch_out = 0, 0, 0, 0, 0, 0, 0
            data += "<tr><td rowspan={} style='border: 1px solid black;text-align:left;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'></td>".format(length, d.name)
            for i in shift:
                shift_attendance_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND shift = %s
                    AND department = %s
                    AND in_time IS NOT NULL
                """, (date, i.name, d.name), as_dict=True)
                shift_attendance = shift_attendance_count[0].count if shift_attendance_count else 0
                data += "<td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td>".format(shift_attendance)
            staff_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Staff", "Sub Staff", "Director")
                AND department = %s
                AND in_time IS NOT NULL
            """, (date, d.name), as_dict=True)
            staff = staff_count[0].count if staff_count else 0
            ops_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Operator")
                AND department = %s
                AND in_time IS NOT NULL
            """, (date, d.name), as_dict=True)
            ops = ops_count[0].count if ops_count else 0
            aps_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Apprentice")
                AND department = %s
                AND in_time IS NOT NULL
            """, (date, d.name), as_dict=True)
            trainee = aps_count[0].count if aps_count else 0
            tr_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Trainee")
                AND department = %s
                AND in_time IS NOT NULL
            """, (date, d.name), as_dict=True)
            trainee_count = tr_count[0].count if tr_count else 0
            cl_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Contractor")
                AND department = %s
                AND in_time IS NOT NULL
            """, (date, d.name), as_dict=True)
            cl = cl_count[0].count if cl_count else 0
            checkout_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND department = %s
                AND in_time IS NOT NULL
                AND out_time IS NOT NULL
            """, (date, d.name), as_dict=True)
            ch_out = checkout_count[0].count if checkout_count else 0
            total_pre += (staff + ops + trainee + cl)
            total_cl += cl
            total_trainee += trainee
            total_ops += ops
            trainee_tr += trainee_count
            total_staff += staff
            totl_ch_out += ch_out
            data += "<td style='border: 1px solid black;text-align:center;background-color:#ADD8E6;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;background-color:#BACC81;padding:2px;line-height:2;font-size:13px'>{}</td></tr>".format(
                (staff + ops + trainee + cl + trainee_count), trainee_count, cl, trainee, ops, staff, ch_out
            )
            department = frappe.get_all("Department", {'disabled': ('!=', 1), "parent_department": d.name}, ['name'])
            for d in department:
                data += "<tr><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td>".format(d.name)
                for i in shift:
                    shift_attendance_count = frappe.db.sql("""
                        SELECT COUNT(*) AS count
                        FROM `tabAttendance`
                        WHERE attendance_date = %s
                        AND shift = %s
                        AND department = %s
                        AND in_time IS NOT NULL
                    """, (date, i.name, d.name), as_dict=True)
                    shift_attendance = shift_attendance_count[0].count if shift_attendance_count else 0
                    data += "<td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td>".format(shift_attendance)
                staff_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND custom_employee_category IN ("Staff", "Sub Staff", "Director")
                    AND department = %s
                    AND in_time IS NOT NULL
                """, (date, d.name), as_dict=True)
                staff = staff_count[0].count if staff_count else 0
                tr_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND custom_employee_category IN ("Trainee")
                    AND department = %s
                    AND in_time IS NOT NULL
                """, (date, d.name), as_dict=True)
                trainee_count = tr_count[0].count if tr_count else 0
                ops_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND custom_employee_category IN ("Operator")
                    AND department = %s
                    AND in_time IS NOT NULL
                """, (date, d.name), as_dict=True)
                ops = ops_count[0].count if ops_count else 0
                aps_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND custom_employee_category IN ("Apprentice")
                    AND department = %s
                    AND in_time IS NOT NULL
                """, (date, d.name), as_dict=True)
                trainee = aps_count[0].count if aps_count else 0
                cl_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND custom_employee_category IN ("Contractor")
                    AND department = %s
                    AND in_time IS NOT NULL
                """, (date, d.name), as_dict=True)
                cl = cl_count[0].count if cl_count else 0
                checkout_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND department = %s
                    AND in_time IS NOT NULL
                    AND out_time IS NOT NULL
                """, (date, d.name), as_dict=True)
                ch_out = checkout_count[0].count if checkout_count else 0
                total_pre += (staff + ops + trainee + cl)
                total_cl += cl
                total_trainee += trainee
                trainee_tr += trainee_count
                total_ops += ops
                total_staff += staff
                totl_ch_out += ch_out
                data += "<td style='border: 1px solid black;text-align:center;background-color:#ADD8E6;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;background-color:#BACC81;padding:2px;line-height:2;font-size:13px'>{}</td></tr>".format(
                    (staff + ops + trainee + cl + trainee_count), trainee_count, cl, trainee, ops, staff, ch_out
                )
            data += "<tr style='border: 1px solid black;text-align:center;background-color:#C0C0C0;padding:2px;line-height:2;font-size:13px'><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>Total</td>"
            for i in shift:
                shift_count = 0
                shift_attendance_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND shift = %s
                    AND department = %s
                    AND in_time IS NOT NULL
                """, (date, i.name, parent_dep), as_dict=True)
                shift_attendance = shift_attendance_count[0].count if shift_attendance_count else 0
                shift_count += shift_attendance
                department = frappe.get_all("Department", {'disabled': ('!=', 1), "parent_department": parent_dep}, ['name'])
                for d in department:
                    shift_attendance_count = frappe.db.sql("""
                        SELECT COUNT(*) AS count
                        FROM `tabAttendance`
                        WHERE attendance_date = %s
                        AND shift = %s
                        AND department = %s
                        AND in_time IS NOT NULL
                    """, (date, i.name, d.name), as_dict=True)
                    shift_attendance = shift_attendance_count[0].count if shift_attendance_count else 0
                    shift_count += shift_attendance
                data += "<td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td>".format(shift_count)
            data += "<td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td><td style='border: 1px solid black;text-align:center;padding:2px;line-height:2;font-size:13px'>{}</td></tr>".format(
                total_pre, total_cl, total_trainee, total_ops, total_staff, trainee_tr, totl_ch_out
            )
        return data

    departments = frappe.get_all("Department", {'disabled': ('!=', 1), "parent_department": "All Departments"}, ['name'])
    sorted_departments = sorted(departments, key=lambda d: (d.name != 'Manufacturing - WAIP', d.name))
    waip_department = [d for d in sorted_departments if d.name == 'Manufacturing - WAIP']
    other_departments = [d for d in sorted_departments if d.name != 'Manufacturing - WAIP']
    tables = []
    if waip_department:
        table_data = "<table class='table table-bordered' cellspacing='0' cellpadding='0' style='font-size: 12px; line-height: 1.5; border-collapse: collapse; margin: 0; padding: 0;'>"

        table_data += "<tr><td colspan={} style='border: 1px solid black; background-color:#f6d992; text-align:center; padding:1.5px;font-size: 13px;'><b>Live Attendance {}</b></td></tr>".format(shift_count + 1 + ec_count_length + 3, time_now_combined)

        table_data += "<tr><td rowspan=2 style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:1.5px;'>Parent Department</td><td rowspan=2 style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:1.5px;'>Department</td><td colspan={} style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:1.5px;'>Shift</td><td colspan={} style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:1.5px;'>Category</td><td rowspan=2 style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:1.5px;'>CheckOut</td></tr>".format(shift_count + 1, ec_count_length)

        table_data += "<tr>"
        for i in shift:
            table_data += "<td style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:1.5px;'>{}</td>".format(i.name)
        table_data += "<td style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:1.5px;'>Total Present</td>"
        for i in ec_count:
            table_data += "<td style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:1.5px;'>{}</td>".format(i.name)
        table_data += "</tr>"

        # Apply same padding in rows
        table_data += generate_table_rows(waip_department)  # Update this function too if needed

        table_data += "</table>"
        tables.append(table_data)


    num_tables = (len(other_departments) + 1) // 2  
    start_index = 0
    for table_index in range(num_tables):
        end_index = start_index + 2  
        departments_to_include = other_departments[start_index:end_index]
        start_index = end_index
        table_data = '<table class="table table-bordered" cellspacing="0" cellpadding="0" style="font-size: 12px; border-collapse: collapse;">'

        table_data += "<tr><td colspan ={} style='border: 1px solid black; background-color:#f6d992; text-align:center; padding:2px;  font-size: 13px;line-height:2'><b>Live Attendance {}</b></td></tr>".format(shift_count + 1 + ec_count_length + 3, time_now_combined)

        table_data += "<tr>"
        table_data += "<td rowspan=2 style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:2px; line-height:2'>Parent Department</td>"
        table_data += "<td rowspan=2 style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:2px; line-height:2'>Department</td>"
        table_data += "<td colspan={} style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:2px; line-height:2'>Shift</td>".format(shift_count + 1)
        table_data += "<td colspan={} style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:2px; line-height:2'>Category</td>".format(ec_count_length)
        table_data += "<td rowspan=2 style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:2px; line-height:2'>CheckOut</td>"
        table_data += "</tr>"

        table_data += "<tr>"
        for i in shift:
            table_data += "<td style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:2px; line-height:2'>{}</td>".format(i.name)

        table_data += "<td style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:2px; line-height:2'>Total Present</td>"

        for i in ec_count:
            table_data += "<td style='border: 1px solid black; background-color:#FFA500; font-weight:bold; text-align:center; padding:2px; line-height:2'>{}</td>".format(i.name)

        table_data += "</tr>"

        table_data += generate_table_rows(departments_to_include)
        table_data += "</table>"
        tables.append(table_data)

    return tables


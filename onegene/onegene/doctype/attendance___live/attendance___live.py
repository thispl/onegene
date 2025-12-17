# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date, datetime, timedelta


class AttendanceLive(Document):
    pass
#Returns the HTML View of Department wise live attendance count against each Shift and Category
@frappe.whitelist(allow_guest=True)
def get_data_system(dept, desn):
    # frappe.errprint(dept)
    # frappe.errprint(desn)
    nowtime = datetime.now()
    nwt = datetime.strftime(nowtime, '%d-%m-%Y %H:%M:%S')
    max_out = datetime.strptime('06:30', '%H:%M').time()

    if nowtime.time() > max_out:
        date1 = nowtime.date()
    else:
        date1 = (nowtime - timedelta(days=1)).date()

    data =''
    
    if dept == "1":
        # frappe.errprint("HI")
        shift=frappe.get_all("Shift Type",{'name':('!=',"4")},['*'],order_by='name ASC')
        shift2=4
        for i in shift:
            shift2+=1
        ec1=0
        ec_count=frappe.get_all("Employee Category",{'name':('not in',['Sub Staff','Director'])},['*'])
        for i in ec_count:
            ec1 +=1 
        data = "<table class='table table-bordered=1'>"
        data += "<tr><td colspan ={}  style='border: 1px solid black;background-color:#f6d992;text-align:center'><b>Live Attendance</b></td><td colspan ={} style='border: 1px solid black;background-color:#f6d992;text-align:center'><b>Date & Time {} </b></td><tr>" .format(shift2,ec1,nwt)
        shift1=1
        for i in shift:
            shift1+=1
        data += "<tr><td rowspan=2 style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center;'>Parent Department</td><td rowspan=2 style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center;'>Department</td><td colspan={} style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center'>Shift</td><td colspan={} style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center'>Category</td><td rowspan=2 style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center'>CheckOut</td></tr>".format(shift1,ec1)        
        data += "<tr>"
        for i in shift:
            data += "<td style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center'>{}</td>".format(i.name)
        data += "<td style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center'>Total Present</td>"        
        
        ec=frappe.get_all("Employee Category",{'name':('not in',['Sub Staff','Director'])},['*'])
        for i in ec:
            data += "<td style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center'>{}</td>".format(i.name)
        data +="</tr>"
        total = 0
        department = frappe.get_all("Department", {'disabled': ('!=', 1),"parent_department":"All Departments"}, ['name'])        
        for d in department:
            length=2
            department1 = frappe.get_all("Department", {'disabled': ('!=', 1),"parent_department":d.name}, ['name'])
            for dep in department1:
                length+=1
            frappe.errprint(length)
            parent_dep=d.name
            total_pre=0
            total_cl=0
            total_tr=0
            total_trainee=0
            total_ops=0
            total_staff=0
            totl_ch_out=0
            data += "<tr><td rowspan={} style='border: 1px solid black;text-align:left'>{}</td><td style='border: 1px solid black;text-align:center'></td>".format(length,d.name)
            for i in shift:
                shift_attendance_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND shift = %s
                    AND department = %s
                    AND in_time IS NOT NULL

                """, (date1, i.name, d.name), as_dict=True)
                shift_attendance = shift_attendance_count[0].count if shift_attendance_count else 0
                data += "<td style='border: 1px solid black;text-align:center'>{}</td>".format(shift_attendance)
            staff_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Staff", "Sub Staff", "Director")
                AND department = %s
                AND in_time IS NOT NULL
            """, (date1,d.name), as_dict=True)
            staff = staff_count[0].count if staff_count else 0
            ops_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Operator")
                AND department = %s
                AND in_time IS NOT NULL
            """, (date1,d.name), as_dict=True)
            ops = ops_count[0].count if ops_count else 0
            trainee_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Trainee")
                AND department = %s
                AND in_time IS NOT NULL
            """, (date1,d.name), as_dict=True)
            tr = trainee_count[0].count if trainee_count else 0
            aps_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Apprentice")
                AND department = %s
                AND in_time IS NOT NULL
            """, (date1,d.name), as_dict=True)
            trainee = aps_count[0].count if aps_count else 0
            cl_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Contractor")
                AND department = %s
                AND in_time IS NOT NULL
            """, (date1,d.name), as_dict=True)
            cl = cl_count[0].count if cl_count else 0
            
            checkout_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND department = %s
                AND in_time IS NOT NULL
                AND out_time IS NOT NULL
            """, (date1,d.name), as_dict=True)
            ch_out = checkout_count[0].count if checkout_count else 0
            total += (staff+ops+trainee+cl+tr)
            total_pre+=(staff+ops+trainee+cl+tr)
            total_cl+=cl
            total_tr+=tr
            total_trainee+=trainee
            total_ops+=ops
            total_staff+=staff
            totl_ch_out+=ch_out
            data += "<td style='border: 1px solid black;text-align:center;background-color:#ADD8E6'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center;background-color:#BACC81'>%s</td>" % ((staff+ops+trainee+cl+tr),tr,cl,trainee,ops,staff,ch_out)
            data += '</tr>'
            department = frappe.get_all("Department", {'disabled': ('!=', 1),"parent_department":d.name}, ['name'])
            for d in department:
                data += "<tr><td style='border: 1px solid black;text-align:center'>%s</td>"%(d.name)
                for i in shift:
                    shift_attendance_count = frappe.db.sql("""
                        SELECT COUNT(*) AS count
                        FROM `tabAttendance`
                        WHERE attendance_date = %s
                        AND shift = %s
                        AND department = %s
                        AND in_time IS NOT NULL
                    """, (date1, i.name, d.name), as_dict=True)
                    shift_attendance = shift_attendance_count[0].count if shift_attendance_count else 0
                    data += "<td style='border: 1px solid black;text-align:center'>{}</td>".format(shift_attendance)
                staff_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND custom_employee_category IN ("Staff", "Sub Staff", "Director")
                    AND department = %s
                    AND in_time IS NOT NULL
                """, (date1,d.name), as_dict=True)
                staff = staff_count[0].count if staff_count else 0
                ops_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND custom_employee_category IN ("Operator")
                    AND department = %s
                    AND in_time IS NOT NULL
                """, (date1,d.name), as_dict=True)
                ops = ops_count[0].count if ops_count else 0
                trainee_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND custom_employee_category IN ("Trainee")
                    AND department = %s
                    AND in_time IS NOT NULL
                """, (date1,d.name), as_dict=True)
                tr = trainee_count[0].count if trainee_count else 0
                aps_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND custom_employee_category IN ("Apprentice")
                    AND department = %s
                    AND in_time IS NOT NULL
                """, (date1,d.name), as_dict=True)
                trainee = aps_count[0].count if aps_count else 0
                cl_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND custom_employee_category IN ("Contractor")
                    AND department = %s
                    AND in_time IS NOT NULL
                """, (date1,d.name), as_dict=True)
                cl = cl_count[0].count if cl_count else 0
                checkout_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND department = %s
                    AND in_time IS NOT NULL
                    AND out_time IS NOT NULL
                """, (date1,d.name), as_dict=True)
                ch_out = checkout_count[0].count if checkout_count else 0
                total += (staff+ops+trainee+cl+tr)
                total_pre+=(staff+ops+trainee+cl+tr)
                total_cl+=cl
                total_tr+=tr
                total_trainee+=trainee
                total_ops+=ops
                total_staff+=staff
                totl_ch_out+=ch_out
                data += "<td style='border: 1px solid black;text-align:center;background-color:#ADD8E6'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center;background-color:#BACC81'>%s</td></tr>" % ((staff+ops+trainee+cl+tr),tr,cl,trainee,ops,staff,ch_out)
            data += "<tr style='border: 1px solid black;text-align:center;background-color:#bfbfbf'><td style='border: 1px solid black;text-align:center'>Total</td>"
            for i in shift:
                shift_count=0
                shift_attendance_count = frappe.db.sql("""
                    SELECT COUNT(*) AS count
                    FROM `tabAttendance`
                    WHERE attendance_date = %s
                    AND shift = %s
                    AND department = %s
                    AND in_time IS NOT NULL

                """, (date1, i.name, parent_dep), as_dict=True)
                shift_attendance = shift_attendance_count[0].count if shift_attendance_count else 0
                shift_count+=shift_attendance
                department = frappe.get_all("Department", {'disabled': ('!=', 1),"parent_department":parent_dep}, ['name'])
                for d in department:
                    shift_attendance_count = frappe.db.sql("""
                        SELECT COUNT(*) AS count
                        FROM `tabAttendance`
                        WHERE attendance_date = %s
                        AND shift = %s
                        AND department = %s
                        AND in_time IS NOT NULL

                    """, (date1, i.name, d.name), as_dict=True)
                    shift_attendance = shift_attendance_count[0].count if shift_attendance_count else 0
                    shift_count+=shift_attendance
                data += "<td style='border: 1px solid black;text-align:center'>{}</td>".format(shift_count)
            data+="<td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td></tr>" % (total_pre,total_tr,total_cl,total_trainee,total_ops,total_staff,totl_ch_out)
        colspan=(shift2)-2
        data += "<tr><td colspan = {} style='border: 1px solid black;text-align:left'>Total Present</td><td colspan=6 style='border: 1px solid black;text-align:left'>{}</td></tr>" .format(colspan,total)
        data += "</table>"
    
    elif desn == "1":
        data = "<table class='table table-bordered=1'>"
        data += "<tr><td colspan = 4 style='border: 1px solid black;background-color:#f6d992;text-align:center'><b>Live Attendance</b></td><td colspan = 3 style='border: 1px solid black;background-color:#f6d992;text-align:center'><b>Date & Time %s </b></td><tr>" % (nwt)

        # frappe.errprint("HI")
        designation = frappe.get_all("Designation", ['name'])
        data += "<tr><td style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center'>Designation</td><td style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center'>Staff</td><td style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center'>Operators</td><td style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center'>Apprentice</td><td style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center'>CL</td><td style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center'>Trainee</td><td style='border: 1px solid black;background-color:#FFA500;font-weight:bold;text-align:center'>Total</td></tr>"
        total = 0
        for d in designation:
            staff_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Staff", "Sub Staff", "Director")
                AND custom_designation = %s
                AND in_time IS NOT NULL
                AND out_time IS NULL
            """, (date1,d.name), as_dict=True)
            staff = staff_count[0].count if staff_count else 0
            trainee_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Trainee")
                AND custom_designation = %s
                AND in_time IS NOT NULL
                AND out_time IS NULL
            """, (date1,d.name), as_dict=True)
            tr = trainee_count[0].count if trainee_count else 0
            ops_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Operator")
                AND custom_designation = %s
                AND in_time IS NOT NULL
                AND out_time IS NULL
            """, (date1,d.name), as_dict=True)
            ops = ops_count[0].count if ops_count else 0
            aps_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Apprentice")
                AND custom_designation = %s
                AND in_time IS NOT NULL
                AND out_time IS NULL
            """, (date1,d.name), as_dict=True)
            trainee = aps_count[0].count if aps_count else 0
            cl_count = frappe.db.sql("""
                SELECT COUNT(*) AS count
                FROM `tabAttendance`
                WHERE attendance_date = %s
                AND custom_employee_category IN ("Contractor")
                AND custom_designation = %s
                AND in_time IS NOT NULL
                AND out_time IS NULL
            """, (date1,d.name), as_dict=True)
            cl = cl_count[0].count if cl_count else 0
            total += (staff+ops+trainee+cl+tr)
            data += "<tr><td style='border: 1px solid black;text-align:left'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td><td style='border: 1px solid black;text-align:center'>%s</td></tr>" % (d.name,staff,ops,trainee,cl,tr,(staff+ops+trainee+cl+tr))
        data += "<tr><td colspan = 6 style='border: 1px solid black;text-align:left'>Total</td><td style='border: 1px solid black;text-align:center'>%s</td></tr>" % (total)
        data += "</table>"
    return data

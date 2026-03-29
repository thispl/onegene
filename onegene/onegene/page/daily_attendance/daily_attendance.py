import frappe
from datetime import datetime, timedelta
from frappe.utils import now_datetime, getdate
@frappe.whitelist()
def get_att_data(date):
    nowtime = now_datetime()
    nowdate=getdate(date)
    import datetime as dt_module
    max_out = dt_module.datetime.strptime('07:30', '%H:%M').time()
    if nowtime.date() == nowdate and nowtime.time() < max_out:
        date1 = (nowtime - timedelta(days=1)).date()
    else:
        date1 = nowdate

    start = datetime.combine(date1, datetime.min.time())
    end = datetime.combine(date1 + timedelta(days=1), datetime.min.time())

   
    query = """
        SELECT 
            emp.gender,
            emp.department,
            emp.employee_category,
            COUNT(DISTINCT e.employee) as count
        FROM `tabEmployee Checkin` e
        JOIN `tabEmployee` emp ON e.employee = emp.name
        WHERE e.time >= %s 
            AND e.time < %s
            AND e.log_type = 'IN'
            AND NOT EXISTS (
                SELECT 1
                FROM `tabEmployee Checkin` e2
                WHERE e2.employee = e.employee
                    AND e2.log_type = 'OUT'
                    AND e2.time > e.time
                    AND e2.time >= %s
                    AND e2.time < %s
            )
        GROUP BY emp.gender, emp.department, emp.employee_category
    """
    ot_hrs = frappe.db.sql("""
        SELECT SUM(ot_hours) as ot_hrs
        FROM `tabOT Request`
        WHERE ot_requested_date = %s
        AND docstatus != 2
    """, (nowdate,), as_dict=True)
    ot_by_dept = frappe.db.sql("""
        SELECT department, SUM(ot_hours) AS total_ot
        FROM `tabOT Request`
        WHERE ot_requested_date = %s
        AND docstatus != 2
        GROUP BY department
    """, (nowdate,), as_dict=True)
    raw_data = frappe.db.sql(query, (start, end, start, end), as_dict=True)

    total_count = 0
    gender_wise = {"Male": 0, "Female": 0, "Other": 0}
    dept_wise = {}
    category_wise = {}

    for row in raw_data:
        c = row.count
        total_count += c

        # 1. Gender Wise
        gen = row.gender or "Unknown"
        gender_wise[gen] = gender_wise.get(gen, 0) + c

        # 2. Department Wise
        dept = row.department or "No Department"
        dept_wise[dept] = dept_wise.get(dept, 0) + c

        # 3. Category Wise
        cat = row.employee_category or "Uncategorized"
        category_wise[cat] = category_wise.get(cat, 0) + c

    return {
        "total": total_count or 0,
        "gender": gender_wise,
        "department": dept_wise,
        "category": category_wise,
        "ot_hrs": ot_hrs or 0,
        "ot_by_dept": ot_by_dept
    }

@frappe.whitelist()
def get_attendance_breakup_details(date, type):
    nowtime = now_datetime()
    nowdate = getdate(date)
    import datetime as dt_module
    from datetime import timedelta, datetime

    # Same logic as your main function to determine the shift date
    max_out = dt_module.datetime.strptime('07:30', '%H:%M').time()
    date1 = (nowtime - timedelta(days=1)).date() if (nowtime.date() == nowdate and nowtime.time() < max_out) else nowdate
    
    start = datetime.combine(date1, datetime.min.time())
    end = datetime.combine(date1 + timedelta(days=1), datetime.min.time())

    # Case 1: OT Hours Breakup (returns dept and hours)
    if type == "OT":
        return frappe.db.sql("""
            SELECT department, SUM(ot_hours) AS ot_hours
            FROM `tabOT Request`
            WHERE ot_requested_date = %s AND docstatus != 2
            GROUP BY department
        """, (nowdate,), as_dict=True)

    # Case 2: Present, Male, or Female Breakup
    # We build the filters dynamically
    gender_filter = ""
    if type == "Male": gender_filter = "AND emp.gender = 'Male'"
    elif type == "Female": gender_filter = "AND emp.gender = 'Female'"

    query = f"""
        SELECT 
            e.employee, 
            emp.employee_name, 
            emp.department
        FROM `tabEmployee Checkin` e
        JOIN `tabEmployee` emp ON e.employee = emp.name
        WHERE e.time >= %s AND e.time < %s
            AND e.log_type = 'IN'
            {gender_filter}
            AND NOT EXISTS (
                SELECT 1 FROM `tabEmployee Checkin` e2
                WHERE e2.employee = e.employee
                AND e2.log_type = 'OUT'
                AND e2.time > e.time
                AND e2.time >= %s AND e2.time < %s
            )
        GROUP BY e.employee
    """
    
    return frappe.db.sql(query, (start, end, start, end), as_dict=True)

@frappe.whitelist()
def get_attendance_drilldown(date, filter_type, filter_value):
    nowtime = now_datetime()
    nowdate = getdate(date)
    import datetime as dt_module
    from datetime import timedelta, datetime

    # Standard shift time logic
    max_out = dt_module.datetime.strptime('07:30', '%H:%M').time()
    date1 = (nowtime - timedelta(days=1)).date() if (nowtime.date() == nowdate and nowtime.time() < max_out) else nowdate
    
    start = datetime.combine(date1, datetime.min.time())
    end = datetime.combine(date1 + timedelta(days=1), datetime.min.time())

    # Build Dynamic Filter
    column_name = "emp.department" if filter_type == "dept" else "emp.employee_category"
    
    query = f"""
        SELECT 
            e.employee, 
            emp.employee_name, 
            emp.department,
            emp.employee_category
        FROM `tabEmployee Checkin` e
        JOIN `tabEmployee` emp ON e.employee = emp.name
        WHERE e.time >= %s AND e.time < %s
            AND e.log_type = 'IN'
            AND {column_name} = %s
            AND NOT EXISTS (
                SELECT 1 FROM `tabEmployee Checkin` e2
                WHERE e2.employee = e.employee
                AND e2.log_type = 'OUT'
                AND e2.time > e.time
                AND e2.time >= %s AND e2.time < %s
            )
        GROUP BY e.employee
    """
    
    return frappe.db.sql(query, (start, end, filter_value, start, end), as_dict=True)

from onegene.mark_attendance import get_actual_shift_start

@frappe.whitelist()
def get_shift_wise_attendance(date, drilldown = False, target_shift = None):
    nowtime = now_datetime()
    nowdate = getdate(date)
    
    import datetime as dt_module
    
    # Standard shift time logic for your dashboard
    max_out = dt_module.datetime.strptime('07:30', '%H:%M').time()
    date1 = (nowtime - timedelta(days=1)).date() if (nowtime.date() == nowdate and nowtime.time() < max_out) else nowdate
    
    start = datetime.combine(date1, datetime.min.time())
    end = datetime.combine(date1 + timedelta(days=1), datetime.min.time())

    # Get the FIRST 'IN' for every employee
    query = """
        SELECT 
            e.employee, 
            emp.employee_name, 
            emp.department, 
            emp.employee_category,
            MIN(e.time) as first_in
        FROM `tabEmployee Checkin` e
        JOIN `tabEmployee` emp ON e.employee = emp.name
        WHERE e.time >= %s AND e.time < %s
            AND e.log_type = 'IN'
            AND NOT EXISTS (
                SELECT 1 FROM `tabEmployee Checkin` e2
                WHERE e2.employee = e.employee
                AND e2.log_type = 'OUT' AND e2.time > e.time
                AND e2.time >= %s AND e2.time < %s
            )
        GROUP BY e.employee
    """
    raw_data = frappe.db.sql(query, (start, end, start, end), as_dict=True)

    shift_counts = {}
    drilldown_list = []

    for row in raw_data:
        # Get Shift using Frappe's standard function
        shift_info = get_actual_shift_start(row.employee, row.first_in)
        
        # --- SAFE CHECK FOR SHIFT INFO ---
        shift_name = "Undefined"
        if shift_info:
            if isinstance(shift_info, dict):
                shift_name = shift_info.get("shift_type", "Undefined")
            elif isinstance(shift_info, str):
                shift_name = shift_info
        # ---------------------------------
        
        if drilldown:
            if shift_name == target_shift:
                drilldown_list.append(row)
        else:
            shift_counts[shift_name] = shift_counts.get(shift_name, 0) + 1

    if drilldown:
        return drilldown_list

    # Prepare summary table rows
    summary = []
    for shift, count in shift_counts.items():
        if shift != "Undefined":
            summary.append({"shift": shift, "count": count})
    
    # Always append Undefined at the end if it exists
    if "Undefined" in shift_counts:
        summary.append({"shift": "Undefined", "count": shift_counts["Undefined"]})
        
    return summary
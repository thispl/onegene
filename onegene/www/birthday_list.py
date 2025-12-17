# @frappe.whitelist()
# def birthday_list():
#     from datetime import datetime
#     today_date = datetime.now().date()
#     employees = frappe.get_all("Employee", {"status": "Active"}, ["*"])
#     data = []
#     has_birthday = False
#     for employee in employees:
#         emp_dob = employee.date_of_birth
#         if emp_dob:
#             if emp_dob.month == today_date.month and emp_dob.day == today_date.day:

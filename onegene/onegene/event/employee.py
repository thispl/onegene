import frappe

def capture_old_name(doc, method, old_name, new_name, merge=False):
    """Capture the old name in the Employee Code (old) field"""
    
    frappe.db.set_value("Employee", doc.name, 
                        {
                            "custom_employee_code_old": old_name,
                            "custom_employee_number_old": doc.employee_number,
                            "employee_number": new_name,
                        })
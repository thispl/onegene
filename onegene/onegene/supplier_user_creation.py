import frappe



@frappe.whitelist()
def supp_user(doc,method):
    if doc.email_id:
        if frappe.db.exists("User",{"email":doc.email_id}):
            return
        else:
            new_user_doc=frappe.new_doc("User")
            new_user_doc.email=doc.email_id
            new_user_doc.first_name = doc.supplier_name
            new_user_doc.username = doc.supplier_code
            new_user_doc.supplier_group = doc.supplier_group
            if doc.supplier_group =="Outsourcing":
                new_user_doc.role_profile_name = "Supplier-Outsourcing"
            else:         
                new_user_doc.role_profile_name = "Supplier-Purchase"
            new_user_doc.module_profile = "Supplier"
            new_user_doc.user_category = "Supplier"
            new_user_doc.send_welcome_email = 1
            new_user_doc.new_password ="wonjin@321"
            new_user_doc.insert()
            
            
            new_user_per_doc = frappe.new_doc("User Permission")
            new_user_per_doc.user = doc.email_id
            new_user_per_doc.allow = "Supplier"
            new_user_per_doc.for_value =doc.name
            new_user_per_doc.apply_to_all_doctypes =1
            new_user_per_doc.is_default =1
            new_user_per_doc.insert() 
            




# @frappe.whitelist()
# def supp_user_exist(doc=None, method=None):
#     suppliers = frappe.db.get_all(
#         "Supplier",
#         filters={"email_id": ("is", "set")},
#         fields=["name", "email_id", "supplier_name", "supplier_code", "supplier_group"]
#     )

#     for supplier in suppliers:
#         if not supplier.email_id:
#             continue

#         user_values = {
#             "first_name": supplier.supplier_name,
#             "username": supplier.supplier_code,
#             "supplier_group" : supplier.supplier_group,
#             "role_profile_name": "Supplier",
#             "module_profile": "Supplier",
            
#         }

#         user_name = frappe.db.exists("User", {"email": supplier.email_id})
        
#         frappe.flags.in_import = True 

#         if user_name:
#             frappe.db.set_value("User", user_name, user_values)
#         else:
#             new_user = frappe.new_doc("User")
#             new_user.update({
#                 "email": supplier.email_id,
#                 "first_name": supplier.supplier_name,
#                 "username": supplier.supplier_code,
#                 "supplier_group" : supplier.supplier_group,
#                 "role_profile_name": "Supplier",
#                 "module_profile": "Supplier",
#                 "send_welcome_email": 1,
#                 "new_password": "wonjin@321"  
#             })
#             new_user.insert(ignore_permissions=True)
        
#         frappe.flags.in_import = False    

        
#         user_perm_name = frappe.db.exists("User Permission", {"user": supplier.email_id})
#         user_perm_values = {
#             "allow": "Supplier",
#             "for_value": supplier.name,
#             "apply_to_all_doctypes": 1,
#             "is_default": 1
#         }

#         if user_perm_name:
#             frappe.db.set_value("User Permission", user_perm_name, user_perm_values)
#         else:
#             new_perm = frappe.new_doc("User Permission")
#             new_perm.update({
#                 "user": supplier.email_id,
#                 **user_perm_values
#             })
#             new_perm.insert(ignore_permissions=True)



@frappe.whitelist()
def supp_user_exist(doc=None, method=None):
    suppliers = frappe.db.get_all(
        "Supplier",
        filters={"email_id": ("is", "set"),"supplier_code": ("not in", ["WV0260"])},
        fields=["name", "email_id", "supplier_name", "supplier_code", "supplier_group"]
    )

    for supplier in suppliers:
        if not supplier.email_id:
            continue

        existing_user_by_email = frappe.db.exists("User", {"email": supplier.email_id})
        existing_user_by_username = frappe.db.exists("User", {"username": supplier.supplier_code})
        role_profile = "Supplier-Outsourcing" if supplier.supplier_group == "Outsourcing" else "Supplier-Purchase"
        user_values = {
            "first_name": supplier.supplier_name,
            "username": supplier.supplier_code,
            "supplier_group": supplier.supplier_group,
            "role_profile_name": role_profile,
            "module_profile": "Supplier",
        }

        user_values_2 = {
            "first_name": supplier.supplier_name,
            "supplier_group": supplier.supplier_group,
            "role_profile_name": role_profile,
            "module_profile": "Supplier",
        }

        frappe.flags.in_import = True

       
        if existing_user_by_email:
            user_values_to_update = user_values.copy()
            user_values_to_update.pop("username", None) 
            frappe.db.set_value("User", existing_user_by_email, user_values)

        
        elif existing_user_by_username:
            
            frappe.log_error(
                message=f"Username conflict for supplier '{supplier.name}' — username '{supplier.supplier_code}' already exists.",
                title="Supplier User Creation Conflict"
            )

            
            frappe.logger().warning(
                f"Skipped supplier {supplier.name} — username '{supplier.supplier_code}' already exists."
            )

            
            frappe.flags.in_import = False
            continue

        
        else:
            new_user = frappe.new_doc("User")
            new_user.update({
                "email": supplier.email_id,
                "first_name": supplier.supplier_name,
                "username": supplier.supplier_code,
                "supplier_group": supplier.supplier_group,
                "role_profile_name": role_profile,
                "module_profile": "Supplier",
                "send_welcome_email": 1,
                "new_password": "wonjin@321"
            })
            new_user.insert(ignore_permissions=True)

        frappe.flags.in_import = False

        
        user_perm_name = frappe.db.exists("User Permission", {"user": supplier.email_id})
        user_perm_values = {
            "allow": "Supplier",
            "for_value": supplier.name,
            "apply_to_all_doctypes": 1,
            "is_default": 1
        }

        if user_perm_name:
            frappe.db.set_value("User Permission", user_perm_name, user_perm_values)
        else:
            new_perm = frappe.new_doc("User Permission")
            new_perm.update({
                "user": supplier.email_id,
                **user_perm_values
            })
            new_perm.insert(ignore_permissions=True)



@frappe.whitelist()
def delete_supp_user(doc,method):
    
    if doc.email_id:
        
        if frappe.db.exists("User",doc.email_id):
            frappe.delete_doc("User",doc.email_id , ignore_missing=True)
            frappe.msgprint(f"User {doc.supplier_code} is successfully deleted")
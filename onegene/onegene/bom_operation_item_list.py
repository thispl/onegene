import frappe

def update_op_item_list_manual():
    
    op_docs = frappe.db.get_all(
        "Operation Item List",
        filters={"owner": "riyaz.a@groupteampro.com"},
        fields=["name"]
    )

    for d in op_docs:
        
        
        bom_item = frappe.db.get_value("Operation Item List",{"name":d["name"]},["bom_item"])
        
       
        
        bom = frappe.db.get_value("BOM", {"item": bom_item}, "name")
        
        if not bom:
            continue
        
        operation = frappe.db.get_value("Operation Item List", {"name":d["name"]}, "operation")
        
        bom_operation = frappe.db.get_all(
            "BOM Operation",
            filters={"parent": bom, "operation": operation},
            fields=["name", "idx"],
            limit=1
        )
        
        if not bom_operation:
            continue
        
        bom_op = bom_operation[0]
        
        update_values={
            "document_name" : bom,
            "operation_name" : bom_op["name"],
            "selected_field" : f"row{bom_op['idx']}"
        }
        
        frappe.db.set_value("Operation Item List",d["name"],update_values)
        
    frappe.db.commit()        
        
    

            
              
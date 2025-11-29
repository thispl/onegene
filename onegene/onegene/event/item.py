import frappe

@frappe.whitelist()
def move_old_items_stock(old_item, new_item):
    warehouses = frappe.db.get_all("Warehouse", {"is_group": 0}, pluck="name")
    stock_items = [] # Stock Entry Details

    for warehouse in warehouses:
        qty = frappe.db.get_value("Bin", {"item_code": old_item, "warehouse": warehouse}, "actual_qty") or 0

        if qty > 0:
            # Source row: from old item
            stock_items.append({
                "item_code": old_item,
                "s_warehouse": warehouse,
                "qty": qty,
                "allow_zero_valuation_rate": 1,
                "expense_account": "Stock Adjustment - WAIP"
            })

            # Target row: to new item
            stock_items.append({
                "item_code": new_item,
                "t_warehouse": warehouse,
                "qty": qty,
                "allow_zero_valuation_rate": 1,
                "expense_account": "Stock Adjustment - WAIP"
            })

    # New Stock Entry
    if not stock_items:
        frappe.msgprint("No stock available to transfer.")
        return

    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.stock_entry_type = "Repack"

    for row in stock_items:
        stock_entry.append("items", row)

    stock_entry.insert(ignore_permissions=True)
    stock_entry.submit()

    frappe.msgprint(
        msg=f"Successfully moved stock from {old_item} to {new_item}.",
        title="Stock Updated",
        indicator="green"
    )

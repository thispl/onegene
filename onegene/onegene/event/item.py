import frappe
from frappe.utils import formatdate, format_datetime

@frappe.whitelist()
def move_old_items_stock(old_item, new_item):
    warehouses = frappe.db.get_all("Warehouse", filters={"name": "Finished Goods - WAIP"}, pluck="name")
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


@frappe.whitelist()
def get_price_history_html(item_code):
    # Last Purchase Rate
	purchase_order_schedules = frappe.db.sql("""
		SELECT pos.purchase_order_number, pos.order_rate_inr, pos.supplier_code, po.transaction_date, po.schedule_date, pos.name as purchase_order_schedule, pos.schedule_date
		FROM `tabPurchase Order Schedule` pos
		INNER JOIN `tabPurchase Order` po
			ON po.name = pos.purchase_order_number
		WHERE pos.docstatus = 1 AND pos.po_type = "Purchase Order" AND pos.item_code = %s
		ORDER BY pos.modified DESC
		LIMIT 10
	""", (item_code), as_dict=1)
 
	html = """
		<div style="margin-bottom: 30px;">
            <p>Purchase History</p>
			<table width="100%" style="border-collapse: separate; border-spacing: 0; border-radius: 8px; overflow:hidden; box-shadow:0 2px 6px rgba(0,0,0,0.2);">
				<tr style="background-color: #777472;">
					<td class="text-white text-right pr-4 pt-2 pb-2"><b>S#</b></td>
					<td class="text-white pr-2 pt-2 pb-2 pl-5"><b>Schedule Date</b></td>
					<td class="text-white pr-2 pt-2 pb-2 pl-5"><b>Purchase Order</b></td>
					<td class="text-white pt-2 pb-2 pl-5"><b>Purchase Order Schedule</b></td>
					<td class="text-white pt-2 pb-2 pl-5"><b>Supplier Code</b></td>
					<td class="text-white text-right pr-2 pt-2 pb-2"><b>Rate</b></td>
				</tr>
	"""
	idx = 0
	if not purchase_order_schedules:
		html += f"""<td colspan=6 class="pt-2 pb-2 pr-4 text-center">No Purchase History</td>"""

	for pos in purchase_order_schedules:
		idx += 1
		html += f"""<tr class="schedule-row" data-schedule="{pos.name}" style="cursor:pointer;{ 'background-color:#e5e8eb;' if idx%2==0 else ''}">"""
		html += f"""
				<td class="pt-2 pb-2 pr-4 text-right">{idx}</td>
				<td class="pt-2 pb-2 pr-2 pl-5">{formatdate(pos.schedule_date)}</td>
				<td class="pt-2 pb-2 pl-5">{pos.purchase_order_number}</td>
				<td class="pt-2 pb-2 pl-5">{pos.purchase_order_schedule}</td>
				<td class="pt-2 pb-2 pl-5">{pos.supplier_code}</td>
				<td class="pt-2 pb-2 pr-2 text-right">{pos.order_rate_inr}</td>
			</tr>
		"""

	html += """
		</table>
	</div>
	"""
	
	# RM Cost
	html += """
		<div style="margin-bottom: 10px;">
            <p>RM Cost Revision</p>
			<table width="100%" style="border-collapse: separate; border-spacing: 0; border-radius: 8px; overflow:hidden; box-shadow:0 2px 6px rgba(0,0,0,0.2);">
				<tr style="background-color: #777472;">
					<td class="text-white text-right pr-4 pt-2 pb-2"><b>S#</b></td>
					<td class="text-white pr-2 pt-2 pb-2 pl-5"><b>Revised On</b></td>
					<td class="text-white pr-2 pt-2 pb-2 pl-5"><b>Revised By</b></td>
					<td class="text-white pt-2 pb-2 pl-3 text-right"><b>RM Cost</b></td>
					<td class="text-white pt-2 pb-2 pr-2 text-right"><b>Revised RM Cost</b></td>
				</tr>
	"""
	idx = 0
	item_doc = frappe.get_doc("Item", item_code)
	if len(item_doc.custom_rm_cost_revisions) == 0:
		html += f"""<td colspan=6 class="pt-2 pb-2 pr-4 text-center">No Logs</td>"""

	for idx, row in enumerate(reversed(item_doc.custom_rm_cost_revisions), start=1):
		html += f"""<tr class="schedule-row" data-schedule="{row.name}"
			style="cursor:pointer;{'background-color:#e5e8eb;' if idx%2==0 else ''}">"""

		html += f"""
			<td class="pt-2 pb-2 pr-4 text-right">{idx}</td>
			<td class="pt-2 pb-2 pr-2 pl-5">
				{format_datetime(row.revised_on, "dd-MM-yyyy HH:mm:ss")}
			</td>
			<td class="pt-2 pb-2 pl-5">{row.revised_by}</td>
			<td class="pt-2 pb-2 pl-3 text-right">{row.rm_cost}</td>
			<td class="pt-2 pb-2 pr-2 text-right">{row.revised_rm_cost}</td>
		</tr>
    """

	html += """
		</table>
	</div>
	"""
	return html

def indian_format(n):
	s = s2 = str(int(n))
	if len(s) > 3:
		s2 = s[-3:]
		s = s[:-3]
		while len(s) > 2:
			s2 = s[-2:] + "," + s2
			s = s[:-2]
		s2 = s + "," + s2
	return s2
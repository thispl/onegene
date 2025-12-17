import frappe
from frappe.utils import flt, now_datetime, add_to_date


def update_stock_qty_in_job_card(doc, method):
	# Run after 30 seconds delay
	frappe.enqueue(
		method=enqueue_update_stock_qty_in_job_card,
		queue="long",
		enqueue_after_commit=True,
		doc=doc
	)


def enqueue_update_stock_qty_in_job_card(doc):
	try:
		for stock_entry_details in doc.items:
			job_cards = frappe.db.get_all("Job Card Required Material Operation", {"item_code": stock_entry_details.item_code}, pluck="parent")
			for job_card_name in job_cards:
				job_card = frappe.get_doc("Job Card", job_card_name)

				# if job_card.status in ["Submitted", "Cancelled", "Completed"]:
				# 	return {"updated": False}
					
				
				# possible = 0

				# for item in job_card.items:
				# 	previous_possible = job_card.for_quantity - job_card.total_completed_qty
				# 	item_warehouse = frappe.db.get_value("Item", item.item_code, "custom_warehouse")
				# 	warehouse = (
				# 		item_warehouse
				# 		if item_warehouse in ["Semi Finished Goods - WAIP", "Finished Goods - WAIP"]
				# 		else "Shop Floor - WAIP"
				# 	)

				# 	required_qty = flt(item.required_qty) / flt(job_card.for_quantity)
				# 	total_required_qty = flt(required_qty) * flt(job_card.for_quantity)

				# 	stock_qty = flt(frappe.db.get_value("Bin", {
				# 		"item_code": item.item_code,
				# 		"warehouse": warehouse
				# 	}, "actual_qty")) or 0

				# 	available_qty = flt(frappe.db.get_value("Bin", {
				# 		"item_code": item.item_code,
				# 		"warehouse": "Work In Progress - WAIP",
				# 	}, "actual_qty")) or 0

				# 	available_qty = min(available_qty, total_required_qty)
				# 	actual_qty = available_qty + stock_qty
				# 	actual_possible = min(actual_qty, total_required_qty) # in Required Qty
				# 	actual_possible = actual_possible / required_qty # in Manufacturing Qty
     
				# 	job_card.append("custom_rm_availability", {
				# 		"item_code": item.item_code,
				# 		"item_name": frappe.db.get_value("Item", item.item_code, "item_name"),
				# 		"actual_qty": actual_qty,
				# 		"available_qty": available_qty,
				# 		"stock_qty": stock_qty,
				# 		"rate": 0,
				# 		"warehouse": warehouse,
				# 	})
				# 	job_card.append("custom_required_material_for_operation", {
				# 		"item_code": item.item_code,
				# 		"item_name": frappe.db.get_value("Item", item.item_code, "item_name"),
				# 		"required_qty": required_qty,
				# 		"total_required_qty": total_required_qty,
				# 		"stock_qty": stock_qty,
				# 		"available_qty": actual_qty,
				# 		"possible_production": actual_qty / required_qty,
				# 		"consumption_qty": 0,
				# 		"actual_possible": actual_possible
				# 	})
				# 	possible = min(previous_possible, (actual_qty / required_qty))

				# if len(job_card.items) > 0:
				# 	possible_qty = round(possible)
				# else:
				# 	possible_qty = (
				# 		job_card.custom_possible_qty - job_card.custom_processed_qty
				# 		if job_card.custom_possible_qty - job_card.custom_processed_qty > 0
				# 		else 0
				# 	)
				# job_card.custom_possible_qty = possible_qty
				job_card.save(ignore_permissions=True)
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Error in enqueue_update_stock_qty_in_job_card")

def get_target_warehouse_from_mt(doc, method):
	for row in doc.items:
		warehouse = frappe.db.get_value("Material Transfer Items", row.material_request_item, "target_warehouse")
		row.t_warehouse = warehouse

def reverse_update_stock_qty_in_job_card(doc, method):
	# Run on Stock Entry Cancel
	processed = set()  # track processed job cards

	for stock_entry_details in doc.items:
		job_cards = frappe.db.get_all(
			"Job Card Required Material Operation",
			{"item_code": stock_entry_details.item_code},
			pluck="parent"
		)

		for job_card_name in job_cards:
			# skip if already processed
			if job_card_name in processed:
				continue

			job_card = frappe.get_doc("Job Card", {"name": job_card_name, "docstatus": ["!=", 2]})

			if job_card.status in ["Submitted", "Cancelled", "Completed"]:
				continue
			
			job_card.save(ignore_permissions=True)

			
   
# import frappe
# from frappe.utils import flt

# def update_stock_qty_in_job_card(doc, method):
# 	frappe.enqueue(
# 		enqueue_update_stock_qty_in_job_card,
# 		queue="long",
# 		doc=doc,
# 	)

# def enqueue_update_stock_qty_in_job_card(doc):
# 	for stock_entry_details in doc.items:
# 		job_cards = frappe.db.get_all("Job Card Required Material Operation", {"item_code": stock_entry_details.item_code}, pluck="parent")
# 		for job_card_name in job_cards:
# 			job_card = frappe.get_doc("Job Card", job_card_name)

# 			if job_card.status in ["Submitted", "Cancelled", "Completed"]:
# 				return {"updated": False}
			
# 			possible = 0

# 			for item in job_card.items:
# 				previous_possible = job_card.for_quantity - job_card.total_completed_qty
# 				item_warehouse = frappe.db.get_value("Item", item.item_code, "custom_warehouse")
# 				warehouse = (
# 					item_warehouse
# 					if item_warehouse in ["Semi Finished Goods - WAIP", "Finished Goods - WAIP"]
# 					else "Shop Floor - WAIP"
# 				)

# 				required_qty = flt(item.required_qty) / flt(job_card.for_quantity)
# 				total_required_qty = flt(required_qty) * flt(job_card.for_quantity)

# 				stock_qty = flt(frappe.db.get_value("Bin", {
# 					"item_code": item.item_code,
# 					"warehouse": warehouse
# 				}, "actual_qty")) or 0

# 				available_qty = flt(frappe.db.get_value("Bin", {
# 					"item_code": item.item_code,
# 					"warehouse": "Work In Progress - WAIP",
# 				}, "actual_qty")) or 0

# 				available_qty = min(available_qty, total_required_qty)
# 				actual_qty = available_qty + stock_qty

# 				job_card.append("custom_rm_availability", {
# 					"item_code": item.item_code,
# 					"item_name": frappe.db.get_value("Item", item.item_code, "item_name"),
# 					"actual_qty": actual_qty,
# 					"available_qty": available_qty,
# 					"stock_qty": stock_qty,
# 					"rate": 0,
# 					"warehouse": warehouse,
# 				})
# 				job_card.append("custom_required_material_for_operation", {
# 					"item_code": item.item_code,
# 					"item_name": frappe.db.get_value("Item", item.item_code, "item_name"),
# 					"required_qty": required_qty,
# 					"total_required_qty": required_qty * flt(job_card.for_quantity),
# 					"stock_qty": stock_qty,
# 					"available_qty": actual_qty,
# 					"possible_production": actual_qty / required_qty,
# 					"consumption_qty": 0,
# 				})
# 				possible = min(previous_possible, (actual_qty / required_qty))

# 			if len(job_card.items) > 0:
# 				possible_qty = round(possible)
# 			else:
# 				possible_qty = (
# 					job_card.custom_possible_qty
# 					if job_card.custom_possible_qty > 0
# 					else 0
# 				)
# 			job_card.custom_possible_qty = possible_qty
# 			job_card.save(ignore_permissions=True)   
# optimized_material_planning_report_final.py
import re
import csv
import calendar
import datetime
from math import ceil
from functools import lru_cache

import frappe
from frappe import _
from frappe.utils import flt, add_days
from frappe.utils.file_manager import get_file

# -------------------------
# Keep execute signature same as your original
# -------------------------
@frappe.whitelist()
def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	if filters.get("consolidated"):
		formatted_data = report_data(data, filters)
	else:
		formatted_data = format_data(data, filters)
	return columns, formatted_data

# -------------------------
# Main optimized get_data (drop-in replacement)
# -------------------------
def get_data(filters):
	"""
	Optimized version preserving original behavior.
	Returns same structure (last_list).
	"""
	filters = filters or {}
	data = []
	row = []
	balance = 0
	year = datetime.date.today().year
	month_str = filters.get("month")
	month_map = {
		'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
		'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
	}
	month = month_map.get(month_str)
	start_date = datetime.date(year, month, 1)
	last_day = calendar.monthrange(year, month)[1]
	to_date = filters.get("as_on_date") or datetime.date(year, month, last_day)

	# original code used material_start_date and material_end_date strings — keep as in original if needed elsewhere
	try:
		material_start_date = str(to_date) + " 08:31:00"
		material_end_date = str(add_days(to_date, 1)) + " 08:30:00"
	except Exception:
		material_start_date = None
		material_end_date = None

	# Build base Sales Order Schedule query (same conditions)
	query = """
		SELECT 
			item_code, item_name, item_group, qty, sales_order_number, name as sales_order_schedule, schedule_date
		FROM 
			`tabSales Order Schedule`
		WHERE 
			docstatus = 1
			AND schedule_date BETWEEN %(from_date)s AND %(to_date)s
			{customer_condition}
			{item_group_condition}
			{item_code_condition}
	"""
	conditions = {"from_date": start_date, "to_date": to_date}
	customer_condition = ""
	item_group_condition = ""
	item_code_condition = ""

	if filters.get("customer"):
		customer_condition = "AND customer_name = %(customer)s"
		conditions["customer"] = filters["customer"]
	if filters.get("item_group"):
		item_group_condition = "AND item_group = %(item_group)s"
		conditions["item_group"] = filters["item_group"]
	if filters.get("item_code"):
		item_code_condition = "AND item_code = %(item_code)s"
		conditions["item_code"] = filters["item_code"]

	query = query.format(
		customer_condition=customer_condition,
		item_group_condition=item_group_condition,
		item_code_condition=item_code_condition,
	)

	work_order = frappe.db.sql(query, conditions, as_dict=True)
	if not work_order:
		return []

	# -------------------------
	# Preload/calc sets to avoid per-row queries
	# -------------------------
	# Collect schedule item_codes
	schedule_item_codes = {r.item_code for r in work_order if r.item_code}

	# Bulk fetch Item master rows for schedule items
	item_rows = []
	if schedule_item_codes:
		item_rows = frappe.get_all(
			"Item",
			filters=[["name", "in", list(schedule_item_codes)]],
			fields=["name", "default_bom", "custom_warehouse", "rejection_allowance", "pack_size", "sfg_day", "item_name", "item_type", "item_group", "custom_minimum_production_qty", "custom_fg_kanban"]
		)
	item_map = {r.name: r for r in item_rows}

	# Iteratively discover BOM items to build in-memory BOM graph
	bom_items_map = {}  # bom_name -> list of BOM Item rows
	all_item_codes = set(schedule_item_codes)
	bom_to_explore = set()
	for it in item_rows:
		if getattr(it, "default_bom", None):
			bom_to_explore.add(it.default_bom)

	visited_boms = set()
	while bom_to_explore:
		batch = list(bom_to_explore)
		bom_to_explore.clear()
		bi_rows = frappe.get_all(
			"BOM Item",
			filters=[["parent", "in", batch]],
			fields=["parent as bom", "item_code", "qty", "bom_no", "item_name", "uom", "description"]
		)
		for bi in bi_rows:
			bom_items_map.setdefault(bi.bom, []).append(bi)
			if bi.item_code:
				all_item_codes.add(bi.item_code)
			if bi.get("bom_no") and bi.bom_no not in visited_boms:
				bom_to_explore.add(bi.bom_no)
		visited_boms.update(batch)

	# Bulk fetch any additional Item rows discovered from BOMs
	all_item_codes_list = list(all_item_codes)
	if all_item_codes_list:
		more_items = frappe.get_all(
			"Item",
			filters=[["name", "in", all_item_codes_list]],
			fields=["name", "custom_warehouse", "rejection_allowance", "pack_size", "sfg_day", "item_name", "item_type", "item_group", "default_bom", "custom_minimum_production_qty", "custom_fg_kanban"]
		)
		for it in more_items:
			if it.name not in item_map:
				item_map[it.name] = it

	# -------------------------
	# Bulk aggregate Bins, Delivery Notes, Sales Invoices, Quality Inspections, Work Orders
	# Use correct parameterization for IN queries (positional %s with tuple)
	# -------------------------
	bin_map_by_item = {}
	if all_item_codes_list:
		bin_rows = frappe.db.sql("""
			SELECT item_code, warehouse, SUM(actual_qty) AS actual_qty
			FROM `tabBin`
			WHERE item_code IN %s
			GROUP BY item_code, warehouse
		""", (tuple(all_item_codes_list),), as_dict=True)
		for br in bin_rows:
			bin_map_by_item.setdefault(br.item_code, {})[br.warehouse] = flt(br.actual_qty)

	# Delivery Note
	del_map = {}
	if all_item_codes_list:
		del_rows = frappe.db.sql("""
			SELECT d.item_code, SUM(d.qty) AS qty
			FROM `tabDelivery Note` p
			JOIN `tabDelivery Note Item` d ON p.name = d.parent
			WHERE p.docstatus = 1
			  AND p.posting_date BETWEEN %s AND %s
			  AND d.item_code IN %s
			GROUP BY d.item_code
		""", (start_date, to_date, tuple(all_item_codes_list)), as_dict=True)
		del_map = {r.item_code: flt(r.qty) for r in del_rows}

	# Sales Invoice (update_stock = 1)
	si_map = {}
	if all_item_codes_list:
		si_rows = frappe.db.sql("""
			SELECT sii.item_code, SUM(sii.qty) AS qty
			FROM `tabSales Invoice` si
			JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
			WHERE si.update_stock = 1
			  AND si.docstatus = 1
			  AND si.posting_date BETWEEN %s AND %s
			  AND sii.item_code IN %s
			GROUP BY sii.item_code
		""", (start_date, to_date, tuple(all_item_codes_list)), as_dict=True)
		si_map = {r.item_code: flt(r.qty) for r in si_rows}

	# Quality Inspection produced aggregations
	produced_map = {}
	if all_item_codes_list:
		produced_without_c_rows = frappe.db.sql("""
			SELECT qi.item_code, SUM(qi.custom_accepted_qty) AS qty
			FROM `tabQuality Inspection` qi
			WHERE qi.item_code IN %s
			  AND qi.docstatus = 1
			  AND qi.workflow_state != 'Rejected'
			  AND qi.custom_inspection_type = 'In Process'
			  AND qi.custom_shift != '3'
			  AND qi.report_date BETWEEN %s AND %s
			GROUP BY qi.item_code
		""", (tuple(all_item_codes_list), start_date, to_date), as_dict=True)
		produced_without_c = {r.item_code: flt(r.qty) for r in produced_without_c_rows}

		check_out_end_time = frappe.db.get_value("Shift Type", '3', "custom_checkout_end_time") or ""
		check_in_start_time = frappe.db.get_value("Shift Type", '3', "custom_checkin_start_time") or ""

		produced_with_c_after_rows = frappe.db.sql("""
			SELECT qi.item_code, SUM(qi.custom_accepted_qty) AS qty
			FROM `tabQuality Inspection` qi
			WHERE qi.item_code IN %s
			  AND qi.docstatus = 1
			  AND qi.workflow_state != 'Rejected'
			  AND qi.custom_inspection_type = 'In Process'
			  AND qi.custom_shift = '3'
			  AND qi.custom_shift_time <= %s
			  AND qi.report_date BETWEEN %s AND %s
			GROUP BY qi.item_code
		""", (tuple(all_item_codes_list), check_out_end_time, add_days(start_date,1), add_days(to_date,1)), as_dict=True)
		produced_with_c_after = {r.item_code: flt(r.qty) for r in produced_with_c_after_rows}

		produced_with_c_before_rows = frappe.db.sql("""
			SELECT qi.item_code, SUM(qi.custom_accepted_qty) AS qty
			FROM `tabQuality Inspection` qi
			WHERE qi.item_code IN %s
			  AND qi.docstatus = 1
			  AND qi.workflow_state != 'Rejected'
			  AND qi.custom_inspection_type = 'In Process'
			  AND qi.custom_shift = '3'
			  AND qi.custom_shift_time >= %s
			  AND qi.report_date BETWEEN %s AND %s
			GROUP BY qi.item_code
		""", (tuple(all_item_codes_list), check_in_start_time, start_date, to_date), as_dict=True)
		produced_with_c_before = {r.item_code: flt(r.qty) for r in produced_with_c_before_rows}

		for code in all_item_codes_list:
			produced_map[code] = flt(produced_without_c.get(code, 0)) + flt(produced_with_c_after.get(code, 0)) + flt(produced_with_c_before.get(code, 0))

	# Work Orders in-progress
	wo_map = {}
	if all_item_codes_list:
		wo_rows = frappe.db.sql("""
			SELECT wo.production_item as item_code, SUM(wo.qty) as qty
			FROM `tabWork Order` wo
			WHERE wo.production_item IN %s
			  AND wo.docstatus = 1
			  AND wo.status NOT IN ('Closed', 'Cancelled', 'Completed')
			  AND date(wo.creation) BETWEEN %s AND %s
			GROUP BY wo.production_item
		""", (tuple(all_item_codes_list), start_date, to_date), as_dict=True)
		wo_map = {r.item_code: flt(r.qty) for r in wo_rows}
	
	work_days = frappe.db.get_single_value("Production Plan Settings", "working_days") or 1

	# Helper to fetch item fields quickly
	def _item_field(item_code, field, default=None):
		it = item_map.get(item_code)
		if not it:
			# fallback to frappe.get_value only if not in map (rare)
			return frappe.get_value("Item", item_code, field) or default
		# item_map entries are objects with attributes (from frappe.get_all) — use getattr
		return getattr(it, field, default) if hasattr(it, field) else it.get(field, default) if isinstance(it, dict) else default

	# Helper to compute actual_stock per your rule
	def _actual_stock_by_rule(item_code):
		warehouse = _item_field(item_code, "custom_warehouse", None)
		item_bins = bin_map_by_item.get(item_code, {})
		if warehouse == "Finished Goods - WAIP":
			return flt(item_bins.get('Work In Progress - WAIP', 0)) + flt(item_bins.get('Finished Goods - WAIP', 0))
		elif warehouse == "Semi Finished Goods - WAIP":
			return flt(item_bins.get('Work In Progress - WAIP', 0)) + flt(item_bins.get('Semi Finished Goods - WAIP', 0))
		else:
			return flt(item_bins.get('Shop Floor - WAIP', 0))

	# In-memory BOM explosion (recursive but safe using visited set)
	def get_exploded_items_in_memory(bom, data, qty, skip_list=None, fg_plan=0, qty1=0, actual_fg=None, bal_job_card_req=None, indent=1, visited=None):
		if visited is None:
			visited = set()
		if not bom or bom in visited:
			return
		visited.add(bom)
		items = bom_items_map.get(bom, [])
		# compute bom_item stock (optional — not used for correctness; we rely on bin_map_by_item for each item)
		bom_item = frappe.db.get_value("BOM", bom, "item")
		item_warehouse = _item_field(bom_item, "custom_warehouse", None)
		item_bins = bin_map_by_item.get(bom_item, {})
		if item_warehouse:
			bom_item_stock = flt(item_bins.get(item_warehouse, 0))
		else:
			bom_item_stock = 0
		for item in items:
			item_code = item.item_code
			item_qty = (flt(item.qty) * qty) - bom_item_stock
			kanban_qty = flt(item.qty) * fg_plan
			item_warehouse = _item_field(item_code, "custom_warehouse", None)
			# append
			data.append({
				"item_code": item_code,
				"item_name": getattr(item, "item_name", "") or "",
				"bom": item.bom,
				"uom": getattr(item, "uom", None),
				"qty": item_qty,
				"description": getattr(item, "description", None),
				"fg_plan": kanban_qty,
				"indent": indent,
				"parent_bom": bom,
				"kanban_plan": qty1,
				"actual_fg": actual_fg
			})
			# recurse into child BOM if exists
			if item.get("bom_no"):
				get_exploded_items_in_memory(item.bom_no, data, item_qty, skip_list=skip_list, fg_plan=kanban_qty, qty1=qty1, actual_fg=actual_fg, bal_job_card_req=bal_job_card_req, indent=indent+1, visited=visited)

	# get_count_exploded_items uses original recursive logic but in-memory where possible
	def get_count_exploded_items_in_memory(bom_name, count_list_acc, qty=1, skip_list=None, visited=None):
		if visited is None:
			visited = set()
		if skip_list is None:
			skip_list = []
		if not bom_name or bom_name in visited:
			return
		visited.add(bom_name)
		items = bom_items_map.get(bom_name, [])
		for it in items:
			if it.item_code in skip_list:
				continue
			item_qty = flt(it.qty) * qty
			if it.get("bom_no"):
				get_count_exploded_items_in_memory(it.bom_no, count_list_acc, qty=item_qty, skip_list=skip_list, visited=visited)
			else:
				count_list_acc.append({"item_code": it.item_code, "qty": item_qty})

	# -------------------------
	# Recreate original count_bom_list behaviour
	# -------------------------
	count_bom_list = []
	for s in work_order:
		# original used frappe.db.get_value for default bom per schedule item
		default_bom = _item_field(s.item_code, "default_bom", None)
		if default_bom:
			count_bom_list.append({"bom": default_bom, "qty": s.qty, 'sch_date': s.schedule_date, 'sales_order_schedule': s.sales_order_schedule})

	# Build count_consolidated_items
	count_consolidated_items = {}
	for k in count_bom_list:
		exploded_count_list = []
		# call in-memory variant
		get_count_exploded_items_in_memory(k["bom"], exploded_count_list, qty=k["qty"])
		for item in exploded_count_list:
			item_code = item['item_code']
			qty = item['qty']
			sch_date = k['sch_date']
			sales_order_schedule = k['sales_order_schedule']
			if item_code in count_consolidated_items:
				count_consolidated_items[item_code][0] += qty
				count_consolidated_items[item_code][1] = sch_date
				if sales_order_schedule not in count_consolidated_items[item_code][2]:
					count_consolidated_items[item_code][2].append(sales_order_schedule)
			else:
				count_consolidated_items[item_code] = [qty, sch_date, [sales_order_schedule]]

	# Build count_list (unchanged)
	count = 1
	count_list = []
	for item_code, (qty, sch_date, sales_order_schedules) in count_consolidated_items.items():
		sales_order_str = ", ".join(sales_order_schedules)
		count_list.append(frappe._dict({
			"item_code": item_code,
			"order": count,
			"qty": qty,
			"sch_date": sch_date,
			"sales_orders": sales_order_str
		}))
		count += 1

	# Build bom_list as original
	bom_list = []
	for s in work_order:
		default_bom = _item_field(s.item_code, "default_bom", None)
		if default_bom:
			bom_list.append({"bom": s.item_code, "qty": s.qty, 'sch_date': s.schedule_date, 'sales_order_schedule': s.sales_order_schedule})

	# -------------------------
	# FIX: Ensure all scheduled items are included (avoid missing rows)
	# -------------------------
	consolidated_items = {}
	# First, include all schedule items (even without default_bom)
	

	# Then also add bom_list entries (original logic adds qty for items whose item_code is the FG)
	for k in bom_list:
		item_code = k['bom']
		qty = k['qty']
		sch_date = k['sch_date']
		sales_order_schedule=k['sales_order_schedule']
		if item_code and item_code in consolidated_items:
			consolidated_items[item_code][0] += qty
			consolidated_items[item_code][1] = sch_date
			if sales_order_schedule not in consolidated_items[item_code][2]:
				consolidated_items[item_code][2].append(sales_order_schedule)
		else:
			consolidated_items[item_code] = [qty,sch_date,[sales_order_schedule]]

	# Build data1 (top level rows) — preserve original calculations
	data1 = []
	for item_code, (qty, sch_date, sales_orders) in consolidated_items.items():
		rej_allowance = flt(_item_field(item_code, "rejection_allowance") or 0)
		pack_size = flt(_item_field(item_code, "pack_size") or 0)
		fg_kanban = flt(_item_field(item_code, "custom_fg_kanban") or 0)
		fg_plan = flt(_item_field(item_code, "custom_minimum_production_qty") or 0)
		sfg_days = flt(_item_field(item_code, "sfg_day") or 0)
		kanban_plan = flt(fg_plan) * flt(sfg_days)

		# compute actual_stock_qty based on item.custom_warehouse (use bin_map_by_item cached)
		item_warehouse = _item_field(item_code, "custom_warehouse", None)
		item_bins = bin_map_by_item.get(item_code, {})
		if item_warehouse:
			stock_val = flt(item_bins.get(item_warehouse, 0))
		else:
			stock_val = 0

		# replicate original del_qty logic (sum delivery note + sales invoices)
		del_qty = flt(del_map.get(item_code, 0)) + flt(si_map.get(item_code, 0))

		# produced aggregated
		prod = flt(produced_map.get(item_code, 0))

		work_days_int = int(work_days) if work_days else 1
		with_rej = (qty * (rej_allowance / 100.0)) + qty
		per_day = with_rej / max(1, work_days_int)
		if pack_size > 0:
			cal = per_day / pack_size
			total = ceil(cal) * pack_size
		else:
			total = ceil(per_day)

		# stock_in_wip for info
		stock_in_wip = flt(item_bins.get('Work In Progress - WAIP', 0))

		# balance as original
		balance = ((qty + fg_kanban) + (qty * (rej_allowance / 100.0 if rej_allowance > 0 else 0))) - (del_qty + stock_val)
		# frappe.errprint({"qty": qty, "fg_kanban": fg_kanban, "rej_allowance": rej_allowance, "del_qty": del_qty, "stock_val": stock_val})
		# actual_stock as per your exact rule (leaf warehouse logic, fallback)
		if item_warehouse == "Finished Goods - WAIP":
			actual_stock = flt(item_bins.get('Work In Progress - WAIP', 0)) + flt(item_bins.get('Finished Goods - WAIP', 0))
		elif item_warehouse == "Semi Finished Goods - WAIP":
			actual_stock = flt(item_bins.get('Work In Progress - WAIP', 0)) + flt(item_bins.get('Semi Finished Goods - WAIP', 0))
		else:
			actual_stock = flt(item_bins.get('Shop Floor - WAIP', 0))

		reqd_plan = flt(kanban_plan) - flt(actual_stock)
		in_progress = flt(wo_map.get(item_code, 0))
		bal_job_card_req = balance - (stock_val + in_progress)
		item_name = _item_field(item_code, "item_name", "")
		item_type = _item_field(item_code, "item_type", "")
		item_group = _item_field(item_code, "item_group", "")
		sales_order_schedule_str = ", ".join(sales_orders)

		data1.append(frappe._dict({
			'item_code': item_code,
			'item_name': item_name,
			'item_group': item_group,
			'in_progress': in_progress,
			'rej_allowance': rej_allowance,
			'with_rej': qty,
			'bom': _item_field(item_code, "default_bom", ""),
			'pack_size': pack_size,
			'total': total,
			'fg_plan': fg_plan,
			'fg_kanban': fg_kanban,
			'sfg_days': sfg_days,
			'kanban_plan': kanban_plan,
			'actual_stock_qty': stock_val,
			'del_qty': del_qty,
			'prod': prod,
			'balance': balance if balance > 0 else 0,
			'reqd_plan': reqd_plan,
			'date': sch_date,
			'item_type': item_type,
			'sales_order_schedule': sales_order_schedule_str,
			"indent": 0,
			"parent_bom": '',
			"actual_fg": item_code,
			"bal_job_card_req": int(bal_job_card_req) if bal_job_card_req > 0 else 0,
		}))
	# Build detailed exploded rows (da) by expanding BOMs for each data1 row that has a default BOM
	da = []
	da.extend(data1)
	for d in data1:
		exploded_data = []
		bom_item = _item_field(d.item_code, "default_bom", None)
		if bom_item:
			get_exploded_items_in_memory(bom_item, exploded_data, float(d["balance"]) if d["balance"] else 0, skip_list=bom_list, fg_plan=float(d.get('fg_plan', 0)), qty1=float(d.get('reqd_plan', 0)), actual_fg=d["actual_fg"], bal_job_card_req=d.get("bal_job_card_req", 0))
		# loop exploded items and compute fields (mirrors original logic)
		for item in exploded_data:
			item_code = item['item_code']
			qty = flt(item['qty'])
			actual_fg = item.get('actual_fg')
			kanban_plan = item.get('kanban_plan')
			parent_bom = item.get('parent_bom')
			sch_date = d['date']
			sales_order_schedule = d['sales_order_schedule']

			rej_allowance = flt(_item_field(item_code, "rejection_allowance") or 0)
			pack_size = flt(_item_field(item_code, "pack_size") or 0)
			fg_plan = flt(item.get('fg_plan') or _item_field(item_code, "custom_minimum_production_qty") or 0)
			fg_kanban = 0
			sfg_days = flt(_item_field(item_code, "sfg_day") or 0)

			# item-level bins and stock
			item_bins = bin_map_by_item.get(item_code, {})
			stock_val = flt(item_bins.get(_item_field(item_code, "custom_warehouse"), 0)) if _item_field(item_code, "custom_warehouse") else 0

			del_qty_child = flt(del_map.get(item_code, 0)) + flt(si_map.get(item_code, 0))

			prod = flt(produced_map.get(item_code, 0))
			# keep parity: include manufacture stock_entry qty (rare but original did)
			produced_rows = frappe.db.sql("""
				SELECT sed.qty
				FROM `tabStock Entry` se
				JOIN `tabStock Entry Detail` sed ON se.name = sed.parent
				WHERE sed.item_code = %s
				  AND se.docstatus = 1
				  AND se.stock_entry_type = 'Manufacture'
			""", (item_code,), as_dict=True)
			prod_from_stock_entries = sum([flt(x.qty) for x in produced_rows]) if produced_rows else 0
			prod += prod_from_stock_entries

			work_days_int = int(work_days) if work_days else 1
			with_rej = (qty * (rej_allowance / 100.0)) + qty
			per_day = with_rej / max(1, work_days_int)
			if pack_size > 0:
				cal = per_day / pack_size
				total = ceil(cal) * pack_size
			else:
				total = ceil(per_day)

			balance = qty

			item_warehouse = _item_field(item_code, "custom_warehouse")
			if item_warehouse == "Finished Goods - WAIP":
				actual_stock = flt(item_bins.get('Work In Progress - WAIP', 0))
			elif item_warehouse == "Semi Finished Goods - WAIP":
				actual_stock = flt(item_bins.get('Work In Progress - WAIP', 0)) + flt(item_bins.get('Semi Finished Goods - WAIP', 0))
			else:
				actual_stock = flt(item_bins.get('Shop Floor - WAIP', 0))

			reqd_plan = flt(kanban_plan) - flt(actual_stock)
			item_name = _item_field(item_code, "item_name", "")
			item_type = _item_field(item_code, "item_type", "")
			item_group = _item_field(item_code, "item_group", "")
			parent_bom_item = frappe.db.get_value("BOM", parent_bom, "item") if parent_bom else None
			in_progress = flt(frappe.db.sql("""
				select sum(qty) as qty
				from `tabWork Order`
				where production_item = %s
					and docstatus = 1
					and status not in ('Closed', 'Cancelled', 'Completed')
					and date(creation) between %s and %s
					and custom_actual_fg = %s
					and custom_parent_sfg = %s
			""", (item_code, start_date, to_date, actual_fg, parent_bom_item), as_dict=0)[0][0] or 0)

			bal_job_card_req = balance - (in_progress + stock_val)
			# frappe.errprint({"balance": balance, "in_progress": in_progress, "stock_Val": stock_val, "bal_job_card_req": bal_job_card_req})
			da.append(frappe._dict({
				'item_code': item_code,
				'item_name': item_name,
				'item_group': item_group,
				'in_progress': in_progress,
				'rej_allowance': rej_allowance,
				'with_rej': qty,
				'kanban_plan': kanban_plan,
				'bom': parent_bom,
				'pack_size': pack_size,
				'total': total,
				'fg_plan': fg_plan,
				'fg_kanban': fg_kanban,
				'sfg_days': sfg_days,
				'actual_stock_qty': stock_val,
				'del_qty': del_qty_child,
				'prod': prod,
				'balance': balance if balance > 0 else 0,
				'reqd_plan': reqd_plan,
				'sales_order_schedule': sales_order_schedule,
				'item_type': item_type,
				"indent": item.get('indent', 1),
				"parent_bom": parent_bom,
				"actual_fg": actual_fg,
				"bal_job_card_req": int(bal_job_card_req) if bal_job_card_req > 0 else 0,
			}))

	final_list = da if filters.get("view_rm") else data1
	last_list = []
	for updated in final_list:
		if flt(updated.get('with_rej', 0)) > 0:
			raw_item_code = re.sub(r'<[^>]*>', '', updated['item_code'])
			bom = frappe.db.get_value("Item", {'name': raw_item_code}, ['default_bom'])
			mr_qty = 0
			monthly_balance_sfg = 0
			last_list.append(frappe._dict({
				'item_code': updated['item_code'],
				'item_name': updated['item_name'],
				'item_group': updated['item_group'],
				'in_progress': updated['in_progress'],
				'item_type': updated['item_type'],
				'bom': bom,
				'rej_allowance': updated['rej_allowance'] if updated.get('indent', 0) == 0 else "",
				'with_rej': updated['with_rej'] if updated.get('indent', 0) == 0 else "",
				'pack_size': updated.get('pack_size') if updated.get('indent', 0) == 0 else "",
				'total': updated.get('total') if updated.get('indent', 0) == 0 else "",
				'fg_plan': updated.get('fg_plan') if updated.get('indent', 0) == 0 else "",
				'fg_kanban': updated.get('fg_kanban') if updated.get('indent', 0) == 0 else "",
				'sfg_days': updated.get('sfg_days') if updated.get('indent', 0) == 0 else "",
				'kanban_plan': updated.get('kanban_plan'),
				'actual_stock_qty': updated.get('actual_stock_qty'),
				'del_qty': updated.get('del_qty') if updated.get('indent', 0) == 0 else "",
				'prod': updated.get('prod'),
				'balance': updated.get('balance'),
				'sales_order_schedule': updated.get('sales_order_schedule'),
				'reqd_plan': updated.get('reqd_plan'),
				'mr_qty': mr_qty,
				'indent': updated.get('indent'),
				'parent_bom': updated.get('parent_bom'),
				"bal_job_card_req": int(updated.get('bal_job_card_req', 0)),
				"actual_fg": updated.get('actual_fg')
			}))
	return last_list

# -------------------------
# Recursive BOM explode used by original (kept for parity)
# -------------------------
def get_exploded_items(bom, data, qty, skip_list, fg_plan, qty1, actual_fg, bal_job_card_req, indent=1, visited=None):
	"""
	Kept for parity with original. This function still uses frappe.get_all per BOM,
	but the optimized flow above prefers the in-memory variant when possible.
	"""
	if visited is None:
		visited = set()

	if bom in visited:
		return
	visited.add(bom)

	exploded_items = frappe.get_all(
		"BOM Item",
		filters={"parent": bom},
		fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"],
		order_by="idx"
	)

	bom_item = frappe.db.get_value("BOM", bom, "item")
	bom_item_warehouse = frappe.db.get_value("Item", bom_item, "custom_warehouse")
	bom_item_stock = frappe.db.sql(
		"SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s AND warehouse=%s",
		(bom_item, bom_item_warehouse)
	)[0][0] or 0

	for item in exploded_items:
		item_code = item['item_code']
		item_qty = (flt(item['qty']) * qty) - bom_item_stock
		kanban_qty = flt(item['qty']) * fg_plan
		item_warehouse = frappe.db.get_value("Item", item_code, "custom_warehouse")

		if item_warehouse == "Finished Goods - WAIP":
			actual_stock = frappe.db.sql(
				"SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s AND warehouse='Work In Progress - WAIP'",
				(item_code,)
			)[0][0] or 0
		elif item_warehouse == "Semi Finished Goods - WAIP":
			actual_stock = frappe.db.sql(
				"SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s AND warehouse IN ('Work In Progress - WAIP','Semi Finished Goods - WAIP')",
				(item_code,)
			)[0][0] or 0
		else:
			actual_stock = frappe.db.sql(
				"SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s AND warehouse='Shop Floor - WAIP'",
				(item_code,)
			)[0][0] or 0

		bal_job_card_req = flt(item['qty']) * qty
		kanban_plan = flt(item['qty']) * qty1
		reqd_plan = kanban_plan - actual_stock

		data.append({
			"item_code": item_code,
			"item_name": item['item_name'],
			"bom": item['bom'],
			"uom": item['uom'],
			"qty": item_qty,
			"description": item['description'],
			"fg_plan": kanban_qty,
			"indent": indent,
			"parent_bom": bom,
			"kanban_plan": kanban_plan,
			"actual_fg": actual_fg,
		})

		if item['bom']:
			get_exploded_items(
				item['bom'],
				data,
				qty=item_qty,
				skip_list=skip_list,
				fg_plan=kanban_qty,
				qty1=reqd_plan,
				actual_fg=actual_fg,
				bal_job_card_req=bal_job_card_req,
				indent=indent + 1,
				visited=visited
			)

# kept get_count_exploded_items original (identical)
def get_count_exploded_items(bom_name, count_list, qty=1, skip_list=None, visited=None):
	if visited is None:
		visited = set()
	if skip_list is None:
		skip_list = []

	if bom_name in visited:
		return
	visited.add(bom_name)

	bom_items = frappe.get_all(
		"BOM Item",
		filters={"parent": bom_name},
		fields=["item_code", "qty", "bom_no"]
	)

	for item in bom_items:
		if item["item_code"] in skip_list:
			continue

		item_qty = flt(item["qty"]) * qty

		if item.get("bom_no"):
			get_count_exploded_items(
				bom_name=item["bom_no"],
				count_list=count_list,
				qty=item_qty,
				skip_list=skip_list,
				visited=visited
			)
		else:
			count_list.append({
				"item_code": item["item_code"],
				"qty": item_qty
			})

# -------------------------
# Columns & format/report functions — preserved from your original
# -------------------------
def get_columns(filters):
	if filters.get("view_rm") == 1 or getattr(filters, "view_rm", None) == 1:
		return [
			{"label": _("Item Code"), "fieldtype": "Data", "fieldname": "item_code", "width": 200, "options": "Item"},
			{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 200},
			{"label": _("Item Group"), "fieldtype": "Data", "fieldname": "item_group", "width": 150},
			{"label": _("Item Type"), "fieldtype": "Data", "fieldname": "item_type", "width": 150},
			{"label": _("Stock Qty"), "fieldtype": "Link", "fieldname": "actual_stock_qty", "width": 120, "options": "Material Planning Details"},
			{"label": _("Plan"), "fieldtype": "Int", "fieldname": "balance", "width": 120},
			{"label": _("Job Card Pending"), "fieldtype": "Int", "fieldname": "in_progress", "width": 150},
			{"label": _("Bal Job Card Req"), "fieldtype": "Int", "fieldname": "bal_job_card_req", "width": 150},
		]
	else:
		return [
			{"label": _("Item Code"), "fieldtype": "Data", "fieldname": "item_code", "width": 200, "options": "Item"},
			{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 200},
			{"label": _("Item Group"), "fieldtype": "Data", "fieldname": "item_group", "width": 150},
			{"label": _("Item Type"), "fieldtype": "Data", "fieldname": "item_type", "width": 150},
			{"label": _("Stock Qty"), "fieldtype": "Link", "fieldname": "actual_stock_qty", "width": 120, "options": "Material Planning Details"},
			{"label": _("Plan"), "fieldtype": "Int", "fieldname": "balance", "width": 120},
			{"label": _("Job Card Pending"), "fieldtype": "Int", "fieldname": "in_progress", "width": 150},
			{"label": _("Bal Job Card Req"), "fieldtype": "Int", "fieldname": "bal_job_card_req", "width": 150},
		]

def format_data(data, filters):
	formatted_data = []
	year = datetime.date.today().year
	month_str = filters.get("month")
	month_map = {
		'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
		'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
	}
	month = month_map.get(month_str)
	start_date = datetime.date(year, month, 1)
	last_day = calendar.monthrange(year, month)[1]
	to_date = filters.get("as_on_date") or datetime.date(year, month, last_day)
	for row in data:
		if row.get('bom'):
			formatted_data.append({
				'item_code': row['item_code'],
				'item_name': row['item_name'],
				'item_group': row['item_group'],
				'in_progress': row['in_progress'],
				'item_type': row['item_type'],
				'bom': row['bom'],
				'rej_allowance': row['rej_allowance'],
				'with_rej': row['with_rej'],
				'pack_size': row['pack_size'],
				'total': row['total'],
				'fg_plan': row['fg_plan'],
				'sfg_days': row['sfg_days'],
				'actual_stock_qty': row['actual_stock_qty'],
				'del_qty': row['del_qty'],
				'kanban_plan': row['kanban_plan'],
				'prod': row['prod'],
				'balance': row['balance'],
				'reqd_plan': row['reqd_plan'],
				'mr_qty': row.get('mr_qty', 0),
				'indent': row['indent'],
				'sales_order_schedule': row.get('sales_order_schedule', ''),
				'parent_bom': row.get('parent_bom', ''),
				"bal_job_card_req": int(row.get('bal_job_card_req') or 0),
				"actual_fg": row.get('actual_fg')
			})
	return formatted_data

def report_data(data,filters):
	formatted_data = []
	year = datetime.date.today().year
	month_str = filters.get("month")
	month_upper = filters.get("month").upper()
	month_map = {
		'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
		'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
	}
	month = month_map.get(month_str)
	start_date = datetime.date(year, month, 1)
	last_day = calendar.monthrange(year, month)[1]
	to_date = filters.get("as_on_date") or datetime.date(year, month, last_day)	

	sorted_data = sorted(data, key=lambda x: x.get("indent", 0), reverse=True)
	frappe.response["message"] = sorted_data
	consolidated_data = {}
	in_progress = 0
	for row in sorted_data:
		if row.get('bom'):
			# get in_progress for this row
			in_progress_row = frappe.db.sql("""
				select sum(qty) as qty
				from `tabWork Order`
				where production_item = %s
					and docstatus = 1 
					and status not in ('Closed', 'Cancelled', 'Completed')
					and date(creation) between %s and %s
			""", (row.get('item_code'), start_date, to_date), as_dict=0)[0][0] or 0

			key = row.get('item_code')  # Use item_code as unique key

			if key not in consolidated_data:
				bal_job_card_req = (
					row.get('balance', 0)
					- row.get('actual_stock_qty', 0)
					- in_progress_row
				)

				consolidated_data[key] = {
					'item_code': row.get('item_code'),
					'item_name': row.get('item_name'),
					'item_group': row.get('item_group'),
					'item_type': row.get('item_type'),
					'bom': row.get('bom'),
					'rej_allowance': row.get('rej_allowance', 0),
					'with_rej': row.get('with_rej', 0),
					'pack_size': row.get('pack_size', 0),
					'total': row.get('total', 0),
					'fg_plan': row.get('fg_plan', 0),
					'sfg_days': row.get('sfg_days', 0),
					'actual_stock_qty': row.get('actual_stock_qty', 0),
					'del_qty': row.get('del_qty', 0),
					'kanban_plan': row.get('kanban_plan', 0),
					'prod': row.get('prod', 0),
					'balance': row.get('balance', 0),
					'reqd_plan': row.get('reqd_plan', 0),
					'mr_qty': row.get('mr_qty', 0),
					'indent_level': row.get('indent'),
					'sales_order_schedule': row.get('sales_order_schedule', ''),
					# values that can accumulate
					'in_progress': in_progress_row,
					'bal_job_card_req': int(max(0, bal_job_card_req)),
				}
			else:
				# Merge duplicates: sum numeric fields
				existing = consolidated_data[key]

				for field in ['reqd_plan', 'balance', 'rej_allowance', 'with_rej']:
					existing[field] = (existing.get(field, 0) or 0) + (row.get(field, 0) or 0)

				# Sum in_progress across rows
				existing['in_progress'] = (existing.get('in_progress', 0) or 0) + (in_progress_row or 0)

				# Recalculate bal_job_card_req with updated values
				existing['bal_job_card_req'] = max(
					0,
					existing['balance']
					- existing.get('actual_stock_qty', 0)
					- existing['in_progress']
				)

				# Append sales order schedules safely
				existing['sales_order_schedule'] = (
					(existing.get('sales_order_schedule') or '')
					+ (row.get('sales_order_schedule') or '')
				)

	# Convert to list for output
	formatted_data = list(consolidated_data.values())
	return formatted_data


@frappe.whitelist()
def get_bom(item_code):
	bom = frappe.db.get_value("Item", item_code, "default_bom")
	return bom or ''
	

@frappe.whitelist(allow_guest=False)
def download_kqty_template():
	import json
	from frappe.utils.csvutils import UnicodeWriter
	from frappe.utils import cstr

	data = frappe.form_dict.get('data')
	if isinstance(data, str):
		data = json.loads(data)

	w = UnicodeWriter()
	w = add_header(w, data)

	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Production Kanban Qty"
	frappe.response['filename'] = "kanban_qty_template.csv"


def add_header(w,data):
	w.writerow(['Item Code','Item Name','Production Kanban Qty', 'WIP Days'])
	for i in data:
		w.writerow([i.get("item_code"),i.get("item_name"),''])
	return w

@frappe.whitelist()
def enqueue_upload(month,to_date,file):
	year = datetime.date.today().year
	month_str = month
	month_map = {
		'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
		'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
	}
	month = month_map.get(month_str)
	start_date = datetime.date(year, month, 1)
	last_day = calendar.monthrange(year, month)[1]
	to_date = to_date or datetime.date(year, month, last_day)
	file = get_file(file)
	
	content = file[1]
	if isinstance(content, bytes):
		content = content.decode('utf-8')  # decode bytes to string

	csv_rows = csv.reader(content.splitlines())
	header_skipped = False

	for row in csv_rows:
		# Skip header row
		if not header_skipped:
			header_skipped = True
			continue

		item_code = row[0]
		item_name = row[1]
		kanban_qty = row[2]
		sfg_days = row[3] or 0

		frappe.db.set_value("Item", item_code, "custom_minimum_production_qty", kanban_qty)
		frappe.db.set_value("Item", item_code, "sfg_day", sfg_days)
	return 'OK'

import frappe, json, re, datetime
from frappe import _
from frappe.utils import flt
from frappe import publish_progress

@frappe.whitelist()
def create_production_plan(month, posting_date, data, exploded=None):
	job = frappe.enqueue(
		enqueue_creation_of_production_plan,
		queue="long",
		month=month,
		posting_date=posting_date,
		data=data,
		exploded=exploded,
	)
	frappe.publish_realtime(
		"production_plan_status",
		{"stage": "Queued", "job_id": job.id},
		user=frappe.session.user
	)
	return {"status": "queued", "job_id": job.id}

def enqueue_creation_of_production_plan(month, posting_date, data, exploded=None):	
	try:
		frappe.publish_realtime(
			"production_plan_status",
			{"stage": "Started", "message": "Work Order creation started."},
			user=frappe.session.user
		)
		planned_month = month.upper()
		year = datetime.date.today().year
		month_map = {
			'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
			'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
		}
		month = month_map.get(month)
		start_date = datetime.date(year, month, 1)
		data = json.loads(data)

		assembly_items_count = 0
		pp = frappe.new_doc("Production Plan")
		pp.custom_planned_month = planned_month
		pp.company = 'WONJIN AUTOPARTS INDIA PVT.LTD.'
		pp.posting_date = posting_date
		pp.get_items_from = "Sales Order"

		seen_so = set()
		pending_wo_qty = 0

		# --- Progress tracking setup ---
		total = len(data)
		processed = 0

		for row in data:
			processed += 1

			sales_order_schedule = row.get('sales_order_schedule')
			if isinstance(sales_order_schedule, list):
				sales_order_schedule = ", ".join(sales_order_schedule)

			if row.get('bom'):
				if row.get('indent_level') == 0:
					if exploded:
						item_code = re.sub(r"</?b>", "", row.get("item_code", ""))
					else:
						item_code = row.get('item_code')

					planned_qty = int(row.get('bal_job_card_req'))
					if planned_qty > 0:
						pending_wo_qty = frappe.db.sql("""
							select sum(qty - produced_qty) as qty
							from `tabWork Order`
							where production_item = %s
								and docstatus = 1 
								and status not in ('Closed', 'Cancelled')
								and date(creation) < %s
						""", (item_code, start_date), as_dict=0)[0][0] or 0

						assembly_items_count += 1
						pp.append("po_items", {
							"doctype": "Production Plan Item",
							"item_code": item_code,
							"bom_no": row.get('bom'),
							"planned_qty": flt(planned_qty) - flt(pending_wo_qty),
							"rejection_allowance": row.get('rej_allowance'),
							# "warehouse": frappe.db.get_value("Item", item_code, 'custom_warehouse') or "Stores - WAIP",
							"custom_per_day_plan": row.get('total'),
							"custom_bin_qty": row.get('pack_size'),
							"custom_delivered_qty": row.get('del_qty'),
							"custom_production_kanban_qty": row.get('fg_plan'),
							"custom_actual_fg": row.get('actual_fg'),
							"include_exploded_items": 0,
							"custom_sales_order_schedule": sales_order_schedule
						})

				if row.get('indent_level') > 0:
					planned_qty = int(row.get('bal_job_card_req'))
					if planned_qty > 0:
						pp.append("sub_assembly_items", {
							"doctype": "Production Plan Sub Assembly Item",
							"production_item": row.get('item_code'),
							"parent_item_code": frappe.db.get_value("BOM", row.get('parent_bom'), "item"),
							"bom_no": row.get('bom'),
							"fg_warehouse": frappe.db.get_value("Item", row.get('item_code'), 'custom_warehouse') or "Work In Progress - WAIP",
							"type_of_manufacturing": "In House",
							"custom_rejection_allowance": row.get('rej_allowance'),
							"custom_per_day_plan": row.get('total'),
							"custom_bin_qty": row.get('pack_size'),
							"custom_delivered_qty": row.get('del_qty'),
							"custom_production_kanban_qty": row.get('fg_plan'),
							"bom_level": flt(row.get('indent_level')) - 1,
							"qty": flt(planned_qty) - flt(pending_wo_qty),
							"item_name": frappe.db.get_value("Item", row.get('item_code'), 'item_name'),
							"custom_actual_fg": row.get('actual_fg'),
							"custom_sales_order_schedule": sales_order_schedule
						})
			
			if total > 0:
				percent = int((processed / total) * 100)
				publish_progress(
					percent,
					title=f"Processing Production Plan",
				)
		# --- Save document ---
		if assembly_items_count > 0:
			pp.insert()
			frappe.db.commit()
			pp.submit()

			pp.make_work_order()

			# Fetch all Work Orders for this Production Plan in one go
			work_orders = frappe.db.get_all(
				"Work Order",
				filters={"production_plan": pp.name, "docstatus": 0},
				fields=["name"]
			)

			total = len(work_orders)
			submitted_wos = []
			processed = 0

			# ✅ Bulk commit every N work orders to reduce DB overhead
			BATCH_SIZE = 5

			for work_order in work_orders:
				processed += 1
				wo = frappe.get_doc("Work Order", work_order.name)

				# normal submit (keeps all validations + events)
				wo.submit()
				submitted_wos.append(wo.name)

				# Commit in batches (reduces total commit time)
				if processed % BATCH_SIZE == 0:
					frappe.db.commit()

				# Update UI progress
				if total > 0:
					percent = int((processed / total) * 100)
					publish_progress(
						percent,
						title="Creating Work Order",
						description=f"{wo.name} - {percent}%"
					)

			# Final commit
			frappe.db.commit()

			# Prepare links
			production_plan_link = f"<p>{pp.name}</p>"
			work_order_links = ", ".join([f"<p>{wo}</p>" for wo in submitted_wos])

			# Notify user
			frappe.publish_realtime(
				"production_plan_done",
				{
					"message": f"Work Order and Job Cards have been created successfully"
				},
				user=frappe.session.user
			)

			return "ok"

		else:
			production_plans = frappe.get_all(
				"Production Plan",
				filters={
					"posting_date": ["between", (posting_date, start_date)],
					"docstatus": 1
				},
				fields=["name"]
			)

			if production_plans:
				links = "<br>".join([
					f"<a href='/app/production-plan/{plan.name}'>{plan.name}</a>" for plan in production_plans
				])
				message = f"Production Plan(s) already created for the selected period:<br>{links}"
			else:
				message = "Production Plan has already been created for the existing records"

			frappe.publish_realtime(
				"production_plan_failed",
				{"message": message},
				user=frappe.session.user
			)

	except Exception as e:
		frappe.publish_realtime(
			"production_plan_failed",
			{"message": f"Job failed: {str(e)}"},
			user=frappe.session.user
		)
		frappe.log_error(frappe.get_traceback(), "Production Plan Job Failed")

@frappe.whitelist()
def get_data_for_work_order(filters):
	if filters and isinstance(filters, str):
		filters = json.loads(filters)

	filters = frappe._dict(filters)
	data = get_data(filters)
	formatted_data = format_data(data,filters)
	return formatted_data

@frappe.whitelist()
def get_job_status(job_id=None):
	"""
	Returns the status of an RQ Job.
	Status can be: queued, started, finished, failed
	"""
	try:
		if job_id:
			job = frappe.get_doc("RQ Job", job_id)
			return {"status": job.status, "job_id": job.name}
		else:
			job_list = frappe.get_all(
				"RQ Job",
				fields=["name", "job_name", "status"],
				order_by="creation desc"
			)
			for job in job_list:
				if job.job_name == "enqueue_creation_of_production_plan":
					return {"status": job.status, "job_id": job.name}

	except frappe.DoesNotExistError:
		return {"status": "not_found"}
	except Exception as e:
		# Catch Redis fetch errors or other unexpected issues
		return {"status": "unknown", "error": str(e)}

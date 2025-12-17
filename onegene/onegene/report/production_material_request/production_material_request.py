# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import calendar
import json
import re
from datetime import date, datetime
from functools import lru_cache
from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import flt, getdate, add_days, ceil

# -------------------------
# Constants / config
# -------------------------
WAREHOUSES_GROUP = (
	'Semi Finished Goods - WAIP',
	'Shop Floor - WAIP',
	'Work In Progress - WAIP',
	'Finished Goods - WAIP',
	'Stores - WAIP'
)
EXCLUDED_MR_FROM_WAREHOUSES = {"Finished Goods - WAIP", "Semi Finished Goods - WAIP"}
COMPANY_NAME = "WONJIN AUTOPARTS INDIA PVT.LTD."

# -------------------------
# Entry point
# -------------------------
def execute(filters=None):
	filters = filters or {}
	columns = get_columns(filters)
	raw = get_data(filters)
	formatted = format_data(raw, filters)
	frappe.errprint(formatted)
	return columns, formatted

# -------------------------
# Helpers
# -------------------------
def _get_month_range_from_filters(filters):
	today = getdate()
	year = today.year
	month_str = filters.get("month")
	if not month_str:
		month = today.month
	else:
		try:
			month = datetime.strptime(month_str[:3], "%b").month
		except Exception:
			month = today.month

	start_date = date(year, month, 1)
	last_day = calendar.monthrange(year, month)[1]
	to_date = filters.get("as_on_date") or date(year, month, last_day)
	material_start_date = f"{to_date} 08:31:00"
	material_end_date = f"{add_days(to_date, 1)} 08:30:00"
	return start_date, to_date, material_start_date, material_end_date

@lru_cache(maxsize=None)
def _get_item_meta(item_code):
	if not item_code:
		return {}
	values = frappe.db.get_value(
		"Item",
		item_code,
		["item_name", "item_group", "item_type", "custom_warehouse", "rejection_allowance", "pack_size", "custom_minimum_production_qty", "default_bom", "custom_fg_kanban"],
		as_dict=True
	) or {}
	return values

def _fetch_bins_for_items(item_codes):
	if not item_codes:
		return {}, {}
	placeholders = ", ".join(["%s"] * len(item_codes))
	query = f"""
		SELECT item_code, warehouse, SUM(actual_qty) as qty
		FROM `tabBin`
		WHERE item_code IN ({placeholders})
		GROUP BY item_code, warehouse
	"""
	rows = frappe.db.sql(query, tuple(item_codes), as_dict=True)
	total_by_item = defaultdict(float)
	by_item_by_warehouse = {}
	for r in rows:
		ic = r.item_code
		wh = r.warehouse
		qty = r.qty or 0
		by_item_by_warehouse[(ic, wh)] = qty
		if wh in WAREHOUSES_GROUP:
			total_by_item[ic] += qty
	return total_by_item, by_item_by_warehouse

def _fetch_plan_qtys(item_codes, target_date):
	if not item_codes:
		return {}
	placeholders = ", ".join(["%s"] * len(item_codes))
	query = f"""
		SELECT item_code, SUM(plan) as plan
		FROM `tabDaily Production Plan Item`
		WHERE item_code IN ({placeholders}) AND `date` = %s
		GROUP BY item_code
	"""
	params = tuple(item_codes) + (target_date,)
	rows = frappe.db.sql(query, params, as_dict=True)
	return {r.item_code: (r.plan or 0) for r in rows}

def _fetch_delivery_sums(item_codes, start_date, to_date):
	if not item_codes:
		return {}
	placeholders = ", ".join(["%s"] * len(item_codes))

	dn_query = f"""
		SELECT dnit.item_code as item_code, SUM(dnit.qty) as qty
		FROM `tabDelivery Note` dn
		LEFT JOIN `tabDelivery Note Item` dnit ON dn.name = dnit.parent
		WHERE dn.docstatus = 1
		  AND dnit.item_code IN ({placeholders})
		  AND dn.posting_date BETWEEN %s AND %s
		GROUP BY dnit.item_code
	"""
	dn_rows = frappe.db.sql(dn_query, tuple(item_codes) + (start_date, to_date), as_dict=True)

	si_query = f"""
		SELECT snit.item_code as item_code, SUM(snit.qty) as qty
		FROM `tabSales Invoice` si
		LEFT JOIN `tabSales Invoice Item` snit ON si.name = snit.parent
		WHERE si.update_stock = 1
		  AND si.docstatus = 1
		  AND snit.item_code IN ({placeholders})
		  AND si.posting_date BETWEEN %s AND %s
		GROUP BY snit.item_code
	"""
	si_rows = frappe.db.sql(si_query, tuple(item_codes) + (start_date, to_date), as_dict=True)

	totals = defaultdict(float)
	for r in dn_rows:
		totals[r.item_code] += r.qty or 0
	for r in si_rows:
		totals[r.item_code] += r.qty or 0
	return dict(totals)

def _fetch_work_orders_in_progress(item_codes, start_date, to_date):
	if not item_codes:
		return {}
	placeholders = ", ".join(["%s"] * len(item_codes))
	params = tuple(item_codes) + (start_date, to_date)
	query = f"""
		SELECT production_item as item_code, SUM(qty) as qty
		FROM `tabWork Order`
		WHERE production_item IN ({placeholders})
		  AND docstatus = 1
		  AND status NOT IN ('Closed', 'Cancelled')
		  AND date(creation) BETWEEN %s AND %s
		GROUP BY production_item
	"""
	rows = frappe.db.sql(query, params, as_dict=True)
	return {r.item_code: (r.qty or 0) for r in rows}

def _fetch_manufacture_stocked_qty(item_codes):
	if not item_codes:
		return {}
	placeholders = ", ".join(["%s"] * len(item_codes))
	query = f"""
		SELECT sed.item_code as item_code, SUM(sed.qty) as qty
		FROM `tabStock Entry` se
		LEFT JOIN `tabStock Entry Detail` sed ON se.name = sed.parent
		WHERE sed.t_warehouse != ''
		  AND sed.item_code IN ({placeholders})
		  AND se.docstatus = 1
		  AND se.stock_entry_type = 'Manufacture'
		GROUP BY sed.item_code
	"""
	rows = frappe.db.sql(query, tuple(item_codes), as_dict=True)
	return {r.item_code: (r.qty or 0) for r in rows}

def _build_bom_children_map():
	children = defaultdict(list)
	# Get BOM Items for BOMs - we assume BOM Items refer to valid BOM parents
	bom_items = frappe.db.get_all(
		"BOM Item",
		fields=["parent", "item_code", "qty", "bom_no", "item_name", "uom", "description", "idx"],
		order_by="parent, idx"
	)
	for b in bom_items:
		children[b.parent].append({
			"item_code": b.item_code,
			"qty": flt(b.qty),
			"bom_no": b.bom_no,
			"item_name": b.item_name,
			"uom": b.uom,
			"description": b.description
		})
	return children

def _build_default_bom_map(item_codes):
	if not item_codes:
		return {}
	placeholders = ", ".join(["%s"] * len(item_codes))
	query = f"""
		SELECT name, default_bom FROM `tabItem` WHERE name IN ({placeholders})
	"""
	rows = frappe.db.sql(query, tuple(item_codes), as_dict=True)
	return {r.name: (r.default_bom or None) for r in rows}

# -------------------------
# BOM explosion (recursive until no children)
# -------------------------
def explode_bom_recursive_parent_plan(root_bom, parent_plan, bom_children_map, ppc_plan_parent=0, indent=1, visited=None, prefetch_maps=None):
	"""
	Explode BOM in-memory, using parent's MR Required (parent_plan) as the child's kanban_plan.
	For each child:
	  - child's kanban_plan = parent_plan
	  - child's qty_required = bom_qty_per_parent * parent_plan
	  - compute child's produced/stock/etc via prefetch_maps if available
	  - child's reqd_plan (MR Required) computed from qty_required minus prod/stock etc (and used as parent_plan for next level)
	Returns a list of rows (dicts).
	"""
	visited = visited or set()
	if not root_bom or root_bom in visited:
		return []
	visited.add(root_bom)
	result = []

	children = bom_children_map.get(root_bom, [])
	# prefetch maps provide fast lookup for bins, produced, delivered, workorders
	total_bins_by_item = prefetch_maps.get("total_bins_by_item", {}) if prefetch_maps else {}
	bins_by_item_warehouse = prefetch_maps.get("bins_by_item_warehouse", {}) if prefetch_maps else {}
	delivered_map = prefetch_maps.get("delivered_map", {}) if prefetch_maps else {}
	manufactured_map = prefetch_maps.get("manufactured_map", {}) if prefetch_maps else {}
	workorder_inprog_map = prefetch_maps.get("workorder_inprog_map", {}) if prefetch_maps else {}
	ppc_tent_map = prefetch_maps.get("ppc_tent_map", {}) if prefetch_maps else {}

	for child in children:
		item_code = child["item_code"]
		bom_qty_per_parent = flt(child["qty"])  # quantity of child per one parent unit
		# child's kanban_plan equals parent's MR Required (propagation rule)
		child_kanban_plan = flt(parent_plan)

		# actual absolute child qty required = bom_qty_per_parent * parent_plan
		child_qty_required = bom_qty_per_parent * child_kanban_plan

		# Use prefetch maps to compute stock/production
		all_stores_child = total_bins_by_item.get(item_code, 0)
		stock_in_sfg_child = bins_by_item_warehouse.get((item_code, 'Semi Finished Goods - WAIP'), 0)
		stock_in_sfs_child = bins_by_item_warehouse.get((item_code, 'Shop Floor - WAIP'), 0)
		stock_in_wip_child = bins_by_item_warehouse.get((item_code, 'Work In Progress - WAIP'), 0)
		prod_child = manufactured_map.get(item_code, 0)
		del_qty_child = delivered_map.get(item_code, 0)
		in_progress_child = flt(workorder_inprog_map.get(item_code, 0))

		# compute rejection allowance & pack size from item meta if available
		meta_child = _get_item_meta(item_code)
		rej_allowance = flt(meta_child.get('rejection_allowance') or 0)
		pack_size = flt(meta_child.get('pack_size') or 0)

		# balance calculation for child (mirrors original logic but using child_qty_required)
		# (qty + rej) - produced (we don't add ppc_tent here for child; parent-driven plan covers that)
		balance_child = (child_qty_required + (child_qty_required * (rej_allowance / 100 if rej_allowance > 0 else 0))) - prod_child

		# actual_stock logic similar to original (based on warehouse)
		warehouse_child = meta_child.get("custom_warehouse")
		if warehouse_child == "Finished Goods - WAIP":
			actual_stock_child = bins_by_item_warehouse.get((item_code, 'Work In Progress - WAIP'), 0) or 0
		elif warehouse_child == "Semi Finished Goods - WAIP":
			actual_stock_child = (bins_by_item_warehouse.get((item_code, 'Work In Progress - WAIP'), 0) +
								  bins_by_item_warehouse.get((item_code, 'Semi Finished Goods - WAIP'), 0)) or 0
		else:
			actual_stock_child = bins_by_item_warehouse.get((item_code, 'Shop Floor - WAIP'), 0) or 0

		# child's reqd_plan is computed as child's kanban_plan * bom_qty_per_parent - actual_stock_child,
		# but we must ensure no negative; also the original code sometimes capped by balance
		# We'll compute candidate_reqd = child_qty_required - actual_stock_child
		candidate_reqd = child_qty_required - actual_stock_child
		candidate_reqd = candidate_reqd if candidate_reqd > 0 else 0
		# final reqd_plan should not exceed balance_child (if balance_child positive)
		reqd_plan_child = candidate_reqd if candidate_reqd <= balance_child else balance_child
		
		# Append the child row
		result.append({
			"item_code": item_code,
			"item_name": child.get("item_name"),
			"bom": child.get("bom_no"),
			"uom": child.get("uom"),
			"qty": child_qty_required,
			"description": child.get("description"),
			# child's kanban_plan (plan to be shown) is equal to parent's MR Required
			"ppc_plan": child_kanban_plan,
			"indent": indent,
			# For display consistency, set kanban_plan to child_kanban_plan (propagated plan)
			"kanban_plan": child_kanban_plan,
			"parent_bom": root_bom,
			"reqd_plan": reqd_plan_child
		})

		# Recurse if the child has its own BOM
		if child.get("bom_no"):
			# pass this child's reqd_plan as the parent_plan for the next level
			child_prefetch_maps = prefetch_maps  # reuse same prefetch maps
			result.extend(explode_bom_recursive_parent_plan(
				child["bom_no"],
				parent_plan=reqd_plan_child,
				bom_children_map=bom_children_map,
				ppc_plan_parent=child_kanban_plan,
				indent=indent + 1,
				visited=visited,
				prefetch_maps=child_prefetch_maps
			))

	return result

def explode_bom_for_count(root_bom, qty, bom_children_map, visited=None):
	visited = visited or set()
	if not root_bom or root_bom in visited:
		return []
	visited.add(root_bom)
	result = []
	children = bom_children_map.get(root_bom, [])
	for child in children:
		item_code = child["item_code"]
		item_qty = flt(child["qty"]) * qty
		result.append({
			"item_code": item_code,
			"qty": item_qty,
			"bom": child.get("bom_no"),
			"item_name": child.get("item_name"),
			"uom": child.get("uom"),
			"description": child.get("description")
		})
		if child.get("bom_no"):
			result.extend(explode_bom_for_count(child["bom_no"], item_qty, bom_children_map, visited=visited))
	return result

# -------------------------
# Main data assembly
# -------------------------
def get_data(filters):
	filters = filters or {}
	start_date, to_date, material_start_date, material_end_date = _get_month_range_from_filters(filters)

	# Build where clause for Sales Order Schedule
	sql_conditions = []
	params = [start_date, to_date]
	if filters.get("customer"):
		sql_conditions.append("customer_name = %s")
		params.append(filters["customer"])
	if filters.get("item_group"):
		sql_conditions.append("item_group = %s")
		params.append(filters["item_group"])
	if filters.get("item_code"):
		sql_conditions.append("item_code = %s")
		params.append(filters["item_code"])
	where_clause = (" AND " + " AND ".join(sql_conditions)) if sql_conditions else ""
	query = f"""
		SELECT item_code, item_name, item_group, qty, sales_order_number, schedule_date
		FROM `tabSales Order Schedule`
		WHERE docstatus = 1
		  AND schedule_date BETWEEN %s AND %s
		{where_clause}
	"""
	work_orders = frappe.db.sql(query, tuple(params), as_dict=True)
	if not work_orders:
		return []

	top_item_codes = list({wo.item_code for wo in work_orders})

	# Preloads
	default_bom_map = _build_default_bom_map(top_item_codes)
	item_meta_cache = {ic: _get_item_meta(ic) for ic in top_item_codes}
	bom_children_map = _build_bom_children_map()

	# Build count_bom_list and expand to count_consolidated_items
	count_bom_list = []
	for s in work_orders:
		# find BOM for this item
		count_bom = default_bom_map.get(s.item_code) or frappe.db.get_value("BOM", {"item": s.item_code, "is_default": 1, "docstatus": 1}, "name")
		if count_bom:
			count_bom_list.append({"bom": count_bom, "qty": s.qty, "sch_date": s.schedule_date, "sales_order_number": s.sales_order_number})

	count_consolidated_items = {}
	for k in count_bom_list:
		exploded = explode_bom_for_count(k["bom"], k["qty"], bom_children_map)
		for item in exploded:
			code = item["item_code"]
			qty = flt(item["qty"])
			sch_date = k["sch_date"]
			so_num = k["sales_order_number"]
			if code in count_consolidated_items:
				count_consolidated_items[code][0] += qty
				count_consolidated_items[code][1] = sch_date
				count_consolidated_items[code][2] = so_num
			else:
				count_consolidated_items[code] = [qty, sch_date, so_num]

	# Build consolidated_items from items having default_bom
	bom_list = []
	for s in work_orders:
		meta = item_meta_cache.get(s.item_code) or {}
		bom = meta.get("default_bom") or None
		if bom:
			bom_list.append({"bom": s.item_code, "qty": s.qty, "sch_date": s.schedule_date, "sales_order_number": s.sales_order_number})

	consolidated_items = {}
	for k in bom_list:
		item_code = k['bom']
		qty = k['qty']
		sch_date = k['sch_date']
		sales_order_number = k['sales_order_number']
		if item_code and item_code in consolidated_items:
			consolidated_items[item_code][0] += qty
			consolidated_items[item_code][1] = sch_date
			consolidated_items[item_code][2] = sales_order_number
		else:
			consolidated_items[item_code] = [qty, sch_date, sales_order_number]

	# Gather all item codes we need to prefetch stocks/plan etc for (consolidated + referenced BOM children)
	initial_item_codes = set(consolidated_items.keys()) | set(count_consolidated_items.keys())
	referenced_bom_children = set()
	for bom, children in bom_children_map.items():
		for child in children:
			referenced_bom_children.add(child["item_code"])
	all_needed_codes = list(initial_item_codes | referenced_bom_children)

	# Prefetch bins, plans, deliveries, manufacture, workorders
	total_bins_by_item, bins_by_item_warehouse = _fetch_bins_for_items(all_needed_codes)
	ppc_plan_map = _fetch_plan_qtys(all_needed_codes, to_date)
	ppc_tent_map = _fetch_plan_qtys(all_needed_codes, add_days(to_date, 1))
	delivered_map = _fetch_delivery_sums(all_needed_codes, start_date, to_date)
	manufactured_map = _fetch_manufacture_stocked_qty(all_needed_codes)
	workorder_inprog_map = _fetch_work_orders_in_progress(all_needed_codes, start_date, to_date)

	prefetch_maps = {
		"total_bins_by_item": total_bins_by_item,
		"bins_by_item_warehouse": bins_by_item_warehouse,
		"ppc_plan_map": ppc_plan_map,
		"ppc_tent_map": ppc_tent_map,
		"delivered_map": delivered_map,
		"manufactured_map": manufactured_map,
		"workorder_inprog_map": workorder_inprog_map,
		"ppc_tent_map": ppc_tent_map
	}

	# Build data1 (top-level consolidated items)
	data1 = []
	for item_code, (qty, sch_date, sales_order_number) in consolidated_items.items():
		meta = _get_item_meta(item_code)
		rej_allowance = flt(meta.get("rejection_allowance") or 0)
		pack_size = flt(meta.get("pack_size") or 0)
		
		fg_kanban = flt(meta.get("custom_fg_kanban") or 0)
		ppc_plan = flt(ppc_plan_map.get(item_code) or 0)
		ppc_tentative_plan = flt(ppc_tent_map.get(item_code) or 0)
		kanban_plan = flt(ppc_plan) + flt(ppc_tentative_plan)
		
		all_stores = total_bins_by_item.get(item_code, 0)
		stock_in_sfg = bins_by_item_warehouse.get((item_code, 'Semi Finished Goods - WAIP'), 0)
		stock_in_sfs = bins_by_item_warehouse.get((item_code, 'Shop Floor - WAIP'), 0)
		stock_in_wip = bins_by_item_warehouse.get((item_code, 'Work In Progress - WAIP'), 0)
		stock_in_sw = bins_by_item_warehouse.get((item_code, meta.get("custom_warehouse")), 0)

		stock = frappe.db.sql("""
			SELECT SUM(actual_qty) as actual_qty 
			FROM `tabBin` 
			WHERE item_code = %s AND warehouse = 'Finished Goods - WAIP'
		""", (item_code,), as_dict=True)[0]
		if not stock["actual_qty"]:
			stock["actual_qty"] = 0

		del_qty = delivered_map.get(item_code, 0)
		prod = manufactured_map.get(item_code, 0)
		in_progress = flt(workorder_inprog_map.get(item_code, 0))

		work_days = frappe.db.get_single_value("Production Plan Settings", "working_days") or 1
		with_rej = qty + (qty * (rej_allowance/100 if rej_allowance>0 else 0))
		per_day = (with_rej / int(work_days)) if int(work_days) > 0 else with_rej

		if pack_size > 0:
			cal = per_day / pack_size
			total = ceil(cal) * pack_size
		else:
			total = ceil(per_day)

		# Balance: keep original style but safer
		balance = ((qty + fg_kanban) +(qty * (rej_allowance / 100 if rej_allowance else 0))) - (del_qty + stock["actual_qty"])
		# balance = (
		# 	qty + (qty * (rej_allowance/100 if rej_allowance > 0 else 0)) + (ppc_tentative_plan * ppc_plan)
		# ) - prod - all_stores

		item_name = meta.get("item_name")
		item_type = meta.get("item_type")
		warehouse = meta.get("custom_warehouse")
		item_group = meta.get("item_group")
		bom = meta.get("default_bom")

		reqd_plan = max(kanban_plan - all_stores, 0)
		reqd_plan = reqd_plan if reqd_plan <= balance else balance
		row = frappe._dict({
			'item_code': item_code,
			'item_name': item_name,
			'item_group': item_group,
			'in_progress': in_progress,
			'rej_allowance': rej_allowance,
			'with_rej': qty,
			'bom': bom,
			'pack_size': pack_size,
			'total': total,
			'ppc_plan': ppc_plan,
			'ppc_tentative_plan': ppc_tentative_plan,
			'kanban_plan': kanban_plan,
			'actual_stock_qty': all_stores,
			'del_qty': del_qty,
			'prod': prod,
			'balance': balance,
			'reqd_plan': reqd_plan,
			'date': sch_date,
			'item_type': item_type,
			'stock_in_sw': stock_in_sw,
			'stock_in_sfg': stock_in_sfg,
			'stock_in_sfs': stock_in_sfs,
			'stock_in_wip': stock_in_wip,
			'warehouse': warehouse,
			'sales_order_number': sales_order_number,
			"indent": 0,
			"parent_bom": ''
		})
		data1.append(row)

	# Build da list (FG + children exploded with propagation)
	da = []
	for d in data1:
		da.append(frappe._dict({
			'item_code': f"<b>{d.item_code}</b>",
			'item_name': d.item_name,
			'item_group': d.item_group,
			'in_progress': d.in_progress,
			'rej_allowance': d.rej_allowance,
			'with_rej': d.with_rej,
			'bom': d.bom,
			'pack_size': d.pack_size,
			'total': d.total,
			'ppc_plan': d.ppc_plan,
			'ppc_tentative_plan': d.ppc_tentative_plan,
			'kanban_plan': d.kanban_plan,
			'actual_stock_qty': d.actual_stock_qty,
			'del_qty': d.del_qty,
			'prod': d.prod,
			'balance': d.balance,
			'reqd_plan': d.reqd_plan,
			'date': d.date,
			'item_type': d.item_type,
			'stock_in_sw': d.stock_in_sw,
			'warehouse': d.warehouse,
			'stock_in_sfg': d.stock_in_sfg,
			'stock_in_sfs': d.stock_in_sfs,
			'stock_in_wip': d.stock_in_wip,
			'sales_order_number': f"<b>{d.sales_order_number}</b>",
			"indent": 0,
			"parent_bom": d.parent_bom
		}))

		# Explode using iterative recursion that propagates reqd_plan downward
		if d.bom:
			# Pass prefetch maps to explosion
			exploded_children = explode_bom_recursive_parent_plan(
				root_bom=d.bom,
				parent_plan=float(d.get("reqd_plan") or 0),
				bom_children_map=bom_children_map,
				ppc_plan_parent=float(d.get("ppc_plan") or 0),
				indent=1,
				visited=set(),
				prefetch_maps=prefetch_maps
			)

			# Append exploded rows to da with computed fields
			for item in exploded_children:
				item_code = item["item_code"]
				meta_child = _get_item_meta(item_code)

				all_stores_child = total_bins_by_item.get(item_code, 0)
				stock_in_sfg_child = bins_by_item_warehouse.get((item_code, 'Semi Finished Goods - WAIP'), 0)
				stock_in_sfs_child = bins_by_item_warehouse.get((item_code, 'Shop Floor - WAIP'), 0)
				stock_in_wip_child = bins_by_item_warehouse.get((item_code, 'Work In Progress - WAIP'), 0)
				stock_in_sw_child = bins_by_item_warehouse.get((item_code, meta_child.get("custom_warehouse")), 0)

				del_qty_child = delivered_map.get(item_code, 0)
				prod_child = manufactured_map.get(item_code, 0)
				in_progress_child = flt(workorder_inprog_map.get(item_code, 0))

				# Use computed values from explosion
				qty = item.get("qty")
				kanban_plan = item.get("kanban_plan")
				parent_bom = item.get("parent_bom")
				reqd_plan_child = item.get("reqd_plan")

				da.append(frappe._dict({
					'item_code': item_code,
					'item_name': meta_child.get("item_name"),
					'item_group': meta_child.get("item_group"),
					'in_progress': in_progress_child,
					'rej_allowance': flt(meta_child.get('rejection_allowance') or 0),
					'with_rej': qty,
					'bom': item.get('bom'),
					'pack_size': flt(meta_child.get('pack_size') or 0),
					'total': None,
					'ppc_plan': item.get('ppc_plan'),
					'ppc_tentative_plan': flt(ppc_tent_map.get(item_code) or 0),
					'kanban_plan': kanban_plan,
					'actual_stock_qty': all_stores_child,
					'del_qty': del_qty_child,
					'prod': prod_child,
					'balance': (qty + (qty * (flt(meta_child.get('rejection_allowance') or 0) / 100))) - prod_child,
					'reqd_plan': reqd_plan_child,
					'sales_order_number': d.sales_order_number,
					'item_type': meta_child.get("item_type"),
					'stock_in_sw': stock_in_sw_child,
					'warehouse': meta_child.get("custom_warehouse"),
					'stock_in_sfg': stock_in_sfg_child,
					'stock_in_sfs': stock_in_sfs_child,
					'stock_in_wip': stock_in_wip_child,
					"indent": item.get("indent"),
					"parent_bom": parent_bom
				}))

	# final_list selection
	final_list = da if filters.get('view_rm') else data1

	# Build last_list with MR qty checks
	last_list = []
	current_bom = None
	for updated in final_list:
		raw_item_code = re.sub(r'<[^>]*>', '', updated['item_code']) if updated.get('item_code') else updated.get('item_code')
		bom_for_raw = frappe.db.get_value("Item", {'name': raw_item_code}, ['default_bom']) or None

		if updated.get('item_type') == 'Process Item' and updated.get('indent') == 0:
			current_bom = bom_for_raw

		if updated.get('with_rej', 0) > 0:
			mr_query = """
				SELECT SUM(`tabMaterial Request Item`.qty) as qty
				FROM `tabMaterial Request`
				LEFT JOIN `tabMaterial Request Item` ON `tabMaterial Request`.name = `tabMaterial Request Item`.parent
				WHERE `tabMaterial Request Item`.custom_indent = %s
				  AND `tabMaterial Request`.transaction_date BETWEEN %s AND %s
				  AND `tabMaterial Request Item`.custom_bom = %s
				  AND `tabMaterial Request Item`.custom_parent_bom = %s
				  AND `tabMaterial Request Item`.sales_order = %s
				  AND `tabMaterial Request Item`.item_code = %s
				  AND `tabMaterial Request`.docstatus != 2
				  AND `tabMaterial Request`.material_request_type = 'Material Transfer'
				  AND `tabMaterial Request`.creation BETWEEN %s AND %s
			"""
			params = (
				updated.get('indent'),
				start_date, to_date,
				current_bom, updated.get('parent_bom'),
				updated.get('sales_order_number'),
				raw_item_code,
				material_start_date, material_end_date
			)
			mr_qty_row = frappe.db.sql(mr_query, params, as_dict=True)
			mr_qty = (mr_qty_row[0].qty if mr_qty_row and mr_qty_row[0].qty else 0)

			last_list.append(frappe._dict({
				'item_code': updated['item_code'],
				'item_name': updated['item_name'],
				'item_group': updated['item_group'],
				'in_progress': updated['in_progress'],
				'item_type': updated['item_type'],
				'stock_in_sw': updated.get('stock_in_sw'),
				'stock_in_sfg': updated.get('stock_in_sfg'),
				'stock_in_sfs': updated.get('stock_in_sfs'),
				'stock_in_wip': updated.get('stock_in_wip'),
				'warehouse': updated.get('warehouse'),
				'bom': bom_for_raw,
				'rej_allowance': updated['rej_allowance'] if updated['indent'] == 0 else "",
				'with_rej': updated['with_rej'],
				'pack_size': updated['pack_size'] if updated['indent'] == 0 else "",
				'total': updated.get('total') if updated['indent'] == 0 else "",
				'ppc_plan': updated.get('ppc_plan') if updated['indent'] == 0 else "",
				'ppc_tentative_plan': updated.get('ppc_tentative_plan') if updated['indent'] == 0 else "",
				'kanban_plan': updated.get('kanban_plan'),
				'actual_stock_qty': updated.get('actual_stock_qty'),
				'del_qty': updated.get('del_qty') if updated['indent'] == 0 else "",
				'prod': updated.get('prod'),
				'balance': updated.get('balance'),
				'sales_order_number': updated.get('sales_order_number'),
				'reqd_plan': updated.get('reqd_plan') if updated.get('reqd_plan', 0) >= 0 else 0,
				'mr_qty': mr_qty,
				'indent': updated.get('indent'),
				'parent_bom': updated.get('parent_bom')
			}))

	return last_list

# -------------------------
# Columns
# -------------------------
def get_columns(filters):
	if filters and (filters.get("view_rm") == 1 or filters.get("view_rm") == '1'):
		return [
			{"label": _("Item Code"), "fieldtype": "Data", "fieldname": "item_code", "width": 200, "options": "Item"},
			{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 200},
			{"label": _("Item Group"), "fieldtype": "Data", "fieldname": "item_group", "width": 150},
			{"label": _("Item Type"), "fieldtype": "Data", "fieldname": "item_type", "width": 150},
			{"label": _("Warehouse"), "fieldtype": "Data", "fieldname": "warehouse", "width": 250},
			{"label": _("Plan"), "fieldtype": "Float", "fieldname": "kanban_plan", "width": 150},
			{"label": _("Stock In SW"), "fieldtype": "Float", "fieldname": "stock_in_sw", "width": 150},
			{"label": _("Stock In SFG"), "fieldtype": "Float", "fieldname": "stock_in_sfg", "width": 150},
			{"label": _("Stock In Shop Floor"), "fieldtype": "Float", "fieldname": "stock_in_sfs", "width": 180},
			{"label": _("Stock In WIP"), "fieldtype": "Float", "fieldname": "stock_in_wip", "width": 150},
			{"label": _("MR Required"), "fieldtype": "Float", "fieldname": "reqd_plan", "width": 150},
		]
	else:
		return [
			{"label": _("Item Code"), "fieldtype": "Data", "fieldname": "item_code", "width": 200, "options": "Item"},
			{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 200},
			{"label": _("Item Group"), "fieldtype": "Data", "fieldname": "item_group", "width": 150},
			{"label": _("Sales Order"), "fieldtype": "Data", "fieldname": "sales_order_number", "width": 200, "options": "Sales Order"},
			{"label": _("Plan"), "fieldtype": "Float", "fieldname": "kanban_plan", "width": 150},
			{"label": _("MR Required"), "fieldtype": "Float", "fieldname": "reqd_plan", "width": 150},
		]

# -------------------------
# Format + Production Plan Report creation
# -------------------------
def format_data(data, filters):
	formatted_data = []
	start_date, to_date, _, _ = _get_month_range_from_filters(filters)
	month_upper = (filters.get("month") or "").upper()

	for row in data:
		sales_order_no = row.get('sales_order_number') or ''
		customer = frappe.db.get_value("Sales Order", {'name': sales_order_no}, ['customer']) if sales_order_no else None

		if filters.get('view_rm') != 1 and sales_order_no:
			exists = frappe.db.exists("Production Plan Report", {
				'item': row['item_code'],
				'date': ('between', (start_date, to_date)),
				'customer': customer
			})

			if exists:
				try:
					ppd = frappe.get_doc("Production Plan Report", {
						'item': row['item_code'],
						'date': ('between', (start_date, to_date)),
						'customer': customer
					})
					ppd.monthly_schedule = float(row.get('with_rej') or 0)
					ppd.stock_qty = float(row.get('actual_stock_qty') or 0)
					ppd.delivered_qty = float(row.get('del_qty') or 0)
					ppd.produced_qty = float(row.get('prod') or 0)
					ppd.monthly_balance = float(row.get('balance') or 0)
					ppd.required_plan = float(row.get('reqd_plan') or 0)
					ppd.customer = customer
					ppd.save(ignore_permissions=True)
					frappe.db.commit()
				except Exception:
					frappe.log_error(frappe.get_traceback(), "Production Material Request - update PPR")
			else:
				try:
					ppd = frappe.new_doc("Production Plan Report")
					ppd.item = row['item_code']
					ppd.item_name = row.get('item_name')
					ppd.item_group = row.get('item_group')
					ppd.in_progress = row.get('in_progress')
					ppd.item_type = row.get('item_type')
					ppd.date = start_date
					ppd.month = month_upper
					ppd.rej_allowance = float(row.get('rej_allowance') or 0)
					ppd.monthly_schedule = float(row.get('with_rej') or 0)
					ppd.bin_qty = float(row.get('pack_size') or 0)
					ppd.per_day_plan = float(row.get('total') or 0)
					ppd.fg_kanban_qty = float(row.get('ppc_plan') or 0)
					ppd.stock_qty = float(row.get('actual_stock_qty') or 0)
					ppd.delivered_qty = float(row.get('del_qty') or 0)
					ppd.produced_qty = float(row.get('prod') or 0)
					ppd.monthly_balance = float(row.get('balance') or 0)
					ppd.required_plan = float(row.get('reqd_plan') or 0)
					ppd.customer = customer
					ppd.save(ignore_permissions=True)
					try:
						ppd.submit()
					except Exception:
						pass
					frappe.db.commit()
				except Exception:
					frappe.log_error(frappe.get_traceback(), "Production Material Request - create PPR")

		formatted_data.append({
			'item_code': row.get('item_code'),
			'item_name': row.get('item_name'),
			'item_group': row.get('item_group'),
			'in_progress': row.get('in_progress'),
			'item_type': row.get('item_type'),
			'warehouse': row.get('warehouse'),
			'stock_in_sw': row.get('stock_in_sw'),
			'stock_in_sfg': row.get('stock_in_sfg'),
			'stock_in_sfs': row.get('stock_in_sfs'),
			'stock_in_wip': row.get('stock_in_wip'),
			'bom': row.get('bom'),
			'rej_allowance': row.get('rej_allowance'),
			'with_rej': row.get('with_rej'),
			'pack_size': row.get('pack_size'),
			'total': row.get('total'),
			'ppc_plan': row.get('ppc_plan'),
			'ppc_tentative_plan': row.get('ppc_tentative_plan'),
			'kanban_plan': row.get('kanban_plan'),
			'actual_stock_qty': row.get('actual_stock_qty'),
			'del_qty': row.get('del_qty'),
			'prod': row.get('prod'),
			'balance': row.get('balance'),
			'reqd_plan': row.get('reqd_plan'),
			'mr_qty': row.get('mr_qty'),
			'indent': row.get('indent'),
			'sales_order_number': row.get('sales_order_number', ''),
			'parent_bom': row.get('parent_bom', '')
		})
	return formatted_data

# -------------------------
# Whitelisted helpers
# -------------------------
@frappe.whitelist()
def get_bom(item_code):
	bom = frappe.db.get_value("Item", item_code, "default_bom")
	return bom or ''

@frappe.whitelist()
def create_mr(data, to_date, month):
	from onegene.onegene.doctype.production_material_request.production_material_request import make_prepared_report

	year = date.today().year
	month_map = {
		'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
		'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
	}
	month_number = month_map.get(month.upper()) if month else None
	if not month_number:
		frappe.throw(_("Invalid month provided."))
	try:
		start_date = date(year, month_number, 1)
	except Exception:
		start_date = date.today().replace(day=1)

	rows = json.loads(data or "[]")
	warehouse_groups = defaultdict(list)
	current_fg_bom = None

	for row in rows:
		indent = int(row.get("indent", 0))
		warehouse = row.get("warehouse")
		reqd_plan = flt(row.get("reqd_plan", 0))
		mr_qty = flt(row.get("mr_qty", 0))

		if indent == 0 and row.get("item_type") == "Process Item":
			current_fg_bom = row.get("bom") or ""
			continue

		if indent > 0 and (reqd_plan - mr_qty) > 0 and (warehouse not in EXCLUDED_MR_FROM_WAREHOUSES):
			row["fg_bom"] = current_fg_bom or ""
			warehouse_groups[warehouse].append(row)

	created_mrs = []
	for warehouse, items in warehouse_groups.items():
		mr_doc = frappe.new_doc("Material Request")
		mr_doc.material_request_type = "Material Transfer"
		mr_doc.set_from_warehouse = warehouse
		mr_doc.set_warehouse = "Shop Floor - WAIP"
		mr_doc.company = COMPANY_NAME
		mr_doc.transaction_date = to_date
		mr_doc.schedule_date = to_date
		mr_doc.title = f"{warehouse} - MR"

		doc_count = 0
		for row in items:
			item_code = row.get("item_code")
			reqd_plan = flt(round(row.get("reqd_plan", 0), 2))
			mr_qty = flt(row.get("mr_qty", 0))
			required_qty = reqd_plan - mr_qty
			if required_qty <= 0:
				continue

			doc_count += 1
			custom_bom = row.get("fg_bom", "")

			shop_floor = frappe.db.sql("""
				SELECT SUM(actual_qty) AS qty FROM `tabBin`
				WHERE item_code = %s AND warehouse = 'Work In Progress - WAIP'
			""", item_code, as_dict=True)[0].qty or 0

			pps = frappe.db.sql("""
				SELECT SUM(actual_qty) AS qty FROM `tabBin`
				WHERE item_code = %s AND warehouse = 'Stores - WAIP'
			""", item_code, as_dict=True)[0].qty or 0

			mr_doc.append("items", {
				"item_code": item_code,
				"qty": required_qty,
				"custom_bom": custom_bom,
				"custom_indent": row.get("indent"),
				"custom_shop_floor_stock": shop_floor,
				"custom_pps": pps,
				"custom_total_req_qty": required_qty,
				"custom_parent_bom": row.get("parent_bom"),
				"sales_order": row.get("sales_order_number"),
				"parent_bom": row.get("parent_bom"),
				"from_warehouse": warehouse
			})

		if doc_count > 0:
			mr_doc.insert(ignore_permissions=True)
			created_mrs.append(mr_doc.name)

	if created_mrs:
		links = "<br>".join([f"<a href='/app/material-request/{name}'>{name}</a>" for name in created_mrs])
		frappe.msgprint(_("Material Requests created successfully:<br>{0}").format(links))
		frappe.msgprint(_("Material Requests வெற்றிகரமாக உருவாக்கப்பட்டது:<br>{0}").format(links))
	else:
		frappe.msgprint(_("Material Requests has been already done for the existing records"))

	try:
		make_prepared_report()
	except Exception:
		frappe.log_error(frappe.get_traceback(), "create_mr: make_prepared_report failed")
	return "ok"

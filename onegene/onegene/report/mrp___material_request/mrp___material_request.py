# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt
import math
import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils import (
	add_days,
	ceil,
	cint,
	comma_and,
	flt,
	get_link_to_form,
	getdate,
	now_datetime,
	datetime,get_first_day,get_last_day,
	nowdate,
	today,
)
def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters):
	last_list = []
	data1 = []
	final_list = []
	da = []
	dic = []
	ict = []
	data4 = []
	final = []
	cons = {}
	console = {}
	consolidate = {}
	consolidated = {}
	consolidated_items = {}
	consolidated_dict = {}
	bom_list = []
	count_consolidated_items = {}
	count_bom_list = []
	count_list = []
	
	if filters.customer:
		os = frappe.get_list("Sales Order Schedule Item", filters={"schedule_date": ["between", (filters.from_date, filters.to_date)],"customer_name":filters.customer},fields=['name', 'item_code', 'qty','schedule_date','sales_order_number'])
	else:
		os = frappe.get_list("Sales Order Schedule Item", filters={"schedule_date": ["between", (filters.from_date, filters.to_date)]},fields=['name', 'item_code', 'qty','schedule_date','sales_order_number'])

	count = 1
	for s in os:
		frappe.log_error("mrp",s.item_code)
		count_bom = frappe.db.get_value("BOM", {'item': s.item_code,'is_default':1,'docstatus':1}, ['name'])
		if count_bom:
			count_bom_list.append({"bom": count_bom, "qty": s.qty,'sch_date':s.schedule_date, 'order_schedule':s.name,'sales_order_number':s.sales_order_number})

	for k in count_bom_list:
		exploded_count_list = []
		
		get_count_exploded_items(k["bom"], exploded_count_list, k["qty"], count_bom_list)

		for item in exploded_count_list:
			item_code = item['item_code']
			qty = item['qty']
			sch_date = k['sch_date']
			sales_order_number=k['sales_order_number']

			if item_code in count_consolidated_items:
				count_consolidated_items[item_code][0] += qty
				count_consolidated_items[item_code][1] = sch_date
				count_consolidated_items[item_code][2] = sales_order_number
			else:
				count_consolidated_items[item_code] = [qty,sch_date,sales_order_number]
	for item_code, (qty,sch_date,sales_order_number) in count_consolidated_items.items():
		count_list.append(frappe._dict({'item_code': item_code,'order':count}))
		count = count+1

	for s in os:
		bom = frappe.db.get_value("Item", {'name': s.item_code}, ['default_bom'])
		if bom:
			bom_list.append({"bom": s.item_code, "qty": s.qty,'sch_date':s.schedule_date,'sales_order_number':s.sales_order_number})
		# bom_list.append({"bom": bom, "qty": s.qty,'sch_date':s.schedule_date})
	for k in bom_list:
		item_code = k['bom']
		qty = k['qty']
		sch_date = k['sch_date']
		sales_order_number=k['sales_order_number']
		if item_code and item_code in consolidated_items:
			consolidated_items[item_code][0] += qty
			consolidated_items[item_code][1] = sch_date
			consolidated_items[item_code][2] = sales_order_number
		else:
			consolidated_items[item_code] = [qty,sch_date,sales_order_number]
	for item_code, (qty,sch_date,sales_order_number) in consolidated_items.items():
		
		pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse != 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse = 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
							left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
							where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
							and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
		today_req = sf[0].qty if sf else 0
		item_billing_type = frappe.db.get_value("Item",{'item_code':item_code},'item_billing_type')
		item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
		stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - WAIP"}, ['actual_qty']) or 0
		rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance')
		item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
		safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock')
		pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
		moq =frappe.db.get_value("Item",{'item_code':item_code},'min_order_qty')
		lead_time_days =frappe.db.get_value("Item",{'item_code':item_code},'lead_time_days')
		item_warehouse = frappe.db.get_value("Item",{'item_code':item_code},'custom_warehouse')
		if item_warehouse:
			stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse = '%s'"""%(item_code,item_warehouse),as_dict = 1)[0]
		else:
			stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s'"""%(item_code),as_dict = 1)[0]
		day = frappe.db.get_single_value("Production Plan Settings", "working_days")
		if qty and qty>0:
			cvr_days = math.floor(qty/day)
			frappe.errprint(cvr_days)
			if stockqty['qty']:
				if stockqty['qty'] > 0 and cvr_days>0:
					cover_days = math.floor(stockqty['qty']/cvr_days)
			else:
				cover_days = 0
		else:
			cover_days = 0
		ppoc_total = 0
		mr_qty = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
		left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
		where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.status = 'Pending' """ % (item_code), as_dict=True)[0]
		if not mr_qty["qty"]:
			mr_qty["qty"] = 0
		ppoc_query = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 """ % (item_code), as_dict=True)[0]
		if not ppoc_query["qty"]:
			ppoc_query["qty"] = 0
		ppoc_receipt = frappe.db.sql("""select sum(`tabPurchase Receipt Item`.qty) as qty from `tabPurchase Receipt`
		left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
		where `tabPurchase Receipt Item`.item_code = '%s' and `tabPurchase Receipt`.status = "Completed" """%(item_code),as_dict=True)[0]
		if not ppoc_receipt["qty"]:
			ppoc_receipt["qty"] = 0
		ppoc_total = ppoc_query["qty"] - ppoc_receipt["qty"]
		if stockqty['qty']:
			stockqty = stockqty['qty']
		else:
			stockqty = 0
		req = qty
		cal = sfs        
		req_qty = req - cal if cal <= req else 0
		reject = (ceil(req) * (rejection/100)) + ceil(req)
		with_rej = ((ceil(req) * (rejection/100)) + ceil(req) + safety_stock)
		if stockqty > with_rej:
			to_order = 0
		if stockqty < with_rej:
			to_order = with_rej - stockqty
		pack = 0
		if pack_size > 0:
			pack = to_order/ pack_size
			to_be_order = ceil(pack) * pack_size
		else:
			to_be_order = ceil(to_order)
		order_qty = 0
		if to_be_order > ppoc_total:
			order_qty = to_be_order - ppoc_total
		if ppoc_total > to_be_order:
			order_qty = 0
		if order_qty > mr_qty["qty"]:
			order_qty = order_qty - mr_qty["qty"]
		if moq > 0 and moq > order_qty:
			order_qty = moq
		exp_date = ''
		if to_be_order >0 and lead_time_days > 0:
			exp_date = add_days(nowdate(), lead_time_days)
		if ceil(req) > 0:
			uom = frappe.db.get_value("Item",item_code,'stock_uom') 
			if item_type == 'Process Item':           
				data1.append(frappe._dict({
					'item_code': item_code,
					'item_name': item_name,
					'schedule_date': frappe.utils.today(),
					'date':sch_date,
					'sales_order_number':sales_order_number,
					'with_rej':with_rej,
					'bom': bom,
					'moq':moq,
					'click' :"Click for Detailed View",
					'qty': to_be_order,
					'actual_stock_qty': str(round(stockqty,5)),
					'safety_stock':safety_stock,
					'qty_with_rejection_allowance':reject,
					'required_qty': str(round(qty,5)),
					'custom_total_req_qty': req,
					'custom_current_req_qty': req,
					'custom_stock_qty_copy': pps,
					'sfs_qty': sfs,
					'custom_requesting_qty': req_qty,
					'custom_today_req_qty': today_req,
					'uom': uom,
					'item_type':item_type,
					'item_billing_type':item_billing_type,
					'pack_size':pack_size,
					'lead_time_days':0,
					'cover_days':str(cover_days),
					'expected_date':' ',
					'po_qty':ppoc_total,
					'to_order':order_qty,
					'mr_qty':mr_qty["qty"]
			 }))
			else :
				data1.append(frappe._dict({
					'item_code': item_code,
					'item_name': item_name,
					'schedule_date': frappe.utils.today(),
					'date':sch_date,
					'sales_order_number':sales_order_number,
					'with_rej':with_rej,
					'bom': bom,
					'moq':moq,
					'click' :"Click for Detailed View",
					'qty': to_be_order,
					'actual_stock_qty': str(round(stockqty,5)),
					'safety_stock':safety_stock,
					'qty_with_rejection_allowance':reject,
					'required_qty': str(round(qty,5)),
					'custom_total_req_qty': req,
					'custom_current_req_qty': req,
					'custom_stock_qty_copy': pps,
					'sfs_qty': sfs,
					'custom_requesting_qty': req_qty,
					'custom_today_req_qty': today_req,
					'uom': uom,
					'item_type':item_type,
					'item_billing_type':item_billing_type,
					'pack_size':pack_size,
					'lead_time_days':lead_time_days,
					'cover_days':str(cover_days),
					'expected_date':exp_date,
					'po_qty':ppoc_total,
					'to_order':order_qty,
					'mr_qty':mr_qty["qty"]
			 }))



	for d in data1:
		exploded_data = []
		bom_item = frappe.db.get_value("BOM", {'item': d['item_code'],'is_default':1,'docstatus':1}, ['name'])
		get_exploded_items(bom_item, exploded_data, float(d["required_qty"]), bom_list)
		
		for item in exploded_data:
			item_code = frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name']) if item['bom'] else item['item_code']
			qty = item['qty']
			sch_date = d['date']
			sales_order_number=d['sales_order_number']
			
			if item_code in consolidated_dict:
				consolidated_dict[item_code][0] += qty
				consolidated_dict[item_code][1] = sch_date
				consolidated_dict[item_code][2] = sales_order_number

			else:
				consolidated_dict[item_code] = [qty, sch_date, sales_order_number]

	mpd = frappe.db.get_list('Material Planning Details',{'date':today()})
	for list in mpd:
		do = frappe.get_doc("Material Planning Details",list.name)
		do.delete()
	for k in data1:
		exists = frappe.db.exists('Material Planning Details',{'item_code':k['item_code'],'date':today()})
		if exists:
			new_doc = frappe.get_doc('Material Planning Details',{'item_code':k['item_code'],'date':today()})
			if new_doc.item_code == k['item_code']:
				to_order = k['with_rej']
				pack = 0
				if k['pack_size'] > 0:
					pack = to_order/ k['pack_size']
				to_be_order = ceil(pack) * k['pack_size']
				exp_date = ''
				if to_be_order >0:
					exp_date = add_days(nowdate(), lead_time_days)

				uom = frappe.db.get_value("Item",k['item_code'],'stock_uom')
				order_qty = to_be_order
				new_doc.append('material_plan',{
					'item_code': k['item_code'],
					'item_name': k['item_name'],
					'schedule_date': k['schedule_date'],
					'pack_size':k['pack_size'],
					'lead_time':k['lead_time_days'],
					'required_qty': k['required_qty'],
					'stock_uom': uom,
					'item_type':item_type,
					'uom': uom,
					'order_schedule_date':k['date'],
					'moq':k['moq'],
					'order_qty':to_be_order,
					'qty':order_qty,
					'expected_date':'',
					'conversion_factor':1,
					'safety_stock':k['safety_stock'],
					'qty_with_rejection_allowance':k['qty_with_rejection_allowance']
				})
				new_doc.save(ignore_permissions=True)
		else:
			uom = frappe.db.get_value("Item",k['item_code'],'stock_uom')
			new_doc = frappe.new_doc('Material Planning Details')
			new_doc.item_code = k['item_code']
			new_doc.date = today()
			new_doc.sales_order=k['sales_order_number']
			if new_doc.item_code == k['item_code']:
				if float(k['actual_stock_qty']) > k['with_rej']:
					to_order = 0
				if float(k['actual_stock_qty']) < k['with_rej']:
					to_order = k['with_rej'] + float(k['safety_stock']) - float(k['actual_stock_qty'])
				pack = 0
				if k['pack_size'] > 0:
					pack = to_order/ k['pack_size']
				to_be_order = ceil(pack) * k['pack_size']
				exp_date = ''
				if to_be_order >0:
					exp_date = add_days(nowdate(), lead_time_days)

				order_qty = 0   
				if to_be_order > k['po_qty']:
					order_qty = to_be_order - k['po_qty']
					if k['moq'] > 0 and k['moq'] > order_qty:
						order_qty = k['moq']
				if k['po_qty'] > (to_be_order):
					order_qty = 0
				new_doc.append('material_plan',{
					'item_code': k['item_code'],
					'item_name': k['item_name'],
					'item_type':item_type,
					'schedule_date': k['schedule_date'],
					'pack_size':k['pack_size'],
					'lead_time':k['lead_time_days'],
					'required_qty': k['required_qty'],
					'sfs_qty': k['sfs_qty'],
					'order_schedule_date':k['date'],
					'stock_uom':uom,
					'moq':k['moq'],
					'uom':uom,
					'po_qty': k['po_qty'],
					'order_qty':order_qty,
					'qty': order_qty,
					'conversion_factor':1,
					'expected_date':exp_date,
					'actual_stock_qty':k['actual_stock_qty'],
					'safety_stock':k['safety_stock'],
					'qty_with_rejection_allowance':k['qty_with_rejection_allowance']
				})
				new_doc.save(ignore_permissions=True)

	for item_code, (qty, sch_date,sales_order_number) in consolidated_dict.items():
		pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse != 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse = 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
							left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
							where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
							and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
		today_req = sf[0].qty if sf else 0
		item_billing_type = frappe.db.get_value("Item",{'item_code':item_code},'item_billing_type')
		item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
		stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - WAIP"}, ['actual_qty']) or 0
		rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance') or 0
		item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
		safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock') or 0
		pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
		moq =frappe.db.get_value("Item",{'item_code':item_code},'min_order_qty') or 0
		lead_time_days =frappe.db.get_value("Item",{'item_code':item_code},'lead_time_days')
		item_warehouse = frappe.db.get_value("Item",{'item_code':item_code},'custom_warehouse')
		if item_warehouse:
			stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse = '%s'"""%(item_code,item_warehouse),as_dict = 1)[0]
		else:
			stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s'"""%(item_code),as_dict = 1)[0]
		# stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' """%(item_code),as_dict = 1)[0]
		day = frappe.db.get_single_value("Production Plan Settings", "working_days")
		# if stockqty['qty']:
		#     if stockqty['qty'] > 0:
		#         cover_days = math.floor(stockqty['qty']/day)
		# else:
		#     cover_days = 0
		if qty and qty>0:
			cvr_days = math.floor(qty/day)
			if stockqty['qty']:
				if stockqty['qty'] > 0 and cvr_days>0:
					cover_days = math.floor(stockqty['qty']/cvr_days)
			else:
				cover_days = 0
		else:
			cover_days = 0
		ppoc_total = 0
		mr_qty = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
		left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
		where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.status = 'Pending' """ % (item_code), as_dict=True)[0]
		if not mr_qty["qty"]:
			mr_qty["qty"] = 0
		ppoc_query = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 """ % (item_code), as_dict=True)[0]
		if not ppoc_query["qty"]:
			ppoc_query["qty"] = 0
		ppoc_receipt = frappe.db.sql("""select sum(`tabPurchase Receipt Item`.qty) as qty from `tabPurchase Receipt`
		left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
		where `tabPurchase Receipt Item`.item_code = '%s' and `tabPurchase Receipt`.status = "Completed" """%(item_code),as_dict=True)[0]
		if not ppoc_receipt["qty"]:
			ppoc_receipt["qty"] = 0
		ppoc_total = ppoc_query["qty"] - ppoc_receipt["qty"]
		if stockqty['qty']:
			stockqty = stockqty['qty']
		else:
			stockqty = 0
		req = qty
		cal = sfs        
		req_qty = req - cal if cal <= req else 0
		reject = (ceil(req) * (rejection/100)) + ceil(req)
		with_rej = ((ceil(req) * (rejection/100)) + ceil(req) + safety_stock)
		if stockqty > with_rej:
			to_order = 0
		if stockqty < with_rej:
			to_order = with_rej - stockqty
		pack = 0
		to_be_order = 0
		if pack_size > 0:
			pack = to_order/ pack_size
			to_be_order = ceil(pack) * pack_size
		else:
			to_be_order = ceil(to_order)
		order_qty = 0
		if to_be_order > ppoc_total:
			order_qty = to_be_order - ppoc_total
		if ppoc_total > to_be_order:
			order_qty = 0
		if order_qty > mr_qty["qty"]:
			order_qty = order_qty - mr_qty["qty"]
		if moq > 0 and moq > order_qty:
			order_qty = moq
		exp_date = ''
		if to_be_order >0 and lead_time_days > 0:
			exp_date = add_days(nowdate(), lead_time_days)
		if ceil(req) > 0:
			uom = frappe.db.get_value("Item",item_code,'stock_uom') 
			if item_type == 'Process Item':           
				da.append(frappe._dict({
					'item_code': item_code,
					'item_name': item_name,
					'schedule_date': frappe.utils.today(),
					'date':sch_date,
					'with_rej':with_rej,
					'sales_order_number':sales_order_number,
					'bom': bom,
					'moq':moq,
					'click' :"Click for Detailed View",
					'qty': to_be_order,
					'actual_stock_qty': str(round(stockqty,5)),
					'safety_stock':safety_stock,
					'qty_with_rejection_allowance':reject,
					'required_qty': str(round(qty,5)),
					'custom_total_req_qty': req,
					'custom_current_req_qty': req,
					'custom_stock_qty_copy': pps,
					'sfs_qty': sfs,
					'custom_requesting_qty': req_qty,
					'custom_today_req_qty': today_req,
					'uom': uom,
					'item_type':item_type,
					'item_billing_type':item_billing_type,
					'pack_size':pack_size,
					'lead_time_days':0,
					'cover_days':str(cover_days),
					'expected_date':' ',
					'po_qty':ppoc_total,
					'to_order':order_qty,
					'mr_qty':mr_qty["qty"]
				}))
			else:
				da.append(frappe._dict({
					'item_code': item_code,
					'item_name': item_name,
					'schedule_date': frappe.utils.today(),
					'date':sch_date,
					'with_rej':with_rej,
					'sales_order_number':sales_order_number,
					'bom': bom,
					'moq':moq,
					'click' :"Click for Detailed View",
					'qty': to_be_order,
					'actual_stock_qty': str(round(stockqty,5)),
					'safety_stock':safety_stock,
					'qty_with_rejection_allowance':reject,
					'required_qty': str(round(qty,5)),
					'custom_total_req_qty': req,
					'custom_current_req_qty': req,
					'custom_stock_qty_copy': pps,
					'sfs_qty': sfs,
					'custom_requesting_qty': req_qty,
					'custom_today_req_qty': today_req,
					'uom': uom,
					'item_type':item_type,
					'item_billing_type':item_billing_type,
					'pack_size':pack_size,
					'lead_time_days':lead_time_days,
					'cover_days':str(cover_days),
					'expected_date':exp_date,
					'po_qty':ppoc_total,
					'to_order':order_qty,
					'mr_qty':mr_qty["qty"]
				}))

	for id in da:
		exploded_data = []       
		bom_item = frappe.db.get_value("BOM", {'item': id['item_code'],'is_default':1,'docstatus':1}, ['name'])
		get_bom_exploded_items(bom_item, exploded_data, float(id["required_qty"]), bom_list)
		frappe.errprint(exploded_data)
		for item in exploded_data:
			if item['bom']:
				if frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name']):
					item_code = frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name'])
			else:
				item_code = item['item_code']
			
			qty = item['qty']
			sch_date = d['date']
			sales_order_number=d['sales_order_number']
			
			if item_code in consolidated:
				consolidated[item_code][0] += qty
				consolidated[item_code][1] = sch_date
				consolidated[item_code][2] = sales_order_number
			else:
				consolidated[item_code] = [qty, sch_date,sales_order_number]

	
	for k in da:
		exists = frappe.db.exists('Material Planning Details',{'item_code':k['item_code'],'date':today()})
		if exists:
			new_doc = frappe.get_doc('Material Planning Details',{'item_code':k['item_code'],'date':today()})
			if new_doc.item_code == k['item_code']:
				to_order = k['with_rej']
				pack = 0
				if k['pack_size'] > 0:
					pack = to_order/ k['pack_size']
				to_be_order = ceil(pack) * k['pack_size']
				exp_date = ''
				if to_be_order >0:
					exp_date = add_days(nowdate(), lead_time_days)

				uom = frappe.db.get_value("Item",k['item_code'],'stock_uom')
				order_qty = to_be_order
				new_doc.append('material_plan',{
					'item_code': k['item_code'],
					'item_name': k['item_name'],
					'schedule_date': k['schedule_date'],
					'pack_size':k['pack_size'],
					'lead_time':k['lead_time_days'],
					'required_qty': k['required_qty'],
					'stock_uom': uom,
					'item_type':item_type,
					'uom': uom,
					'order_schedule_date':k['date'],
					'moq':k['moq'],
					'order_qty':to_be_order,
					'qty':order_qty,
					'expected_date':'',
					'conversion_factor':1,
					'safety_stock':k['safety_stock'],
					'qty_with_rejection_allowance':k['qty_with_rejection_allowance']
				})
				new_doc.save(ignore_permissions=True)
		else:
			uom = frappe.db.get_value("Item",k['item_code'],'stock_uom')
			new_doc = frappe.new_doc('Material Planning Details')
			new_doc.item_code = k['item_code']
			new_doc.sales_order=k['sales_order_number']
			new_doc.date = today()
			if new_doc.item_code == k['item_code']:
				if float(k['actual_stock_qty']) > k['with_rej']:
					to_order = 0
				if float(k['actual_stock_qty']) < k['with_rej']:
					to_order = k['with_rej'] + float(k['safety_stock']) - float(k['actual_stock_qty'])
				pack = 0
				if k['pack_size'] > 0:
					pack = to_order/ k['pack_size']
				to_be_order = ceil(pack) * k['pack_size']
				exp_date = ''
				if to_be_order >0:
					exp_date = add_days(nowdate(), lead_time_days)

				order_qty = 0   
				if to_be_order > k['po_qty']:
					order_qty = to_be_order - k['po_qty']
					if k['moq'] > 0 and k['moq'] > order_qty:
						order_qty = k['moq']
				if k['po_qty'] > (to_be_order):
					order_qty = 0
				new_doc.append('material_plan',{
					'item_code': k['item_code'],
					'item_name': k['item_name'],
					'item_type':item_type,
					'schedule_date': k['schedule_date'],
					'pack_size':k['pack_size'],
					'lead_time':k['lead_time_days'],
					'required_qty': k['required_qty'],
					'sfs_qty': k['sfs_qty'],
					'order_schedule_date':k['date'],
					'stock_uom':uom,
					'moq':k['moq'],
					'uom':uom,
					'po_qty': k['po_qty'],
					'order_qty':order_qty,
					'qty': order_qty,
					'conversion_factor':1,
					'expected_date':exp_date,
					'actual_stock_qty':k['actual_stock_qty'],
					'safety_stock':k['safety_stock'],
					'qty_with_rejection_allowance':k['qty_with_rejection_allowance']
				})
				new_doc.save(ignore_permissions=True)

	for item_code, (qty,sch_date,sales_order_number) in consolidated.items():
		pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse != 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse = 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
							left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
							where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
							and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
		today_req = sf[0].qty if sf else 0
		item_billing_type = frappe.db.get_value("Item",{'item_code':item_code},'item_billing_type')
		item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
		stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - WAIP"}, ['actual_qty']) or 0
		rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance') or 0
		item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
		safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock') or 0
		pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
		moq =frappe.db.get_value("Item",{'item_code':item_code},'min_order_qty') or 0
		lead_time_days =frappe.db.get_value("Item",{'item_code':item_code},'lead_time_days')
		item_warehouse = frappe.db.get_value("Item",{'item_code':item_code},'custom_warehouse')
		if item_warehouse:
			stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse = '%s'"""%(item_code,item_warehouse),as_dict = 1)[0]
		else:
			stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s'"""%(item_code),as_dict = 1)[0]
		# stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' """%(item_code),as_dict = 1)[0]
		day = frappe.db.get_single_value("Production Plan Settings", "working_days")
		if qty and qty>0:
			cvr_days = math.floor(qty/day)
			if stockqty['qty']:
				if stockqty['qty'] > 0 and cvr_days>0:
					cover_days = math.floor(stockqty['qty']/cvr_days)
			else:
				cover_days = 0
		else:
			cover_days = 0
		ppoc_total = 0
		mr_qty = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
		left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
		where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.status = 'Pending' """ % (item_code), as_dict=True)[0]
		if not mr_qty["qty"]:
			mr_qty["qty"] = 0
		ppoc_query = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 """ % (item_code), as_dict=True)[0]
		if not ppoc_query["qty"]:
			ppoc_query["qty"] = 0
		ppoc_receipt = frappe.db.sql("""select sum(`tabPurchase Receipt Item`.qty) as qty from `tabPurchase Receipt`
		left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
		where `tabPurchase Receipt Item`.item_code = '%s' and `tabPurchase Receipt`.status = "Completed" """%(item_code),as_dict=True)[0]
		if not ppoc_receipt["qty"]:
			ppoc_receipt["qty"] = 0
		ppoc_total = ppoc_query["qty"] - ppoc_receipt["qty"]
		if stockqty['qty']:
			stockqty = stockqty['qty']
		else:
			stockqty = 0
		req = qty
		cal = sfs        
		req_qty = req - cal if cal <= req else 0
		reject = (ceil(req) * (rejection/100)) + ceil(req)
		with_rej = ((ceil(req) * (rejection/100)) + ceil(req) + safety_stock)
		if stockqty > with_rej:
			to_order = 0
		if stockqty < with_rej:
			to_order = with_rej - stockqty
		pack = 0
		to_be_order = 0
		if pack_size > 0:
			pack = to_order/ pack_size
			to_be_order = ceil(pack) * pack_size
		else:
			to_be_order = ceil(to_order)
		order_qty = 0
		if to_be_order > ppoc_total:
			order_qty = to_be_order - ppoc_total
		if ppoc_total > to_be_order:
			order_qty = 0
		if order_qty > mr_qty["qty"]:
			order_qty = order_qty - mr_qty["qty"]
		if moq > 0 and moq > order_qty:
			order_qty = moq
		exp_date = ''
		if to_be_order >0 and lead_time_days > 0:
			exp_date = add_days(nowdate(), lead_time_days)
		if ceil(req) > 0:
			uom = frappe.db.get_value("Item",item_code,'stock_uom')  
			if item_type == 'Process Item':         
				dic.append(frappe._dict({
					'item_code': item_code,
					'item_name': item_name,
					'schedule_date': frappe.utils.today(),
					'sales_order_number':sales_order_number,
					'date':sch_date,
					'with_rej':with_rej,
					'bom': bom,
					'moq':moq,
					'click' :"Click for Detailed View",
					'qty': to_be_order,
					'actual_stock_qty': str(round(stockqty,5)),
					'safety_stock':safety_stock,
					'qty_with_rejection_allowance':reject,
					'required_qty': str(round(qty,5)),
					'custom_total_req_qty': req,
					'custom_current_req_qty': req,
					'custom_stock_qty_copy': pps,
					'sfs_qty': sfs,
					'custom_requesting_qty': req_qty,
					'custom_today_req_qty': today_req,
					'uom': uom,
					'item_type':item_type,
					'item_billing_type':item_billing_type,
					'pack_size':pack_size,
					'lead_time_days':0,
					'cover_days':str(cover_days),
					'expected_date':' ',
					'po_qty':ppoc_total,
					'to_order':order_qty,
					'mr_qty':mr_qty["qty"]
				}))
			else:
				dic.append(frappe._dict({
				'item_code': item_code,
				'item_name': item_name,
				'schedule_date': frappe.utils.today(),
				'sales_order_number':sales_order_number,
				'date':sch_date,
				'with_rej':with_rej,
				'bom': bom,
				'moq':moq,
				'click' :"Click for Detailed View",
				'qty': to_be_order,
				'actual_stock_qty': str(round(stockqty,5)),
				'safety_stock':safety_stock,
				'qty_with_rejection_allowance':reject,
				'required_qty': str(round(qty,5)),
				'custom_total_req_qty': req,
				'custom_current_req_qty': req,
				'custom_stock_qty_copy': pps,
				'sfs_qty': sfs,
				'custom_requesting_qty': req_qty,
				'custom_today_req_qty': today_req,
				'uom': uom,
				'item_type':item_type,
				'item_billing_type':item_billing_type,
				'pack_size':pack_size,
				'lead_time_days':lead_time_days,
				'cover_days':str(cover_days),
				'expected_date':exp_date,
				'po_qty':ppoc_total,
				'to_order':order_qty,
				'mr_qty':mr_qty["qty"]
			}))

	bomlist = []

	for di in dic:
		exploded = []       
		bom_item = frappe.db.get_value("BOM", {'item': di['item_code'],'is_default':1,'docstatus':1}, ['name'])
		if bom_item:
			get_sub_bom_exploded_items(bom_item, exploded, float(di["required_qty"]), bomlist)
		for item in exploded:
			if item['bom']:
				if frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name']):
					item_code = frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name'])
			else:
				item_code = item['item_code']
			qty = item['qty']
			sch_date = d['date']
			sales_order_number= d['sales_order_number']
			
			if item_code in consolidate:
				consolidate[item_code][0] += qty
				consolidate[item_code][1] = sch_date
				consolidate[item_code][2] = sales_order_number
			else:
				consolidate[item_code] = [qty, sch_date, sales_order_number]

	for k in dic:
		exists = frappe.db.exists('Material Planning Details',{'item_code':k['item_code'],'date':today()})
		if exists:
			new_doc = frappe.get_doc('Material Planning Details',{'item_code':k['item_code'],'date':today()})
			if new_doc.item_code == k['item_code']:
				to_order = k['with_rej']
				pack = 0
				if k['pack_size'] > 0:
					pack = to_order/ k['pack_size']
				to_be_order = ceil(pack) * k['pack_size']
				exp_date = ''
				if to_be_order >0:
					exp_date = add_days(nowdate(), lead_time_days)

				uom = frappe.db.get_value("Item",k['item_code'],'stock_uom')
				order_qty = to_be_order
				new_doc.append('material_plan',{
					'item_code': k['item_code'],
					'item_name': k['item_name'],
					'schedule_date': k['schedule_date'],
					'pack_size':k['pack_size'],
					'lead_time':k['lead_time_days'],
					'required_qty': k['required_qty'],
					'stock_uom': uom,
					'item_type':item_type,
					'uom': uom,
					'order_schedule_date':k['date'],
					'moq':k['moq'],
					'order_qty':to_be_order,
					'qty':order_qty,
					'expected_date':'',
					'conversion_factor':1,
					'safety_stock':k['safety_stock'],
					'qty_with_rejection_allowance':k['qty_with_rejection_allowance']
				})
				new_doc.save(ignore_permissions=True)
		else:
			uom = frappe.db.get_value("Item",k['item_code'],'stock_uom')
			new_doc = frappe.new_doc('Material Planning Details')
			new_doc.item_code = k['item_code']
			new_doc.sales_order=k['sales_order_number']
			new_doc.date = today()
			if new_doc.item_code == k['item_code']:
				if float(k['actual_stock_qty']) > k['with_rej']:
					to_order = 0
				if float(k['actual_stock_qty']) < k['with_rej']:
					to_order = k['with_rej'] + float(k['safety_stock']) - float(k['actual_stock_qty'])
				pack = 0
				if k['pack_size'] > 0:
					pack = to_order/ k['pack_size']
				to_be_order = ceil(pack) * k['pack_size']
				exp_date = ''
				if to_be_order >0:
					exp_date = add_days(nowdate(), lead_time_days)

				order_qty = 0   
				if to_be_order > k['po_qty']:
					order_qty = to_be_order - k['po_qty']
					if k['moq'] > 0 and k['moq'] > order_qty:
						order_qty = k['moq']
				if k['po_qty'] > (to_be_order):
					order_qty = 0
				new_doc.append('material_plan',{
					'item_code': k['item_code'],
					'item_name': k['item_name'],
					'item_type':item_type,
					'schedule_date': k['schedule_date'],
					'pack_size':k['pack_size'],
					'lead_time':k['lead_time_days'],
					'required_qty': k['required_qty'],
					'sfs_qty': k['sfs_qty'],
					'order_schedule_date':k['date'],
					'stock_uom':uom,
					'moq':k['moq'],
					'uom':uom,
					'po_qty': k['po_qty'],
					'order_qty':order_qty,
					'qty': order_qty,
					'conversion_factor':1,
					'expected_date':exp_date,
					'actual_stock_qty':k['actual_stock_qty'],
					'safety_stock':k['safety_stock'],
					'qty_with_rejection_allowance':k['qty_with_rejection_allowance']
				})
				new_doc.save(ignore_permissions=True)

	for item_code, (qty,sch_date,sales_order_number) in consolidate.items():
		pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse != 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse = 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
							left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
							where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
							and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
		today_req = sf[0].qty if sf else 0
		item_billing_type = frappe.db.get_value("Item",{'item_code':item_code},'item_billing_type')
		item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
		stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - WAIP"}, ['actual_qty']) or 0
		rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance') or 0
		item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
		safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock') or 0
		pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
		moq =frappe.db.get_value("Item",{'item_code':item_code},'min_order_qty') or 0
		lead_time_days =frappe.db.get_value("Item",{'item_code':item_code},'lead_time_days')
		item_warehouse = frappe.db.get_value("Item",{'item_code':item_code},'custom_warehouse')
		if item_warehouse:
			stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse = '%s'"""%(item_code,item_warehouse),as_dict = 1)[0]
		else:
			stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s'"""%(item_code),as_dict = 1)[0]
		# stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' """%(item_code),as_dict = 1)[0]
		day = frappe.db.get_single_value("Production Plan Settings", "working_days")
		if qty and qty>0:
			cvr_days = math.floor(qty/day)
			if stockqty['qty']:
				if stockqty['qty'] > 0 and cvr_days>0:
					cover_days = math.floor(stockqty['qty']/cvr_days)
			else:
				cover_days = 0
		else:
			cover_days = 0
		ppoc_total = 0
		mr_qty = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
		left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
		where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.status = 'Pending' """ % (item_code), as_dict=True)[0]
		if not mr_qty["qty"]:
			mr_qty["qty"] = 0
		ppoc_query = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 """ % (item_code), as_dict=True)[0]
		if not ppoc_query["qty"]:
			ppoc_query["qty"] = 0
		ppoc_receipt = frappe.db.sql("""select sum(`tabPurchase Receipt Item`.qty) as qty from `tabPurchase Receipt`
		left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
		where `tabPurchase Receipt Item`.item_code = '%s' and `tabPurchase Receipt`.status = "Completed" """%(item_code),as_dict=True)[0]
		if not ppoc_receipt["qty"]:
			ppoc_receipt["qty"] = 0
		ppoc_total = ppoc_query["qty"] - ppoc_receipt["qty"]
		if stockqty['qty']:
			stockqty = stockqty['qty']
		else:
			stockqty = 0
		req = qty
		cal = sfs        
		req_qty = req - cal if cal <= req else 0
		reject = (ceil(req) * (rejection/100)) + ceil(req)
		with_rej = ((ceil(req) * (rejection/100)) + ceil(req) + safety_stock)
		if stockqty > with_rej:
			to_order = 0
		if stockqty < with_rej:
			to_order = with_rej - stockqty
		pack = 0
		to_be_order = 0
		if pack_size > 0:
			pack = to_order/ pack_size
			to_be_order = ceil(pack) * pack_size
		else:
			to_be_order = ceil(to_order)
		order_qty = 0
		if to_be_order > ppoc_total:
			order_qty = to_be_order - ppoc_total
		if ppoc_total > to_be_order:
			order_qty = 0
		if order_qty > mr_qty["qty"]:
			order_qty = order_qty - mr_qty["qty"]
		if moq > 0 and moq > order_qty:
			order_qty = moq
		exp_date = ''
		if to_be_order >0 and lead_time_days > 0:
			exp_date = add_days(nowdate(), lead_time_days)
		if ceil(req) > 0:
			uom = frappe.db.get_value("Item",item_code,'stock_uom')
			if item_type == 'Process Item':            
				data4.append(frappe._dict({
					'item_code': item_code,
					'item_name': item_name,
					'schedule_date': frappe.utils.today(),
					'date':sch_date,
					'sales_order_number':sales_order_number,
					'with_rej':with_rej,
					'bom': bom,
					'moq':moq,
					'click' :"Click for Detailed View",
					'qty': to_be_order,
					'actual_stock_qty': str(round(stockqty,5)),
					'safety_stock':safety_stock,
					'qty_with_rejection_allowance':reject,
					'required_qty': str(round(qty,5)),
					'custom_total_req_qty': req,
					'custom_current_req_qty': req,
					'custom_stock_qty_copy': pps,
					'sfs_qty': sfs,
					'custom_requesting_qty': req_qty,
					'custom_today_req_qty': today_req,
					'uom': uom,
					'item_type':item_type,
					'item_billing_type':item_billing_type,
					'pack_size':pack_size,
					'lead_time_days':0,
					'cover_days':str(cover_days),
					'expected_date':' ',
					'po_qty':ppoc_total,
					'to_order':order_qty,
					'mr_qty':mr_qty["qty"]
				}))
			else:
				data4.append(frappe._dict({
				'item_code': item_code,
				'item_name': item_name,
				'schedule_date': frappe.utils.today(),
				'date':sch_date,
				'sales_order_number':sales_order_number,
				'with_rej':with_rej,
				'bom': bom,
				'moq':moq,
				'click' :"Click for Detailed View",
				'qty': to_be_order,
				'actual_stock_qty': str(round(stockqty,5)),
				'safety_stock':safety_stock,
				'qty_with_rejection_allowance':reject,
				'required_qty': str(round(qty,5)),
				'custom_total_req_qty': req,
				'custom_current_req_qty': req,
				'custom_stock_qty_copy': pps,
				'sfs_qty': sfs,
				'custom_requesting_qty': req_qty,
				'custom_today_req_qty': today_req,
				'uom': uom,
				'item_type':item_type,
				'item_billing_type':item_billing_type,
				'pack_size':pack_size,
				'lead_time_days':lead_time_days,
				'cover_days':str(cover_days),
				'expected_date':exp_date,
				'po_qty':ppoc_total,
				'to_order':order_qty,
				'mr_qty':mr_qty["qty"]
			}))

	bomlist = []

	for ct in data4:
		exploded = []       
		bom_item = frappe.db.get_value("BOM", {'item': ct['item_code'],'is_default':1,'docstatus':1}, ['name'])
		if bom_item:
			get_sub_bom_exploded_items(bom_item, exploded, float(ct["required_qty"]), bomlist)
		for item in exploded:
			if item['bom']:
				if frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name']):
					item_code = frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name'])
			else:
				item_code = item['item_code']
			qty = item['qty']
			sch_date = d['date']
			sales_order_number = d['sales_order_number']
			
			if item_code in console:
				console[item_code][0] += qty
				console[item_code][1] = sch_date
				console[item_code][2] = sales_order_number
			else:
				console[item_code] = [qty, sch_date, sales_order_number]

	for k in data4:
		exists = frappe.db.exists('Material Planning Details',{'item_code':k['item_code'],'date':today()})
		if exists:
			new_doc = frappe.get_doc('Material Planning Details',{'item_code':k['item_code'],'date':today()})
			if new_doc.item_code == k['item_code']:
				to_order = k['with_rej']
				pack = 0
				if k['pack_size'] > 0:
					pack = to_order/ k['pack_size']
				to_be_order = ceil(pack) * k['pack_size']
				exp_date = ''
				if to_be_order >0:
					exp_date = add_days(nowdate(), lead_time_days)

				uom = frappe.db.get_value("Item",k['item_code'],'stock_uom')
				order_qty = to_be_order
				new_doc.append('material_plan',{
					'item_code': k['item_code'],
					'item_name': k['item_name'],
					'schedule_date': k['schedule_date'],
					'pack_size':k['pack_size'],
					'lead_time':k['lead_time_days'],
					'required_qty': k['required_qty'],
					'stock_uom': uom,
					'item_type':item_type,
					'uom': uom,
					'order_schedule_date':k['date'],
					'moq':k['moq'],
					'order_qty':to_be_order,
					'qty':order_qty,
					'expected_date':'',
					'conversion_factor':1,
					'safety_stock':k['safety_stock'],
					'qty_with_rejection_allowance':k['qty_with_rejection_allowance']
				})
				new_doc.save(ignore_permissions=True)
		else:
			uom = frappe.db.get_value("Item",k['item_code'],'stock_uom')
			new_doc = frappe.new_doc('Material Planning Details')
			new_doc.item_code = k['item_code']
			new_doc.sales_order=k['sales_order_number']
			new_doc.date = today()
			if new_doc.item_code == k['item_code']:
				if float(k['actual_stock_qty']) > k['with_rej']:
					to_order = 0
				if float(k['actual_stock_qty']) < k['with_rej']:
					to_order = k['with_rej'] + float(k['safety_stock']) - float(k['actual_stock_qty'])
				pack = 0
				if k['pack_size'] > 0:
					pack = to_order/ k['pack_size']
				to_be_order = ceil(pack) * k['pack_size']
				exp_date = ''
				if to_be_order >0:
					exp_date = add_days(nowdate(), lead_time_days)

				order_qty = 0   
				if to_be_order > k['po_qty']:
					order_qty = to_be_order - k['po_qty']
					if k['moq'] > 0 and k['moq'] > order_qty:
						order_qty = k['moq']
				if k['po_qty'] > (to_be_order):
					order_qty = 0
				new_doc.append('material_plan',{
					'item_code': k['item_code'],
					'item_name': k['item_name'],
					'item_type':item_type,
					'schedule_date': k['schedule_date'],
					'pack_size':k['pack_size'],
					'lead_time':k['lead_time_days'],
					'required_qty': k['required_qty'],
					'sfs_qty': k['sfs_qty'],
					'order_schedule_date':k['date'],
					'stock_uom':uom,
					'moq':k['moq'],
					'uom':uom,
					'po_qty': k['po_qty'],
					'order_qty':order_qty,
					'qty': order_qty,
					'conversion_factor':1,
					'expected_date':exp_date,
					'actual_stock_qty':k['actual_stock_qty'],
					'safety_stock':k['safety_stock'],
					'qty_with_rejection_allowance':k['qty_with_rejection_allowance']
				})
				new_doc.save(ignore_permissions=True)

	for item_code, (qty,sch_date,sales_order_number) in console.items():
		pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse != 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse = 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
							left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
							where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
							and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
		today_req = sf[0].qty if sf else 0
		item_billing_type = frappe.db.get_value("Item",{'item_code':item_code},'item_billing_type')
		item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
		stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - WAIP"}, ['actual_qty']) or 0
		rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance') or 0
		item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
		safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock') or 0
		pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
		moq =frappe.db.get_value("Item",{'item_code':item_code},'min_order_qty') or 0
		lead_time_days =frappe.db.get_value("Item",{'item_code':item_code},'lead_time_days')
		item_warehouse = frappe.db.get_value("Item",{'item_code':item_code},'custom_warehouse')
		if item_warehouse:
			stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse = '%s'"""%(item_code,item_warehouse),as_dict = 1)[0]
		else:
			stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s'"""%(item_code),as_dict = 1)[0]
		# stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' """%(item_code),as_dict = 1)[0]
		day = frappe.db.get_single_value("Production Plan Settings", "working_days")
		if qty and qty>0:
			cvr_days = math.floor(qty/day)
			if stockqty['qty']:
				if stockqty['qty'] > 0 and cvr_days>0:
					cover_days = math.floor(stockqty['qty']/cvr_days)
			else:
				cover_days = 0
		else:
			cover_days = 0
		ppoc_total = 0
		mr_qty = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
		left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
		where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.status = 'Pending' """ % (item_code), as_dict=True)[0]
		if not mr_qty["qty"]:
			mr_qty["qty"] = 0
		ppoc_query = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 """ % (item_code), as_dict=True)[0]
		if not ppoc_query["qty"]:
			ppoc_query["qty"] = 0
		ppoc_receipt = frappe.db.sql("""select sum(`tabPurchase Receipt Item`.qty) as qty from `tabPurchase Receipt`
		left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
		where `tabPurchase Receipt Item`.item_code = '%s' and `tabPurchase Receipt`.status = "Completed" """%(item_code),as_dict=True)[0]
		if not ppoc_receipt["qty"]:
			ppoc_receipt["qty"] = 0
		ppoc_total = ppoc_query["qty"] - ppoc_receipt["qty"]
		if stockqty['qty']:
			stockqty = stockqty['qty']
		else:
			stockqty = 0
		req = qty
		cal = sfs        
		req_qty = req - cal if cal <= req else 0
		reject = (ceil(req) * (rejection/100)) + ceil(req)
		with_rej = ((ceil(req) * (rejection/100)) + ceil(req) + safety_stock)
		if stockqty > with_rej:
			to_order = 0
		if stockqty < with_rej:
			to_order = with_rej - stockqty
		pack = 0
		to_be_order = 0
		if pack_size > 0:
			pack = to_order/ pack_size
			to_be_order = ceil(pack) * pack_size
		else:
			to_be_order = ceil(to_order)
		order_qty = 0
		if to_be_order > ppoc_total:
			order_qty = to_be_order - ppoc_total
		if ppoc_total > to_be_order:
			order_qty = 0
		if order_qty > mr_qty["qty"]:
			order_qty = order_qty - mr_qty["qty"]
		if moq > 0 and moq > order_qty:
			order_qty = moq
		exp_date = ''
		if to_be_order >0 and lead_time_days > 0:
			exp_date = add_days(nowdate(), lead_time_days)
		if ceil(req) > 0:
			uom = frappe.db.get_value("Item",item_code,'stock_uom')
			if item_type == 'Process Item' :            
				ict.append(frappe._dict({
					'item_code': item_code,
					'item_name': item_name,
					'schedule_date': frappe.utils.today(),
					'date':sch_date,
					'sales_order_number':sales_order_number,
					'with_rej':with_rej,
					'bom': bom,
					'moq':moq,
					'click' :"Click for Detailed View",
					'qty': to_be_order,
					'actual_stock_qty': str(round(stockqty,5)),
					'safety_stock':safety_stock,
					'qty_with_rejection_allowance':reject,
					'required_qty': str(round(qty,5)),
					'custom_total_req_qty': req,
					'custom_current_req_qty': req,
					'custom_stock_qty_copy': pps,
					'sfs_qty': sfs,
					'custom_requesting_qty': req_qty,
					'custom_today_req_qty': today_req,
					'uom': uom,
					'item_type':item_type,
					'item_billing_type':item_billing_type,
					'pack_size':pack_size,
					'lead_time_days':0,
					'cover_days':str(cover_days),
					'expected_date':' ',
					'po_qty':ppoc_total,
					'to_order':order_qty,
					'mr_qty':mr_qty["qty"]
				}))
			else: 
					ict.append(frappe._dict({
					'item_code': item_code,
					'item_name': item_name,
					'schedule_date': frappe.utils.today(),
					'date':sch_date,
					'sales_order_number':sales_order_number,
					'with_rej':with_rej,
					'bom': bom,
					'moq':moq,
					'click' :"Click for Detailed View",
					'qty': to_be_order,
					'actual_stock_qty': str(round(stockqty,5)),
					'safety_stock':safety_stock,
					'qty_with_rejection_allowance':reject,
					'required_qty': str(round(qty,5)),
					'custom_total_req_qty': req,
					'custom_current_req_qty': req,
					'custom_stock_qty_copy': pps,
					'sfs_qty': sfs,
					'custom_requesting_qty': req_qty,
					'custom_today_req_qty': today_req,
					'uom': uom,
					'item_type':item_type,
					'item_billing_type':item_billing_type,
					'pack_size':pack_size,
					'lead_time_days':lead_time_days,
					'cover_days':str(cover_days),
					'expected_date':exp_date,
					'po_qty':ppoc_total,
					'to_order':order_qty,
					'mr_qty':mr_qty["qty"]
				}))

	bomlist = []

	for f in ict:
		exploded = []       
		bom_item = frappe.db.get_value("BOM", {'item': f['item_code'],'is_default':1,'docstatus':1}, ['name'])
		if bom_item:
			get_sub_bom_exploded_items(bom_item, exploded, float(f["required_qty"]), bomlist)
		for item in exploded:
			if item['bom']:
				if frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name']):
					item_code = frappe.db.get_value("Item", {'default_bom': item['bom']}, ['name'])
			else:
				item_code = item['item_code']
			qty = item['qty']
			sch_date = d['date']
			sales_order_number = d['sales_order_number']
			
			if item_code in cons:
				cons[item_code][0] += qty
				cons[item_code][1] = sch_date
				cons[item_code][2] = sales_order_number
			else:
				cons[item_code] = [qty, sch_date, sales_order_number]

	for k in ict:
		exists = frappe.db.exists('Material Planning Details',{'item_code':k['item_code'],'date':today()})
		if exists:
			new_doc = frappe.get_doc('Material Planning Details',{'item_code':k['item_code'],'date':today()})
			if new_doc.item_code == k['item_code']:
				to_order = k['with_rej']
				pack = 0
				if k['pack_size'] > 0:
					pack = to_order/ k['pack_size']
				to_be_order = ceil(pack) * k['pack_size']
				exp_date = ''
				if to_be_order >0:
					exp_date = add_days(nowdate(), lead_time_days)

				uom = frappe.db.get_value("Item",k['item_code'],'stock_uom')
				order_qty = to_be_order
				new_doc.append('material_plan',{
					'item_code': k['item_code'],
					'item_name': k['item_name'],
					'schedule_date': k['schedule_date'],
					'pack_size':k['pack_size'],
					'lead_time':k['lead_time_days'],
					'required_qty': k['required_qty'],
					'stock_uom': uom,
					'item_type':item_type,
					'uom': uom,
					'order_schedule_date':k['date'],
					'moq':k['moq'],
					'order_qty':to_be_order,
					'qty':order_qty,
					'expected_date':'',
					'conversion_factor':1,
					'safety_stock':k['safety_stock'],
					'qty_with_rejection_allowance':k['qty_with_rejection_allowance']
				})
				new_doc.save(ignore_permissions=True)
		else:
			uom = frappe.db.get_value("Item",k['item_code'],'stock_uom')
			new_doc = frappe.new_doc('Material Planning Details')
			new_doc.item_code = k['item_code']
			new_doc.sales_order=k['sales_order_number']
			new_doc.date = today()
			if new_doc.item_code == k['item_code']:
				if float(k['actual_stock_qty']) > k['with_rej']:
					to_order = 0
				if float(k['actual_stock_qty']) < k['with_rej']:
					to_order = k['with_rej'] + float(k['safety_stock']) - float(k['actual_stock_qty'])
				pack = 0
				if k['pack_size'] > 0:
					pack = to_order/ k['pack_size']
				to_be_order = ceil(pack) * k['pack_size']
				exp_date = ''
				if to_be_order >0:
					exp_date = add_days(nowdate(), lead_time_days)

				order_qty = 0   
				if to_be_order > k['po_qty']:
					order_qty = to_be_order - k['po_qty']
					if k['moq'] > 0 and k['moq'] > order_qty:
						order_qty = k['moq']
				if k['po_qty'] > (to_be_order):
					order_qty = 0
				new_doc.append('material_plan',{
					'item_code': k['item_code'],
					'item_name': k['item_name'],
					'item_type':item_type,
					'schedule_date': k['schedule_date'],
					'pack_size':k['pack_size'],
					'lead_time':k['lead_time_days'],
					'required_qty': k['required_qty'],
					'sfs_qty': k['sfs_qty'],
					'order_schedule_date':k['date'],
					'stock_uom':uom,
					'moq':k['moq'],
					'uom':uom,
					'po_qty': k['po_qty'],
					'order_qty':order_qty,
					'qty': order_qty,
					'conversion_factor':1,
					'expected_date':exp_date,
					'actual_stock_qty':k['actual_stock_qty'],
					'safety_stock':k['safety_stock'],
					'qty_with_rejection_allowance':k['qty_with_rejection_allowance']
				})
				new_doc.save(ignore_permissions=True)

	for item_code, (qty,sch_date,sales_order_number) in cons.items():
		pps = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse != 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sfs = frappe.db.sql("""select sum(actual_qty) as qty from `tabBin` where item_code = %s and warehouse = 'SFS Store - WAIP' """, (item_code), as_dict=1)[0].qty or 0
		sf = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
							left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
							where `tabMaterial Request Item`.item_code = %s and `tabMaterial Request`.docstatus != 2
							and `tabMaterial Request`.transaction_date = CURDATE() """, (item_code), as_dict=1)
		today_req = sf[0].qty if sf else 0
		item_billing_type = frappe.db.get_value("Item",{'item_code':item_code},'item_billing_type')
		item_type =frappe.db.get_value("Item",{'item_code':item_code},'item_type')
		stock = frappe.db.get_value("Bin", {'item_code': item_code, 'warehouse': "SFS Store - WAIP"}, ['actual_qty']) or 0
		rejection =frappe.db.get_value("Item",{'item_code':item_code},'rejection_allowance') or 0
		item_name =frappe.db.get_value("Item",{'item_code':item_code},'item_name')
		safety_stock =frappe.db.get_value("Item",{'item_code':item_code},'safety_stock') or 0
		pack_size =frappe.db.get_value("Item",{'item_code':item_code},'pack_size')
		moq =frappe.db.get_value("Item",{'item_code':item_code},'min_order_qty') or 0
		lead_time_days =frappe.db.get_value("Item",{'item_code':item_code},'lead_time_days')
		item_warehouse = frappe.db.get_value("Item",{'item_code':item_code},'custom_warehouse')
		if item_warehouse:
			stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' and warehouse = '%s'"""%(item_code,item_warehouse),as_dict = 1)[0]
		else:
			stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s'"""%(item_code),as_dict = 1)[0]
		# stockqty = frappe.db.sql(""" select item_code,sum(actual_qty) as qty from `tabBin` where item_code = '%s' """%(item_code),as_dict = 1)[0]
		day = frappe.db.get_single_value("Production Plan Settings", "working_days")
		# if stockqty['qty']:
		#     if stockqty['qty'] > 0:
		#         cover_days = math.floor(stockqty['qty']/day)
		# else:
		#     cover_days = 0
		if qty and qty>0:
			cvr_days = math.floor(qty/day)
			if stockqty['qty']:
				if stockqty['qty'] > 0 and cvr_days>0:
					cover_days = math.floor(stockqty['qty']/cvr_days)
			else:
				cover_days = 0
		else:
			cover_days = 0
		ppoc_total = 0
		mr_qty = frappe.db.sql("""select sum(`tabMaterial Request Item`.qty) as qty from `tabMaterial Request`
		left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
		where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.status = 'Pending' """ % (item_code), as_dict=True)[0]
		if not mr_qty["qty"]:
			mr_qty["qty"] = 0
		ppoc_query = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 """ % (item_code), as_dict=True)[0]
		if not ppoc_query["qty"]:
			ppoc_query["qty"] = 0
		ppoc_receipt = frappe.db.sql("""select sum(`tabPurchase Receipt Item`.qty) as qty from `tabPurchase Receipt`
		left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
		where `tabPurchase Receipt Item`.item_code = '%s' and `tabPurchase Receipt`.status = "Completed" """%(item_code),as_dict=True)[0]
		if not ppoc_receipt["qty"]:
			ppoc_receipt["qty"] = 0
		ppoc_total = ppoc_query["qty"] - ppoc_receipt["qty"]
		if stockqty['qty']:
			stockqty = stockqty['qty']
		else:
			stockqty = 0
		req = qty
		cal = sfs        
		req_qty = req - cal if cal <= req else 0
		reject = (ceil(req) * (rejection/100)) + ceil(req)
		with_rej = ((ceil(req) * (rejection/100)) + ceil(req) + safety_stock)
		if stockqty > with_rej:
			to_order = 0
		if stockqty < with_rej:
			to_order = with_rej - stockqty
		pack = 0
		to_be_order = 0
		if pack_size > 0:
			pack = to_order/ pack_size
			to_be_order = ceil(pack) * pack_size
		else:
			to_be_order = ceil(to_order)
		order_qty = 0
		if to_be_order > ppoc_total:
			order_qty = to_be_order - ppoc_total
		if ppoc_total > to_be_order:
			order_qty = 0
		if order_qty > mr_qty["qty"]:
			order_qty = order_qty - mr_qty["qty"]
		if moq > 0 and moq > order_qty:
			order_qty = moq
		exp_date = ''
		if to_be_order >0 and lead_time_days > 0:
			exp_date = add_days(nowdate(), lead_time_days)
		if ceil(req) > 0:
			uom = frappe.db.get_value("Item",item_code,'stock_uom')
			if item_type == 'Process Item' :

				final.append(frappe._dict({
					'item_code': item_code,
					'item_name': item_name,
					'schedule_date': frappe.utils.today(),
					'date':sch_date,
					'sales_order_number':sales_order_number,
					'with_rej':with_rej,
					'bom': bom,
					'moq':moq,
					'click' :"Click for Detailed View",
					'qty': to_be_order,
					'actual_stock_qty': str(round(stockqty,5)),
					'safety_stock':safety_stock,
					'qty_with_rejection_allowance':reject,
					'required_qty': str(round(qty,5)),
					'custom_total_req_qty': req,
					'custom_current_req_qty': req,
					'custom_stock_qty_copy': pps,
					'sfs_qty': sfs,
					'custom_requesting_qty': req_qty,
					'custom_today_req_qty': today_req,
					'uom': uom,
					'item_type':item_type,
					'item_billing_type':item_billing_type,
					'pack_size':pack_size,
					'lead_time_days':0,
					'cover_days':str(cover_days),
					'expected_date':' ',
					'po_qty':ppoc_total,
					'to_order':order_qty,
					'mr_qty':mr_qty["qty"]
				}))
			else :
				final.append(frappe._dict({
				'item_code': item_code,
				'item_name': item_name,
				'schedule_date': frappe.utils.today(),
				'date':sch_date,
				'sales_order_number':sales_order_number,
				'with_rej':with_rej,
				'bom': bom,
				'moq':moq,
				'click' :"Click for Detailed View",
				'qty': to_be_order,
				'actual_stock_qty': str(round(stockqty,5)),
				'safety_stock':safety_stock,
				'qty_with_rejection_allowance':reject,
				'required_qty': str(round(qty,5)),
				'custom_total_req_qty': req,
				'custom_current_req_qty': req,
				'custom_stock_qty_copy': pps,
				'sfs_qty': sfs,
				'custom_requesting_qty': req_qty,
				'custom_today_req_qty': today_req,
				'uom': uom,
				'item_type':item_type,
				'item_billing_type':item_billing_type,
				'pack_size':pack_size,
				'lead_time_days':lead_time_days,
				'cover_days':str(cover_days),
				'expected_date':exp_date,
				'po_qty':ppoc_total,
				'to_order':order_qty,
				'mr_qty':mr_qty["qty"]
			}))
	
	for k in final:
		exists = frappe.db.exists('Material Planning Details',{'item_code':k['item_code'],'date':today()})
		if exists:
			new_doc = frappe.get_doc('Material Planning Details',{'item_code':k['item_code'],'date':today()})
			if new_doc.item_code == k['item_code']:
				to_order = k['with_rej']
				pack = 0
				if k['pack_size'] > 0:
					pack = to_order/ k['pack_size']
				to_be_order = ceil(pack) * k['pack_size']
				exp_date = ''
				if to_be_order >0:
					exp_date = add_days(nowdate(), lead_time_days)

				uom = frappe.db.get_value("Item",k['item_code'],'stock_uom')
				order_qty = to_be_order
				new_doc.append('material_plan',{
					'item_code': k['item_code'],
					'item_name': k['item_name'],
					'schedule_date': k['schedule_date'],
					'pack_size':k['pack_size'],
					'lead_time':k['lead_time_days'],
					'required_qty': k['required_qty'],
					'stock_uom': uom,
					'item_type':item_type,
					'uom': uom,
					'order_schedule_date':k['date'],
					'moq':k['moq'],
					'order_qty':to_be_order,
					'qty':order_qty,
					'expected_date':'',
					'conversion_factor':1,
					'safety_stock':k['safety_stock'],
					'qty_with_rejection_allowance':k['qty_with_rejection_allowance']
				})
				new_doc.save(ignore_permissions=True)
		else:
			uom = frappe.db.get_value("Item",k['item_code'],'stock_uom')
			new_doc = frappe.new_doc('Material Planning Details')
			new_doc.item_code = k['item_code']
			new_doc.sales_order=k['sales_order_number']
			new_doc.date = today()
			if new_doc.item_code == k['item_code']:
				if float(k['actual_stock_qty']) > k['with_rej']:
					to_order = 0
				if float(k['actual_stock_qty']) < k['with_rej']:
					to_order = k['with_rej'] + float(k['safety_stock']) - float(k['actual_stock_qty'])
				pack = 0
				if k['pack_size'] > 0:
					pack = to_order/ k['pack_size']
				to_be_order = ceil(pack) * k['pack_size']
				exp_date = ''
				if to_be_order >0:
					exp_date = add_days(nowdate(), lead_time_days)

				order_qty = 0   
				if to_be_order > k['po_qty']:
					order_qty = to_be_order - k['po_qty']
					if k['moq'] > 0 and k['moq'] > order_qty:
						order_qty = k['moq']
				if k['po_qty'] > (to_be_order):
					order_qty = 0
				new_doc.append('material_plan',{
					'item_code': k['item_code'],
					'item_name': k['item_name'],
					'item_type':item_type,
					'schedule_date': k['schedule_date'],
					'pack_size':k['pack_size'],
					'lead_time':k['lead_time_days'],
					'required_qty': k['required_qty'],
					'sfs_qty': k['sfs_qty'],
					'order_schedule_date':k['date'],
					'stock_uom':uom,
					'moq':k['moq'],
					'uom':uom,
					'po_qty': k['po_qty'],
					'order_qty':order_qty,
					'qty': order_qty,
					'conversion_factor':1,
					'expected_date':exp_date,
					'actual_stock_qty':k['actual_stock_qty'],
					'safety_stock':k['safety_stock'],
					'qty_with_rejection_allowance':k['qty_with_rejection_allowance']
				})
				new_doc.save(ignore_permissions=True)

	# list = da
	final_list = data1 + da +dic + data4 + ict + final
	# final_list = data4

	for corrected in count_list:
		for updated in final_list:
			if corrected['item_code'] == updated['item_code'] :
				if updated['item_type'] != 'Process Item':
					last_list.append(frappe._dict({
						'item_code': updated['item_code'],
						'item_name': updated['item_name'],
						'item_type': updated['item_type'],
						'item_billing_type': updated['item_billing_type'],
						'uom': updated['uom'],
						'required_qty': updated['required_qty'],
						'qty_with_rejection_allowance': updated['qty_with_rejection_allowance'],
						'sfs_qty': updated['sfs_qty'],
						'actual_stock_qty': updated['actual_stock_qty'],
						'safety_stock': updated['safety_stock'],
						'pack_size': updated['pack_size'],
						'qty': updated['qty'],
						'mr_qty':updated['mr_qty'],
						'po_qty': updated['po_qty'],
						'moq': updated['moq'],
						'to_order': updated['to_order'],
						'lead_time_days': updated['lead_time_days'],
						'cover_days':str(updated['cover_days']),
						'expected_date': updated['expected_date'],
					}))
		# frappe.errprint(corrected['item_code'])

	return last_list

def get_exploded_items(bom, data, qty, skip_list):
	exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"])

	for item in exploded_items:
		item_code = item['item_code']
		# item_qty = flt(item['qty'])
		item_qty = flt(item['qty']) * qty
		data.append({"item_code": item_code,"item_name": item['item_name'],"bom": item['bom'],"uom": item['uom'],"qty": item_qty,"description": item['description']})
		# if item['bom']:
		#     get_exploded_items(item['bom'], data, qty=item_qty, skip_list=skip_list)



def get_bom_exploded_items(bom, data, qty, skip_list):
	exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"])

	for item in exploded_items:
		item_code = item['item_code']
		if item_code in skip_list:
			continue
		item_qty = flt(item['qty']) * qty
		data.append({"item_code": item_code,"item_name": item['item_name'],"bom": item['bom'],"uom": item['uom'],"qty": item_qty,"description": item['description']})
		# if item['bom']:
		#     get_exploded_items(item['bom'], data, qty=item_qty, skip_list=skip_list)

def get_sub_bom_exploded_items(bom, data_list, qty, skip_list):
	exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"])
	for item in exploded_items:
		item_code = item['item_code']
		item_qty = flt(item['qty']) * qty
		data_list.append({"item_code": item_code,"item_name": item['item_name'],"bom": item['bom'],"uom": item['uom'],"qty": item_qty,"description": item['description']})
		# if item['bom']:
		#     get_exploded_items(item['bom'], data, qty=item_qty, skip_list=skip_list)

def get_count_exploded_items(bom, count_list, qty, skip_list):
	bomitem = frappe.db.get_value("Item", {'default_bom': bom}, ['name'])
	count_list.append({
			"item_code": bomitem,
			"qty": qty,
		})
	exploded_items = frappe.get_all("BOM Item", filters={"parent": bom},fields=["qty", "bom_no as bom", "item_code", "item_name", "description", "uom"])

	for item in exploded_items:
		item_code = item['item_code']
		item_qty = flt(item['qty']) * qty
		count_list.append({"item_code": item_code,"item_name": item['item_name'],"bom": item['bom'],"uom": item['uom'],"qty": item_qty,"description": item['description']})
		if item['bom']:
			get_count_exploded_items(item['bom'], count_list, qty=item_qty, skip_list=skip_list)


def get_columns():
	return [
		{"label": _("Item Code"),"fieldtype": "Data","fieldname": "item_code","width": 180,"options": "Item"},
		{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 290},
		{"label": _("Item Type"), "fieldtype": "Data", "fieldname": "item_type", "width": 150},
		{"label": _("Item Billing Type"), "fieldtype": "Data", "fieldname": "item_billing_type", "width": 150},
		{"label": _("UOM"), "fieldtype": "Data", "fieldname": "uom", "width": 100},
		# {"label": _("Required Qty"), "fieldtype": "Link", "fieldname": "required_qty", "width": 150, "options": "Material Planning Details"},
		# {"label": _("Qty with Rejection Allowance"), "fieldtype": "Float", "fieldname": "qty_with_rejection_allowance", "width": 180},
		# {"label": _("SFS Qty"), "fieldtype": "Float", "fieldname": "sfs_qty", "width": 150},
		# {"label": _("Actual Stock Qty"), "fieldtype": "Link", "fieldname": "actual_stock_qty", "width": 150, "options": "Material Planning Details"},
		# {"label": _("Safety Stock"), "fieldtype": "Float", "fieldname": "safety_stock", "width": 150},
		# {"label": _("Pack Size"), "fieldtype": "Data", "fieldname": "pack_size", "width": 150},
		# {"label": _("Order Qty"), "fieldtype": "Float", "fieldname": "qty", "width": 150},
		# {"label": _("MR Qty"), "fieldtype": "Float", "fieldname": "mr_qty", "width": 150},
		# {"label": _("PO Qty"), "fieldtype": "Float", "fieldname": "po_qty", "width": 150},
		# {"label": _("MOQ"), "fieldtype": "Float", "fieldname": "moq", "width": 150},
		{"label": _("Qty to Order"), "fieldtype": "Float", "fieldname": "to_order", "width": 150},
		# {"label": _("Covers days"), "fieldtype": "Link", "fieldname": "cover_days", "width": 150,"options": "Material Planning Details"},
		# {"label": _("Lead Time Days"), "fieldtype": "Data", "fieldname": "lead_time_days", "width": 150},
		# {"label": _("Expected Date"), "fieldtype": "Link", "fieldname": "expected_date", "width": 130, "options": "Material Planning Details"},
	]

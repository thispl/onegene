import frappe
from frappe.utils import (
	flt,
	cint,
	cstr,
	get_html_format,
	get_url_to_form,
	gzip_decompress,
	format_duration,today,
	get_first_day,
	get_last_day
)
from frappe.desk.query_report import get_report_doc
import json

@frappe.whitelist()
def generate_mrp_report():
	report_name = "MRP Test"
	from_date = get_first_day(today())
	to_date = get_last_day(from_date)
	filters = {"from_date": from_date, "to_date": to_date}
	background_enqueue_run(report_name, frappe.as_json(filters))

@frappe.whitelist()
def create_scheduled_job_type():
	pos = frappe.db.exists('Scheduled Job Type', 'onegene.onegene.api.generate_mrp_report_mr')
	if not pos:
		sjt = frappe.new_doc("Scheduled Job Type")
		sjt.update({
			"method" : 'onegene.onegene.api.generate_mrp_report_mr',
			"frequency" : 'Cron',
			"cron_format":"00 00 * * *"  
		})
		sjt.save(ignore_permissions=True)


@frappe.whitelist()
def background_enqueue_run(report_name, filters=None, user=None):
	"""run reports in background"""
	if not user:
		user = frappe.session.user
	report = get_report_doc(report_name)
	track_instance = frappe.get_doc(
		{
			"doctype": "Prepared Report",
			"report_name": report_name,
			"filters": json.dumps(json.loads(filters)),
			"ref_report_doctype": report_name,
			"report_type": report.report_type,
			"query": report.query,
			"module": report.module,
		}
	)
	track_instance.insert(ignore_permissions=True)
	frappe.db.commit()
	# track_instance.enqueue_report()

	print({
		"name": track_instance.name,
		"redirect_url": get_url_to_form("Prepared Report", track_instance.name),
	})

@frappe.whitelist()
def generate_mrp_report_mr():
	report_name = "MRP - Material Request"
	from_date = get_first_day(today())
	to_date = get_last_day(from_date)
	filters = {"from_date": from_date, "to_date": to_date}
	background_enqueue_run(report_name, frappe.as_json(filters))
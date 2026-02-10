from . import __version__ as app_version


app_name = "onegene"
app_title = "ONEGENE"
app_publisher = "TEAMPRO"
app_description = "Manufacturing"
app_email = "mohamedshajith.j@groupteampro.com"
app_license = "MIT"

# Includes in <head>
# ------------------

desk_include_js = [
    "/assets/onegene/js/desk_custom.js"
]

# include js, css files in header of desk.html
# app_include_css = "/assets/onegene/css/onegene.css"
# app_include_js = "/assets/onegene/js/onegene.js"

# include js, css files in header of web template
# web_include_css = "/assets/onegene/css/onegene.css"
# web_include_js = "/assets/onegene/js/onegene.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "onegene/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Item" : "public/js/item.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
doctype_tree_js = {"BOM" : "public/js/bom_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
role_home_page = {
	"Supplier": "supplier-delivery"
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
	"methods":[
		"onegene.onegene.custom.get_data_system",
		"onegene.onegene.utils.packing_list",
		
	] 
	# "filters": "onegene.utils.jinja_filters"
}

# jenv = {
#     "filters": {
#         "amount_in_words": get_amount_in_words
#     }
# }

# Installation
# ------------

# before_install = "onegene.install.before_install"
# after_install = "onegene.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "onegene.uninstall.before_uninstall"
# after_uninstall = "onegene.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "onegene.utils.before_app_install"
# after_app_install = "onegene.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "onegene.utils.before_app_uninstall"
# after_app_uninstall = "onegene.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "onegene.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Leave Application": "onegene.overrides.CustomLeaveApplication",
	"Compensatory Leave Request":"onegene.overrides.CustomCompensatoryLeaveRequest",
	"Salary Slip": "onegene.overrides.CustomSalarySlip",
	"Attendance Request": "onegene.overrides.CustomAttendanceRequest",
	"Job Card": "onegene.overrides.CustomJobCard",
	"Stock Entry": "onegene.overrides.CustomStockEntry",
	# "Production Plan": "onegene.overrides.CustomProductionPlan"
}

# Document Events
# ---------------
# Hook on document methods and events


doc_events = {
	"Employee Separation": {
		"on_submit" : "onegene.onegene.doctype.resignation_form.resignation_form.update_employee",
		"on_cancel" : "onegene.onegene.doctype.resignation_form.resignation_form.revert_employee"
	},
		"Attendance":{
		"on_update":"onegene.onegene.custom.comp_off_for_ot",
	},
	# "Purchase Receipt": {
	#     "validate": "onegene.onegene.custom.warehouse_set_in_child_table"
	# }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"onegene.tasks.all"
	# ],
	"cron": {
		 "0 2 * * * *" : [
			"onegene.mark_attendance.mark_att_multidate"
		],
		"0 */2 * * *":"onegene.onegene.doctype.production_material_request.production_material_request.make_prepared_report",
		"30 8 * * *":"onegene.onegene.custom.update_jobcard_posting_date",
		"*/20 * * * *" : [
			"onegene.mark_attendance.enqueue_mark_att"
		],
		"00 00 01 * *" : [
			"onegene.onegene.custom.bday_allocate"
		],
		"0 0 * * *" : [
			"onegene.onegene.custom.mail_alert_for_safety_stock"
		],
		"*/15 * * * *" : [
			"onegene.onegene.custom.update_issue_status_from_teampro"
		],
        "0 8 * * *": [
            "onegene.onegene.custom.zero_ot"
        ],
        "0 */2 * * *": [
            "onegene.onegene.report.bom_cost.bom_cost.update_bom_cost_scheduler"
        ]
	},
	# "hourly": [
	# 	"onegene.tasks.hourly"
	# ],
	# "weekly": [
	# 	"onegene.tasks.weekly"
	# ],
	# "all": [
	# 	"onegene.tasks.all"
	# ],
	"daily": [
		"onegene.onegene.custom.update_quality_inspection_age",
		# "onegene.onegene.custom.generate_production_plan",
		"onegene.onegene.custom.update_machine_age",
	],
	"hourly": [
		"onegene.onegene.custom.mail_alert_for_safety_stock"
	],
	# "weekly": [
	# 	"onegene.tasks.weekly"
	# ],
	"monthly":[
		# "onegene.tasks.monthly",
		"onegene.onegene.custom.sick_leave_allocation",
		"onegene.onegene.custom.create_lwf",
	],
}

fixtures = [
    {
        "dt": "Custom DocPerm",
    },
]

# Testing
# -------

# before_tests = "onegene.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.manufacturing.doctype.bom.bom.get_children": "onegene.onegene.custom.custom_get_children"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "onegene.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["onegene.utils.before_request"]
# after_request = ["onegene.utils.after_request"]

# Job Events
# ----------
# before_job = ["onegene.utils.before_job"]
# after_job = ["onegene.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"onegene.auth.validate"
# ]

# permission_query_conditions = {
#     "Material Request": "onegene.onegene.custom.get_permission_query_conditions"
# }

# has_permission = {
#     "Material Request": "onegene.onegene.custom.has_permission",
#     "Employee": "onegene.onegene.custom.has_permission"
# }



doc_events = {
	"Stock Entry":{
		"validate":"onegene.utils.validate_qty",
		"on_cancel": ["onegene.onegene.custom.mark_stock_entry_as_cancelled",
                "onegene.onegene.stock_entry.reverse_update_stock_qty_in_job_card"],
        # "before_submit": "onegene.onegene.stock_entry.get_target_warehouse_from_mt",
		'on_submit':['onegene.onegene.custom.update_material_req',
					 "onegene.onegene.stock_entry.update_stock_qty_in_job_card"
                     ]
	},
	"Sales Order":{
		"after_insert" : ["onegene.onegene.custom.mark_order_created_in_iom"],
		"validate": [
			# "onegene.onegene.custom.validate_schedule_item_table",
			"onegene.onegene.custom.validate_customer_po",
			"onegene.onegene.custom.create_cutomer_po",
			"onegene.onegene.custom.validate_item_rate",
			   ],
		"on_submit": [
				"onegene.onegene.custom.create_sales_open_order",
				"onegene.onegene.custom.create_sales_order_schedule_from_so"
				],
		"on_cancel": ["onegene.onegene.custom.cancel_order_schedule_on_so_cancel"],
		"on_trash": "onegene.onegene.custom.unmark_order_created_in_iom",
		# "on_update": "onegene.onegene.custom.return_total_schedule",
	},
	"Sales Order Schedule Item": {
		"on_trash": "onegene.onegene.custom.delete_sales_order_schedule",
	},
	 "Material Request":{
		"before_insert": "onegene.onegene.custom.update_title_in_mr",
        "validate":"onegene.onegene.custom.set_hod"
        # "on_update": "onegene.onegene.custom.set_hod"
		# "on_submit":["onegene.onegene.custom.create_po"]	
		# "validate": "onegene.onegene.custom.update_mr_items",
	},
	"Employee":{
		"validate": "onegene.onegene.custom.inactive_employee",
		'after_insert':'onegene.onegene.custom.create_user_id',
		"on_update": ["onegene.onegene.custom.renamed_doc","onegene.onegene.custom.update_birthday_alowance","onegene.onegene.custom.mark_disable"]
	},
	"User":{
		'after_insert':'onegene.onegene.custom.remove_system_manager_role',
	},
	# "Sales Order Schedule":{
	# 	"on_update": ["onegene.onegene.utils.open_qty_so","onegene.onegene.utils.update_order_sch_qty"]
	# },
	"Delivery Note":{
		"on_submit": "onegene.onegene.utils.update_order_schedule_table",
		"on_cancel": "onegene.onegene.utils.revert_order_schedule_table"
	},
	"Salary Slip":{
		# "after_insert":["onegene.onegene.custom.weekly_off","onegene.onegene.custom.fixed_salary"],
		# "validate":"onegene.onegene.custom.fixed_salary"
		"after_insert":["onegene.onegene.custom.fixed_salary"],
	},
	"Attendance Request":{
		"on_submit": ["onegene.onegene.custom.od_hours_update"],
		"on_cancel": ["onegene.onegene.custom.att_request_cancel"],
		"validate":"onegene.onegene.custom.condition_for_ar",
		"on_trash": "onegene.onegene.custom.validate_on_trash"
	},
	'Scheduled Job Log':{
	   "validate":"onegene.onegene.custom.schedule_log_fail" 
	},
	'Logistics Request':{
		"after_insert":"onegene.onegene.custom.change_workflow_state"

	},
	'Sales Invoice': {
		"validate": ["onegene.onegene.custom.calculate_total_cbm","onegene.onegene.custom.validate_sales_invoice","onegene.onegene.custom.validate_item_rate","onegene.onegene.custom.update_the_changes_to_lr","onegene.onegene.custom.check_approved_lr",
		"onegene.onegene.custom.update_datetime_and_approver_details_in_Si", "onegene.onegene.custom.update_hod_time","onegene.onegene.custom.get_calculated_height",
        "onegene.onegene.custom.make_url_for_si","onegene.onegene.custom.update_port_in_si","onegene.onegene.custom.trigger_notification_based_on_the_workflow_in_si", "onegene.onegene.event.sales_invoice.set_posting_date_as_creation"],
		"before_insert": ["onegene.onegene.custom.sales_invoice_custom_autoname","onegene.utils.update_si_name"],
		"on_submit":["onegene.utils.update_lr_status", "onegene.onegene.custom.mark_qid_for_si", "onegene.onegene.custom.update_datetime_and_approver_details_finance"],
		'after_insert':[
			# 'onegene.utils.create_gate_entry',
			"onegene.onegene.custom.trigger_notification_based_on_the_workflow_in_si_for_draft"],
		"on_cancel": "onegene.onegene.custom.unmark_qid_for_si",
		'on_trash':'onegene.onegene.custom.unmark_qid_for_si',
		
	},
	 "Quality Inspection": {
		"validate": [
            		"onegene.onegene.quality_inspection.validate_qi_on_save",
                     "onegene.onegene.quality_inspection.create_qid_data",
					 "onegene.onegene.quality_inspection.validate_possible_inspection_qty",
					],
		"before_submit": "onegene.onegene.custom.validate_qi_on_submission",
		"on_submit": [
                      "onegene.onegene.quality_inspection.create_stock_entry_for_rejections",
					  "onegene.onegene.quality_inspection.update_quality_pending_status",
					  "onegene.onegene.custom.create_stock_entry_after_qc",
					  "onegene.onegene.custom.complete_last_job_card",
					  ],
		"on_cancel": [
					  "onegene.onegene.quality_inspection.revert_quality_pending_status",
					  "onegene.onegene.quality_inspection.remove_quality_inspection_from_job_card",
					  "onegene.onegene.quality_inspection.cancel_stock_entry"],
	},
	
	# "Attendance":{
	# 	"on_update": ["onegene.onegene.utils.mark_wh_ot_with_employee"]
	# },
	# "Sales Order Schedule":{
	# 	"on_update": "onegene.onegene.custom.get_pending_qty"
	# # 	"on_update": "onegene.onegene.custom.get_customer_name.",
	# },
   
	"Employee Separation": {
		"on_submit" : "onegene.onegene.doctype.resignation_form.resignation_form.update_employee",
		"on_cancel" : "onegene.onegene.doctype.resignation_form.resignation_form.revert_employee"
	},
	"Leave Application":{
		"after_insert": "onegene.onegene.custom.otbalance",
		"on_submit":"onegene.onegene.custom.otbalance",
		"on_cancel": "onegene.onegene.custom.cancel_leave_application",
		"validate": ["onegene.onegene.custom.restrict_for_zero_balance","onegene.onegene.custom.condition_for_la"],
		"on_trash": "onegene.onegene.custom.validate_on_trash"
	},
	"Compensatory Leave Request":{
		"validate":"onegene.onegene.custom.condition_for_compoff_lr",
		"on_trash": "onegene.onegene.custom.validate_on_trash"
	},
	"Attendance Permission":{
		"validate":"onegene.onegene.custom.condition_for_ap",
	},
	"Night Shift Auditors Plan Swapping":{
	   "validate":"onegene.onegene.custom.condition_for_nsaps", 
	},
	"Purchase Order": {
		"before_rename": "onegene.onegene.custom.rename_docname_field_in_po",
		"validate": "onegene.onegene.custom.validate_item_rate",
		"on_submit": [
			"onegene.onegene.custom.create_purchase_open_order",
			"onegene.onegene.custom.create_purchase_order_schedule_from_po",
			"onegene.onegene.custom.reload_po",
			"onegene.onegene.doctype.mr_scheduling.mr_scheduling.update_schedule_qty_in_material_request"
		],
		"after_insert": [
    		'onegene.onegene.doctype.mr_scheduling.mr_scheduling.update_po_number',
			"onegene.onegene.custom.mark_order_created_in_iom"
        ],
		"on_trash":['onegene.onegene.doctype.mr_scheduling.mr_scheduling.remove_po_number',
            "onegene.onegene.custom.unmark_order_created_in_iom"]
	},
	"Purchase Order Schedule Item": {
		"on_trash": "onegene.onegene.custom.delete_purchase_order_schedule",
	},
 
	"Address":{
		"before_save":"onegene.onegene.custom.customer_address_validate",
		"validate": "onegene.onegene.custom.update_tax_category_by_state",
	},
	
	"Purchase Receipt": {
		"after_insert": "onegene.onegene.custom.update_pr_in_sdn",
		"validate": "onegene.onegene.custom.validate_item_rate",
		"on_submit": ["onegene.onegene.custom.update_received_stock_in_order_schedule",
                # "onegene.onegene.custom.create_quality_pending_documents"
                ],
		"on_cancel": "onegene.onegene.custom.revert_received_stock_in_order_schedule",
		"on_trash": "onegene.onegene.custom.remove_pr_in_sdn",
	},
	
	"Department":{
		'validate':"onegene.onegene.custom.update_ot_hrs",
	},
 
	"Sales Order Item":{
		"on_update":"onegene.onegene.custom.sales_order_item_on_update"
	},
	"Production Plan": {
		
		"on_submit": [
            "onegene.onegene.custom.sales_order_schedule_reference",
            # "onegene.onegene.custom.create_work_order_from_production_plan",
		]
	},
	"Work Order": {
		"before_insert": ["onegene.onegene.custom.update_transfer_material_against_and_operation",
						  "onegene.onegene.custom.update_actual_fg_in_work_order",
						  "onegene.onegene.custom.queue_the_work_order"
						  ],
        "before_submit": "onegene.onegene.custom.set_required_item_in_work_order",
		"on_trash": "onegene.onegene.custom.unmark_work_order",
		"on_cancel": "onegene.onegene.custom.unmark_work_order",
	},
	"Job Card": {
		"before_save": "onegene.onegene.custom.set_auto_name_for_time_logs",
		"before_insert": ["onegene.onegene.custom.update_item_name_in_jobcard",
						  "onegene.onegene.custom.queue_the_job_card"
						  ],
        "after_insert": "onegene.onegene.custom.remove_supervisor_and_department",
		"validate": [
					"onegene.onegene.custom.get_raw_materials_for_jobcard",
					"onegene.onegene.custom.update_quantity_in_job_card",
					"onegene.onegene.custom.get_tool_data",
					"onegene.onegene.custom.set_docname_for_time_logs",
					"onegene.onegene.custom.update_the_queued_status",
					
					# "onegene.onegene.custom.make_url_for_scan_barcode",
					# "onegene.onegene.custom.update_completed_qty_in_tool"
					# "onegene.onegene.custom.create_stock_entry"
					],
		"on_submit": [
					# "onegene.onegene.custom.create_quality_inspection_from_job_card",
					"onegene.onegene.custom.update_the_queued_status"],
		"on_cancel": "onegene.onegene.custom.revert_processed_qty_in_tool",
		"on_trash":"onegene.onegene.custom.revert_processed_qty_in_tool",
	},
	"Supplier":{
     
        "before_insert":"onegene.onegene.custom.supplier_naming_before",
		"after_insert": ["onegene.onegene.supplier_user_creation.supp_user","onegene.onegene.custom.supplier_naming_after"],
		"on_trash":"onegene.onegene.supplier_user_creation.delete_supp_user"
	},

	"BOM": {
		"on_submit": "onegene.onegene.custom.bom_connection_from_fg_to_child"
	},
    "Customer":{
        "validate":"onegene.onegene.custom.update_customer_tax_category"
	}
 
 
}
from . import __version__ as app_version

app_name = "onegene"
app_title = "ONEGENE"
app_publisher = "TEAMPRO"
app_description = "Manufacturing"
app_email = "mohamedshajith.j@groupteampro.com"
app_license = "MIT"

# Includes in <head>
# ------------------

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
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "onegene.utils.jinja_methods",
#	"filters": "onegene.utils.jinja_filters"
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

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"onegene.tasks.all"
	# ],
	"daily": [
		"onegene.tasks.daily",
		"onegene.onegene.custom.generate_production_plan"
	],
	"cron": {
		"0 0 26 * *" : [
			"onegene.onegene.custom.bday_allocate"
		],
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
        "onegene.tasks.daily",
        "onegene.onegene.custom.generate_production_plan"
    ],
    # "hourly": [
    # 	"onegene.tasks.hourly"
    # ],
    # "weekly": [
    # 	"onegene.tasks.weekly"
    # ],
    "monthly":[
		# "onegene.tasks.monthly",
		"onegene.onegene.custom.sick_leave_allocation",
	],
}

# Testing
# -------

# before_tests = "onegene.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "onegene.event.get_events"
# }
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

doc_events = {
	"Sales Order":{
		"on_submit": ["onegene.onegene.custom.get_open_order","onegene.onegene.custom.create_order_schedule_from_so"],
		"on_cancel": ["onegene.onegene.custom.cancel_order_schedule_on_so_cancel"],
		"on_update": "onegene.onegene.custom.return_total_schedule",
		"on_update_after_submit":"onegene.onegene.utils.update_child_item"
	},
	"Employee":{
		"validate": "onegene.onegene.custom.inactive_employee"
	},
	"Order Schedule":{
		"on_update": ["onegene.onegene.utils.open_qty_so","onegene.onegene.utils.update_order_sch_qty"]
	},
	"Delivery Note":{
		"on_submit": "onegene.onegene.utils.update_order_schedule_table",
		"on_cancel": "onegene.onegene.utils.revert_order_schedule_table"
	},
	"Salary Slip":{
		"after_insert":["onegene.onegene.custom.weekly_off","onegene.onegene.custom.overtime_hours","onegene.onegene.custom.fixed_salary"],
	}
	# "Order Schedule":{
	# 	"on_update": "onegene.onegene.custom.get_pending_qty"
	# # 	"on_update": "onegene.onegene.custom.get_customer_name.",
	# },

}
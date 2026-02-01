import frappe

def execute():
    # Ensure schema is correct if earlier versions had wrong DocType flags/fields
    frappe.reload_doc("alphax_report_studio", "doctype", "ars_report_format")
    frappe.reload_doc("alphax_report_studio", "doctype", "ars_report_line")
    frappe.reload_doc("alphax_report_studio", "doctype", "ars_dataset")
    frappe.reload_doc("alphax_report_studio", "doctype", "ars_settings")

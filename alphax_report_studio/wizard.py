import json
import frappe

def _get_settings():
    return frappe.get_single("ARS Settings")

@frappe.whitelist()
def wizard_create_report(report_name: str, dataset: str = None, report_type: str = "Table",
                         group_by: str = None, from_date: str = None, to_date: str = None):
    """Create a simple report format (and optional dataset link) for non-developers.
    This does NOT require SQL; it uses your Dataset definition (recommended) or GL defaults.
    """
    if not report_name:
        frappe.throw("Report Name is required")

    settings = _get_settings()
    dataset = dataset or getattr(settings, "default_dataset_name", None)

    doc = frappe.new_doc("ARS Report Format")
    doc.title = report_name
    doc.report_type = report_type
    if hasattr(doc, "dataset") and dataset:
        doc.dataset = dataset

    # Minimal default columns for Table
    if report_type == "Table":
        cols = [
            {"fieldname":"account","label":"Account","fieldtype":"Link","options":"Account","width":180},
            {"fieldname":"account_name","label":"Account Name","fieldtype":"Data","width":260},
            {"fieldname":"debit","label":"Debit","fieldtype":"Currency","width":120},
            {"fieldname":"credit","label":"Credit","fieldtype":"Currency","width":120},
            {"fieldname":"department","label":"Department","fieldtype":"Link","options":"Department","width":160},
        ]
        doc.columns_json = json.dumps(cols)

    # Lines: Header + Data placeholder + Totals
    lines = []
    def add_line(line_type, label, data_source="Blank Line", line_reference=None):
        line_reference = line_reference or frappe.scrub(label).upper()
        lines.append({
            "doctype":"ARS Report Line",
            "line_type": line_type,
            "label": label,
            "line_reference": line_reference,
            "display_name": label,
            "data_source": data_source,
        })

    add_line("Heading", report_name, "Blank Line", "HDR")
    # The engine in api.py supports Account balances; keep as base
    add_line("Field", "Rows", "Account Data", "ROWS")
    add_line("Grand Total", "Total", "Calculated Amount", "TOTAL")

    doc.set("lines", lines)
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name}

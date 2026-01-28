import frappe
from frappe import _

@frappe.whitelist()
def run_report_format(report_format, filters=None):
    """Run a report format and return rows (label, value)."""
    filters = frappe.parse_json(filters) if filters else {}
    doc = frappe.get_doc("ARS Report Format", report_format)
    rows = []
    # MVP: if Custom SQL -> execute and return raw
    if doc.data_source_type == "Custom SQL" and doc.sql_query:
        data = frappe.db.sql(doc.sql_query, filters, as_dict=True)
        return {"type":"table", "data": data}
    # Basic: Account-based using GL Entry amounts
    # filters supported: from_date, to_date, company, cost_center, project, branch
    gl_filters = {}
    if filters.get("company"): gl_filters["company"] = filters["company"]
    if filters.get("from_date") and filters.get("to_date"):
        gl_filters["posting_date"] = ["between", [filters["from_date"], filters["to_date"]]]
    # dimension filters (optional)
    for dim in ["cost_center","project","branch","custom_division","department"]:
        if filters.get(dim): gl_filters[dim] = filters[dim]

    def gl_sum(account, extra=None):
        f = dict(gl_filters)
        if extra: f.update(extra)
        f["account"] = account
        return frappe.db.get_value("GL Entry", f, "sum(debit) - sum(credit)") or 0

    for line in doc.lines:
        if line.line_type in ("Header","Blank"):
            rows.append({"label": line.label, "value": None, "meta":{"type": line.line_type, "bold": bool(line.bold), "indent": line.indent}})
        elif line.line_type == "Account" and line.account:
            val = gl_sum(line.account, frappe.parse_json(line.filter_dimension) if line.filter_dimension else None)
            rows.append({"label": line.label, "value": float(val), "meta":{"type":"Account","bold": bool(line.bold), "indent": line.indent}})
        elif line.line_type == "Total":
            # total of all previous numeric values at same indent level
            total = sum(r["value"] for r in rows if isinstance(r.get("value"), (int,float)))
            rows.append({"label": line.label, "value": float(total), "meta":{"type":"Total","bold": True, "indent": line.indent}})
        elif line.line_type == "Formula" and line.formula:
            # Simple formula engine: LINE('label')
            env = {}
            for r in rows:
                if r.get("label") and isinstance(r.get("value"), (int,float)):
                    env[r["label"]] = r["value"]
            expr = line.formula
            # Replace LINE('X') with env.get('X',0)
            import re
            def repl(m): return str(env.get(m.group(1), 0))
            expr2 = re.sub(r"LINE\('([^']+)'\)", repl, expr)
            try:
                val = eval(expr2, {"__builtins__": {}}, {})
            except Exception:
                val = 0
            rows.append({"label": line.label, "value": float(val), "meta":{"type":"Formula","bold": bool(line.bold), "indent": line.indent}})
        else:
            rows.append({"label": line.label, "value": None, "meta":{"type": line.line_type, "bold": bool(line.bold), "indent": line.indent}})
    return {"type":"lines", "data": rows}

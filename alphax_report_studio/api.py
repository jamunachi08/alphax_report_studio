import frappe
from frappe import _


def _get_studio_settings():
    """Return ARS Studio Settings singleton dict (safe)."""
    try:
        return frappe.get_cached_doc("ARS Studio Settings", "ARS Studio Settings")
    except Exception:
        return None


def _safe_fieldname(fieldname: str) -> str:
    """Allow only simple column identifiers to avoid SQL injection."""
    if not fieldname:
        return ""
    fieldname = str(fieldname).strip()
    import re
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", fieldname):
        return ""
    return fieldname


def _apply_sql_tokens(sql: str, tokens: dict) -> str:
    """Replace {{TOKEN}} placeholders in SQL with safe identifiers."""
    if not sql:
        return sql
    out = sql
    for k, v in (tokens or {}).items():
        out = out.replace("{{" + str(k) + "}}", str(v))
    return out

@frappe.whitelist()
def run_report_format(report_format, filters=None):
    """Run a report format and return rows (label, value)."""
    filters = frappe.parse_json(filters) if filters else {}
    doc = frappe.get_doc("ARS Report Format", report_format)
    rows = []
    settings = _get_studio_settings()
    # Dynamic dimension mapping: allow SQL templates to use {{LOB_FIELD}}
    lob_field = None
    if hasattr(doc, "lob_field") and doc.lob_field:
        lob_field = doc.lob_field
    elif settings and getattr(settings, "lob_field", None):
        lob_field = settings.lob_field
    lob_field = _safe_fieldname(lob_field) or "department"
    sql_tokens = {"LOB_FIELD": lob_field}
    # MVP: if Custom SQL -> execute and return raw
    if doc.data_source_type == "Custom SQL" and doc.sql_query:
        q = _apply_sql_tokens(doc.sql_query, sql_tokens)
        data = frappe.db.sql(q, filters, as_dict=True)
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


@frappe.whitelist()
def run_dataset(dataset, filters=None, limit=None):
    """Execute an ARS Dataset SQL with optional filters."""
    filters = frappe.parse_json(filters) if filters else {}
    limit = int(limit) if limit else None
    ds = frappe.get_doc("ARS Dataset", dataset)
    if not ds.sql_query:
        frappe.throw(_("Dataset has no SQL Query"))
    settings = _get_studio_settings()
    lob_field = _safe_fieldname(getattr(settings, "lob_field", None)) or "department"
    q = _apply_sql_tokens(ds.sql_query, {"LOB_FIELD": lob_field})
    if limit:
        # naive limit append if not present; safe for MariaDB/Postgres
        q = f"SELECT * FROM ({q}) t LIMIT {limit}"
    data = frappe.db.sql(q, filters, as_dict=True)
    return {"columns": list(data[0].keys()) if data else [], "data": data}

def _agg(values, agg):
    vals=[v for v in values if v is not None]
    if not vals:
        return 0
    if agg=="Count":
        return len(vals)
    if agg=="Average":
        return sum(vals)/len(vals)
    if agg=="Min":
        return min(vals)
    if agg=="Max":
        return max(vals)
    # Sum default
    return sum(vals)

@frappe.whitelist()
def run_pivot(pivot, filters=None):
    """Run an ARS Pivot and return a pivot matrix."""
    filters = frappe.parse_json(filters) if filters else {}
    pv = frappe.get_doc("ARS Pivot", pivot)
    ds = frappe.get_doc("ARS Dataset", pv.dataset)
    if not ds.sql_query:
        frappe.throw(_("Dataset has no SQL Query"))
    # merge default filters
    if pv.filters_json:
        try:
            default_filters = frappe.parse_json(pv.filters_json)
            if isinstance(default_filters, dict):
                for k,v in default_filters.items():
                    filters.setdefault(k,v)
        except Exception:
            pass

    settings = _get_studio_settings()
    lob_field = _safe_fieldname(getattr(settings, "lob_field", None)) or "department"
    q = _apply_sql_tokens(ds.sql_query, {"LOB_FIELD": lob_field})
    data = frappe.db.sql(q, filters, as_dict=True)
    row_fields=[f.strip() for f in (pv.row_fields or '').split(',') if f.strip()]
    col_fields=[f.strip() for f in (pv.column_fields or '').split(',') if f.strip()]
    measure = pv.measure_field
    agg = pv.agg or "Sum"
    if not row_fields:
        row_fields=[]
    if not col_fields:
        col_fields=[]
    # Build keys
    def key(rec, fields):
        return " | ".join(str(rec.get(f,'')) for f in fields) if fields else "All"
    rows=set()
    cols=set()
    cell={}
    for rec in data:
        rk=key(rec,row_fields)
        ck=key(rec,col_fields)
        rows.add(rk); cols.add(ck)
        cell.setdefault((rk,ck), []).append(rec.get(measure) if measure else 1)
    rows_sorted=sorted(rows)
    cols_sorted=sorted(cols)
    matrix=[]
    for rk in rows_sorted:
        row=[]
        for ck in cols_sorted:
            row.append(float(_agg(cell.get((rk,ck), []), agg)))
        matrix.append(row)
    return {
        "row_fields": row_fields,
        "column_fields": col_fields,
        "rows": rows_sorted,
        "columns": cols_sorted,
        "values": matrix,
        "agg": agg,
        "measure": measure
    }

@frappe.whitelist()
def run_chart(chart, filters=None):
    """Run an ARS Chart and return data suitable for frappe charts."""
    filters = frappe.parse_json(filters) if filters else {}
    ch = frappe.get_doc("ARS Chart", chart)
    if ch.pivot:
        pv = run_pivot(ch.pivot, filters=filters)
        # Default: use columns as labels, first row as dataset
        labels = pv["columns"]
        datasets = []
        for i, rname in enumerate(pv["rows"][:20]):  # safety
            datasets.append({"name": rname, "values": pv["values"][i]})
        return {"type": ch.chart_type or "Bar", "labels": labels, "datasets": datasets}
    if ch.dataset:
        ds_res = run_dataset(ch.dataset, filters=filters, limit=5000)
        data = ds_res["data"]
        x=ch.x_field
        y=ch.y_field
        series=ch.series_field
        if not x or not y:
            frappe.throw(_("Chart needs x_field and y_field"))
        labels=sorted(list({str(d.get(x,'')) for d in data}))
        if series:
            series_vals=sorted(list({str(d.get(series,'')) for d in data}))
            datasets=[]
            for sv in series_vals:
                vals=[]
                for lab in labels:
                    vals.append(sum(float(d.get(y) or 0) for d in data if str(d.get(x,''))==lab and str(d.get(series,''))==sv))
                datasets.append({"name": sv, "values": vals})
        else:
            vals=[]
            for lab in labels:
                vals.append(sum(float(d.get(y) or 0) for d in data if str(d.get(x,''))==lab))
            datasets=[{"name": ch.title, "values": vals}]
        return {"type": ch.chart_type or "Bar", "labels": labels, "datasets": datasets}
    frappe.throw(_("Chart must link to a Pivot or Dataset"))

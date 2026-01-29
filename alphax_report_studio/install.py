import frappe

def after_install():
    """Post-install bootstrap (safe & idempotent)."""
    try:
        # Create singleton settings with sensible defaults
        if not frappe.db.exists("ARS Studio Settings", "ARS Studio Settings"):
            doc = frappe.get_doc({
                "doctype": "ARS Studio Settings",
                "lob_field": "department",
                "enable_sql_tokens": 1,
            })
            doc.insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception:
        # Never block app install
        pass

def after_migrate():
    try:
        frappe.db.commit()
    except Exception:
        pass

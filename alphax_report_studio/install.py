import frappe

def after_install():
    # Keep installation safe & idempotent
    try:
        frappe.db.commit()
    except Exception:
        pass

def after_migrate():
    try:
        frappe.db.commit()
    except Exception:
        pass

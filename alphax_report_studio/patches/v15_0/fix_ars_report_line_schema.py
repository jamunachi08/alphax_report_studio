import frappe

def execute():
    table = "tabARS Report Line"
    cols = frappe.db.get_table_columns(table) if frappe.db.table_exists(table) else []
    if not cols:
        return
    def add_col(name, ddl):
        if name not in cols:
            frappe.db.sql(f"ALTER TABLE `{table}` ADD COLUMN {ddl}")
    # These columns are required for Child Table
    add_col("parent", "`parent` varchar(140)")
    add_col("parenttype", "`parenttype` varchar(140)")
    add_col("parentfield", "`parentfield` varchar(140)")
    add_col("idx", "`idx` int(11) NOT NULL DEFAULT 0")
    frappe.db.commit()

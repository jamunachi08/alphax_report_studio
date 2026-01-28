app_name = "alphax_report_studio"
app_title = "AlphaX Report Studio"
app_publisher = "IRSAA / AlphaX"
app_description = "Excel-style MIS & Financial Report Designer + Pivot + Charts"
app_email = "support@alphax.local"
app_license = "MIT"

# Keep hook paths stable (no double module)
after_install = ["alphax_report_studio.install.after_install"]
after_migrate = ["alphax_report_studio.install.after_migrate"]

# Desk
app_icon = "octicon octicon-graph"
app_color = "#2D6A9F"

# JS for builder doctype forms (optional)
doctype_js = {
    "ARS Report Format": "public/js/ars_report_format.js",
}

# Web routes (Desk Page)
# `page/ars_report_studio_builder` folder provides route: ars-report-studio-builder

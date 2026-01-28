# AlphaX Report Studio (alphax_report_studio)

A clean, installable Frappe app that provides an Excel-style **Report Format Designer**:
- Define **Report Formats**
- Define **Report Lines** (groups, headings, totals, formulas)
- Dimension filters (JSON) for Branch / Cost Center / Project, etc.

This is a **starter foundation** (clean structure) to stop install issues permanently.

## Install
```bash
bench get-app alphax_report_studio https://github.com/<YOUR_ORG>/alphax_report_studio.git
bench --site <yoursite> install-app alphax_report_studio
```

## Doctypes
- ARS Report Format
- ARS Report Line

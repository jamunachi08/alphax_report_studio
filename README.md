# AlphaX Report Studio (alphax_report_studio)

A **report designer** for ERPNext/Frappe that lets you build:

- Financial statement formats (Trial Balance / P&L / Balance Sheet / Cashflow)
- MIS breakdown reports (LOB-wise, dimension-wise)
- Pivot tables (Row/Column grouping + measure aggregation)
- Charts (bar/line/pie) using Frappe Charts

## Install

```bash
bench get-app https://github.com/jamunachi08/AlphaX_MIS_Next.git
bench --site <site-name> install-app alphax_report_studio
bench --site <site-name> migrate
```

## Start using

Go to: **Report Studio → ARS Report Format** and create a format.

Open the builder page: **Report Studio → Report Studio Builder**

## Notes

This app is designed to be **install-safe** (hooks don’t assume data).

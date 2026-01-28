from setuptools import setup, find_packages

setup(
    name="alphax_report_studio",
    version="1.0.0",
    description="AlphaX Report Studio - Excel-style MIS/Financial report designer for Frappe",
    author="IRSAA / AlphaX",
    author_email="support@alphax.local",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)

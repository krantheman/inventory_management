from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in inventory_management/__init__.py
from inventory_management import __version__ as version

setup(
	name="inventory_management",
	version=version,
	description="Inventory management system",
	author="krantheman",
	author_email="ims@frappe.io",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)

from setuptools import find_packages, setup

setup(
    name="ferum_customs",
    version="1.0.0",
    description="Ferum custom code package for Frappe/ERPNext",
    author="Dmitriyrus99",
    author_email="Dmitriyrus99@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools>=42",  # Specify a minimum version for setuptools
        "frappe>=13.0.0",  # Add Frappe dependency
        "erpnext>=13.0.0",  # Add ERPNext dependency
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Frappe",
        "Framework :: ERPNext",
    ],
    python_requires='>=3.6',  # Specify the minimum Python version
)

# Changelog:
# Version 1.0.0 - Initial release
# - Added Frappe and ERPNext dependencies
# - Improved package metadata

from setuptools import find_packages, setup

setup(
    name="ferum_customs",
    version="1.0.0",
    description="Ferum custom code package",
    author="Dmitriyrus99",
    author_email="Dmitriyrus99@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools>=42",  # Specify a minimum version for setuptools
        # Add other dependencies related to Frappe/ERPNext if applicable
    ],
    classifiers=[  # Add classifiers for better package metadata
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Specify the minimum Python version
)

# Changelog:
# Version 1.0.0 - Initial release

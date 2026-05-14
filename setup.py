from setuptools import setup, find_packages

setup(
    name="avd-monitor",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.110.0",
        "uvicorn[standard]>=0.29.0",
        "jinja2>=3.1.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.27.0",
    ],
    extras_require={
        "azure": [
            "azure-identity>=1.15.0",
            "azure-mgmt-desktopvirtualization>=1.0.0",
            "azure-monitor-query>=1.3.0",
            "azure-mgmt-compute>=30.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "avd-monitor=avd_monitor.main:app",
        ]
    },
    python_requires=">=3.10",
)

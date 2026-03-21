"""
MasterChief Enterprise DevOps Platform
A comprehensive, modular enterprise DevOps automation platform
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="masterchief",
    version="2.0.0",
    author="MasterChief Team",
    description="Enterprise DevOps Automation Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jbalestrine/masterchief",
    packages=find_packages(include=["core*", "echo*", "features*", "blueprints*", "utils*", "tf_wizard*", "platform*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.14",
    ],
    python_requires=">=3.10",
    install_requires=[
        # Web Framework
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "Flask-Login>=0.6.0",
        "Flask-SocketIO>=5.0.0",
        "werkzeug>=3.0.0",
        "python-socketio>=5.0.0",
        "python-engineio>=4.0.0",
        # System & Utility
        "psutil>=5.9.0",
        "requests>=2.31.0",
        "PyYAML>=6.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
        # Security & Auth
        "cryptography>=46.0.5",
        "cffi>=2.0.0",
        "PyJWT>=2.8.0",
        "authlib>=1.3.0",
        "jsonschema>=4.17.0",
        "pydantic>=2.5.0",
        "bcrypt>=4.0.0",
        "python-jose>=3.3.0",
        # Background Scheduling
        "apscheduler>=3.10.0",
        "sqlalchemy>=2.0.0",
        # Source Control
        "gitpython>=3.1.0",
        "git-filter-repo>=2.47.0",
        # IRC Bridge
        "irc>=20.0.0",
        # Production WSGI
        "gunicorn>=21.0.0",
        # Testing
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "httpx>=0.25.0",
        # Cloud & DevOps
        "azure-identity>=1.15.0",
        "azure-mgmt-resource>=23.0.0",
        "azure-mgmt-compute>=30.0.0",
        "azure-mgmt-storage>=21.0.0",
        "azure-core>=1.29.0",
        "azure-devops>=7.1.0b4",
        "boto3>=1.34.0",
        "kubernetes>=28.0.0",
        "docker>=7.0.0",
        "hvac>=2.0.0",
        "paramiko>=3.4.0",
        "python-gitlab>=4.0.0",
        "PyGithub>=2.1.0",
        # Image Processing
        "Pillow>=10.0.0",
        # Infrastructure
        "ansible>=9.0.0",
        # Metrics & Observability
        "prometheus-client>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "isort>=5.12.0",
            "pylint>=3.0.0",
            "types-PyYAML>=6.0.0",
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=2.0.0",
            "ipython>=8.18.0",
            "pre-commit>=3.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "masterchief=core.cli.main:cli",
            "tf-wizard=tf_wizard.app:main",
        ],
    },
)

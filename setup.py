"""
MasterChief Enterprise DevOps Platform
A comprehensive, modular enterprise DevOps automation platform
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="masterchief",
    version="1.0.0",
    author="MasterChief Team",
    description="Enterprise DevOps Automation Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jbalestrine/masterchief",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.1.0",
        "pyyaml>=6.0",
        "jinja2>=3.1.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.0.0",
        "redis>=5.0.0",
        "psycopg2-binary>=2.9.0",
        "sqlalchemy>=2.0.0",
        "azure-identity>=1.15.0",
        "azure-keyvault-secrets>=4.7.0",
        "azure-mgmt-compute>=30.0.0",
        "azure-mgmt-network>=25.0.0",
        "azure-mgmt-storage>=21.0.0",
        "ansible>=8.0.0",
        "kubernetes>=28.0.0",
        "docker>=6.1.0",
        "prometheus-client>=0.19.0",
        "grafana-api>=1.0.3",
        "irc>=20.0.0",
        "websockets>=12.0",
        "fluent-logger>=0.10.0",
        "httpx>=0.25.0",
        "aiohttp>=3.9.0",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
            "isort>=5.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "masterchief=core.cli.main:cli",
        ],
    },
)

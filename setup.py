"""Setup configuration for helloworld-devops project."""

from setuptools import setup, find_packages

setup(
    name="helloworld-devops",
    version="1.0.0",
    description="Simple calculator API for demonstrating CI/CD concepts",
    author="UNIR DevOps Course",
    packages=find_packages(exclude=["test", "test.*"]),
    python_requires=">=3.6",
    install_requires=[
        "Flask==2.3.0",
        "pytest==7.4.0",
        "pytest-cov==4.1.0",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.0",
            "pytest-cov==4.1.0",
        ]
    },
)

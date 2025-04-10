from setuptools import setup, find_packages

setup(
    name="warehouse_recommender",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        
        "numpy>=1.19.0",
        "pydantic>=1.8.0",
        "pytest>=6.2.5",
        "pytest-asyncio>=0.15.1",
        "httpx>=0.18.2",
        "scikit-learn>=1.0.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "scikit-learn>=0.24.2",
        "joblib>=1.0.2",
        "geopy>=2.2.0",
    ],
) 
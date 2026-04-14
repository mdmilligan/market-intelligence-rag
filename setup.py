from setuptools import find_packages, setup


setup(
    name="market-intelligence-rag",
    version="0.1.0",
    description="CLI-first SEC ingestion and retrieval pipeline for market intelligence RAG.",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "beautifulsoup4>=4.12,<5",
        "openai>=1.30,<2",
        "qdrant-client>=1.9,<2",
        "requests>=2.31,<3",
    ],
    entry_points={
        "console_scripts": [
            "market-rag=market_intelligence_rag.cli:main",
        ]
    },
)

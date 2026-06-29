from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pawpy-cli",
    version="1.0.0b0",
    author="Danyal Khattak",
    author_email="Danyalkhattak739@icloud.com",
    description=(
        "Advanced wordlist generator for OSINT, " "pentesting, and security research"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Danyalkhattak/pawpy",
    project_urls={
        "Bug Reports": "https://github.com/Danyalkhattak/pawpy/issues",
        "Source": "https://github.com/Danyalkhattak/pawpy",
        "Documentation": "https://github.com/Danyalkhattak/pawpy#readme",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.0.0",
        "pyfiglet>=0.8.post1",
        "zxcvbn>=4.4.28",
    ],
    extras_require={
        "api": [
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
        ],
        "gpu": [
            "cupy",
        ],
        "websocket": [
            "websockets>=12.0",
        ],
        "all": [
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
            "cupy",
            "websockets>=12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pawpy=pawpy.cli:main",
        ],
    },
    keywords=[
        "wordlist",
        "password",
        "osint",
        "pentesting",
        "cybersecurity",
        "security",
        "dictionary",
        "generator",
        "cli",
        "redteam",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
)

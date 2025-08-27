from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith('#')]

setup(
    name="jarvis-assistant",
    version="2.0.0",
    author="JARVIS Team",
    author_email="team@jarvis.dev",
    description="Asistente de IA avanzado, multimodal y seguro",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jarvis",
    packages=find_packages(include=['jarvis', 'jarvis.*']),
    install_requires=requirements,
    include_package_data=True,
    package_data={
        '': ['*.txt', '*.md', '*.toml', '*.json'],
    },
    entry_points={
        'console_scripts': [
            'jarvis=jarvis.main:cli_main',
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

from setuptools import setup, find_packages

setup(
    name="nucquery",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich",
    ],
    package_data={
        'nucquery': ['data/*.json', 'data/*.dat'],
    },
    entry_points={
        'console_scripts': [
            'nucquery=nucquery.nuclide_query:main',
        ],
    },
    author="Your Name",
    description="Nuclide Query Tool",
)

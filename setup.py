from setuptools import setup, find_packages

required = ["polyline", "matplotlib", "requests", "osgridconverter"]

dev_required = ["pytest", "mypy"]

setup(
    name='stravatools',
    version='0.1',
    description='Collection of Strava tools',
    author='Paul',
    author_email='pwastallard@googlemail.com',
    install_requires=required,
    extras_require={"dev": dev_required},
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'strava_summary=stravatools.summary:main',
            'strava_find=stravatools.strava_find:main',
            'strava_get=stravatools.get_week:main',
            'strava_gridplot=stravatools.gridplot:main',
            'strava_csv_totals=stravatools.csv_totals:main',
        ]
    }
)

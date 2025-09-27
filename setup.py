from setuptools import setup, find_packages

setup(
    name='ingress-leaderboard',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'python-telegram-bot',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'ingress-leaderboard = main:main',
        ],
    },
)
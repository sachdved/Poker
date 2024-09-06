from setuptools import setup, find_packages

setup(
    name='poker',
    version='0.1',
    description='A package to evaluate poker hand strength',
    author='Vedant Sachdeva',
    author_email='sachdved@gmail.com',
    url='https://github.com/sachdved/Poker',
    package_dir={'': 'src'},  # Tell setuptools to look in 'src' for packages
    packages=find_packages(where='src'),  # Find all packages in 'src'
    install_requires=[
        'numpy',
    ],
    python_requires='>=3.6',
)
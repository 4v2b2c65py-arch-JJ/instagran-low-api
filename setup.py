"""
Setup configuration for instagran-low-api package
Complete solution for device OS reaction data gathering and cross-service callbacks.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

setup(
    name='instagran-low-api',
    version='1.0.0',
    author='4v2b2c65py-arch-JJ',
    author_email='dev@instagran-low-api.com',
    description='Complete solution for device OS reaction data gathering and cross-service callbacks',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/4v2b2c65py-arch-JJ/instagran-low-api',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=[
        'numpy>=1.21.0',
        'matplotlib>=3.5.0',
        'pytz>=2023.3',
        'aiohttp>=3.8.0',
        'requests>=2.28.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
        ],
        'pinecone': [
            'pinecone-client>=3.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'instagran-api=neural_orchestrator.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

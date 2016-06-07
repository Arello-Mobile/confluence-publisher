import os
from setuptools import setup, find_packages

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

long_description = open('README.rst' if os.path.exists('README.rst') else 'README.md').read()

setup(
    name='confluence-publisher',
    version='1.2.0',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    license='MIT',
    description='Tool for publishing Sphinx generated documents to Confluence',
    long_description=long_description,
    url='https://github.com/Arello-Mobile/confluence-publisher',
    author='Arello Mobile',
    install_requires=open('requirements.txt').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Documentation',
    ],
    entry_points={
        'console_scripts': [
            'conf_page_maker = conf_publisher.page_maker:main',
            'conf_publisher = conf_publisher.publish:main'
        ]
    }
)

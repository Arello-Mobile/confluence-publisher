import os
from setuptools import setup

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='confluence_publisher',
    version='1.0.0',
    packages=['conf_publisher'],
    include_package_data=True,
    license='BSD License',
    description='Tool for publishing Sphinx generated documents to Confluence',
    url='https://github.com/Arello-Mobile/confluence-publisher',
    author='Arello Mobile',
    install_requires=open('requirements.txt').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Documentation',
    ],
    entry_points={
        'console_scripts': [
            'conf_page_maker = conf_publisher.page_maker:main',
            'conf_publisher = conf_publisher.publish:main'
        ]
    }
)
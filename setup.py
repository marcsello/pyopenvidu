#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['requests', 'requests-toolbelt']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Marcell Pünkösd",
    author_email='punkosdmarcell@rocketmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Topic :: Communications',
        'Topic :: Communications :: Conferencing',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    description="Python interface to the OpenVidu WebRTC videoconference library.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pyopenvidu',
    name='pyopenvidu',
    packages=find_packages(include=['pyopenvidu', 'pyopenvidu.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/marcsello/pyopenvidu',
    project_urls={
        "Documentation": "https://pyopenvidu.readthedocs.io/",
        "Code": "https://github.com/marcsello/pyopenvidu",
        "Issue tracker": "https://github.com/marcsello/pyopenvidu/issues",
    },
    version='0.2.0',
    zip_safe=False,
)

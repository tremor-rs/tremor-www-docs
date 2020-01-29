#!/usr/bin/env python
"""Setup tremor-mkdocs-lexer."""
from setuptools import setup, find_packages

entry_points = '''
[pygments.lexers]
tremor=tremor_mkdocs_lexer:TremorLexer
trickle=tremor_mkdocs_lexer:TrickleLexer
'''

setup(
    name='tremor-mkdocs-lexer',
    version='0.5.2',
    description='Pygments lexer package for tremor-script v0.5.2+ and tremor-query v0.6+',
    author='Darach Ennis',
    author_email='dennis[at]wayfair.com',
    url='https://github.com/wayfair-tremor/tremor-mkdocs-lexer',
    packages=find_packages(),
    entry_points=entry_points,
    install_requires=[
        'Pygments>=2.3.1'
    ],
    zip_safe=True,
    license='Apache License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)

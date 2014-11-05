from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='plone.app.vulnerabilities',
      version=version,
      description='',
      long_description='\n\n'.join([
            open('README.rst').read(),
            open(os.path.join('src', 'plone', 'app', 'vulnerabilities', 'README.txt')).read()
      ]),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      package_dir={'': 'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'test': [
                  'plone.app.testing',
              ]
      },
      install_requires=[
          'setuptools',
          'Plone',
          'plone.app.dexterity',
          'plone.directives.form',
          'plone.app.textfield',
          'plone.namedfile',
          'plone.autoform'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

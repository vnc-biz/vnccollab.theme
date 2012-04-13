from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='vnccollab.theme',
      version=version,
      description="An installable theme for VNC Collaboration Plone 4 Site.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='web zope plone theme',
      author='Vitaliy Podoba',
      author_email='vitaliypodoba@gmail.com',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['vnccollab'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'cioppino.twothumbs',
          'Products.Carousel',
          'simplejson',
          'pytz',
          'textile',
          'pyzimbra',
          'zope.testbrowser',
          'BeautifulSoup',
          'pyactiveresource',
          'wsapi4plone.core',
          'z3c.jbot'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

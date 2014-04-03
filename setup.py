from setuptools import setup, find_packages
import os

version = open('version.txt').read()

setup(name='vnccollab.theme',
      version=version,
      description="An installable theme for VNC Collaboration Plone 4 Site.",
      long_description=open(os.path.join("docs", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='web zope plone theme',
      author='Vitaliy Podoba',
      author_email='vitaliy.podoba@vnc.biz',
      url='https://redmine.vnc.biz/redmine/projects/vnc-plone-theme',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['vnccollab'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pytz',
          'textile',
          'pyzimbra',
          'z3c.jbot',
          'tldextract',
          'simplejson',
          'five.formlib',
          'BeautifulSoup',
          'zope.testbrowser',
          'wsapi4plone.core',
          'pyactiveresource',
          'cioppino.twothumbs',
          'sc.social.bookmarks',
          'Products.Carousel',
          'Products.AdvancedQuery',
          'Products.CMFNotification',
          'plone.api',
          'plone.app.jquery',
          'plone.app.jquerytools',
          'collective.notices',
          'collective.js.jqueryui',
          'collective.quickupload',
          'collective.xmpp.chat',
          'collective.plonetruegallery',
          'collective.z3cform.datepicker',
          'collective.braveportletsmanager',
          'collective.customizablePersonalizeForm',
          'vnccollab.common',
          'vnccollab.content',
      ],
      extras_require={'test': ['plone.app.testing']},
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

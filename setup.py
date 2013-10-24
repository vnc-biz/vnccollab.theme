from setuptools import setup, find_packages
import os

version = '1.7.5'

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
      author_email='vitaliy.podoba@vnc.biz',
      url='https://redmine.vnc.biz/redmine/projects/vnc-plone-theme',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['vnccollab'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'simplejson',
          'pytz',
          'textile',
          'pyzimbra',
          'BeautifulSoup',
          'zope.testbrowser',
          'five.formlib',
          'Products.CMFNotification',
          'pyactiveresource',
          'cioppino.twothumbs',
          'Products.Carousel',
          'wsapi4plone.core',
          'z3c.jbot',
          'tldextract',
          'Products.AdvancedQuery',
          'collective.xmpp.chat',
          'plone.api',
          'plone.app.jquery',
          'plone.app.jquerytools',
          'jarn.xmpp.core',
          'jarn.jsi18n',
          'jarn.xmpp.collaboration',
          'collective.js.jqueryui',
          'collective.plonetruegallery',
          'collective.z3cform.datepicker',
          'collective.customizablePersonalizeForm',
          'collective.notices',
          'sc.social.bookmarks',
          'vnccollab.common',
      ],
      extras_require={'test': ['plone.app.testing']},
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

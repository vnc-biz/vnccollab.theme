vnccollab.theme
===============

Introduction
------------

VNC Collaboration Theme is the official VCP theme. It include serveral convenience
functionality as:

* A customized dashboard.
* Dashlet viewlet: a way to integrate several sources of news.
* An anonymous homepage redirector.
* A wizard to add new content.
* Integration with zimbra (requires zimbra server extensions).
* Integration with redmine (requires redmine server extensions).
* "Like" functionality.
* Etherpad portlet.
* Generic Iframe portlet.
* World Clock portlet.


Installation
------------

Please read INSTALL.rst for details about the installation.


Usage
-----

The functionality offered in this add-on is implemented as portlets and viewlets.
To add them to your site, follow one of the following procedures:

* Use the web interface to add a portlet or a viewlet.
* Programmatically, adding an import step to your site's policy manager add-on.

The first option is easier, but the configuration will be stored in the ZODB. The
second option requires programming.

Known Issues
------------

Due to the use of plone.app.jquery 1.7.2, there could be some issues with
overlays in Plone 4.2.


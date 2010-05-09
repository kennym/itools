#############################################################################
This is a personal fork of python-itools. You can find the original code at:
					   http://www.hforge.org/itools.
#############################################################################

itools is a Python library, it groups a number of packages into a single
meta-package for easier development and deployment.

The packages included are:

  itools.abnf             itools.ical             itools.srx
  itools.core             itools.log              itools.stl
  itools.csv              itools.odf              itools.tmx
  itools.datatypes        itools.office           itools.uri
  itools.fs               itools.pdf              itools.web
  itools.gettext          itools.pkg              itools.workflow
  itools.git              itools.python           itools.xapian
  itools.handlers         itools.relaxng          itools.xliff
  itools.html             itools.rest             itools.xml
  itools.http             itools.rss              itools.xmlfile
  itools.i18n             itools.soup

The scripts included are:

  igettext-build.py       ipkg-build.py           ipkg-update-locale.py
  igettext-extract.py     ipkg-copyright.py       ixapian-inspect.py
  igettext-merge.py       ipkg-info.py
  iodf-greek.py           ipkg-quality.py


Requirements
=============

Software    Version  Used by          Home
----------  -------  ---------------  ----------------------------------------
Python        2.6.4  itools           http://www.python.org/
pkg-config     0.23  itools           http://pkg-config.freedesktop.org/
glib           2.20  itools.fs        http://www.gtk.org/
pygobject      2.18  itools.fs        http://www.pygtk.org/
libsoup        2.28  itools.soup      http://live.gnome.org/LibSoup
reportlab       2.3  itools.pdf       http://www.reportlab.org/
xapian        1.0.8  itools.xapian    http://www.xapian.org/
pywin32         212  (Windows)        http://sf.net/projects/pywin32/
PIL           1.1.6  itools.handlers  http://www.pythonware.com/products/pil/
matplotlib     0.91  ipkg-quality.py  http://matplotlib.sourceforge.net/

Note: you will find packages like pkg-config and glib compiled for Windows
on http://ftp.gnome.org/pub/gnome/binaries/win32/ (don't forget to check
the "dependencies" directory).

For indexing office documents like PDF, DOC and XLS, you can install libraries
and Python packages.  They are not mandatory for installing itools.

Software    Version  Format           Home
----------  -------  ---------------  ----------------------------------------
xlrd          0.6.1  XLS              http://www.lexicon.net/sjmachin/xlrd.htm
poppler      0.10.4  PDF              http://poppler.freedesktop.org/
wv2           0.2.3  DOC              https://sourceforge.net/projects/wvware


Install
=============

If you are reading this instructions you probably have already unpacked
the itools tarball with the command line:

  $ tar xzf itools-X.Y.Z.tar.gz

And changed the working directory this way:

  $ cd itools-X.Y.Z

So now to install itools you just need to type this:

  $ python setup.py install

Unit Tests
=============

To run the unit tests just type:

  $ cd test
  $ python test.py

If there are errors, please report either to the issue tracker or to
the mailing list:

  - http://bugs.hforge.org/
  - http://www.hforge.org/community


Documentation
=============

The documentation is distributed as a separate package, itools-docs.
The PDF file can be downloaded from http://www.hforge.org/itools


Resources
=============

Home
http://www.hforge.org/itools

Mailing list
http://www.hforge.org/community/
http://archives.hforge.org/index.cgi?list=itools

Bug Tracker
http://bugs.hforge.org


Copyright
=============

Copyright (C) 2002-2010 Juan David Ibáñez Palomar <jdavid@itaapy.com>
Copyright (C) 2005-2010 Luis Arturo Belmar-Letelier <luis@itaapy.com>
Copyright (C) 2005-2010 Hervé Cauwelier <herve@itaapy.com>
Copyright (C) 2005-2010 Nicolas Deram <nicolas@itaapy.com>

And others. Check the CREDITS file for complete list.


License
=============

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


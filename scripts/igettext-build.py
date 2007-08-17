#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2003-2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007 Sylvain Taverne <sylvain@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the Standard Library
from optparse import OptionParser
import sys
import zipfile
# Import from itools
import itools
from itools.handlers import get_handler
from itools.gettext import PO
import itools.html
import itools.stl
import itools.odf



if __name__ == '__main__':
    version = 'itools %s' % itools.__version__
    description = ('Builds a new file from the given source file, but'
                   ' replacing the translatable messages by the'
                   ' translations found in the PO file.')
    parser = OptionParser('%prog <source file> <PO file>',
                          version=version, description=description)

    parser.add_option('-o', '--output',
                      help="The output will be written to the given file,"
                           " instead of printed to the standard output.")

    options, args = parser.parse_args()

    if len(args) != 2:
        parser.error('incorrect number of arguments')

    if options.output is None:
        output = sys.stdout
    else:
        output = open(options.output, 'w')

    try:
        source, po = args
        if zipfile.is_zipfile(source) and options.output is None:
            parser.error('The option -o is needed\n')

        handler = get_handler(source)
        try:
            # Extract the messages
            po = get_handler(po)
            output.write(handler.translate(po))
        except:
            parser.error('The file "%s" could not be processed\n' % filename)
    finally:
        if options.output is not None:
            output.close()
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

# Import from itools
import itools
from itools.handlers import get_handler
from itools.gettext import PO
import itools.html
import itools.stl
import itools.odf



if __name__ == '__main__':
    version = 'itools %s' % itools.__version__
    description = ('Extracts the translatable messages from the given source'
                   ' files. Builds a PO file with these messages, and prints'
                   ' to the standard output.')
    parser = OptionParser('%prog [OPTIONS] [<file>...]',
                          version=version, description=description)

    parser.add_option('-o', '--output',
                      help="The output will be written to the given file,"
                           " instead of printed to the standard output.")

    options, args = parser.parse_args()
    if len(args) == 0:
        parser.error('Needs at least one source file.')

    if options.output is None:
        output = sys.stdout
    else:
        output = open(options.output, 'w')

    try:
        po = PO()
        for filename in args:
            handler = get_handler(filename)
            try:
                get_messages = handler.get_messages
            except AttributeError:
                sys.stderr.write('ERROR: The file "%s" could not be processed\n' % filename)
                continue
            # Extract the messages
            for msgid, line_number in get_messages():
                po.set_message(msgid, references={filename: [line_number]})

        # XXX Should omit the header?
        output.write(po.to_str())
    finally:
        if options.output is not None:
            output.close()
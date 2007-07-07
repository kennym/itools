# -*- coding: UTF-8 -*-
# Copyright (C) 2005 J. David Ibáñez <jdavid@itaapy.com>
# Copyright (C) 2005 Luis A. Belmar Letelier <luis@itaapy.com>
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
import compiler

# Import from itools
from text import Text
from registry import register_handler_class


class VisitorUnicode(object):

    def __init__(self):
        self.messages = []


    def visitConst(self, const):
        if isinstance(const.value, unicode):
            self.messages.append((const.value, const.lineno))



class Python(Text):

    class_mimetypes = ['text/x-python']
    class_extension = 'py'


    def new(self, **kw):
        Text.new(self, **kw)


    def _load_state_from_file(self, file):
        Text._load_state_from_file(self, file)


    #########################################################################
    # API
    #########################################################################
    def get_messages(self):
        ast = compiler.parse(self.to_str())
        visitor = VisitorUnicode()
        compiler.walk(ast, visitor)
        return visitor.messages


register_handler_class(Python)

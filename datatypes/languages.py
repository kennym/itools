# -*- coding: UTF-8 -*-
# Copyright (C) 2005 Nicolas Oyez <nicoyez@gmail.com>
# Copyright (C) 2005-2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
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

# Import from itools
from base import DataType


class LanguageTag(DataType):

    @staticmethod
    def decode(value):
        res = value.split('-', 1)
        if len(res) < 2:
            return (res[0].lower(), None)
        else:
            return (res[0].lower(), res[1].upper())


    @staticmethod
    def encode(value):
        language, locality = value
        if locality is None:
            return language.lower()
        return '%s-%s' % (language.lower(), locality.upper())
##        return '-'.join([i for i in value if i != None])


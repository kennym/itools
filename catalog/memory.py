# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

"""
Implements a catalog in memory.
"""

# Import from itools
from fields import get_field


# TODO Refactor this code with the rest of itools.catalog


class Index(dict):

    def _normalise_word(self, word):
        # XXX temporary until we analyse as the catalog does
        if word is None:
            return None
        elif isinstance(word, bool):
            word = unicode(int(word))
        elif not isinstance(word, basestring):
            word = unicode(word)
        elif isinstance(word, unicode):
            word = word.lower()

        return word


    def search_word(self, word):
        word = self._normalise_word(word)

        if word in self:
            return self[word].copy()

        return {}


    def search_range(self, left, right):
        left = self._normalise_word(left)
        right = self._normalise_word(right)

        rows = {}

        if not left:
            for key in self.keys():
                if  key < right:
                    for number in self[key]:
                        rows[number] = rows.get(number, 0) + 1
        elif not right:
            for key in self.keys():
                if left <= key:
                    for number in self[key]:
                        rows[number] = rows.get(number, 0) + 1
        else:
            for key in self.keys():
                if left <= key < right:
                    for number in self[key]:
                        rows[number] = rows.get(number, 0) + 1

        return rows



class MemoryCatalog(object):

    __slots__ = ['indexes', 'analysers']

    def __init__(self):
        self.indexes = {}
        self.analysers = {}


    def add_index(self, name, analyser_name):
        self.indexes[name] = Index()
        self.analysers[name] = get_field(analyser_name)


    def index_document(self, document, number):
        for name in self.indexes:
            index = self.indexes[name]
            analyser = self.analysers[name]

            value = document.get_value(name)
            for word, position in analyser.split(value):
                index.setdefault(word, {})
                index[word].setdefault(number, [])
                index[word][number].append(position)


    def unindex_document(self, document, number):
        for name in self.indexes:
            index = self.indexes[name]
            analyser = self.analysers[name]

            value = document.get_value(name)
            for word, position in analyser.split(value):
                del index[word][number]
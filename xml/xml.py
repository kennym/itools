# -*- coding: UTF-8 -*-
# Copyright (C) 2003-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007-2008 Sylvain Taverne <sylvain@itaapy.com>
# Copyright (C) 2008 David Versmisse <david.versmisse@itaapy.com>
# Copyright (C) 2008 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2008 Matthieu France <matthieu@itaapy.com>
# Copyright (C) 2008 Wynand Winterbach <wynand.winterbach@gmail.com>
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
from itools.datatypes import XMLAttribute, XMLContent
from namespaces import get_namespace, is_empty
from parser import START_ELEMENT, END_ELEMENT


# Serialize
def get_qname(tag_uri, tag_name):
    """Returns the fully qualified name.
    """
    if tag_uri is None:
        return tag_name
    prefix = get_namespace(tag_uri).prefix
    if prefix is None:
        return tag_name
    return '%s:%s' % (prefix, tag_name)


def get_attribute_qname(namespace, local_name):
    """Returns the fully qualified name"""
    if namespace is None:
        return local_name

    prefix = get_namespace(namespace).prefix
    if prefix is None:
        return local_name

    # Namespace declarations for the default namespace lack the local
    # name (e.g. xmlns="http://www.example.org"). Here 'xmlns' is always
    # the prefix, and there is not a local name. This an special case.
    if local_name is None:
        return prefix

    return '%s:%s' % (prefix, local_name)


def get_start_tag(value):
    tag_uri, tag_name, attributes = value
    s = '<%s' % get_qname(tag_uri, tag_name)
    # Output the attributes
    for attr_uri, attr_name in attributes:
        value = attributes[(attr_uri, attr_name)]
        qname = get_attribute_qname(attr_uri, attr_name)
        value = XMLAttribute.encode(value)
        s += ' %s="%s"' % (qname, value)
    # Close the start tag
    if is_empty(tag_uri, tag_name):
        return s + '/>'
    else:
        return s + '>'


def get_end_tag(tag_uri, tag_name):
    if is_empty(tag_uri, tag_name):
        return ''
    return '</%s>' % get_qname(tag_uri, tag_name)


def get_doctype(name, doctype):
    return '<!DOCTYPE %s %s>' % (name, doctype.to_str())


def stream_to_str_xmldecl(value):
    version, encoding, standalone = value
    if standalone is None:
        return '<?xml version="%s" encoding="%s"?>' % (version, encoding)
    else:
        return '<?xml version="%s" encoding="%s" standalone="%s"?>' % value


stream_to_str_map = (
    stream_to_str_xmldecl,             # XML_DECL
    lambda x: get_doctype(x[0], x[1]), # DOCUMENT_TYPE
    get_start_tag,                     # START_ELEMENT
    lambda x: get_end_tag(x[0], x[1]), # END_ELEMENT
    XMLContent.encode,                 # TEXT
    lambda x: '<!--%s-->' % x,         # COMMENT
    lambda x: '',                      # PI
    lambda x: '<![CDATA[%s]]>' % x)    # CDATA


def stream_to_str(stream, encoding='UTF-8', map=stream_to_str_map):
    return ''.join( map[x](y) for x, y, z in stream )



def find_end(events, start):
    """Receives a list of events and a position in the list of an start
    element.

    Returns the position in the list where the element ends.
    """
    c = 1
    n = len(events)
    i = start + 1
    while i < n:
        event, value, line = events[i]
        if event == START_ELEMENT:
            c += 1
        elif event == END_ELEMENT:
            c -= 1
            if c == 0:
                return i
        i = i + 1
    return None


def get_element(events, name):
    i = 0
    for event, value, line in events:
        if event == START_ELEMENT:
            if name == value[1]:
                return Element(events, i)
        i += 1
    return None


class Element(object):

    __slots__ = ['events', 'start', 'end']

    def __init__(self, events, start):
        self.events = events
        self.start = start
        self.end = find_end(events, start)


    def get_content_elements(self):
        events = self.events

        i = self.start + 1
        while i < self.end:
            yield events[i]
            i += 1


    def get_content(self, encoding='UTF-8'):
        return stream_to_str(self.get_content_elements())


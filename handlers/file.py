# -*- coding: UTF-8 -*-
# Copyright (C) 2003-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007 Henry Obein <henry@itaapy.com>
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
from copy import deepcopy
from cStringIO import StringIO
from datetime import datetime

# Import from itools
from itools.fs import vfs
from base import Handler
from registry import register_handler_class



class File(Handler):
    """This is the base handler class for any file handler. It is also used
    as the default handler class for any file resource that has not a more
    specific handler.

    The variables 'timestamp' and 'dirty' define the state of the file
    handler:

       timestamp/dirty => means...
       -------------------------------------
       None/None => not loaded (yet)
       None/<dt> => new
       <dt>/None => loaded, but not changed
       <dt>/<dt> => loaded, and changed

    """

    # By default handlers are not loaded
    timestamp = None
    dirty = None


    def __init__(self, key=None, string=None, database=None, **kw):
        if database is not None:
            self.database = database
        if key is None:
            self.reset()
            self.dirty = datetime.now()
            if string is not None:
                # A handler from a byte string
                self.load_state_from_string(string)
            else:
                # A handler from some input data
                self.new(**kw)
        else:
            self.key = self.database.fs.resolve_key(key)


    def reset(self):
        pass


    def new(self, data=''):
        self.data = data


    def __getattr__(self, name):
        # Not attached to a key or already loaded (should be correctly
        # initialized)
        if self.key is None or self.timestamp is not None:
            message = "'%s' object has no attribute '%s'"
            raise AttributeError, message % (self.__class__.__name__, name)

        # Load and try again
        self.load_state()
        return getattr(self, name)


    #########################################################################
    # Load / Save
    #########################################################################
    def _load_state_from_file(self, file):
        """Method to be overriden by sub-classes."""
        self.data = file.read()


    def load_state(self):
        fs = self.database.fs
        file = fs.open(self.key)
        self.reset()
        try:
            self._load_state_from_file(file)
        except Exception:
            self._clean_state()
            raise
        finally:
            file.close()

        self.timestamp = fs.get_mtime(self.key)
        self.dirty = None


    def load_state_from_uri(self, uri):
        file = vfs.open(uri)
        try:
            self.load_state_from_file(file)
        finally:
            file.close()


    def load_state_from_file(self, file):
        self.set_changed()
        self.reset()
        try:
            self._load_state_from_file(file)
        except Exception:
            self._clean_state()
            raise


    def load_state_from_string(self, string):
        file = StringIO(string)
        self.load_state_from_file(file)


    def save_state(self):
        file = self.safe_open(self.key, 'w')
        try:
            self.save_state_to_file(file)
        finally:
            file.close()
        # Update the timestamp
        self.timestamp = self.database.fs.get_mtime(self.key)
        self.dirty = None


    def save_state_to(self, key):
        # If there is an empty folder in the given key, remove it
        fs = self.database.fs if self.database is not None else vfs
        if fs.is_folder(key) and not fs.get_names(key):
            fs.remove(key)
        # Save the file
        file = self.safe_make_file(key)
        try:
            self.save_state_to_file(file)
        finally:
            file.close()


    def save_state_to_file(self, file):
        # We call "to_str" so this method will be good for sub-classes
        data = self.to_str()
        # Write and truncate (calls to "_save_state" must be done with the
        # pointer pointing to the beginning)
        file.write(data)
        file.truncate(file.tell())


    clone_exclude = frozenset(['database', 'key', 'timestamp', 'dirty'])
    def clone(self, cls=None):
        # Define the class to build
        if cls is None:
            cls = self.__class__
        elif not issubclass(cls, self.__class__):
            msg = 'the given class must be a subclass of the object'
            raise ValueError, msg

        # Load first, if needed
        if self.dirty is None:
            if self.key is not None and self.timestamp is None:
                self.load_state()

        # Copy the state
        copy = object.__new__(cls)
        copy.reset()
        for name in self.__dict__:
            if name not in cls.clone_exclude:
                value = getattr(self, name)
                value = deepcopy(value)
                setattr(copy, name, value)
        copy.dirty = datetime.now()
        return copy


    def is_outdated(self):
        if self.key is None:
            return False

        timestamp = self.timestamp
        # It cannot be out-of-date if it has not been loaded yet
        if timestamp is None:
            return False

        mtime = self.database.fs.get_mtime(self.key)
        # If the resource layer does not support mtime... we are...
        if mtime is None:
            return True

        return mtime > timestamp


    def set_changed(self):
        # Invalid handler
        if self.key is None and self.dirty is None:
            raise RuntimeError, 'cannot change an orphaned file handler'

        # Free handler (not attached to a database)
        if self.database is None:
            self.dirty = datetime.now()
            return

        # Phantoms
        database = self.database
        if database.is_phantom(self):
            database.cache[self.key] = self
            database.handlers_new2old[self.key] = None
            return

        # Check nothing weird happened
        if self.key is None or database.cache.get(self.key) is not self:
            raise RuntimeError, 'database inconsistency!'

        # Update database state
        if self.timestamp:
            # Case 1: loaded
            self.dirty = datetime.now()
            database.handlers_new2old[self.key] = self.key
            database.handlers_old2new[self.key] = self.key
        elif self.dirty:
            # Case 2: new
            database.handlers_new2old[self.key] = None
        else:
            # Case 3: not loaded (yet)
            self.load_state()
            self.dirty = datetime.now()
            database.handlers_new2old[self.key] = self.key
            database.handlers_old2new[self.key] = self.key


    def _clean_state(self):
        names = [ x for x in self.__dict__ if x not in ('database', 'key') ]
        for name in names:
            delattr(self, name)


    def abort_changes(self):
        # Not attached to a key or not changed
        if self.key is None or self.dirty is None:
            return
        # Abort
        self._clean_state()


    #########################################################################
    # API
    #########################################################################
    def get_mtime(self):
        """Returns the last modification time.
        """
        # Modified or new handler
        if self.dirty is not None:
            return self.dirty

        # Loaded but not modified
        if self.timestamp is not None:
            return self.timestamp

        # Not yet loaded, check the FS
        return self.database.fs.get_mtime(self.key)


    def to_str(self):
        return self.data


    def set_data(self, data):
        self.set_changed()
        self.data = data


    def to_text(self):
        raise NotImplementedError


    def is_empty(self):
        raise NotImplementedError



register_handler_class(File)

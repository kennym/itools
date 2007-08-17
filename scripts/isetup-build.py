#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2006 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2006-2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
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
from datetime import datetime
from optparse import OptionParser
import os
import sys

# Import from itools
import itools
from itools.uri import Path
from itools import vfs
from itools.handlers import Config, get_handler
import itools.gettext
from itools.xhtml import Document
import itools.stl



def get_commit_metadata(reference):
    lines = os.popen('git-cat-file commit %s' % reference).readlines()
    # The commit id
    commit_id = lines[0].strip().split()[1]
    # The author
    for line in lines:
        if line.startswith('author'):
            author = line
            break
    else:
        raise ValueError, ("cannot find the commit author, "
            "please report the output of 'git-cat-file commit %s'" % reference)
    # The timestamp
    timestamp = datetime.fromtimestamp(int(author.strip().split()[-2]))

    return commit_id, timestamp



def get_version():
    # Find out the current branch
    for line in os.popen('git-branch').readlines():
        if line.startswith('*'):
            branch_name = line[2:-1]
            break
    else:
        return None

    # Look for tags
    cmd = 'git-ls-remote -t . %s*' % branch_name
    tags = [ x.strip().split('/')[-1] for x in os.popen(cmd).readlines() ]

    # And the version name is...
    if tags:
        # Sort so "0.13.10" > "0.13.9"
        key = lambda tag: tuple([ int(x) for x in tag.split('.')])
        tags.sort(key=key)
        # Get the version name
        version_name = tags[-1]
    else:
        version_name = branch_name

    # Get the timestamp
    head_id, head_timestamp = get_commit_metadata('HEAD')
    tag_id, tag_timestamp = get_commit_metadata(version_name)

    if not tags or tag_id != head_id:
        timestamp = head_timestamp.strftime('%Y%m%d%H%M')
        return '%s-%s' % (version_name, timestamp)

    return version_name



if __name__ == '__main__':
    # The command line parser
    version = 'itools %s' % itools.__version__
    description = ('Builds the package.')
    parser = OptionParser('%prog', version=version, description=description)

    options, args = parser.parse_args()
    if len(args) != 0:
        parser.error('incorrect number of arguments')

    # Try using git facilities
    git_available = bool(os.popen('git-branch').read())
    if not git_available:
        print "Warning: not using git."

    # Read configuration for languages
    config = Config('setup.conf')
    source_language = config.get_value('source_language', default='en')
    target_languages = config.get_value('target_languages', default='').split()

    # Initialize the list of files to install (the MANIFEST)
    manifest = ['MANIFEST']
    if git_available:
        cmd = 'git-ls-files'
    else:
        cmd = ('find -type f|grep -Ev "^./(build|dist)"'
               '|grep -Ev "*.(~|pyc|%s)"' % '|'.join(target_languages))
    for path in os.popen(cmd).readlines():
        path = path.strip()
        if not os.path.islink(path):
            manifest.append(path)

    # Build MO files
    print '(1) Compiling message catalogs:',
    sys.stdout.flush()
    for language in [source_language] + target_languages:
        print language,
        sys.stdout.flush()
        os.system('msgfmt locale/%s.po -o locale/%s.mo' % (language, language))
        # Add to the manifest
        manifest.append('locale/%s.mo' % language)
    print 'OK'

    # Load message catalogs
    message_catalogs = {}
    for language in target_languages:
        path = 'locale/%s.po' % language
        message_catalogs[language] = (get_handler(path), vfs.get_mtime(path))

    # Build the templates in the target languages
    print '(2) Building XHTML files',
    sys.stdout.flush()
    # XXX The directory "cms/skeleton" is specific to itools, should not be
    # hardcoded.
    cmd = 'find -name "*.x*ml.%s"| grep -Ev "^./(build|dist|cms/skeleton)"'
    for path in os.popen(cmd % source_language).readlines():
        # Load the handler
        path = path.strip()
        src_mtime = vfs.get_mtime(path)
        src = Document(path)
        done = False
        # Build the translation
        n = path.rfind('.')
        for language in target_languages:
            po, po_mtime = message_catalogs[language]
            dst = '%s.%s' % (path[:n], language)
            # Add to the manifest
            manifest.append(dst[2:])
            # Skip the file if it is already up-to-date
            if vfs.exists(dst):
                dst_mtime = vfs.get_mtime(dst)
                if dst_mtime > src_mtime and dst_mtime > po_mtime:
                    continue
            try:
                data = src.translate(po)
            except:
                print 'Error with file "%s"' % path
                raise
            open(dst, 'w').write(data)
            done = True
        # Done
        if done is True:
            sys.stdout.write('*')
        else:
            sys.stdout.write('.')
        sys.stdout.flush()
    print ' OK'

    # Find out the version string
    manifest.append('version.txt')
    if git_available:
        print '(3) Find out the version string',
        sys.stdout.flush()
        version = get_version()
        open('version.txt', 'w').write(version)
        print 'OK'

    # Build the manifest file
    print '(4) Building list of files to install',
    sys.stdout.flush()
    manifest.sort()
    open('MANIFEST', 'w').write('\n'.join(manifest))
    print 'OK'
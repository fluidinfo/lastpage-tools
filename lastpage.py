#!/usr/bin/env python

"""
A command line utility for working with LastPage (see http://lastpage.me).
Run with --help for brief help.

Released into the public domain on August 2nd, 2011 by Fluidinfo Inc.
"""

import re
import sys
import time
import optparse
from datetime import datetime
from subprocess import Popen
from fom.session import Fluid

defaultUser = None
defaultPassword = None


def deleteTag(fi, tag):
    """
    Delete all instances of the tag C{tag} from Fluidinfo.

    @param fi: a C{Fluid} instance.
    @param tag: the tag to use.
    """
    fdb.values.delete('has %s' % tag, [tag])


def getTag(fi, tag):
    """
    Get all instances of the tag C{tag} from Fluidinfo.

    @param fi: a C{Fluid} instance.
    @param tag: the tag to use.
    """
    urls = []
    response = fdb.values.get('has %s' % tag, [u'fluiddb/about'])
    for obj in response.value['results']['id'].values():
        urls.append(obj['fluiddb/about']['value'])
    return urls


def setTag(fi, tag, url):
    """
    Put a tag C{tag} on the Fluidinfo object about C{url}.

    @param fi: a C{Fluid} instance.
    @param tag: the tag to use.
    @param url: The url indicating which object to put the tag onto.
    """
    now = int(time.mktime(datetime.utcnow().timetuple()))
    fdb.about[url][tag].put(now)


def browse(url):
    """
    Open the user's browser on C{url}.

    @param url: The url to open.
    """
    if sys.platform.startswith('linux'):
        opener = '/usr/bin/xdg-open'
    elif sys.platform == 'darwin':
        opener = '/usr/bin/open'
    try:
        Popen([opener, url])
    except NameError:
        print >>sys.stderr, (
            "Sorry, I don't know how to open pages on %s systems." %
            sys.platform)


if __name__ == '__main__':
    opts = optparse.OptionParser()
    opts.add_option('--user',
                    action='store',
                    type='string',
                    default=defaultUser,
                    help='The Fluidinfo username (default %default).')
    opts.add_option('--password',
                    action='store',
                    type='string',
                    default=defaultPassword,
                    help="The Fluidinfo user's password (default %default).")
    opts.add_option('-c', '--custom',
                    action='store',
                    type='string',
                    default='',
                    help="A custom suffix for the lastpage URL.")
    opts.add_option('-u', '--url',
                    action='store',
                    type='string',
                    default='',
                    dest='url',
                    help="The URL to store (default none).")
    opts.add_option('-d', '--delete',
                    action='store_true',
                    default=False,
                    help='If True, delete the tag (default %default).')
    opts.add_option('-s', '--show',
                    action='store_true',
                    default=False,
                    help='If True, print the current URL (default %default).')
    opts.add_option('-o', '--open',
                    action='store_true',
                    default=False,
                    help='If True, open the current URL (default %default).')

    args, opt = opts.parse_args()

    # Check that any custom URL suffix is legal as a Fluidinfo tag name.
    if args.custom:
        if not re.match('^[\:\.\-\w/]+$', args.custom, re.UNICODE):
            print >>sys.stderr, ('Custom suffixes can only contain letters, '
                                 'digits, dot, hyphen, colon, and slash.')
            sys.exit(1)
        args.custom = '-' + args.custom.replace('/', '-')

    # Get an instance of fom.session.Fluid and provide it with credentials,
    # if we have been given a password to use.
    fdb = Fluid()
    if args.password:
        if not args.user:
            print >>sys.stderr, 'Please use --user USERNAME.'
            sys.exit(1)
        if not args.password:
            print >>sys.stderr, 'Please use --password PASSWORD.'
            sys.exit(1)
        fdb.login(args.user, args.password)

    # The Fluidinfo tag that will be acted on.
    tag = '%s/lastpage%s' % (args.user, args.custom)

    # Prepend 'http://' if it looks like we can be helpful.
    if args.url and not args.url.startswith('http'):
        args.url = 'http://' + args.url

    if args.url:
        # Set the tag on the Fluidinfo object about url.
        deleteTag(fdb, tag)
        setTag(fdb, tag, args.url)
    elif args.delete:
        # Delete all instances of the tag.
        deleteTag(fdb, tag)
    elif args.show:
        # Print all instances of the tag.
        for url in getTag(fdb, tag):
            print url
    elif args.open:
        # Browse to the URL, if there's just one.
        urls = getTag(fdb, tag)
        nurls = len(urls)
        if nurls == 0:
            print 'Tag %s currently does not point to any URL.'
        elif nurls == 1:
            url = urls[0]
            if url.startswith('http'):
                browse(url)
            else:
                print 'Value %s does not look like a URL.' % url
        else:
            print 'Multiple values of %s are set:' % tag
            for url in urls:
                print url

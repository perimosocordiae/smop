# SMOP compiler -- Simple Matlab/Octave to Python compiler
# Copyright 2011-2013 Victor Leikehman

import sys
import os
import re
from optparse import OptionParser
import parse
import resolve
import rewrite
import backend  # this adds the _backend function to all nodes

version = '0.23'


def parse_options():
    op = OptionParser(description='SMOP compiler version %s' % version,
                      usage='Usage: %prog [options] file-list')
    op.add_option('-o', '--output', type=str, default='-', metavar='FILENAME',
                  help='Output file name. Defaults to stdout')
    op.add_option('-X', '--exclude', type=str, default='', metavar='FILES',
                  help='Ignore files listed in comma-separated list FILES')
    op.add_option('--version', action='store_true', help='Show version and exit')
    op.add_option('--no-comments', action='store_false', dest='with_comments',
                  default=True, help='Strip comments')
    op.add_option('--resolve', action='store_true', dest='do_resolve',
                  default=True, help='Apply the "resolve" pass [True]')
    op.add_option('--no-resolve', action='store_false', dest='do_resolve',
                  default=True)
    op.add_option('--rewrite', action='store_true', dest='do_rewrite',
                  default=False, help='Apply the "rewrite" pass [False]')
    op.add_option('--no-rewrite', action='store_false', dest='do_rewrite',
                  default=False)
    op.add_option('--typeof', action='store_true', dest='do_typeof',
                  default=False, help='Apply the "typeof" pass [False]')
    op.add_option('--no-typeof', action='store_false', dest='do_typeof',
                  default=False)
    op.add_option('--rename', action='store_true', dest='do_rename',
                  default=False, help='Apply the "rename" pass [False]')
    op.add_option('--no-rename', action='store_false', dest='do_rename',
                  default=False)
    opts, args = op.parse_args()

    if opts.version:
        print "SMOP compiler version %s" % version
        sys.exit()
    return opts, args


def translate_file(filename, with_comments=True, do_resolve=True,
                   do_rename=False, do_typeof=False, do_rewrite=False):
    buf = open(filename).read()

    # move each comment alone on a line
    # to avoid errors by trailing comment
    # and minimally change parsing rules
    buf = re.sub("%+", "\n %", buf)
    # ensure the last char is a newline
    if buf[-1] != '\n':
        buf += '\n'

    func_list = parse.parse(buf, with_comments)
    symtab = {}

    for func_obj in func_list:
        if do_typeof:
            symtab[func_obj.head.ident.name] = func_obj
        if do_resolve:
            resolve.resolve(func_obj)
        if do_rename:
            resolve.rename(func_obj)

    if do_typeof:
        for func_obj in func_list:
            func_obj.apply([], symtab)

    if do_rewrite:
        for func_obj in func_list:
            rewrite.rewrite(func_obj)

    return '\n'.join(func_obj._backend() for func_obj in func_list)


def translate(input_files, opts):
    fp = open(opts.output, "w") if opts.output != "-" else sys.stdout
    print >> fp, "# Autogenerated with SMOP version %s" % version
    print >> fp, "# " + " ".join(sys.argv)
    print >> fp, "from __future__ import division"
    print >> fp, "import numpy as np"
    print >> fp, "from scipy.io import loadmat,savemat"
    print >> fp, "import os\n"

    for filename in input_files:
        print >>sys.stderr, "Processing file: '%s'" % filename
        print >>fp, translate_file(filename, opts.with_comments,
                                   opts.do_resolve, opts.do_rename,
                                   opts.do_typeof, opts.do_rewrite)


def main():
    opts, args = parse_options()
    exclude_list = set(opts.exclude.split(','))

    input_files = []
    for filename in args:
        if not filename.endswith(".m"):
            print >>sys.stderr, "Ignored file: '%s'" % filename
        elif os.path.basename(filename) in exclude_list:
            print >>sys.stderr, "Excluded file: '%s'" % filename
        else:
            input_files.append(filename)

    if not input_files:
        print >>sys.stderr, "No files to translate."
        sys.exit()

    translate(input_files, opts)

if __name__ == "__main__":
    main()

# SMOP compiler -- Simple Matlab/Octave to Python compiler
# Copyright 2011-2013 Victor Leikehman

import sys
import glob
import os
import re
from optparse import OptionParser
import parse
import resolve
import backend
import rewrite

version = '0.23'


def main():
    op = OptionParser(description='SMOP compiler version %s' % version,
                      usage='Usage: %prog [options] file-list')
    op.add_option(
        '-o', '--output', type=str, default='a.py', metavar='FILENAME',
        help='By default create file named a.py, use - for stdout')
    op.add_option('-X', '--exclude', type=str, default='', metavar='FILES',
                  help='Ignore files listed in comma-separated list FILES')
    op.add_option('--strict', action='store_true',
                  help='Stop on the first error')
    op.add_option('--verbose', action='store_true')
    op.add_option('--version', action='store_true')
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
    opts, args = op.parse_args()

    if opts.version:
        print "SMOP compiler version 0.23"
        sys.exit()

    exclude_list = opts.exclude.split(',')

    fp = open(opts.output, "w") if opts.output != "-" else sys.stdout
    print >> fp, "# Autogenerated with SMOP version %s" % version
    print >> fp, "# " + " ".join(sys.argv)
    print >> fp, "from __future__ import division"
    print >> fp, "import numpy as np"
    print >> fp, "from scipy.io import loadmat,savemat"
    print >> fp, "import os\n"

    for pattern in args:
        for filename in glob.glob(os.path.expanduser(pattern)):
            if not filename.endswith(".m"):
                print "\tIngored file: '%s'" % filename
                continue
            if os.path.basename(filename) in exclude_list:
                print "\tExcluded file: '%s'" % filename
                continue
            print filename
            buf = open(filename).read()

            # move each comment alone on a line
            # to avoid errors by trailing comment
            # and minimally change parsing rules
            buf = re.sub("%", "\n %", buf)

            func_list = parse.parse(buf if buf[-1] == '\n' else buf + '\n',
                                    opts.with_comments)

            try:
                symtab = {}
                for func_obj in func_list:
                    try:
                        func_name = func_obj.head.ident.name
                        symtab[func_name] = func_obj
                        print "\t", func_name
                    except AttributeError:
                        if opts.verbose:
                            print "\tJunk ignored"
                        if opts.strict:
                            return
                        continue
                    if opts.do_resolve:
                        resolve.resolve(func_obj)

                if opts.do_typeof:
                    for func_obj in func_list:
                        func_obj.apply([], symtab)

                if opts.do_rewrite:
                    for func_obj in func_list:
                        rewrite.rewrite(func_obj)

                for func_obj in func_list:
                    s = backend.backend(func_obj)
                    print >> fp, s
            except Exception as ex:
                print repr(ex)
                if opts.strict:
                    return


if __name__ == "__main__":
    main()

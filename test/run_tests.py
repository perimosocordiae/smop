import sys
import os
import difflib
from glob import glob

# Hack smop into the path
this_file = os.path.realpath(__file__)
test_dir = os.path.dirname(this_file)
sys.path.insert(0, os.path.join(test_dir, '..'))
from smop.main import translate_file


def main():
  test_files = [name[:-3] for name in glob(test_dir+'/*.py') if name != this_file]
  for test in test_files:
    smop_out = translate_file(test+'.m').splitlines()
    expected_out = open(test+'.py').read().splitlines()
    diff = list(difflib.unified_diff(expected_out, smop_out, fromfile='expected', tofile='actual', n=0, lineterm=''))
    print 'test "%s":' % os.path.basename(test),
    if diff:
      print 'failed'
      for line in diff:
        print line
    else:
      print 'ok'


if __name__ == '__main__':
  main()

#!/usr/bin/env python2.7
import re
import sys


diff_re = re.compile(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@')

def parse_patch(patch):
    base = set()
    head = set()
    base_lineno = 1
    head_lineno = 1

    for line in patch.splitlines():
        diff_m = diff_re.match(line)
        if diff_m:
            base_lineno = int(diff_m.group(1))
            head_lineno = int(diff_m.group(3))
        else:
            if line.startswith('+'):
                head.add(head_lineno)
                head_lineno += 1
            elif line.startswith('-'):
                base.add(base_lineno)
                base_lineno += 1
            else:
                base_lineno += 1
                head_lineno += 1
    return base, head

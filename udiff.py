#!/usr/bin/env python2.7
import collections
import re
import sys


diff_re = re.compile(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@')

def parse_patch(patch):
    base = set()
    head = set()
    changes = []
    change = None

    for line in patch.splitlines():
        diff_m = diff_re.match(line)
        if diff_m:
            base_lineno = int(diff_m.group(1))
            head_lineno = int(diff_m.group(3))
        else:
            if line.startswith('-'):
                if change is None:
                    change = []
                    changes.append(change)
                base.add(base_lineno)
                change.append((False, base_lineno, head_lineno))

                base_lineno += 1
            elif line.startswith('+'):
                if change is None:
                    change = []
                    changes.append(change)
                head.add(head_lineno)
                change.append((True, base_lineno, head_lineno))

                head_lineno += 1
            else:
                change = None
                base_lineno += 1
                head_lineno += 1

    base_alt = collections.defaultdict(int)
    head_alt = collections.defaultdict(int)
    for change in changes:
        base_change = filter(lambda n: n[0], change) 
        head_change = filter(lambda n: not n[0], change)
        blanks = len(base_change) - len(head_change)
        if blanks > 0:
            lineno = sorted(change, key=lambda t: t[1], reverse=True)[0][1]
            base_alt[lineno] = blanks
        elif blanks < 0:
            lineno = sorted(change, key=lambda t: t[2])[0][2]
            head_alt[lineno - blanks] = -blanks

    return base, head, base_alt, head_alt

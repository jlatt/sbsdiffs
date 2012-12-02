#!/usr/bin/env python2.7
import collections
import re
import sys


diff_re = re.compile(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@')

Hunk = collections.namedtuple('Hunk', ('is_add', 'base_lineno', 'head_lineno'))

def parse_patch(patch):
    changes = []
    change = None
    for line in patch.splitlines():
        diff_m = diff_re.match(line)
        if diff_m:
            # start a new anchor in a group of hunka
            base_lineno = int(diff_m.group(1))
            head_lineno = int(diff_m.group(3))
        else:
            is_del = line.startswith('-')
            is_add = line.startswith('+')
            is_reg = not (is_del or is_add)
            if is_del or is_add:
                if change is None:
                    change = []
                    changes.append(change)

                change.append(Hunk(is_add, base_lineno, head_lineno))

            if is_reg or is_del:
                base_lineno += 1

            if is_reg or is_add:
                head_lineno += 1

            if is_reg:
                # start a new hunk group
                change = None

    base = set()
    head = set()
    base_alt = collections.defaultdict(int)
    head_alt = collections.defaultdict(int)
    for change in changes:
        base_change = [hunk for hunk in change if not hunk.is_add]
        head_change = [hunk for hunk in change if     hunk.is_add]

        base |= set(hunk.base_lineno for hunk in base_change)
        head |= set(hunk.head_lineno for hunk in head_change)

        blanks = len(head_change) - len(base_change)
        if blanks > 0:
            lineno = sorted(change, key=lambda t: t.base_lineno, reverse=True)[0].base_lineno
            base_alt[lineno] = blanks
        elif blanks < 0:
            lineno = sorted(change, key=lambda t: t.head_lineno, reverse=True)[0].head_lineno
            head_alt[lineno] = -blanks

    return base, head, base_alt, head_alt

#!/usr/bin/env python3
"""Inventory of every page: geometry of the block, number of lines."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import page as PG

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    out = {}
    for n in range(lo, hi + 1):
        try:
            b = PG.block(n)
            ls = b.pop('lines', [])
            b['line_boxes'] = [[l['y0'], l['y1'], l['x0'], l['x1']] for l in ls]
        except Exception as e:
            b = {'leaf': n, 'error': str(e)}
        out[n] = b
        print(n, b.get('n_lines'), b.get('just_mm'), b.get('step_px'), flush=True)
    with open(os.path.join(P, 'tools', 'inv_%d_%d.json' % (lo, hi)), 'w') as fh:
        json.dump(out, fh)

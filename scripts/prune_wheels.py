#!/usr/bin/env python3
"""Prune wheels in dist/ to only keep those whose METADATA Version matches
the selected version passed via the SELECTED_VER environment variable.

This helper is used by the GitHub Actions workflow to robustly remove
unrelated wheel files before publishing.
"""
import os
import zipfile
import sys


def main():
    ver = os.environ.get('SELECTED_VER') or os.environ.get('UI_ENGINE_VERSION')
    if not ver:
        print('ERROR: SELECTED_VER or UI_ENGINE_VERSION must be set', file=sys.stderr)
        sys.exit(2)

    print('Pruning wheels to only keep version:', ver)
    if not os.path.isdir('dist'):
        print('dist/ not found; nothing to do')
        return

    for fname in os.listdir('dist'):
        if not fname.endswith('.whl'):
            continue
        path = os.path.join('dist', fname)
        try:
            with zipfile.ZipFile(path) as z:
                metas = [n for n in z.namelist() if n.endswith('METADATA')]
                if not metas:
                    print('No METADATA for', fname, '-> removing')
                    os.remove(path)
                    continue
                meta = z.read(metas[0]).decode(errors='ignore')
                published = next(
                    (
                        line.split(':', 1)[1].strip()
                        for line in meta.splitlines()
                        if line.startswith('Version:')
                    ),
                    None,
                )
                if published != ver:
                    print('Wheel', fname, 'has version', published, '-> removing')
                    os.remove(path)
                else:
                    print('Keeping wheel', fname)
        except Exception as exc:
            print('Error reading', fname, exc)
            try:
                os.remove(path)
            except Exception:
                pass


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
import argparse
import contextlib
import sys

import toml
from cleo.io.outputs.buffered_output import BufferedOutput
from poetry.console.application import Application as PoetryApplication


@contextlib.contextmanager
def ch_argv(args):
    old_argv = sys.argv.copy()
    sys.argv = args
    try:
        yield
    finally:
        sys.argv = old_argv


def parse_toml():
    with open("pyproject.toml", "r", encoding="utf8") as fh:
        data = toml.load(fh)
    deps = data["tool"]["poetry"]["dependencies"]
    # deps.update(data["tool"]["poetry"]["group"]["dev"]["dependencies"])
    return deps


def poetry_check_lock():
    with ch_argv(["poetry", "lock", "--check", "-q"]):
        app = PoetryApplication()
        app.catch_exceptions(False)
        app.auto_exits(False)
        return not bool(app.run())


def poetry_export():
    with ch_argv(["poetry", "export", "--format", "requirements.txt", "--without-hashes"]):
        out = BufferedOutput()
        app = PoetryApplication()
        app.catch_exceptions(False)
        app.auto_exits(False)
        app.run(output=out)
        return out.fetch()


def main():
    parser = argparse.ArgumentParser(
        description="poetry pre-commit hook",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--check", action="store_true", help="check lock file", default=True)
    parser.add_argument(
        "--export",
        help="export requirements.txt location",
        default="src/requirements.txt",
    )
    args = parser.parse_args()
    if args.check and not poetry_check_lock():
        print("Poetry lock is not up to date")
        sys.exit(1)
    if args.export.strip() != "":
        depends = parse_toml()
        preqs = poetry_export()
        with open(args.export, "w", encoding="utf8") as f:
            for line in preqs.splitlines(True):
                if line.startswith(tuple(depends.keys())):
                    f.write(line)


if __name__ == "__main__":
    main()

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
    extras = (data["tool"]["poetry"]).get("extras", {})
    return deps, list(extras.keys())


def poetry_check_lock():
    with ch_argv(["poetry", "lock", "--check", "-q"]):
        app = PoetryApplication()
        app.catch_exceptions(False)
        app.auto_exits(False)
        return not bool(app.run())


def poetry_export(extras=None):
    args = ["poetry", "export", "--format", "requirements.txt", "--without-hashes"]
    for extra in extras:
        args.append("-E")
        args.append(extra)
    with ch_argv(args):
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
    parser.add_argument("--no-check", action="store_true", help="check lock file", default=False)
    parser.add_argument(
        "--export",
        help="export requirements.txt location",
        default="src/requirements.txt",
    )
    args = parser.parse_args()
    if not args.no_check and not poetry_check_lock():
        print("Poetry lock is not up to date")
        sys.exit(1)
    if args.export.strip() != "":
        depends, extras = parse_toml()
        preqs = poetry_export(extras)
        with open(args.export, "w", encoding="utf8") as f:
            for line in preqs.splitlines(True):
                if line.split("==")[0] in depends:
                    f.write(line)


if __name__ == "__main__":
    main()

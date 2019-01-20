#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import click
import subprocess


def run(cmd):
    click.echo("RUN: %s" % cmd)
    return subprocess.check_call(cmd, shell=True)


def run_path(cmd):
    return run("%s %s" % (sys.executable, cmd))


def run_module(cmd):
    return run("%s -m %s" % (sys.executable, cmd))


@click.group()
def main():
    """Execute CI actions"""

    pass


@main.command()
@click.option(
    "-e",
    "--env",
    multiple=True,
    default=["default"],
    type=click.Choice(["default", "mypy", "flake8"]),
)
def test(env):
    """Test the project
    """
    envs = env
    for env in envs:
        if env == "default":
            run_module("pip install -r./requirements_dev.txt")
            run_module("pip install -r./requirements.txt")
            run_path("setup.py test")
        elif env == "mypy":
            run_module("pip install mypy")
            run_module("mypy -m pywinio --ignore-missing-imports")
        elif env == "flake8":
            run_module("pip install flake8")
            run_module("flake8 pywinio tests")


@main.command()
def pack():
    """Build distructbution
    """

    run_path("setup.py sdist --formats=zip")


@main.command()
@click.pass_context
def deploy(ctx):
    """Deploy this project"""

    ctx.invoke(pack)
    run_module("pip install twine")
    run_module("twine upload dist/*")


if __name__ == "__main__":
    main()

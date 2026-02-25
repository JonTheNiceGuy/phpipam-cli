import json

import click

from ipam.client import PhpIpamClient
from ipam.config import load_profile


pass_client = click.make_pass_decorator(PhpIpamClient)


def get_client(ctx: click.Context | None = None) -> PhpIpamClient:
    if ctx is None:
        ctx = click.get_current_context()
    return ctx.obj


def format_output(data: dict | list) -> str:
    return json.dumps(data, indent=2)

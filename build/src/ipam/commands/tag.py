import click

from ipam.helpers import get_client, format_output


@click.group("tag")
def tag():
    """Manage IP address tags."""


@tag.command("list")
@click.pass_context
def tag_list(ctx):
    """List all tags."""
    client = get_client(ctx)
    data = client.get("tools/tags")
    if not data:
        click.echo("No tags found.")
        return
    data.sort(key=lambda t: t.get("type", "").lower())
    for t in data:
        click.echo(
            f"{t['id']:>4}  {t.get('type', ''):<20}  "
            f"bg={t.get('bgcolor', '')}  fg={t.get('fgcolor', '')}"
        )


@tag.command("show")
@click.argument("tag_id")
@click.pass_context
def tag_show(ctx, tag_id):
    """Show details of a tag."""
    client = get_client(ctx)
    data = client.get("tools/tags", tag_id)
    click.echo(format_output(data))


@tag.command("add")
@click.option("--type", "tag_type", required=True, help="Tag type name")
@click.option("--bgcolor", default="#000", help="Background colour")
@click.option("--fgcolor", default="#fff", help="Foreground colour")
@click.option("--compress", default=None, help="Compress (Yes/No)")
@click.option("--locked", default=None, help="Locked (Yes/No)")
@click.pass_context
def tag_add(ctx, tag_type, bgcolor, fgcolor, compress, locked):
    """Add a new tag."""
    client = get_client(ctx)
    payload = {"type": tag_type, "bgcolor": bgcolor, "fgcolor": fgcolor}
    if compress is not None:
        payload["compress"] = compress
    if locked is not None:
        payload["locked"] = locked
    result = client.post("tools/tags", data=payload)
    click.echo(f"Tag created (id: {result['id']})")


@tag.command("update")
@click.argument("tag_id")
@click.option("--type", "tag_type", default=None, help="Tag type name")
@click.option("--bgcolor", default=None, help="Background colour")
@click.option("--fgcolor", default=None, help="Foreground colour")
@click.option("--compress", default=None, help="Compress (Yes/No)")
@click.option("--locked", default=None, help="Locked (Yes/No)")
@click.pass_context
def tag_update(ctx, tag_id, tag_type, bgcolor, fgcolor, compress, locked):
    """Update a tag."""
    client = get_client(ctx)
    payload = {}
    if tag_type is not None:
        payload["type"] = tag_type
    if bgcolor is not None:
        payload["bgcolor"] = bgcolor
    if fgcolor is not None:
        payload["fgcolor"] = fgcolor
    if compress is not None:
        payload["compress"] = compress
    if locked is not None:
        payload["locked"] = locked
    client.patch("tools/tags", int(tag_id), data=payload)
    click.echo("Tag updated.")


@tag.command("delete")
@click.argument("tag_id")
@click.pass_context
def tag_delete(ctx, tag_id):
    """Delete a tag."""
    client = get_client(ctx)
    client.delete("tools/tags", int(tag_id))
    click.echo("Tag deleted.")

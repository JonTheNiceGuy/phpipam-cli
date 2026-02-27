import click

from ipam.helpers import get_client, format_output


@click.group("l2domain")
def l2domain():
    """Manage L2 domains."""


@l2domain.command("list")
@click.pass_context
def l2domain_list(ctx):
    """List all L2 domains."""
    client = get_client(ctx)
    data = client.get("l2domains")
    if not data:
        click.echo("No L2 domains found.")
        return
    data.sort(key=lambda d: d.get("name", "").lower())
    for d in data:
        click.echo(f"{d['id']:>4}  {d.get('name', ''):<30}  {d.get('description', '')}")


@l2domain.command("show")
@click.argument("l2domain_id")
@click.pass_context
def l2domain_show(ctx, l2domain_id):
    """Show details of an L2 domain."""
    client = get_client(ctx)
    data = client.get("l2domains", l2domain_id)
    click.echo(format_output(data))


@l2domain.command("add")
@click.option("--name", required=True, help="L2 domain name")
@click.option("--description", default="", help="Description")
@click.pass_context
def l2domain_add(ctx, name, description):
    """Add a new L2 domain."""
    client = get_client(ctx)
    payload = {"name": name, "description": description}
    result = client.post("l2domains", data=payload)
    click.echo(f"L2 domain created (id: {result['id']})")


@l2domain.command("update")
@click.argument("l2domain_id")
@click.option("--name", default=None, help="L2 domain name")
@click.option("--description", default=None, help="Description")
@click.pass_context
def l2domain_update(ctx, l2domain_id, name, description):
    """Update an L2 domain."""
    client = get_client(ctx)
    payload = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    client.patch("l2domains", int(l2domain_id), data=payload)
    click.echo("L2 domain updated.")


@l2domain.command("delete")
@click.argument("l2domain_id")
@click.pass_context
def l2domain_delete(ctx, l2domain_id):
    """Delete an L2 domain."""
    client = get_client(ctx)
    client.delete("l2domains", int(l2domain_id))
    click.echo("L2 domain deleted.")

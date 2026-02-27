import click

from ipam.helpers import get_client, format_output


@click.group("nameserver")
def nameserver():
    """Manage nameservers."""


@nameserver.command("list")
@click.pass_context
def nameserver_list(ctx):
    """List all nameservers."""
    client = get_client(ctx)
    data = client.get("tools/nameservers")
    if not data:
        click.echo("No nameservers found.")
        return
    data.sort(key=lambda n: n.get("name", "").lower())
    for n in data:
        click.echo(
            f"{n['id']:>4}  {n.get('name', ''):<20}  "
            f"{n.get('namesrv1', ''):<15}  {n.get('description', '')}"
        )


@nameserver.command("show")
@click.argument("nameserver_id")
@click.pass_context
def nameserver_show(ctx, nameserver_id):
    """Show details of a nameserver."""
    client = get_client(ctx)
    data = client.get("tools/nameservers", nameserver_id)
    click.echo(format_output(data))


@nameserver.command("add")
@click.option("--name", required=True, help="Nameserver name")
@click.option("--namesrv1", default="", help="Nameserver IP address")
@click.option("--description", default="", help="Description")
@click.pass_context
def nameserver_add(ctx, name, namesrv1, description):
    """Add a new nameserver."""
    client = get_client(ctx)
    payload = {"name": name, "namesrv1": namesrv1, "description": description}
    result = client.post("tools/nameservers", data=payload)
    click.echo(f"Nameserver created (id: {result['id']})")


@nameserver.command("update")
@click.argument("nameserver_id")
@click.option("--name", default=None, help="Nameserver name")
@click.option("--namesrv1", default=None, help="Nameserver IP address")
@click.option("--description", default=None, help="Description")
@click.pass_context
def nameserver_update(ctx, nameserver_id, name, namesrv1, description):
    """Update a nameserver."""
    client = get_client(ctx)
    payload = {}
    if name is not None:
        payload["name"] = name
    if namesrv1 is not None:
        payload["namesrv1"] = namesrv1
    if description is not None:
        payload["description"] = description
    client.patch("tools/nameservers", int(nameserver_id), data=payload)
    click.echo("Nameserver updated.")


@nameserver.command("delete")
@click.argument("nameserver_id")
@click.pass_context
def nameserver_delete(ctx, nameserver_id):
    """Delete a nameserver."""
    client = get_client(ctx)
    client.delete("tools/nameservers", int(nameserver_id))
    click.echo("Nameserver deleted.")

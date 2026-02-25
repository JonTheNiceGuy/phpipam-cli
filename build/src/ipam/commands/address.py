import click

from ipam.helpers import get_client, format_output


@click.group("address")
def address():
    """Manage IP addresses."""


@address.command("list")
@click.option("--subnet-id", required=True, help="Subnet ID to list addresses for")
@click.pass_context
def address_list(ctx, subnet_id):
    """List addresses in a subnet."""
    client = get_client(ctx)
    data = client.get("subnets", subnet_id, "addresses")
    if not data:
        click.echo("No addresses found.")
        return
    for a in data:
        click.echo(f"{a['id']:>4}  {a['ip']}  {a.get('hostname', '')}  {a.get('description', '')}")


@address.command("show")
@click.argument("address_id")
@click.pass_context
def address_show(ctx, address_id):
    """Show details of an address."""
    client = get_client(ctx)
    data = client.get("addresses", address_id)
    click.echo(format_output(data))


@address.command("add")
@click.option("--ip", required=True, help="IP address")
@click.option("--subnet-id", required=True, help="Subnet ID")
@click.option("--hostname", default="", help="Hostname")
@click.option("--description", default="", help="Description")
@click.pass_context
def address_add(ctx, ip, subnet_id, hostname, description):
    """Add a new IP address."""
    client = get_client(ctx)
    payload = {
        "ip": ip,
        "subnetId": subnet_id,
        "hostname": hostname,
        "description": description,
    }
    result = client.post("addresses", data=payload)
    click.echo(f"Address created (id: {result['id']})")


@address.command("update")
@click.argument("address_id")
@click.option("--hostname", default=None, help="Hostname")
@click.option("--description", default=None, help="Description")
@click.pass_context
def address_update(ctx, address_id, hostname, description):
    """Update an address."""
    client = get_client(ctx)
    payload = {}
    if hostname is not None:
        payload["hostname"] = hostname
    if description is not None:
        payload["description"] = description
    client.patch("addresses", int(address_id), data=payload)
    click.echo("Address updated.")


@address.command("delete")
@click.argument("address_id")
@click.pass_context
def address_delete(ctx, address_id):
    """Delete an address."""
    client = get_client(ctx)
    client.delete("addresses", int(address_id))
    click.echo("Address deleted.")


@address.command("search")
@click.argument("ip")
@click.pass_context
def address_search(ctx, ip):
    """Search for an IP address."""
    client = get_client(ctx)
    data = client.get("addresses", "search", ip)
    if not data:
        click.echo("No addresses found.")
        return
    for a in data:
        click.echo(f"{a['id']:>4}  {a['ip']}  {a.get('hostname', '')}  {a.get('description', '')}")

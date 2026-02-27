import click

from ipam.helpers import get_client, format_output


@click.group("circuit")
def circuit():
    """Manage circuits."""


@circuit.command("list")
@click.pass_context
def circuit_list(ctx):
    """List all circuits."""
    client = get_client(ctx)
    data = client.get("circuits")
    if not data:
        click.echo("No circuits found.")
        return
    data.sort(key=lambda c: c.get("cid", "").lower())
    for c in data:
        click.echo(
            f"{c['id']:>4}  {c.get('cid', ''):<20}  "
            f"{c.get('status', ''):<10}  {c.get('comment', '')}"
        )


@circuit.command("show")
@click.argument("circuit_id")
@click.pass_context
def circuit_show(ctx, circuit_id):
    """Show details of a circuit."""
    client = get_client(ctx)
    data = client.get("circuits", circuit_id)
    click.echo(format_output(data))


@circuit.command("add")
@click.option("--cid", required=True, help="Circuit ID")
@click.option("--provider", required=True, help="Provider ID")
@click.option("--status", default="Active", help="Status")
@click.option("--capacity", default=None, help="Capacity")
@click.option("--device1", default=None, help="Device 1 ID")
@click.option("--location1", default=None, help="Location 1 ID")
@click.option("--device2", default=None, help="Device 2 ID")
@click.option("--location2", default=None, help="Location 2 ID")
@click.option("--comment", default="", help="Comment")
@click.pass_context
def circuit_add(ctx, cid, provider, status, capacity, device1, location1,
                device2, location2, comment):
    """Add a new circuit."""
    client = get_client(ctx)
    payload = {
        "cid": cid, "provider": provider, "status": status, "comment": comment,
    }
    if capacity is not None:
        payload["capacity"] = capacity
    if device1 is not None:
        payload["device1"] = device1
    if location1 is not None:
        payload["location1"] = location1
    if device2 is not None:
        payload["device2"] = device2
    if location2 is not None:
        payload["location2"] = location2
    result = client.post("circuits", data=payload)
    click.echo(f"Circuit created (id: {result['id']})")


@circuit.command("update")
@click.argument("circuit_id")
@click.option("--cid", default=None, help="Circuit ID")
@click.option("--provider", default=None, help="Provider ID")
@click.option("--status", default=None, help="Status")
@click.option("--capacity", default=None, help="Capacity")
@click.option("--device1", default=None, help="Device 1 ID")
@click.option("--location1", default=None, help="Location 1 ID")
@click.option("--device2", default=None, help="Device 2 ID")
@click.option("--location2", default=None, help="Location 2 ID")
@click.option("--comment", default=None, help="Comment")
@click.pass_context
def circuit_update(ctx, circuit_id, cid, provider, status, capacity,
                   device1, location1, device2, location2, comment):
    """Update a circuit."""
    client = get_client(ctx)
    payload = {}
    if cid is not None:
        payload["cid"] = cid
    if provider is not None:
        payload["provider"] = provider
    if status is not None:
        payload["status"] = status
    if capacity is not None:
        payload["capacity"] = capacity
    if device1 is not None:
        payload["device1"] = device1
    if location1 is not None:
        payload["location1"] = location1
    if device2 is not None:
        payload["device2"] = device2
    if location2 is not None:
        payload["location2"] = location2
    if comment is not None:
        payload["comment"] = comment
    client.patch("circuits", int(circuit_id), data=payload)
    click.echo("Circuit updated.")


@circuit.command("delete")
@click.argument("circuit_id")
@click.pass_context
def circuit_delete(ctx, circuit_id):
    """Delete a circuit."""
    client = get_client(ctx)
    client.delete("circuits", int(circuit_id))
    click.echo("Circuit deleted.")


# --- Provider sub-group ---


@circuit.group("provider")
def provider():
    """Manage circuit providers."""


@provider.command("list")
@click.pass_context
def provider_list(ctx):
    """List all circuit providers."""
    client = get_client(ctx)
    data = client.get("circuits", "providers")
    if not data:
        click.echo("No providers found.")
        return
    data.sort(key=lambda p: p.get("name", "").lower())
    for p in data:
        click.echo(
            f"{p['id']:>4}  {p.get('name', ''):<30}  {p.get('description', '')}"
        )


@provider.command("show")
@click.argument("provider_id")
@click.pass_context
def provider_show(ctx, provider_id):
    """Show details of a circuit provider."""
    client = get_client(ctx)
    data = client.get("circuits", "providers", provider_id)
    click.echo(format_output(data))


@provider.command("add")
@click.option("--name", required=True, help="Provider name")
@click.option("--description", default="", help="Description")
@click.option("--contact", default="", help="Contact info")
@click.pass_context
def provider_add(ctx, name, description, contact):
    """Add a new circuit provider."""
    client = get_client(ctx)
    payload = {"name": name, "description": description, "contact": contact}
    result = client.post("circuits", "providers", data=payload)
    click.echo(f"Provider created (id: {result['id']})")


@provider.command("update")
@click.argument("provider_id")
@click.option("--name", default=None, help="Provider name")
@click.option("--description", default=None, help="Description")
@click.option("--contact", default=None, help="Contact info")
@click.pass_context
def provider_update(ctx, provider_id, name, description, contact):
    """Update a circuit provider."""
    client = get_client(ctx)
    payload = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if contact is not None:
        payload["contact"] = contact
    client.patch("circuits/providers", int(provider_id), data=payload)
    click.echo("Provider updated.")


@provider.command("delete")
@click.argument("provider_id")
@click.pass_context
def provider_delete(ctx, provider_id):
    """Delete a circuit provider."""
    client = get_client(ctx)
    client.delete("circuits/providers", int(provider_id))
    click.echo("Provider deleted.")

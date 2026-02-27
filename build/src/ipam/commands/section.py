import click

from ipam.helpers import get_client, format_output


@click.group("section")
def section():
    """Manage sections."""


@section.command("list")
@click.pass_context
def section_list(ctx):
    """List all sections."""
    client = get_client(ctx)
    data = client.get("sections")
    if not data:
        click.echo("No sections found.")
        return
    data.sort(key=lambda s: s.get("name", "").lower())
    for s in data:
        click.echo(f"{s['id']:>4}  {s.get('name', ''):<30}  {s.get('description', '')}")


@section.command("show")
@click.argument("section_id")
@click.pass_context
def section_show(ctx, section_id):
    """Show details of a section."""
    client = get_client(ctx)
    data = client.get("sections", section_id)
    click.echo(format_output(data))


@section.command("add")
@click.option("--name", required=True, help="Section name")
@click.option("--description", default="", help="Description")
@click.option("--master-section", default=None, help="Parent section ID")
@click.pass_context
def section_add(ctx, name, description, master_section):
    """Add a new section."""
    client = get_client(ctx)
    payload = {"name": name, "description": description}
    if master_section is not None:
        payload["masterSection"] = master_section
    result = client.post("sections", data=payload)
    click.echo(f"Section created (id: {result['id']})")


@section.command("update")
@click.argument("section_id")
@click.option("--name", default=None, help="Section name")
@click.option("--description", default=None, help="Description")
@click.option("--master-section", default=None, help="Parent section ID")
@click.pass_context
def section_update(ctx, section_id, name, description, master_section):
    """Update a section."""
    client = get_client(ctx)
    payload = {}
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if master_section is not None:
        payload["masterSection"] = master_section
    client.patch("sections", int(section_id), data=payload)
    click.echo("Section updated.")


@section.command("delete")
@click.argument("section_id")
@click.pass_context
def section_delete(ctx, section_id):
    """Delete a section."""
    client = get_client(ctx)
    client.delete("sections", int(section_id))
    click.echo("Section deleted.")

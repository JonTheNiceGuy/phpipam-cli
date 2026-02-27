import click

from ipam.helpers import get_client, format_output


@click.group("customer")
def customer():
    """Manage customers."""


@customer.command("list")
@click.pass_context
def customer_list(ctx):
    """List all customers."""
    client = get_client(ctx)
    data = client.get("tools/customers")
    if not data:
        click.echo("No customers found.")
        return
    data.sort(key=lambda c: c.get("title", "").lower())
    for c in data:
        click.echo(
            f"{c['id']:>4}  {c.get('title', ''):<30}  "
            f"{c.get('city', ''):<15}  {c.get('contact_person', '')}"
        )


@customer.command("show")
@click.argument("customer_id")
@click.pass_context
def customer_show(ctx, customer_id):
    """Show details of a customer."""
    client = get_client(ctx)
    data = client.get("tools/customers", customer_id)
    click.echo(format_output(data))


@customer.command("add")
@click.option("--title", required=True, help="Customer name")
@click.option("--address", default="", help="Street address")
@click.option("--city", default="", help="City")
@click.option("--state", default="", help="State/region")
@click.option("--postcode", default="", help="Postal code")
@click.option("--contact-person", default="", help="Contact person name")
@click.option("--contact-phone", default="", help="Contact phone")
@click.option("--contact-mail", default="", help="Contact email")
@click.option("--note", default="", help="Notes")
@click.pass_context
def customer_add(ctx, title, address, city, state, postcode,
                 contact_person, contact_phone, contact_mail, note):
    """Add a new customer."""
    client = get_client(ctx)
    payload = {
        "title": title, "address": address, "city": city,
        "state": state, "postcode": postcode,
        "contact_person": contact_person, "contact_phone": contact_phone,
        "contact_mail": contact_mail, "note": note,
    }
    result = client.post("tools/customers", data=payload)
    click.echo(f"Customer created (id: {result['id']})")


@customer.command("update")
@click.argument("customer_id")
@click.option("--title", default=None, help="Customer name")
@click.option("--address", default=None, help="Street address")
@click.option("--city", default=None, help="City")
@click.option("--state", default=None, help="State/region")
@click.option("--postcode", default=None, help="Postal code")
@click.option("--contact-person", default=None, help="Contact person name")
@click.option("--contact-phone", default=None, help="Contact phone")
@click.option("--contact-mail", default=None, help="Contact email")
@click.option("--note", default=None, help="Notes")
@click.pass_context
def customer_update(ctx, customer_id, title, address, city, state, postcode,
                    contact_person, contact_phone, contact_mail, note):
    """Update a customer."""
    client = get_client(ctx)
    payload = {}
    if title is not None:
        payload["title"] = title
    if address is not None:
        payload["address"] = address
    if city is not None:
        payload["city"] = city
    if state is not None:
        payload["state"] = state
    if postcode is not None:
        payload["postcode"] = postcode
    if contact_person is not None:
        payload["contact_person"] = contact_person
    if contact_phone is not None:
        payload["contact_phone"] = contact_phone
    if contact_mail is not None:
        payload["contact_mail"] = contact_mail
    if note is not None:
        payload["note"] = note
    client.patch("tools/customers", int(customer_id), data=payload)
    click.echo("Customer updated.")


@customer.command("delete")
@click.argument("customer_id")
@click.pass_context
def customer_delete(ctx, customer_id):
    """Delete a customer."""
    client = get_client(ctx)
    client.delete("tools/customers", int(customer_id))
    click.echo("Customer deleted.")

import click
import pytest

from ipam.helpers import get_client, format_output


class TestGetClient:
    def test_get_client_with_context(self):
        ctx = click.Context(click.Command("test"))
        ctx.obj = "fake-client"
        assert get_client(ctx) == "fake-client"

    def test_get_client_without_context(self):
        ctx = click.Context(click.Command("test"))
        ctx.obj = "fake-client"
        with ctx:
            assert get_client() == "fake-client"


class TestFormatOutput:
    def test_format_dict(self):
        result = format_output({"key": "value"})
        assert '"key": "value"' in result

    def test_format_list(self):
        result = format_output([1, 2, 3])
        assert "1" in result
        assert "3" in result

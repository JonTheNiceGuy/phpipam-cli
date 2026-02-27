from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ipam.cli import cli


@pytest.fixture
def mock_client():
    with patch("ipam.commands.customer.get_client") as mock_get:
        client = MagicMock()
        mock_get.return_value = client
        yield client


class TestCustomerList:
    def test_customer_list(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "1", "title": "Acme Corp", "city": "London",
             "contact_person": "John"},
            {"id": "2", "title": "Globex", "city": "Paris",
             "contact_person": "Jane"},
        ]
        result = runner.invoke(cli, ["--profile", "test", "customer", "list"])
        assert result.exit_code == 0
        assert "Acme Corp" in result.output
        assert "Globex" in result.output

    def test_customer_list_empty(self, runner, mock_client):
        mock_client.get.return_value = []
        result = runner.invoke(cli, ["--profile", "test", "customer", "list"])
        assert result.exit_code == 0
        assert "No customers found" in result.output

    def test_customer_list_sorted(self, runner, mock_client):
        mock_client.get.return_value = [
            {"id": "2", "title": "Zulu Inc", "city": "", "contact_person": ""},
            {"id": "1", "title": "Alpha Ltd", "city": "", "contact_person": ""},
        ]
        result = runner.invoke(cli, ["--profile", "test", "customer", "list"])
        assert result.exit_code == 0
        lines = [l for l in result.output.strip().splitlines() if l.strip()]
        assert "Alpha" in lines[0]
        assert "Zulu" in lines[1]


class TestCustomerShow:
    def test_customer_show(self, runner, mock_client):
        mock_client.get.return_value = {
            "id": "1", "title": "Acme Corp", "city": "London",
        }
        result = runner.invoke(cli, ["--profile", "test", "customer", "show", "1"])
        assert result.exit_code == 0
        assert "Acme Corp" in result.output


class TestCustomerAdd:
    def test_customer_add(self, runner, mock_client):
        mock_client.post.return_value = {
            "code": 201, "success": True, "id": 3, "data": "Customer created",
        }
        result = runner.invoke(
            cli,
            ["--profile", "test", "customer", "add", "--title", "NewCo",
             "--city", "Berlin", "--contact-person", "Max"],
        )
        assert result.exit_code == 0
        assert "created" in result.output.lower()


class TestCustomerUpdate:
    def test_customer_update_title(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "customer", "update", "1",
             "--title", "Renamed"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/customers", 1, data={"title": "Renamed"}
        )

    def test_customer_update_contact_person(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "customer", "update", "1",
             "--contact-person", "Alice"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/customers", 1, data={"contact_person": "Alice"}
        )

    def test_customer_update_address_and_city(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "customer", "update", "1",
             "--address", "123 New St", "--city", "Munich"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/customers", 1,
            data={"address": "123 New St", "city": "Munich"}
        )

    def test_customer_update_state_and_postcode(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "customer", "update", "1",
             "--state", "Bavaria", "--postcode", "80331"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/customers", 1,
            data={"state": "Bavaria", "postcode": "80331"}
        )

    def test_customer_update_contact_phone_and_mail(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "customer", "update", "1",
             "--contact-phone", "+49123", "--contact-mail", "a@b.com"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/customers", 1,
            data={"contact_phone": "+49123", "contact_mail": "a@b.com"}
        )

    def test_customer_update_note(self, runner, mock_client):
        mock_client.patch.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli,
            ["--profile", "test", "customer", "update", "1",
             "--note", "VIP customer"],
        )
        assert result.exit_code == 0
        mock_client.patch.assert_called_once_with(
            "tools/customers", 1, data={"note": "VIP customer"}
        )


class TestCustomerDelete:
    def test_customer_delete(self, runner, mock_client):
        mock_client.delete.return_value = {"code": 200, "success": True}
        result = runner.invoke(
            cli, ["--profile", "test", "customer", "delete", "1"]
        )
        assert result.exit_code == 0
        assert "deleted" in result.output.lower()

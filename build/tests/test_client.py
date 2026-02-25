import httpx
import pytest
from pytest_httpx import HTTPXMock

from ipam.client import PhpIpamClient


@pytest.fixture
def client():
    return PhpIpamClient(
        url="https://ipam.example.com",
        app_id="myapp",
        token="test-token-123",
    )


class TestClientInit:
    def test_base_url_construction(self, client):
        assert client.base_url == "https://ipam.example.com/api/myapp"

    def test_token_in_headers(self, client):
        assert client._headers()["token"] == "test-token-123"

    def test_trailing_slash_stripped(self):
        c = PhpIpamClient(
            url="https://ipam.example.com/",
            app_id="myapp",
            token="tok",
        )
        assert c.base_url == "https://ipam.example.com/api/myapp"


class TestAuthenticate:
    def test_authenticate_returns_token(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://ipam.example.com/api/myapp/user/",
            method="POST",
            json={
                "code": 200,
                "success": True,
                "data": {
                    "token": "new-token-abc",
                    "expires": "2026-02-25 20:00:00",
                },
            },
        )
        token = PhpIpamClient.authenticate(
            url="https://ipam.example.com",
            app_id="myapp",
            username="admin",
            password="secret",
        )
        assert token == "new-token-abc"

    def test_authenticate_failure_raises(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://ipam.example.com/api/myapp/user/",
            method="POST",
            status_code=401,
            json={
                "code": 401,
                "success": False,
                "message": "Invalid credentials",
            },
        )
        with pytest.raises(Exception, match="Invalid credentials"):
            PhpIpamClient.authenticate(
                url="https://ipam.example.com",
                app_id="myapp",
                username="admin",
                password="wrong",
            )


class TestGet:
    def test_get_subnets(self, client, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://ipam.example.com/api/myapp/subnets/",
            method="GET",
            json={
                "code": 200,
                "success": True,
                "data": [{"id": 1, "subnet": "10.0.0.0", "mask": 24}],
            },
        )
        result = client.get("subnets")
        assert result == [{"id": 1, "subnet": "10.0.0.0", "mask": 24}]

    def test_get_single_resource(self, client, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://ipam.example.com/api/myapp/subnets/1/",
            method="GET",
            json={
                "code": 200,
                "success": True,
                "data": {"id": 1, "subnet": "10.0.0.0", "mask": 24},
            },
        )
        result = client.get("subnets", 1)
        assert result["id"] == 1

    def test_get_sub_resource(self, client, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://ipam.example.com/api/myapp/subnets/1/addresses/",
            method="GET",
            json={
                "code": 200,
                "success": True,
                "data": [{"id": 10, "ip": "10.0.0.1"}],
            },
        )
        result = client.get("subnets", 1, "addresses")
        assert result[0]["ip"] == "10.0.0.1"

    def test_get_not_found_raises(self, client, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://ipam.example.com/api/myapp/subnets/999/",
            method="GET",
            status_code=404,
            json={
                "code": 404,
                "success": False,
                "message": "No subnets found",
            },
        )
        with pytest.raises(Exception, match="No subnets found"):
            client.get("subnets", 999)


class TestPost:
    def test_create_subnet(self, client, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://ipam.example.com/api/myapp/subnets/",
            method="POST",
            status_code=201,
            json={
                "code": 201,
                "success": True,
                "id": 5,
                "data": "Subnet created",
            },
        )
        result = client.post("subnets", data={"subnet": "10.1.0.0", "mask": 24})
        assert result["id"] == 5

    def test_create_address(self, client, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://ipam.example.com/api/myapp/addresses/",
            method="POST",
            status_code=201,
            json={
                "code": 201,
                "success": True,
                "id": 42,
                "data": "Address created",
            },
        )
        result = client.post(
            "addresses", data={"ip": "10.0.0.5", "subnetId": 1}
        )
        assert result["id"] == 42


class TestPatch:
    def test_update_subnet(self, client, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://ipam.example.com/api/myapp/subnets/1/",
            method="PATCH",
            json={
                "code": 200,
                "success": True,
                "data": "Subnet updated",
            },
        )
        result = client.patch("subnets", 1, data={"description": "Updated"})
        assert result["success"] is True


class TestDelete:
    def test_delete_subnet(self, client, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://ipam.example.com/api/myapp/subnets/1/",
            method="DELETE",
            json={
                "code": 200,
                "success": True,
                "data": "Subnet deleted",
            },
        )
        result = client.delete("subnets", 1)
        assert result["success"] is True


class TestSearch:
    def test_search_cidr(self, client, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            url="https://ipam.example.com/api/myapp/subnets/cidr/10.0.0.0/24/",
            method="GET",
            json={
                "code": 200,
                "success": True,
                "data": [{"id": 1, "subnet": "10.0.0.0", "mask": 24}],
            },
        )
        result = client.get("subnets", "cidr", "10.0.0.0/24")
        assert result[0]["subnet"] == "10.0.0.0"

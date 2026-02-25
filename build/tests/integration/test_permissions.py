import pytest

from ipam.client import PhpIpamError

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Read-Only token (permission level 1)
# ---------------------------------------------------------------------------

class TestReadOnlyPermissions:
    """The R/O token can read any resource but cannot create, update, or delete."""

    def test_can_read_sections(self, ro_client):
        sections = ro_client.get("sections")
        assert isinstance(sections, list)

    def test_can_read_subnet(self, ro_client, existing_subnet):
        subnet = ro_client.get("subnets", existing_subnet)
        assert subnet["subnet"] == "10.240.0.0"

    def test_can_read_vlan(self, ro_client, existing_vlan):
        vlan = ro_client.get("vlan", existing_vlan)
        assert int(vlan["number"]) == 800

    def test_can_read_address(self, ro_client, existing_address):
        addr = ro_client.get("addresses", existing_address)
        assert addr["ip"] == "10.240.0.100"

    def test_cannot_create_subnet(self, ro_client, test_section_id):
        with pytest.raises(PhpIpamError):
            ro_client.post("subnets", data={
                "subnet": "10.250.0.0",
                "mask": "24",
                "sectionId": str(test_section_id),
            })

    def test_cannot_create_vlan(self, ro_client):
        with pytest.raises(PhpIpamError):
            ro_client.post("vlan", data={
                "number": "850",
                "name": "ShouldFail",
            })

    def test_cannot_update_subnet(self, ro_client, existing_subnet):
        with pytest.raises(PhpIpamError):
            ro_client.patch("subnets", existing_subnet, data={
                "description": "hacked",
            })

    def test_cannot_delete_subnet(self, ro_client, existing_subnet):
        with pytest.raises(PhpIpamError):
            ro_client.delete("subnets", existing_subnet)


# ---------------------------------------------------------------------------
# Read/Write token (permission level 2)
# ---------------------------------------------------------------------------

class TestReadWritePermissions:
    """The R/W token can read and write but cannot perform admin operations."""

    def test_can_read_subnet(self, rw_client, existing_subnet):
        subnet = rw_client.get("subnets", existing_subnet)
        assert subnet is not None

    def test_can_create_and_delete_subnet(self, rw_client, test_section_id):
        result = rw_client.post("subnets", data={
            "subnet": "10.251.0.0",
            "mask": "24",
            "sectionId": str(test_section_id),
        })
        assert "id" in result
        rw_client.delete("subnets", result["id"])

    def test_can_create_and_delete_vlan(self, rw_client):
        result = rw_client.post("vlan", data={
            "number": "851",
            "name": "RWTestVLAN",
        })
        assert "id" in result
        rw_client.delete("vlan", result["id"])

    def test_can_update_subnet(self, rw_client, existing_subnet):
        rw_client.patch("subnets", existing_subnet, data={
            "description": "RW updated",
        })
        subnet = rw_client.get("subnets", existing_subnet)
        assert subnet["description"] == "RW updated"
        # Reset for other tests
        rw_client.patch("subnets", existing_subnet, data={
            "description": "Perm test subnet",
        })

    def test_cannot_list_all_users(self, rw_client):
        with pytest.raises(PhpIpamError):
            rw_client.get("user", "all")


# ---------------------------------------------------------------------------
# Read/Write/Admin token (permission level 3)
# ---------------------------------------------------------------------------

class TestReadWriteAdminPermissions:
    """The R/W/Admin token can do everything, including admin operations."""

    def test_can_read_subnet(self, rwa_client, existing_subnet):
        subnet = rwa_client.get("subnets", existing_subnet)
        assert subnet is not None

    def test_can_create_and_delete_subnet(self, rwa_client, test_section_id):
        result = rwa_client.post("subnets", data={
            "subnet": "10.252.0.0",
            "mask": "24",
            "sectionId": str(test_section_id),
        })
        assert "id" in result
        rwa_client.delete("subnets", result["id"])

    def test_can_list_all_users(self, rwa_client):
        users = rwa_client.get("user", "all")
        assert isinstance(users, list)
        assert len(users) > 0

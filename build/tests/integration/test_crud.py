import pytest

from ipam.client import PhpIpamError

pytestmark = pytest.mark.integration


class TestSectionCrud:
    def test_list_sections(self, rwa_client):
        sections = rwa_client.get("sections")
        assert isinstance(sections, list)
        assert len(sections) > 0

    def test_read_section(self, rwa_client, test_section_id):
        section = rwa_client.get("sections", test_section_id)
        assert section["name"] == "IntegrationTest"


class TestSubnetCrud:
    @pytest.fixture
    def subnet_id(self, rwa_client, test_section_id):
        result = rwa_client.post("subnets", data={
            "subnet": "10.200.0.0",
            "mask": "24",
            "sectionId": str(test_section_id),
            "description": "CRUD test subnet",
        })
        yield result["id"]
        try:
            rwa_client.delete("subnets", result["id"])
        except PhpIpamError:
            pass

    def test_create_subnet(self, rwa_client, test_section_id):
        result = rwa_client.post("subnets", data={
            "subnet": "10.201.0.0",
            "mask": "24",
            "sectionId": str(test_section_id),
            "description": "Create test",
        })
        assert "id" in result
        rwa_client.delete("subnets", result["id"])

    def test_read_subnet(self, rwa_client, subnet_id):
        subnet = rwa_client.get("subnets", subnet_id)
        assert subnet["subnet"] == "10.200.0.0"
        assert subnet["mask"] == "24"
        assert subnet["description"] == "CRUD test subnet"

    def test_update_subnet(self, rwa_client, subnet_id):
        rwa_client.patch("subnets", subnet_id, data={
            "description": "Updated via integration test",
        })
        subnet = rwa_client.get("subnets", subnet_id)
        assert subnet["description"] == "Updated via integration test"

    def test_list_subnets_contains_created(self, rwa_client, subnet_id):
        subnets = rwa_client.get("subnets")
        ids = [int(s["id"]) for s in subnets]
        assert int(subnet_id) in ids

    def test_search_by_cidr(self, rwa_client, subnet_id):
        results = rwa_client.get("subnets", "cidr", "10.200.0.0/24")
        assert any(int(s["id"]) == int(subnet_id) for s in results)

    def test_delete_subnet(self, rwa_client, test_section_id):
        result = rwa_client.post("subnets", data={
            "subnet": "10.202.0.0",
            "mask": "24",
            "sectionId": str(test_section_id),
        })
        subnet_id = result["id"]
        rwa_client.delete("subnets", subnet_id)
        with pytest.raises(PhpIpamError):
            rwa_client.get("subnets", subnet_id)


class TestAddressCrud:
    @pytest.fixture
    def subnet_for_addresses(self, rwa_client, test_section_id):
        result = rwa_client.post("subnets", data={
            "subnet": "10.210.0.0",
            "mask": "24",
            "sectionId": str(test_section_id),
        })
        yield result["id"]
        try:
            rwa_client.delete("subnets", result["id"])
        except PhpIpamError:
            pass

    @pytest.fixture
    def address_id(self, rwa_client, subnet_for_addresses):
        result = rwa_client.post("addresses", data={
            "ip": "10.210.0.10",
            "subnetId": str(subnet_for_addresses),
            "hostname": "testhost",
            "description": "CRUD test address",
        })
        yield result["id"]
        try:
            rwa_client.delete("addresses", result["id"])
        except PhpIpamError:
            pass

    def test_create_address(self, rwa_client, subnet_for_addresses):
        result = rwa_client.post("addresses", data={
            "ip": "10.210.0.20",
            "subnetId": str(subnet_for_addresses),
            "hostname": "createtest",
        })
        assert "id" in result
        rwa_client.delete("addresses", result["id"])

    def test_read_address(self, rwa_client, address_id):
        addr = rwa_client.get("addresses", address_id)
        assert addr["ip"] == "10.210.0.10"
        assert addr["hostname"] == "testhost"

    def test_update_address(self, rwa_client, address_id):
        rwa_client.patch("addresses", address_id, data={
            "hostname": "updated-host",
        })
        addr = rwa_client.get("addresses", address_id)
        assert addr["hostname"] == "updated-host"

    def test_search_address(self, rwa_client, address_id):
        results = rwa_client.get("addresses", "search", "10.210.0.10")
        assert any(int(a["id"]) == int(address_id) for a in results)

    def test_delete_address(self, rwa_client, subnet_for_addresses):
        result = rwa_client.post("addresses", data={
            "ip": "10.210.0.30",
            "subnetId": str(subnet_for_addresses),
        })
        addr_id = result["id"]
        rwa_client.delete("addresses", addr_id)
        with pytest.raises(PhpIpamError):
            rwa_client.get("addresses", addr_id)


class TestVlanCrud:
    @pytest.fixture
    def vlan_id(self, rwa_client):
        result = rwa_client.post("vlan", data={
            "number": "900",
            "name": "TestVLAN900",
            "description": "CRUD test VLAN",
        })
        yield result["id"]
        try:
            rwa_client.delete("vlan", result["id"])
        except PhpIpamError:
            pass

    def test_create_vlan(self, rwa_client):
        result = rwa_client.post("vlan", data={
            "number": "901",
            "name": "CreateTestVLAN",
        })
        assert "id" in result
        rwa_client.delete("vlan", result["id"])

    def test_read_vlan(self, rwa_client, vlan_id):
        vlan = rwa_client.get("vlan", vlan_id)
        assert int(vlan["number"]) == 900
        assert vlan["name"] == "TestVLAN900"

    def test_update_vlan(self, rwa_client, vlan_id):
        rwa_client.patch("vlan", vlan_id, data={"name": "UpdatedVLAN"})
        vlan = rwa_client.get("vlan", vlan_id)
        assert vlan["name"] == "UpdatedVLAN"

    def test_list_vlans_contains_created(self, rwa_client, vlan_id):
        vlans = rwa_client.get("vlan")
        ids = [int(v["vlanId"]) for v in vlans]
        assert int(vlan_id) in ids

    def test_delete_vlan(self, rwa_client):
        result = rwa_client.post("vlan", data={
            "number": "902",
            "name": "DeleteTestVLAN",
        })
        vlan_id = result["id"]
        rwa_client.delete("vlan", vlan_id)
        with pytest.raises(PhpIpamError):
            rwa_client.get("vlan", vlan_id)

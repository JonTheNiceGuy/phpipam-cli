import subprocess
import time
from pathlib import Path

import httpx
import pytest

from ipam.client import PhpIpamClient, PhpIpamError

PROJECT_ROOT = Path(__file__).parent.parent.parent
PHPIPAM_URL = "http://localhost:8080"
DB_ROOT_PASS = "root_password"
DB_NAME = "phpipam"
ADMIN_USER = "Admin"
ADMIN_PASS = "ipamadmin"


# ---------------------------------------------------------------------------
# Docker / DB helpers
# ---------------------------------------------------------------------------

def _docker_compose(*args, input_text=None):
    cmd = ["docker", "compose"] + list(args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        input=input_text,
    )


def _run_sql(sql):
    return _docker_compose(
        "exec", "-T", "phpipam-mariadb",
        "mariadb", "-u", "root", f"-p{DB_ROOT_PASS}", DB_NAME,
        "-e", sql,
    )


def _wait_for_db(timeout=120):
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = _docker_compose(
            "exec", "-T", "phpipam-mariadb",
            "mariadb", "-u", "root", f"-p{DB_ROOT_PASS}", "-e", "SELECT 1",
        )
        if result.returncode == 0:
            return
        time.sleep(2)
    raise TimeoutError("MariaDB not ready within timeout")


def _wait_for_web(timeout=120):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = httpx.get(PHPIPAM_URL, follow_redirects=True, timeout=5)
            if r.status_code < 500:
                return
        except (httpx.ConnectError, httpx.TimeoutException):
            pass
        time.sleep(2)
    raise TimeoutError("phpIPAM web not ready within timeout")


# ---------------------------------------------------------------------------
# Schema & data setup
# ---------------------------------------------------------------------------

def _setup_schema():
    result = _run_sql("SHOW TABLES LIKE 'settings';")
    if "settings" in result.stdout:
        return

    schema = _docker_compose(
        "exec", "-T", "phpipam-web", "cat", "/phpipam/db/SCHEMA.sql",
    )
    if schema.returncode != 0:
        raise RuntimeError(f"Failed to read SCHEMA.sql: {schema.stderr}")

    imp = _docker_compose(
        "exec", "-T", "phpipam-mariadb",
        "mariadb", "-u", "root", f"-p{DB_ROOT_PASS}", DB_NAME,
        input_text=schema.stdout,
    )
    if imp.returncode != 0:
        raise RuntimeError(f"Schema import failed: {imp.stderr}")


def _setup_admin():
    hash_result = _docker_compose(
        "exec", "-T", "phpipam-web",
        "php", "-r", f"echo password_hash('{ADMIN_PASS}', PASSWORD_DEFAULT);",
    )
    if hash_result.returncode != 0:
        raise RuntimeError(f"Password hash failed: {hash_result.stderr}")

    pw_hash = hash_result.stdout.strip()

    check = _run_sql(f"SELECT username FROM users WHERE username = '{ADMIN_USER}';")
    if ADMIN_USER in check.stdout:
        _run_sql(
            f"UPDATE users SET password = '{pw_hash}' "
            f"WHERE username = '{ADMIN_USER}';"
        )
    else:
        _run_sql(
            f"INSERT INTO users "
            f"(username, password, role, real_name, passChange, lang) "
            f"VALUES ('{ADMIN_USER}', '{pw_hash}', 'Administrator', "
            f"'Admin', 'No', 'english');"
        )


def _enable_unsafe_api():
    """Allow API over HTTP by setting api_allow_unsafe in phpipam config."""
    _docker_compose(
        "exec", "-T", "phpipam-web",
        "sh", "-c",
        "grep -q api_allow_unsafe /phpipam/config.docker.php || "
        "printf '\\n$api_allow_unsafe = true;\\n' >> /phpipam/config.docker.php",
    )


def _setup_api():
    # Ensure settings row exists with API enabled
    check = _run_sql("SELECT COUNT(*) AS cnt FROM settings;")
    if "\t0\n" in check.stdout or check.stdout.strip().endswith("0"):
        _run_sql(
            "INSERT INTO settings (id, siteTitle, siteAdminName, "
            "siteAdminMail, api) "
            "VALUES (1, 'phpIPAM', 'Admin', 'admin@test.local', 1);"
        )
    else:
        _run_sql("UPDATE settings SET api = 1;")

    # Allow API over plain HTTP for testing
    _enable_unsafe_api()

    # Recreate test API apps using 'none' security (HTTP + token auth)
    _run_sql(
        "DELETE FROM api WHERE app_id IN ('test_ro', 'test_rw', 'test_rwa');"
    )
    _run_sql(
        "INSERT INTO api "
        "(app_id, app_code, app_permissions, app_security) "
        "VALUES "
        "('test_ro',  'ro_code_123',  1, 'none'), "
        "('test_rw',  'rw_code_123',  2, 'none'), "
        "('test_rwa', 'rwa_code_123', 3, 'none');"
    )


def _get_token(app_id):
    resp = httpx.post(
        f"{PHPIPAM_URL}/api/{app_id}/user/",
        auth=(ADMIN_USER, ADMIN_PASS),
        timeout=10,
    )
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"Token request failed for {app_id}: {data}")
    return data["data"]["token"]


# ---------------------------------------------------------------------------
# Session fixtures
# ---------------------------------------------------------------------------

def _toggle_module(column, enabled):
    """Enable or disable a phpIPAM module via the settings table."""
    _run_sql(
        f"UPDATE settings SET {column} = {1 if enabled else 0} WHERE id = 1;"
    )


@pytest.fixture
def toggle_module():
    """Fixture that provides a function to toggle modules, with auto-restore."""
    toggled = []

    def _toggle(column, enabled):
        toggled.append(column)
        _toggle_module(column, enabled)

    yield _toggle

    # Re-enable all toggled modules after the test
    for col in toggled:
        _toggle_module(col, True)


@pytest.fixture(scope="session")
def phpipam_service():
    """Start Docker containers and configure phpIPAM for testing."""
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
        )
        if result.returncode != 0:
            pytest.skip("Docker Compose not available")
    except FileNotFoundError:
        pytest.skip("Docker not installed")

    _docker_compose("up", "-d")
    _wait_for_db()
    _setup_schema()
    _wait_for_web()
    _setup_admin()
    _setup_api()
    return PHPIPAM_URL


@pytest.fixture(scope="session")
def ro_client(phpipam_service):
    """Read-only API client (permission level 1)."""
    return PhpIpamClient(
        url=phpipam_service, app_id="test_ro", token=_get_token("test_ro"),
    )


@pytest.fixture(scope="session")
def rw_client(phpipam_service):
    """Read/Write API client (permission level 2)."""
    return PhpIpamClient(
        url=phpipam_service, app_id="test_rw", token=_get_token("test_rw"),
    )


@pytest.fixture(scope="session")
def rwa_client(phpipam_service):
    """Read/Write/Admin API client (permission level 3)."""
    return PhpIpamClient(
        url=phpipam_service, app_id="test_rwa", token=_get_token("test_rwa"),
    )


@pytest.fixture(scope="session")
def test_section_id(rwa_client):
    """Create (or find) a section for integration tests."""
    try:
        result = rwa_client.post("sections", data={
            "name": "IntegrationTest",
            "description": "Section for integration tests",
            "showVLAN": "1",
            "showVRF": "1",
        })
        return result["id"]
    except PhpIpamError:
        sections = rwa_client.get("sections")
        for s in sections:
            if s["name"] == "IntegrationTest":
                return int(s["id"])
        raise


@pytest.fixture(scope="session")
def existing_subnet(rwa_client, test_section_id):
    """A subnet that persists for the session, used by permission tests."""
    try:
        result = rwa_client.post("subnets", data={
            "subnet": "10.240.0.0",
            "mask": "24",
            "sectionId": str(test_section_id),
            "description": "Perm test subnet",
        })
        subnet_id = result["id"]
    except PhpIpamError:
        results = rwa_client.get("subnets", "cidr", "10.240.0.0/24")
        subnet_id = int(results[0]["id"])

    yield subnet_id

    try:
        rwa_client.delete("subnets", subnet_id)
    except PhpIpamError:
        pass


@pytest.fixture(scope="session")
def existing_vlan(rwa_client):
    """A VLAN that persists for the session, used by permission tests."""
    try:
        result = rwa_client.post("vlan", data={
            "number": "800",
            "name": "PermTestVLAN",
            "description": "Permission test VLAN",
        })
        vlan_id = result["id"]
    except PhpIpamError:
        vlans = rwa_client.get("vlan")
        vlan_id = int(next(v["vlanId"] for v in vlans if int(v.get("number", 0)) == 800))

    yield vlan_id

    try:
        rwa_client.delete("vlan", vlan_id)
    except PhpIpamError:
        pass


@pytest.fixture(scope="session")
def existing_address(rwa_client, existing_subnet):
    """An address that persists for the session, used by permission tests."""
    try:
        result = rwa_client.post("addresses", data={
            "ip": "10.240.0.100",
            "subnetId": str(existing_subnet),
            "hostname": "permtest",
            "description": "Perm test address",
        })
        addr_id = result["id"]
    except PhpIpamError:
        results = rwa_client.get("addresses", "search", "10.240.0.100")
        addr_id = int(results[0]["id"])

    yield addr_id

    try:
        rwa_client.delete("addresses", addr_id)
    except PhpIpamError:
        pass

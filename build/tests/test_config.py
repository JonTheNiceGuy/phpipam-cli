import os
from pathlib import Path

import pytest

from ipam.config import load_profile, save_profile, list_profiles, delete_profile


@pytest.fixture
def config_dir(tmp_path):
    return tmp_path / ".ipam"


@pytest.fixture
def config_file(config_dir):
    return config_dir / "config"


class TestLoadProfile:
    def test_load_existing_profile(self, config_file):
        config_file.parent.mkdir(parents=True)
        config_file.write_text(
            "[profile myserver]\n"
            "url = https://ipam.example.com\n"
            "app_id = myapp\n"
            "token = abc123\n"
        )
        profile = load_profile("myserver", config_file)
        assert profile["url"] == "https://ipam.example.com"
        assert profile["app_id"] == "myapp"
        assert profile["token"] == "abc123"

    def test_load_nonexistent_profile_raises(self, config_file):
        config_file.parent.mkdir(parents=True)
        config_file.write_text(
            "[profile other]\n"
            "url = https://other.example.com\n"
        )
        with pytest.raises(KeyError, match="nosuch"):
            load_profile("nosuch", config_file)

    def test_load_from_missing_file_raises(self, config_file):
        with pytest.raises(FileNotFoundError):
            load_profile("any", config_file)

    def test_load_multiple_profiles(self, config_file):
        config_file.parent.mkdir(parents=True)
        config_file.write_text(
            "[profile server1]\n"
            "url = https://s1.example.com\n"
            "app_id = app1\n"
            "token = tok1\n"
            "\n"
            "[profile server2]\n"
            "url = https://s2.example.com\n"
            "app_id = app2\n"
            "token = tok2\n"
        )
        p1 = load_profile("server1", config_file)
        p2 = load_profile("server2", config_file)
        assert p1["url"] == "https://s1.example.com"
        assert p2["url"] == "https://s2.example.com"


class TestSaveProfile:
    def test_save_new_profile(self, config_file):
        save_profile(
            "myserver",
            {
                "url": "https://ipam.example.com",
                "app_id": "myapp",
                "token": "abc123",
            },
            config_file,
        )
        assert config_file.exists()
        profile = load_profile("myserver", config_file)
        assert profile["url"] == "https://ipam.example.com"
        assert profile["app_id"] == "myapp"
        assert profile["token"] == "abc123"

    def test_save_creates_parent_directory(self, config_file):
        assert not config_file.parent.exists()
        save_profile("test", {"url": "https://test.com"}, config_file)
        assert config_file.parent.exists()
        assert config_file.exists()

    def test_save_preserves_existing_profiles(self, config_file):
        save_profile("first", {"url": "https://first.com"}, config_file)
        save_profile("second", {"url": "https://second.com"}, config_file)
        p1 = load_profile("first", config_file)
        p2 = load_profile("second", config_file)
        assert p1["url"] == "https://first.com"
        assert p2["url"] == "https://second.com"

    def test_save_overwrites_existing_profile(self, config_file):
        save_profile("srv", {"url": "https://old.com"}, config_file)
        save_profile("srv", {"url": "https://new.com"}, config_file)
        profile = load_profile("srv", config_file)
        assert profile["url"] == "https://new.com"

    def test_config_file_permissions(self, config_file):
        save_profile("test", {"url": "https://test.com"}, config_file)
        mode = oct(config_file.stat().st_mode & 0o777)
        assert mode == "0o600", f"Config file should be 0600, got {mode}"


class TestListProfiles:
    def test_list_empty(self, config_file):
        config_file.parent.mkdir(parents=True)
        config_file.write_text("")
        assert list_profiles(config_file) == []

    def test_list_profiles(self, config_file):
        config_file.parent.mkdir(parents=True)
        config_file.write_text(
            "[profile alpha]\nurl = https://a.com\n\n"
            "[profile beta]\nurl = https://b.com\n"
        )
        names = list_profiles(config_file)
        assert names == ["alpha", "beta"]

    def test_list_from_missing_file(self, config_file):
        assert list_profiles(config_file) == []


class TestDeleteProfile:
    def test_delete_existing_profile(self, config_file):
        config_file.parent.mkdir(parents=True)
        config_file.write_text(
            "[profile keep]\nurl = https://keep.com\n\n"
            "[profile remove]\nurl = https://remove.com\n"
        )
        delete_profile("remove", config_file)
        assert list_profiles(config_file) == ["keep"]
        with pytest.raises(KeyError):
            load_profile("remove", config_file)

    def test_delete_nonexistent_profile_raises(self, config_file):
        config_file.parent.mkdir(parents=True)
        config_file.write_text("[profile keep]\nurl = https://keep.com\n")
        with pytest.raises(KeyError, match="nosuch"):
            delete_profile("nosuch", config_file)

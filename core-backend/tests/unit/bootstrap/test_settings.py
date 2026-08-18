from platform_core.bootstrap.settings import Settings, get_settings


def test_get_settings_should_return_settings_instance_with_expected_defaults():
    settings = get_settings()

    assert isinstance(settings, Settings)
    assert settings.service_name == "backend"
    assert settings.environment == "development"


def test_get_settings_when_called_twice_should_return_cached_instance():
    assert get_settings() is get_settings()

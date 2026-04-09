import factory
from cryptography.fernet import Fernet
from factory.django import DjangoModelFactory

from apps.agents.models import AgentProvider, AgentAPIKey, AgentConfig

# Một Fernet key cố định dùng xuyên suốt test suite.
# Các test class dùng @override_settings(AGENT_ENCRYPTION_KEY=TEST_FERNET_KEY)
TEST_FERNET_KEY = Fernet.generate_key().decode()
_fernet = Fernet(TEST_FERNET_KEY.encode())

# Raw key mẫu cho test
TEST_RAW_KEY = "sk-proj-testkey-1234567890abcdefghij"


class UserFactory(DjangoModelFactory):
    class Meta:
        model = "users.User"
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user{n}@test.com")
    full_name = factory.Sequence(lambda n: f"Test User {n}")
    is_active = True
    is_staff = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "TestPass123!")
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, password=password, **kwargs)


class AdminUserFactory(UserFactory):
    is_staff = True
    is_superuser = True

    class Meta:
        model = "users.User"
        django_get_or_create = ("email",)


class AgentProviderFactory(DjangoModelFactory):
    class Meta:
        model = AgentProvider

    name = factory.Sequence(lambda n: f"Provider {n}")
    slug = factory.Sequence(lambda n: f"provider-{n}")
    description = "Test provider"
    website_url = "https://example.com"
    is_active = True


class AgentAPIKeyFactory(DjangoModelFactory):
    class Meta:
        model = AgentAPIKey

    provider = factory.SubFactory(AgentProviderFactory)
    name = factory.Sequence(lambda n: f"Key {n}")
    encrypted_key = factory.LazyFunction(
        lambda: _fernet.encrypt(TEST_RAW_KEY.encode()).decode()
    )
    key_preview = "sk-proj-t...****"
    is_active = True
    priority = 1
    expires_at = None
    created_by = None


class AgentConfigFactory(DjangoModelFactory):
    class Meta:
        model = AgentConfig

    provider = factory.SubFactory(AgentProviderFactory)
    name = factory.Sequence(lambda n: f"Config {n}")
    model_name = "gpt-4o"
    config_json = factory.LazyFunction(lambda: {"temperature": 0.7, "max_tokens": 2048})
    is_default = False
    is_active = True

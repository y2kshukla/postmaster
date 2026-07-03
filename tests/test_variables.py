import sys
sys.path.insert(0, 'src')

from postmaster.services.variable_resolver import VariableResolver
from postmaster.models.environment import Environment, EnvironmentVariable


class TestVariableResolver:
    def setup_method(self):
        self.resolver = VariableResolver()
        self.env = Environment(
            name="Test",
            variables=[
                EnvironmentVariable(name="base_url", value="https://api.example.com"),
                EnvironmentVariable(name="token", value="abc123"),
            ],
        )

    def test_resolve_env_var(self):
        result = self.resolver.resolve("{{base_url}}/users", self.env)
        assert result == "https://api.example.com/users"

    def test_resolve_env_nested(self):
        result = self.resolver.resolve("{{env.base_url}}/v1", self.env)
        assert result == "https://api.example.com/v1"

    def test_resolve_uuid(self):
        result = self.resolver.resolve("{{$uuid}}", self.env)
        assert len(result) == 32  # hex uuid

    def test_resolve_timestamp(self):
        result = self.resolver.resolve("{{$timestamp}}", self.env)
        assert result.isdigit()

    def test_resolve_multiple(self):
        result = self.resolver.resolve(
            "{{$uuid}} - {{base_url}}/users", self.env
        )
        assert len(result) > 0

    def test_no_match_keeps_original(self):
        result = self.resolver.resolve("{{unknown_var}}", self.env)
        assert result == "{{unknown_var}}"

    def test_no_variables(self):
        result = self.resolver.resolve("plain text", self.env)
        assert result == "plain text"

    def test_empty_string(self):
        result = self.resolver.resolve("", self.env)
        assert result == ""

    def test_local_variable_override(self):
        self.resolver.set_local("token", "local_token")
        result = self.resolver.resolve("{{token}}", self.env)
        assert result == "local_token"

    def test_global_variable(self):
        self.resolver.set_global("api_key", "global_key")
        result = self.resolver.resolve("{{api_key}}", None)
        assert result == "global_key"

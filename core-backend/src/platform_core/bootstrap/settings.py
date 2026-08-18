"""Configuração e variáveis de ambiente (RA-005, Capítulo 66 — bootstrap/).

Os valores de referência abaixo (portas, credenciais de desenvolvimento)
batem com o docker-compose.yml de referência de PB-006, Passo 6 — nunca um
segredo real. Uma aplicação consumidora que precisar de configuração
adicional deverá criar sua própria subclasse de `Settings`, em vez de
adicionar campos específicos de domínio aqui."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "backend"
    environment: str = "development"

    # Bate com o serviço "postgres" do docker-compose.yml de referência
    # (PB-006, Passo 6) — apenas desenvolvimento local, nunca segredo real.
    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/app"

    # URL do realm no Identity Provider (issuer OIDC), usada para descobrir
    # o JWKS e validar o claim "iss" de todo access token (ADR-021/ADR-022).
    keycloak_issuer_url: str = "http://localhost:8080/realms/app"

    # Client ID esperado no claim "aud"/"azp". None desativa essa validação —
    # para um client público de SPA, o Identity Provider nem sempre inclui
    # "aud" no access token por padrão, então validar isso é opcional aqui.
    keycloak_audience: str | None = None

    # Origens explícitas por ambiente (SEC-001, Seção 8) — nunca "*" numa
    # aplicação autenticada. Cada aplicação consumidora deverá sobrescrever
    # via variável de ambiente com as origens reais do seu frontend.
    cors_allowed_origins: list[str] = ["http://localhost:5173"]

    # Bate com o serviço "valkey" do docker-compose.yml de referência
    # (PB-006, Passo 6).
    valkey_url: str = "redis://localhost:6379/0"


@lru_cache
def get_settings() -> Settings:
    return Settings()

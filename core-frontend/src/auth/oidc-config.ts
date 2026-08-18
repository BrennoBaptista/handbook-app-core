import { InMemoryWebStorage, WebStorageStateStore } from "oidc-client-ts";
import type { AuthProviderNoUserManagerProps } from "react-oidc-context";

export interface CreateOidcConfigOptions {
  /** URL do realm/issuer no Identity Provider (ex.: Keycloak — ADR-021). */
  authority: string;
  /** Client ID público configurado no Identity Provider (Authorization Code + PKCE). */
  clientId: string;
  /** Caminho do callback de login, relativo à origem. @default "/auth/callback" */
  callbackPath?: string;
  /** @default "openid profile email" */
  scope?: string;
}

/**
 * RA-008, Seção 11 / RN-FE-004 — o token de acesso nunca deverá ser
 * persistido em localStorage/sessionStorage. `userStore` guarda o usuário
 * autenticado (access_token + refresh_token inclusos) — forçamos memória
 * pura em vez do padrão da biblioteca (sessionStorage). O efeito colateral é
 * perder a sessão ao recarregar a página; mitigado por
 * `automaticSilentRenew` + `useSilentSignInOnLoad` (../auth/silent-signin)
 * tentando reaproveitar a sessão SSO que o próprio Identity Provider mantém
 * (RA-008, Seção 11.1 — Cenário B).
 */
export function createOidcConfig(
  options: CreateOidcConfigOptions,
): AuthProviderNoUserManagerProps {
  const callbackPath = options.callbackPath ?? "/auth/callback";

  return {
    authority: options.authority,
    client_id: options.clientId,
    redirect_uri: `${window.location.origin}${callbackPath}`,
    post_logout_redirect_uri: window.location.origin,
    scope: options.scope ?? "openid profile email",
    response_type: "code",
    automaticSilentRenew: true,
    userStore: new WebStorageStateStore({ store: new InMemoryWebStorage() }),
    onSigninCallback: () => {
      window.history.replaceState({}, document.title, window.location.pathname);
    },
  };
}

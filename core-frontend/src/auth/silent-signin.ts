import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { useAuth } from "react-oidc-context";

/**
 * O token de acesso vive só em memória (RN-FE-004) — um reload de página
 * derruba a sessão local mesmo que a sessão SSO do próprio Identity Provider
 * ainda esteja ativa. Esta tentativa silenciosa reaproveita essa sessão sem
 * exigir clique em "Entrar" de novo. Uma falha aqui ("login_required") é o
 * resultado normal quando não há sessão SSO ativa, não um erro (RA-008,
 * Seção 11.1 — Cenário B).
 *
 * `callbackPath` deverá ser o mesmo valor passado a `createOidcConfig` —
 * evita disparar o signin silencioso durante o próprio processamento do
 * callback de login.
 */
export function useSilentSignInOnLoad(callbackPath = "/auth/callback") {
  const auth = useAuth();
  const location = useLocation();
  const attempted = useRef(false);

  useEffect(() => {
    if (attempted.current) return;
    if (location.pathname === callbackPath) return;
    if (auth.isLoading || auth.isAuthenticated) return;

    attempted.current = true;
    auth.signinSilent().catch(() => {
      // Sem sessão SSO ativa — usuário permanece deslogado até clicar em
      // "Entrar", comportamento esperado.
    });
  }, [auth, location.pathname, callbackPath]);
}

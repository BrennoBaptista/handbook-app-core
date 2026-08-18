import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "react-oidc-context";

export interface ProtectedRouteProps {
  children: ReactNode;
  /** Rota para onde redirecionar quando não autenticado. @default "/" */
  redirectTo?: string;
  /** Exibido enquanto a sessão ainda está sendo resolvida. */
  loadingFallback?: ReactNode;
}

/**
 * RA-008, Seção 11 — o frontend nunca decide autorização como mecanismo de
 * segurança, apenas como conveniência de UX; a decisão real é sempre do
 * backend (SEC-001, Seção 5). Este componente só evita renderizar a rota
 * protegida sem sessão local — cada chamada à API continua validando o
 * token no backend independentemente disto.
 */
export function ProtectedRoute({
  children,
  redirectTo = "/",
  loadingFallback = null,
}: ProtectedRouteProps) {
  const auth = useAuth();

  if (auth.isLoading) {
    return <>{loadingFallback}</>;
  }

  if (!auth.isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  return <>{children}</>;
}

import type { ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider, type AuthProviderProps } from "react-oidc-context";
import { BrowserRouter } from "react-router-dom";

const queryClient = new QueryClient();

export interface ProvidersProps {
  children: ReactNode;
  oidcConfig: AuthProviderProps;
}

/**
 * Composição padrão de providers de aplicação (RA-008): autenticação OIDC,
 * cache de dados de servidor (TanStack Query — OTS-001, Seção 7.3) e
 * roteamento client-side. A aplicação consumidora passa seu próprio
 * `oidcConfig` (ver `createOidcConfig`) — este componente nunca conhece
 * detalhes de um Identity Provider específico.
 */
export function Providers({ children, oidcConfig }: ProvidersProps) {
  return (
    <AuthProvider {...oidcConfig}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>{children}</BrowserRouter>
      </QueryClientProvider>
    </AuthProvider>
  );
}

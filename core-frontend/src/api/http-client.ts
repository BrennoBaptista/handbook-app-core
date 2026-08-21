import { useAuth } from "react-oidc-context";

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly details: Record<string, unknown>;

  constructor(
    code: string,
    message: string,
    status: number,
    details: Record<string, unknown>,
  ) {
    super(message);
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export interface ApiClient {
  request<T>(path: string, init?: RequestInit): Promise<T>;
}

/**
 * RN-FE-002 — nenhum componente de UI deverá chamar a API diretamente; toda
 * comunicação passa por este client, consumido através de hooks de cada
 * feature (RA-008, Seção 6). Anexa o access_token em memória quando
 * disponível; endpoints públicos funcionam normalmente sem ele.
 *
 * `baseUrl` é obrigatório e específico de cada aplicação consumidora — este
 * pacote nunca presume onde o backend está hospedado. Uso recomendado:
 *
 *     // shared/api/client.ts, na aplicação consumidora
 *     export const { useApiClient } = createApiClient(import.meta.env.VITE_API_BASE_URL);
 */
export function createApiClient(baseUrl: string): {
  useApiClient: () => ApiClient;
} {
  function useApiClient(): ApiClient {
    const auth = useAuth();

    async function request<T>(path: string, init?: RequestInit): Promise<T> {
      const headers = new Headers(init?.headers);
      // `FormData` (upload de arquivo/multipart) nunca deve ganhar um
      // Content-Type manual — o browser precisa gerar o próprio boundary
      // (`multipart/form-data; boundary=...`) a partir do body; forçar
      // "application/json" aqui quebra qualquer upload que passe por este
      // client (handbook-test-app, specs/furos.md F-030).
      const isFormData = init?.body instanceof FormData;
      if (!isFormData) {
        headers.set("Content-Type", "application/json");
      }
      if (auth.user?.access_token) {
        headers.set("Authorization", `Bearer ${auth.user.access_token}`);
      }

      const response = await fetch(`${baseUrl}${path}`, { ...init, headers });

      if (!response.ok) {
        const body = await response.json().catch(() => null);
        const error = body?.error;
        // Contrato único de erro — API-001, Seção 7.
        throw new ApiError(
          error?.code ?? "UNKNOWN_ERROR",
          error?.message ?? response.statusText,
          response.status,
          error?.details ?? {},
        );
      }

      if (response.status === 204) {
        return undefined as T;
      }

      return response.json() as Promise<T>;
    }

    return { request };
  }

  return { useApiClient };
}

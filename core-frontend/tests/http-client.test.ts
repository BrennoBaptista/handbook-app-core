import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { ApiError, createApiClient } from "../src/api/http-client";

const mockUseAuth = vi.fn();
vi.mock("react-oidc-context", () => ({
  useAuth: () => mockUseAuth(),
}));

describe("createApiClient", () => {
  beforeEach(() => {
    mockUseAuth.mockReturnValue({ user: null });
    global.fetch = vi.fn();
  });

  it("should attach the access token when authenticated", async () => {
    mockUseAuth.mockReturnValue({ user: { access_token: "token-123" } });
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(JSON.stringify({ data: [] }), { status: 200 }),
    );

    const { useApiClient } = createApiClient("http://api.test");
    const { result } = renderHook(() => useApiClient());

    await result.current.request("/products");

    const [, init] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0];
    expect((init.headers as Headers).get("Authorization")).toBe("Bearer token-123");
  });

  it("should not attach an Authorization header when unauthenticated", async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(JSON.stringify({ data: [] }), { status: 200 }),
    );

    const { useApiClient } = createApiClient("http://api.test");
    const { result } = renderHook(() => useApiClient());

    await result.current.request("/products");

    const [, init] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0];
    expect((init.headers as Headers).get("Authorization")).toBeNull();
  });

  it("should return parsed JSON body on success", async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(JSON.stringify({ data: [{ id: 1 }] }), { status: 200 }),
    );

    const { useApiClient } = createApiClient("http://api.test");
    const { result } = renderHook(() => useApiClient());

    const body = await result.current.request("/products");

    expect(body).toEqual({ data: [{ id: 1 }] });
  });

  it("should return undefined for a 204 response", async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(null, { status: 204 }),
    );

    const { useApiClient } = createApiClient("http://api.test");
    const { result } = renderHook(() => useApiClient());

    const body = await result.current.request("/products/1");

    expect(body).toBeUndefined();
  });

  it("should throw ApiError with the API-001 error contract on failure", async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response(
        JSON.stringify({
          error: { code: "NOT_FOUND", message: "Not found.", details: { id: "1" } },
        }),
        { status: 404 },
      ),
    );

    const { useApiClient } = createApiClient("http://api.test");
    const { result } = renderHook(() => useApiClient());

    await expect(result.current.request("/products/1")).rejects.toMatchObject({
      code: "NOT_FOUND",
      message: "Not found.",
      status: 404,
      details: { id: "1" },
    });
  });

  it("should fall back to defaults when the error body is not well-formed", async () => {
    (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue(
      new Response("not json", {
        status: 500,
        statusText: "Internal Server Error",
      }),
    );

    const { useApiClient } = createApiClient("http://api.test");
    const { result } = renderHook(() => useApiClient());

    await expect(result.current.request("/boom")).rejects.toMatchObject({
      code: "UNKNOWN_ERROR",
      message: "Internal Server Error",
      status: 500,
    });
  });
});

describe("ApiError", () => {
  it("should expose code, status and details", () => {
    const error = new ApiError("X", "message", 400, { field: "y" });

    expect(error.code).toBe("X");
    expect(error.message).toBe("message");
    expect(error.status).toBe(400);
    expect(error.details).toEqual({ field: "y" });
  });
});

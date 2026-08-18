import { describe, expect, it } from "vitest";
import { createOidcConfig } from "../src/auth/oidc-config";

describe("createOidcConfig", () => {
  it("should use the provided authority and clientId", () => {
    const config = createOidcConfig({
      authority: "http://localhost:8080/realms/app",
      clientId: "web-frontend",
    });

    expect(config.authority).toBe("http://localhost:8080/realms/app");
    expect(config.client_id).toBe("web-frontend");
  });

  it("should default the callback path to /auth/callback", () => {
    const config = createOidcConfig({
      authority: "http://localhost:8080/realms/app",
      clientId: "web-frontend",
    });

    expect(config.redirect_uri).toBe(`${window.location.origin}/auth/callback`);
  });

  it("should honor a custom callback path", () => {
    const config = createOidcConfig({
      authority: "http://localhost:8080/realms/app",
      clientId: "web-frontend",
      callbackPath: "/sso/callback",
    });

    expect(config.redirect_uri).toBe(`${window.location.origin}/sso/callback`);
  });

  it("should default scope to openid profile email", () => {
    const config = createOidcConfig({
      authority: "http://localhost:8080/realms/app",
      clientId: "web-frontend",
    });

    expect(config.scope).toBe("openid profile email");
  });

  it("should honor a custom scope", () => {
    const config = createOidcConfig({
      authority: "http://localhost:8080/realms/app",
      clientId: "web-frontend",
      scope: "openid profile",
    });

    expect(config.scope).toBe("openid profile");
  });

  it("should always use the Authorization Code flow", () => {
    const config = createOidcConfig({
      authority: "http://localhost:8080/realms/app",
      clientId: "web-frontend",
    });

    expect(config.response_type).toBe("code");
    expect(config.automaticSilentRenew).toBe(true);
  });
});

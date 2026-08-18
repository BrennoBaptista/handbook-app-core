import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { useSilentSignInOnLoad } from "../src/auth/silent-signin";

const mockUseAuth = vi.fn();
const mockUseLocation = vi.fn();

vi.mock("react-oidc-context", () => ({
  useAuth: () => mockUseAuth(),
}));
vi.mock("react-router-dom", () => ({
  useLocation: () => mockUseLocation(),
}));

describe("useSilentSignInOnLoad", () => {
  const signinSilent = vi.fn();

  beforeEach(() => {
    signinSilent.mockReset().mockResolvedValue(undefined);
    mockUseLocation.mockReturnValue({ pathname: "/" });
  });

  it("should attempt a silent sign-in when not authenticated and not loading", () => {
    mockUseAuth.mockReturnValue({
      isLoading: false,
      isAuthenticated: false,
      signinSilent,
    });

    renderHook(() => useSilentSignInOnLoad());

    expect(signinSilent).toHaveBeenCalledTimes(1);
  });

  it("should not attempt when already authenticated", () => {
    mockUseAuth.mockReturnValue({
      isLoading: false,
      isAuthenticated: true,
      signinSilent,
    });

    renderHook(() => useSilentSignInOnLoad());

    expect(signinSilent).not.toHaveBeenCalled();
  });

  it("should not attempt while auth is still loading", () => {
    mockUseAuth.mockReturnValue({
      isLoading: true,
      isAuthenticated: false,
      signinSilent,
    });

    renderHook(() => useSilentSignInOnLoad());

    expect(signinSilent).not.toHaveBeenCalled();
  });

  it("should not attempt on the callback path", () => {
    mockUseLocation.mockReturnValue({ pathname: "/auth/callback" });
    mockUseAuth.mockReturnValue({
      isLoading: false,
      isAuthenticated: false,
      signinSilent,
    });

    renderHook(() => useSilentSignInOnLoad());

    expect(signinSilent).not.toHaveBeenCalled();
  });

  it("should honor a custom callback path", () => {
    mockUseLocation.mockReturnValue({ pathname: "/sso/callback" });
    mockUseAuth.mockReturnValue({
      isLoading: false,
      isAuthenticated: false,
      signinSilent,
    });

    renderHook(() => useSilentSignInOnLoad("/sso/callback"));

    expect(signinSilent).not.toHaveBeenCalled();
  });

  it("should only attempt once even if re-rendered", () => {
    mockUseAuth.mockReturnValue({
      isLoading: false,
      isAuthenticated: false,
      signinSilent,
    });

    const { rerender } = renderHook(() => useSilentSignInOnLoad());
    rerender();
    rerender();

    expect(signinSilent).toHaveBeenCalledTimes(1);
  });
});

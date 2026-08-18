import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "../src/auth/protected-route";

const mockUseAuth = vi.fn();
vi.mock("react-oidc-context", () => ({
  useAuth: () => mockUseAuth(),
}));

describe("ProtectedRoute", () => {
  it("should render children when authenticated", () => {
    mockUseAuth.mockReturnValue({ isLoading: false, isAuthenticated: true });

    render(
      <MemoryRouter>
        <ProtectedRoute>
          <p>secret content</p>
        </ProtectedRoute>
      </MemoryRouter>,
    );

    expect(screen.getByText("secret content")).toBeInTheDocument();
  });

  it("should render the loading fallback while auth is resolving", () => {
    mockUseAuth.mockReturnValue({ isLoading: true, isAuthenticated: false });

    render(
      <MemoryRouter>
        <ProtectedRoute loadingFallback={<p>loading...</p>}>
          <p>secret content</p>
        </ProtectedRoute>
      </MemoryRouter>,
    );

    expect(screen.getByText("loading...")).toBeInTheDocument();
    expect(screen.queryByText("secret content")).not.toBeInTheDocument();
  });

  it("should redirect to the default route when not authenticated", () => {
    mockUseAuth.mockReturnValue({ isLoading: false, isAuthenticated: false });

    render(
      <MemoryRouter initialEntries={["/account"]}>
        <Routes>
          <Route path="/" element={<p>home page</p>} />
          <Route
            path="/account"
            element={
              <ProtectedRoute>
                <p>secret content</p>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText("home page")).toBeInTheDocument();
    expect(screen.queryByText("secret content")).not.toBeInTheDocument();
  });

  it("should redirect to a custom route when provided", () => {
    mockUseAuth.mockReturnValue({ isLoading: false, isAuthenticated: false });

    render(
      <MemoryRouter initialEntries={["/account"]}>
        <Routes>
          <Route path="/login" element={<p>login page</p>} />
          <Route
            path="/account"
            element={
              <ProtectedRoute redirectTo="/login">
                <p>secret content</p>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText("login page")).toBeInTheDocument();
  });
});

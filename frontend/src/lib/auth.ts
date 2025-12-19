const TOKEN_KEY = "pharmacy_auth_token";
const USER_KEY = "pharmacy_user";

export interface AuthUser {
  user_id: string;
  full_name: string;
  preferred_language: string;
}

// Use sessionStorage instead of localStorage so tokens are cleared when tab closes
// This prevents caching issues and ensures fresh login on new tabs
const storage = sessionStorage;

export function getToken(): string | null {
  return storage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  storage.setItem(TOKEN_KEY, token);
}

export function removeToken(): void {
  storage.removeItem(TOKEN_KEY);
}

export function getUser(): AuthUser | null {
  const userStr = storage.getItem(USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

export function setUser(user: AuthUser): void {
  storage.setItem(USER_KEY, JSON.stringify(user));
}

export function removeUser(): void {
  storage.removeItem(USER_KEY);
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

export function logout(): void {
  removeToken();
  removeUser();
}


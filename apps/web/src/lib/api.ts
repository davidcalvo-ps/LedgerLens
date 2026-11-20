/**
 * Thin fetch wrapper for the Django core API.
 *
 * Auth is a same-origin session cookie (HttpOnly, so JavaScript never sees
 * it). Unsafe requests echo the readable CSRF cookie in `X-CSRFToken`.
 * A 401 means the session is gone; subscribers (the auth provider) are told
 * so the app can send the person back to the sign-in page.
 */

export const CSRF_COOKIE = 'ledgerlens_csrftoken';
const API_ROOT = '/api/v1';
const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS']);

export class ApiError extends Error {
  readonly status: number;
  readonly body: unknown;

  constructor(status: number, body: unknown) {
    super(errorMessage(status, body));
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

/** Human-readable message from a DRF error body (`{detail}` or field errors). */
export function errorMessage(status: number, body: unknown): string {
  if (body && typeof body === 'object') {
    const detail = (body as Record<string, unknown>).detail;
    if (typeof detail === 'string') return detail;
    const first = Object.values(body as Record<string, unknown>)[0];
    if (Array.isArray(first) && typeof first[0] === 'string') return first[0];
  }
  if (status >= 500) return 'The server had a problem. Please try again.';
  return `Request failed (${status}).`;
}

export function readCookie(cookieString: string, name: string): string | null {
  for (const part of cookieString.split(';')) {
    const [key, ...rest] = part.trim().split('=');
    if (key === name) return decodeURIComponent(rest.join('='));
  }
  return null;
}

type Listener = () => void;
const unauthorizedListeners = new Set<Listener>();

/** Subscribe to "the session is no longer valid". Returns an unsubscribe function. */
export function onUnauthorized(listener: Listener): () => void {
  unauthorizedListeners.add(listener);
  return () => unauthorizedListeners.delete(listener);
}

async function csrfToken(): Promise<string> {
  const existing = readCookie(document.cookie, CSRF_COOKIE);
  if (existing) return existing;
  await fetch(`${API_ROOT}/auth/csrf`, { credentials: 'same-origin' });
  const issued = readCookie(document.cookie, CSRF_COOKIE);
  if (!issued) throw new ApiError(0, { detail: 'Could not start a secure session.' });
  return issued;
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';
  body?: unknown;
  signal?: AbortSignal;
  /** Do not broadcast a 401 (used by sign-in, where 401 is not "expired"). */
  quietUnauthorized?: boolean;
}

export async function api<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const method = options.method ?? 'GET';
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (options.body !== undefined) headers['Content-Type'] = 'application/json';
  if (!SAFE_METHODS.has(method)) headers['X-CSRFToken'] = await csrfToken();

  const response = await fetch(`${API_ROOT}${path}`, {
    method,
    headers,
    credentials: 'same-origin',
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
    signal: options.signal,
  });

  if (response.status === 204) return undefined as T;

  const body: unknown = response.headers.get('Content-Type')?.includes('application/json')
    ? await response.json()
    : null;

  if (!response.ok) {
    if (response.status === 401 && !options.quietUnauthorized) {
      unauthorizedListeners.forEach((listener) => listener());
    }
    throw new ApiError(response.status, body);
  }
  return body as T;
}

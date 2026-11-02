export type CartItem = {
  id: number;
  sku: string;
  name: string;
  slug: string;
  size_uk: string;
  quantity: number;
  unit_price: number;
  line_total: number;
  available: number;
  reservation_expires_at: string | null;
};

export type Cart = {
  token: string;
  status: string;
  expires_at: string | null;
  items: CartItem[];
  subtotal_inr: number;
  total_units: number;
  reservation_minutes: number;
  rules: Record<string, string | number>;
};

const CART_TOKEN_KEY = "santvana.cart.token";
const CART_BASE = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
).replace(/\/$/, "");

export function readCartToken(): string | null {
  try {
    return window.localStorage.getItem(CART_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function writeCartToken(token: string): void {
  try {
    window.localStorage.setItem(CART_TOKEN_KEY, token);
  } catch {
    // Storage can be unavailable in private modes. The cart still works for
    // this page view; it just cannot be restored on the next visit.
  }
}

export function clearCartToken(): void {
  try {
    window.localStorage.removeItem(CART_TOKEN_KEY);
  } catch {
    // Ignore storage failures.
  }
}

async function parse(response: Response): Promise<Cart> {
  const data: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const detail =
      data && typeof data === "object" && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : `Cart request failed (${response.status})`;
    throw new Error(detail);
  }
  return data as Cart;
}

async function request(
  path: string,
  init: RequestInit,
  token?: string,
): Promise<Cart> {
  const headers: Record<string, string> = {
    accept: "application/json",
    "content-type": "application/json",
  };
  if (token) headers["X-Cart-Token"] = token;
  const response = await fetch(`${CART_BASE}${path}`, {
    ...init,
    cache: "no-store",
    headers,
  });
  return parse(response);
}

export function createCart(): Promise<Cart> {
  return request("/cart", { method: "POST" });
}

export function fetchCart(token: string): Promise<Cart> {
  return request("/cart", { method: "GET" }, token);
}

export function addCartItem(
  token: string,
  sku: string,
  quantity: number,
): Promise<Cart> {
  return request(
    "/cart/items",
    { method: "POST", body: JSON.stringify({ sku, quantity }) },
    token,
  );
}

export function updateCartItem(
  token: string,
  itemId: number,
  quantity: number,
): Promise<Cart> {
  return request(
    `/cart/items/${itemId}`,
    { method: "PATCH", body: JSON.stringify({ quantity }) },
    token,
  );
}

export function removeCartItem(token: string, itemId: number): Promise<Cart> {
  return request(`/cart/items/${itemId}`, { method: "DELETE" }, token);
}

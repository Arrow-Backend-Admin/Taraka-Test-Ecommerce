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
  max_reservable: number;
  reservation_expires_at: string | null;
};

export type Cart = {
  status: string;
  expires_at: string | null;
  items: CartItem[];
  subtotal_inr: number;
  total_units: number;
  reservation_minutes: number;
  rules: Record<string, string | number>;
};

const CART_BASE = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
).replace(/\/$/, "");

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

async function request(path: string, init: RequestInit): Promise<Cart> {
  const response = await fetch(`${CART_BASE}${path}`, {
    ...init,
    cache: "no-store",
    // The guest cart token is an httpOnly cookie. It is never exposed to
    // JavaScript, so every cart call must opt in to sending credentials.
    credentials: "include",
    headers: {
      accept: "application/json",
      "content-type": "application/json",
    },
  });
  return parse(response);
}

export function createCart(): Promise<Cart> {
  return request("/cart", { method: "POST" });
}

export function fetchCart(): Promise<Cart> {
  return request("/cart", { method: "GET" });
}

export function addCartItem(sku: string, quantity: number): Promise<Cart> {
  return request("/cart/items", {
    method: "POST",
    body: JSON.stringify({ sku, quantity }),
  });
}

export function updateCartItem(
  itemId: number,
  quantity: number,
): Promise<Cart> {
  return request(`/cart/items/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify({ quantity }),
  });
}

export function removeCartItem(itemId: number): Promise<Cart> {
  return request(`/cart/items/${itemId}`, { method: "DELETE" });
}

export async function clearCart(): Promise<void> {
  try {
    await fetch(`${CART_BASE}/cart`, {
      method: "DELETE",
      credentials: "include",
    });
  } catch {
    // The cookie may already be gone. Nothing to recover.
  }
}

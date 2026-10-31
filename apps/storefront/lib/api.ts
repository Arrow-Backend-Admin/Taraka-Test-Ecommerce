export type PublicProduct = {
  id: string;
  name: string;
  slug: string;
  category: string;
  sub_category: string | null;
  audience: string | null;
  tier: string;
  tier_label: string | null;
  colour: string;
  colour_hex: string;
  price_inr: number;
  mrp_inr: number;
  summary: string | null;
  hero: boolean;
  image: string | null;
  features: string[];
};

const API_BASE = (
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000"
).replace(/\/$/, "");

const UNRESOLVED = /\[TO CONFIRM/i;

export function safeText(value: unknown): string | null {
  if (typeof value !== "string") return null;
  return UNRESOLVED.test(value) ? null : value;
}

function isSafeProduct(value: unknown): value is PublicProduct {
  if (!value || typeof value !== "object") return false;
  const product = value as Record<string, unknown>;
  if (
    typeof product.id !== "string" ||
    typeof product.name !== "string" ||
    typeof product.price_inr !== "number"
  ) {
    return false;
  }
  return !UNRESOLVED.test(JSON.stringify(product));
}

export async function getCatalogue(): Promise<PublicProduct[]> {
  try {
    const response = await fetch(`${API_BASE}/catalogue`, {
      cache: "no-store",
      headers: { accept: "application/json" },
    });
    if (!response.ok) return [];
    const data: unknown = await response.json();
    if (!Array.isArray(data)) return [];
    return data.filter(isSafeProduct);
  } catch {
    return [];
  }
}

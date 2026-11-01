export type PublicImage = {
  role: string;
  filename: string;
  url: string | null;
  alt: string;
  is_placeholder: boolean;
  aspect: string;
  placeholder_notice: string | null;
};

export type PublicVariant = {
  sku: string;
  size_uk: string;
  size_eu: string | null;
  size_us_men: string | null;
  size_us_women: string | null;
  foot_length_cm: number | null;
  foot_length_note: string | null;
  price_inr: number;
  available: number;
};

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
  images: PublicImage[];
  status: string;
  preview: boolean;
  features: string[];
  unresolved_fields?: string[];
  description?: string | null;
  sizes?: PublicVariant[];
  materials?: Record<string, string>;
  fit_notes?: string | null;
  care?: string | null;
  seo_title?: string | null;
  seo_description?: string | null;
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

export function previewDraftsEnabled(): boolean {
  return (
    process.env.PREVIEW_DRAFTS === "true" &&
    process.env.APP_ENV !== "production"
  );
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

function catalogueUrl(previewDrafts: boolean): string {
  const query = previewDrafts ? "?preview_drafts=true" : "";
  return `${API_BASE}/catalogue${query}`;
}

export async function getCatalogue(options?: {
  previewDrafts?: boolean;
}): Promise<PublicProduct[]> {
  const previewDrafts = Boolean(options?.previewDrafts && previewDraftsEnabled());
  try {
    const response = await fetch(catalogueUrl(previewDrafts), {
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

export async function getProduct(
  slug: string,
  options?: { previewDrafts?: boolean },
): Promise<PublicProduct | null> {
  const previewDrafts = Boolean(options?.previewDrafts && previewDraftsEnabled());
  const query = previewDrafts ? "?preview_drafts=true" : "";
  try {
    const response = await fetch(
      `${API_BASE}/catalogue/${encodeURIComponent(slug)}${query}`,
      {
        cache: "no-store",
        headers: { accept: "application/json" },
      },
    );
    if (!response.ok) return null;
    const data: unknown = await response.json();
    return isSafeProduct(data) ? data : null;
  } catch {
    return null;
  }
}

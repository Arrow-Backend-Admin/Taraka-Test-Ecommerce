export type PublicImage = {
  role: string;
  filename: string;
  url: string | null;
  alt: string;
  is_placeholder: boolean;
  aspect: string;
  placeholder_notice: string | null;
  kind: "photo" | "image_coming" | string;
  changes: string | null;
  source: string | null;
  source_title: string | null;
  source_url: string | null;
  photographer: string | null;
  licence_name: string | null;
  licence_url: string | null;
  attribution: string | null;
  qa_result: string | null;
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

export type CatalogueFilters = {
  q?: string;
  category?: string;
  colour?: string;
  size?: string;
  minPrice?: string;
  maxPrice?: string;
};

export type Facet = { value: string; label?: string; hex?: string; count: number };

export type Facets = {
  categories: Facet[];
  colours: Facet[];
  sizes: Facet[];
  price: { min: number | null; max: number | null };
};

export type StockSize = {
  sku: string;
  size_uk: string;
  available: number;
};

export type Stock = {
  slug: string;
  sizes: StockSize[];
  as_of: string;
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

function catalogueQuery(
  previewDrafts: boolean,
  filters?: CatalogueFilters,
): string {
  const params = new URLSearchParams();
  if (previewDrafts) params.set("preview_drafts", "true");
  if (filters?.q) params.set("q", filters.q);
  if (filters?.category) params.set("category", filters.category);
  if (filters?.colour) params.set("colour", filters.colour);
  if (filters?.size) params.set("size", filters.size);
  if (filters?.minPrice) params.set("min_price", filters.minPrice);
  if (filters?.maxPrice) params.set("max_price", filters.maxPrice);
  const query = params.toString();
  return query ? `?${query}` : "";
}

export async function getCatalogue(options?: {
  previewDrafts?: boolean;
  filters?: CatalogueFilters;
}): Promise<PublicProduct[]> {
  const previewDrafts = Boolean(options?.previewDrafts && previewDraftsEnabled());
  try {
    const response = await fetch(
      `${API_BASE}/catalogue${catalogueQuery(previewDrafts, options?.filters)}`,
      {
        cache: "no-store",
        headers: { accept: "application/json" },
      },
    );
    if (!response.ok) return [];
    const data: unknown = await response.json();
    if (!Array.isArray(data)) return [];
    return data.filter(isSafeProduct);
  } catch {
    return [];
  }
}

export async function getFacets(options?: {
  previewDrafts?: boolean;
  filters?: CatalogueFilters;
}): Promise<Facets | null> {
  const previewDrafts = Boolean(options?.previewDrafts && previewDraftsEnabled());
  try {
    const response = await fetch(
      `${API_BASE}/catalogue/facets${catalogueQuery(
        previewDrafts,
        options?.filters,
      )}`,
      {
        cache: "no-store",
        headers: { accept: "application/json" },
      },
    );
    if (!response.ok) return null;
    const data: unknown = await response.json();
    if (!data || typeof data !== "object") return null;
    return data as Facets;
  } catch {
    return null;
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

export async function getStock(slug: string): Promise<Stock | null> {
  try {
    const response = await fetch(
      `${API_BASE}/catalogue/${encodeURIComponent(slug)}/stock`,
      {
        cache: "no-store",
        headers: { accept: "application/json" },
      },
    );
    if (!response.ok) return null;
    const data: unknown = await response.json();
    if (!data || typeof data !== "object") return null;
    return data as Stock;
  } catch {
    return null;
  }
}

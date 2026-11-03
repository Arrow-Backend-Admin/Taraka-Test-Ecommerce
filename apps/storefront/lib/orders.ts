export type OrderItem = {
  product_name: string;
  product_slug: string;
  sku: string;
  size_uk: string;
  quantity: number;
  unit_price_paise: number;
  line_total_paise: number;
  taxable_value_paise: number;
  gst_paise: number;
  gst_rate_pct: number;
};

export type OrderPayment = {
  provider_order_id: string;
  status: string;
  amount_paise: number;
  method: string | null;
};

export type OrderAddress = {
  line1: string;
  line2: string | null;
  city: string;
  state: string;
  pincode: string;
  country: string;
};

export type Order = {
  public_id: string;
  status: string;
  currency: string;
  created_at: string;
  paid_at: string | null;
  expired_at: string | null;
  reservation_expires_at: string | null;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  address: OrderAddress;
  seller: { state: string; gstin: string };
  items: OrderItem[];
  subtotal_paise: number;
  gst_paise: number;
  shipping_paise: number;
  total_paise: number;
  latest_payment: OrderPayment | null;
  next_action: string;
  message: string;
};

export type CheckoutOptions = {
  provider: string;
  key_id: string | null;
  order_id: string;
  amount_paise: number;
  currency: string;
  name: string;
  description: string;
  mock: boolean;
  prefill: { name: string; email: string; contact: string };
};

export type OrderCreated = Order & { checkout: CheckoutOptions | null };

export type CheckoutRequest = {
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  address: {
    line1: string;
    line2?: string | null;
    city: string;
    state: string;
    pincode: string;
    country: string;
  };
};

export type PaymentVerifyResult = {
  verified: boolean;
  order_status: string;
  message: string;
};

// Mirrors apps/api/app/schemas.py. This list only drives the select control;
// the API validates the state again and rejects anything it does not know.
export const INDIAN_STATES = [
  "Andhra Pradesh",
  "Arunachal Pradesh",
  "Assam",
  "Bihar",
  "Chhattisgarh",
  "Goa",
  "Gujarat",
  "Haryana",
  "Himachal Pradesh",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "Madhya Pradesh",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Mizoram",
  "Nagaland",
  "Odisha",
  "Punjab",
  "Rajasthan",
  "Sikkim",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "Uttar Pradesh",
  "Uttarakhand",
  "West Bengal",
  "Andaman and Nicobar Islands",
  "Chandigarh",
  "Dadra and Nagar Haveli and Daman and Diu",
  "Delhi",
  "Jammu and Kashmir",
  "Ladakh",
  "Lakshadweep",
  "Puducherry",
] as const;

const API_BASE = (
  (typeof window === "undefined" ? process.env.API_URL : undefined) ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000"
).replace(/\/$/, "");

function detailMessage(data: unknown, fallback: string): string {
  if (!data || typeof data !== "object" || !("detail" in data)) return fallback;
  const detail = (data as { detail: unknown }).detail;
  if (typeof detail === "string") return detail;
  if (detail && typeof detail === "object" && "message" in detail) {
    return String((detail as { message: unknown }).message);
  }
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0] as { msg?: unknown };
    if (first && typeof first.msg === "string") return first.msg;
  }
  return fallback;
}

async function parse<T>(response: Response, fallback: string): Promise<T> {
  const data: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(detailMessage(data, `${fallback} (${response.status})`));
  }
  return data as T;
}

export class OrderRequestError extends Error {
  orderId?: string;

  constructor(message: string, orderId?: string) {
    super(message);
    this.name = "OrderRequestError";
    this.orderId = orderId;
  }
}

export async function createOrder(payload: CheckoutRequest): Promise<OrderCreated> {
  const response = await fetch(`${API_BASE}/orders`, {
    method: "POST",
    cache: "no-store",
    credentials: "include",
    headers: {
      accept: "application/json",
      "content-type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  const data: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    let orderId: string | undefined;
    if (data && typeof data === "object" && "detail" in data) {
      const detail = (data as { detail: unknown }).detail;
      if (detail && typeof detail === "object" && "order_id" in detail) {
        orderId = String((detail as { order_id: unknown }).order_id);
      }
    }
    throw new OrderRequestError(
      detailMessage(data, `Could not create the order (${response.status})`),
      orderId,
    );
  }
  return data as OrderCreated;
}

export async function getOrder(publicId: string): Promise<Order | null> {
  try {
    const response = await fetch(`${API_BASE}/orders/${encodeURIComponent(publicId)}`, {
      cache: "no-store",
      headers: { accept: "application/json" },
    });
    if (!response.ok) return null;
    return (await response.json()) as Order;
  } catch {
    return null;
  }
}

export async function retryPayment(publicId: string): Promise<OrderCreated> {
  const response = await fetch(
    `${API_BASE}/orders/${encodeURIComponent(publicId)}/payment`,
    {
      method: "POST",
      cache: "no-store",
      credentials: "include",
      headers: { accept: "application/json" },
    },
  );
  return parse<OrderCreated>(response, "Could not start the payment");
}

export async function verifyPaymentHint(
  publicId: string,
  payload: {
    razorpay_order_id: string;
    razorpay_payment_id: string;
    razorpay_signature: string;
  },
): Promise<PaymentVerifyResult> {
  const response = await fetch(
    `${API_BASE}/orders/${encodeURIComponent(publicId)}/payment-verify`,
    {
      method: "POST",
      cache: "no-store",
      credentials: "include",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify(payload),
    },
  );
  return parse<PaymentVerifyResult>(response, "Could not verify the payment");
}

export async function mockPay(publicId: string): Promise<Order> {
  const response = await fetch(
    `${API_BASE}/orders/${encodeURIComponent(publicId)}/mock-pay`,
    {
      method: "POST",
      cache: "no-store",
      credentials: "include",
      headers: { accept: "application/json" },
    },
  );
  return parse<Order>(response, "Could not complete the mock payment");
}

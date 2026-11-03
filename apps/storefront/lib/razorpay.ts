import type { CheckoutOptions } from "./orders";

export type RazorpayResponse = {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
};

type RazorpayOptions = {
  key: string;
  order_id: string;
  amount: number;
  currency: string;
  name: string;
  description: string;
  prefill: { name: string; email: string; contact: string };
  notes: Record<string, string>;
  theme: { color: string };
  handler: (response: RazorpayResponse) => void;
  modal: { ondismiss: () => void };
};

type RazorpayInstance = {
  open: () => void;
  on: (event: string, handler: () => void) => void;
};

declare global {
  interface Window {
    Razorpay?: new (options: RazorpayOptions) => RazorpayInstance;
  }
}

export function loadRazorpay(): Promise<void> {
  if (typeof window === "undefined") {
    return Promise.reject(new Error("Razorpay checkout needs a browser."));
  }
  if (window.Razorpay) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(
      "script[data-razorpay-checkout]",
    );
    if (existing) {
      existing.addEventListener("load", () => resolve());
      existing.addEventListener("error", () =>
        reject(new Error("Could not load Razorpay checkout.")),
      );
      return;
    }
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.async = true;
    script.dataset.razorpayCheckout = "true";
    script.onload = () => resolve();
    script.onerror = () =>
      reject(new Error("Could not load Razorpay checkout. Check the network."));
    document.body.appendChild(script);
  });
}

export async function openRazorpayCheckout({
  checkout,
  publicId,
  onPaid,
  onDismiss,
  onFailed,
}: {
  checkout: CheckoutOptions;
  publicId: string;
  onPaid: (response: RazorpayResponse) => void;
  onDismiss: () => void;
  onFailed: () => void;
}): Promise<void> {
  if (!checkout.key_id) {
    throw new Error(
      "Payment is not configured on this server. Use the local mock payment or contact the store.",
    );
  }
  await loadRazorpay();
  const Razorpay = window.Razorpay;
  if (!Razorpay) throw new Error("Razorpay checkout did not load.");
  const instance = new Razorpay({
    key: checkout.key_id,
    order_id: checkout.order_id,
    amount: checkout.amount_paise,
    currency: checkout.currency,
    name: checkout.name,
    description: checkout.description,
    prefill: checkout.prefill,
    notes: { order_id: publicId },
    theme: { color: "#1F1B16" },
    handler: onPaid,
    modal: { ondismiss: onDismiss },
  });
  instance.on("payment.failed", onFailed);
  instance.open();
}

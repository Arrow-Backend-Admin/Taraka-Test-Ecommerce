"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { fetchCart, type Cart } from "@/lib/cart";
import {
  INDIAN_STATES,
  OrderRequestError,
  createOrder,
  mockPay,
  verifyPaymentHint,
  type CheckoutOptions,
  type OrderCreated,
} from "@/lib/orders";
import { openRazorpayCheckout } from "@/lib/razorpay";

const inr = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

type Message = { kind: "info" | "error"; text: string } | null;

type FormValues = {
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  line1: string;
  line2: string;
  city: string;
  state: string;
  pincode: string;
};

const EMPTY_FORM: FormValues = {
  customer_name: "",
  customer_email: "",
  customer_phone: "",
  line1: "",
  line2: "",
  city: "",
  state: "Karnataka",
  pincode: "",
};

export function CheckoutForm() {
  const router = useRouter();
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [values, setValues] = useState<FormValues>(EMPTY_FORM);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<Message>(null);
  const [created, setCreated] = useState<OrderCreated | null>(null);
  const [failedOrderId, setFailedOrderId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchCart()
      .then((next) => {
        if (!cancelled) setCart(next);
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setLoadError(
            error instanceof Error
              ? error.message
              : "Could not read your cart reservation.",
          );
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const totalUnits = useMemo(
    () => cart?.items.reduce((sum, item) => sum + item.quantity, 0) ?? 0,
    [cart],
  );

  function update(field: keyof FormValues, value: string) {
    setValues((current) => ({ ...current, [field]: value }));
  }

  async function openRazorpay(order: OrderCreated) {
    const checkout: CheckoutOptions | null = order.checkout;
    if (!checkout || !checkout.key_id) {
      setMessage({
        kind: "error",
        text: "Payment is not configured on this server. Use the local mock payment or contact the store.",
      });
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      await openRazorpayCheckout({
        checkout,
        publicId: order.public_id,
        onPaid: (response) => {
          // A valid browser signature is only a hint. The order page waits for
          // the signed webhook before it says "paid".
          void verifyPaymentHint(order.public_id, response)
            .catch(() => null)
            .finally(() => {
              router.push(`/orders/${order.public_id}`);
            });
        },
        onDismiss: () => {
          setBusy(false);
          setMessage({
            kind: "info",
            text: "The payment window closed. The reservation is held until it expires; you can reopen the payment.",
          });
        },
        onFailed: () => {
          setMessage({
            kind: "error",
            text: "The payment did not complete. The reservation is held until it expires.",
          });
        },
      });
    } catch (error) {
      setBusy(false);
      setMessage({
        kind: "error",
        text:
          error instanceof Error
            ? error.message
            : "Could not open Razorpay checkout.",
      });
    }
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setMessage(null);
    setFailedOrderId(null);
    try {
      const order = await createOrder({
        customer_name: values.customer_name,
        customer_email: values.customer_email,
        customer_phone: values.customer_phone,
        address: {
          line1: values.line1,
          line2: values.line2.trim() || null,
          city: values.city,
          state: values.state,
          pincode: values.pincode,
          country: "India",
        },
      });
      setCreated(order);
      if (order.checkout?.mock) {
        setBusy(false);
        setMessage({
          kind: "info",
          text: "Order created. Local review mode does not contact Razorpay; simulate the signed webhook below.",
        });
        return;
      }
      await openRazorpay(order);
    } catch (error) {
      setBusy(false);
      if (error instanceof OrderRequestError && error.orderId) {
        setFailedOrderId(error.orderId);
      }
      setMessage({
        kind: "error",
        text:
          error instanceof Error
            ? error.message
            : "Could not place the order. Try again.",
      });
    }
  }

  async function handleMockPay() {
    if (!created || busy) return;
    setBusy(true);
    setMessage(null);
    try {
      await mockPay(created.public_id);
      router.push(`/orders/${created.public_id}`);
    } catch (error) {
      setBusy(false);
      setMessage({
        kind: "error",
        text:
          error instanceof Error
            ? error.message
            : "Could not simulate the payment.",
      });
    }
  }

  if (loading) {
    return (
      <p className="mt-8 font-body text-sm text-muted">
        Reading your reservation…
      </p>
    );
  }

  if (loadError) {
    return (
      <div className="mt-8 rounded-md border border-[#a62b22]/30 bg-[#fbeae7] p-5 font-body text-sm leading-6 text-[#7a1f18]">
        <p>{loadError}</p>
        <p className="mt-2">
          Reservations last 15 minutes.{" "}
          <Link className="underline underline-offset-4" href="/catalogue">
            Return to the catalogue
          </Link>{" "}
          to add a size again.
        </p>
      </div>
    );
  }

  if (!cart || cart.status !== "active" || cart.items.length === 0) {
    return (
      <div className="mt-8 rounded-md border border-black/10 bg-white/60 p-5 font-body text-sm leading-6 text-muted">
        <p>
          {cart && cart.status !== "active"
            ? "This reservation expired and its units were released."
            : "Your cart is empty."}
        </p>
        <p className="mt-2">
          <Link className="underline underline-offset-4" href="/catalogue">
            Choose a size in the catalogue
          </Link>{" "}
          to start a new reservation.
        </p>
      </div>
    );
  }

  if (created) {
    return (
      <div className="mt-8 space-y-5">
        <div className="rounded-lg border border-black/10 bg-white/60 p-5">
          <p className="font-body text-[0.75rem] uppercase tracking-[0.14em] text-muted">
            Order created
          </p>
          <h2 className="mt-2 font-display text-2xl font-semibold">
            {created.public_id}
          </h2>
          <p className="mt-2 font-body text-sm leading-6 text-muted">
            {created.message}
          </p>
          <p className="mt-3 font-body text-sm">
            Total{" "}
            <span className="font-display text-lg font-semibold">
              {inr.format(created.total_paise / 100)}
            </span>{" "}
            <span className="text-muted">(GST included)</span>
          </p>

          {created.checkout?.mock ? (
            <div className="mt-4 rounded-md border border-black/10 bg-[#f4efe4] p-4">
              <p className="font-body text-sm leading-6 text-muted">
                Local review mode. No Razorpay account is contacted. This button
                signs a fake webhook and runs the same confirmation path as a
                real payment.
              </p>
              <button
                type="button"
                onClick={() => void handleMockPay()}
                disabled={busy}
                className="mt-3 rounded-full bg-ink px-6 py-3 font-body text-sm text-paper disabled:bg-black/20"
              >
                {busy ? "Confirming…" : "Simulate a successful payment"}
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => void openRazorpay(created)}
              disabled={busy}
              className="mt-4 rounded-full bg-ink px-6 py-3 font-body text-sm text-paper disabled:bg-black/20"
            >
              {busy ? "Opening…" : "Open Razorpay checkout"}
            </button>
          )}

          <p className="mt-4 font-body text-sm">
            <Link
              className="underline decoration-black/20 underline-offset-4"
              href={`/orders/${created.public_id}`}
            >
              View order status
            </Link>
          </p>
        </div>

        {message ? <MessageBlock message={message} /> : null}
      </div>
    );
  }

  return (
    <div className="mt-8 grid gap-8 lg:grid-cols-[minmax(0,1fr)_22rem]">
      <form className="space-y-6" onSubmit={(event) => void handleSubmit(event)}>
        <section className="rounded-lg border border-black/10 bg-white/60 p-5">
          <h2 className="font-display text-xl font-semibold">Contact</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <Field label="Full name" htmlFor="customer_name">
              <input
                id="customer_name"
                required
                minLength={2}
                autoComplete="name"
                value={values.customer_name}
                onChange={(event) => update("customer_name", event.target.value)}
                className={inputClass}
              />
            </Field>
            <Field label="Email" htmlFor="customer_email">
              <input
                id="customer_email"
                type="email"
                required
                autoComplete="email"
                value={values.customer_email}
                onChange={(event) => update("customer_email", event.target.value)}
                className={inputClass}
              />
            </Field>
            <Field label="Mobile number" htmlFor="customer_phone">
              <input
                id="customer_phone"
                type="tel"
                required
                inputMode="tel"
                autoComplete="tel"
                placeholder="98765 43210"
                value={values.customer_phone}
                onChange={(event) => update("customer_phone", event.target.value)}
                className={inputClass}
              />
            </Field>
          </div>
        </section>

        <section className="rounded-lg border border-black/10 bg-white/60 p-5">
          <h2 className="font-display text-xl font-semibold">
            Delivery address
          </h2>
          <p className="mt-1 font-body text-sm text-muted">
            Shipping is limited to India. The API validates the state and
            pincode again.
          </p>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <Field
              label="Address line 1"
              htmlFor="line1"
              className="sm:col-span-2"
            >
              <input
                id="line1"
                required
                minLength={5}
                autoComplete="address-line1"
                value={values.line1}
                onChange={(event) => update("line1", event.target.value)}
                className={inputClass}
              />
            </Field>
            <Field
              label="Address line 2 (optional)"
              htmlFor="line2"
              className="sm:col-span-2"
            >
              <input
                id="line2"
                autoComplete="address-line2"
                value={values.line2}
                onChange={(event) => update("line2", event.target.value)}
                className={inputClass}
              />
            </Field>
            <Field label="City" htmlFor="city">
              <input
                id="city"
                required
                minLength={2}
                autoComplete="address-level2"
                value={values.city}
                onChange={(event) => update("city", event.target.value)}
                className={inputClass}
              />
            </Field>
            <Field label="State or union territory" htmlFor="state">
              <select
                id="state"
                required
                value={values.state}
                onChange={(event) => update("state", event.target.value)}
                className={inputClass}
              >
                {INDIAN_STATES.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Pincode" htmlFor="pincode">
              <input
                id="pincode"
                required
                inputMode="numeric"
                pattern="[1-9][0-9]{5}"
                maxLength={6}
                autoComplete="postal-code"
                value={values.pincode}
                onChange={(event) =>
                  update("pincode", event.target.value.replace(/\D/g, ""))
                }
                className={inputClass}
              />
            </Field>
          </div>
        </section>

        {message ? <MessageBlock message={message} /> : null}

        {failedOrderId ? (
          <p className="font-body text-sm">
            The order was saved but payment could not start.{" "}
            <Link
              className="underline decoration-black/20 underline-offset-4"
              href={`/orders/${failedOrderId}`}
            >
              Open the order to retry
            </Link>
            .
          </p>
        ) : null}

        <div className="flex flex-wrap items-center gap-4">
          <button
            type="submit"
            disabled={busy}
            className="rounded-full bg-ink px-6 py-3 font-body text-sm text-paper transition-colors hover:bg-ground disabled:cursor-not-allowed disabled:bg-black/20"
          >
            {busy ? "Creating order…" : "Create order and pay"}
          </button>
          <p className="font-body text-xs leading-5 text-muted">
            Card details go to Razorpay&apos;s hosted checkout. The store never
            receives or stores them.
          </p>
        </div>
      </form>

      <aside className="space-y-4 rounded-lg border border-black/10 bg-white/60 p-5">
        <div className="flex items-baseline justify-between gap-3">
          <h2 className="font-display text-xl font-semibold">Your order</h2>
          <p className="font-body text-xs text-muted">
            {cart.expires_at
              ? `Reserved until ${new Date(cart.expires_at).toLocaleTimeString("en-IN")}`
              : null}
          </p>
        </div>
        <ul className="divide-y divide-black/10">
          {cart.items.map((item) => (
            <li key={item.id} className="py-3 font-body text-sm">
              <div className="flex justify-between gap-3">
                <span>
                  {item.name}
                  <span className="block text-muted">
                    {item.size_uk} · {item.quantity} ×{" "}
                    {inr.format(item.unit_price)}
                  </span>
                </span>
                <span className="whitespace-nowrap">
                  {inr.format(item.line_total)}
                </span>
              </div>
            </li>
          ))}
        </ul>
        <div className="flex items-baseline justify-between border-t border-black/10 pt-3 font-body text-sm">
          <span>
            {totalUnits} unit{totalUnits === 1 ? "" : "s"}
          </span>
          <span className="font-display text-lg font-semibold">
            {inr.format(cart.subtotal_inr)}
          </span>
        </div>
        <p className="font-body text-xs leading-5 text-muted">
          Prices include GST. The per-line tax split appears on the
          confirmation. Shipping is not charged in this milestone.
        </p>
        <p className="font-body text-xs leading-5 text-muted">
          Cash on delivery is not offered. Payment is confirmed only after a
          signed Razorpay webhook; the browser callback is a hint.
        </p>
        <p className="font-body text-sm">
          <Link
            className="underline decoration-black/20 underline-offset-4"
            href="/catalogue"
          >
            Keep shopping
          </Link>
        </p>
      </aside>
    </div>
  );
}

const inputClass =
  "w-full rounded-md border border-black/15 bg-white/70 px-3 py-2 font-body text-sm text-ink outline-none focus:border-black/40";

function Field({
  label,
  htmlFor,
  className,
  children,
}: {
  label: string;
  htmlFor: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <label className={`block font-body text-sm text-muted ${className ?? ""}`}>
      <span className="block pb-1">{label}</span>
      {children}
    </label>
  );
}

function MessageBlock({ message }: { message: NonNullable<Message> }) {
  return (
    <p
      aria-live="polite"
      className={`rounded-md border p-3 font-body text-sm leading-6 ${
        message.kind === "error"
          ? "border-[#a62b22]/30 bg-[#fbeae7] text-[#7a1f18]"
          : "border-[#2f6b4f]/30 bg-[#eaf4ee] text-[#22503b]"
      }`}
    >
      {message.text}
    </p>
  );
}

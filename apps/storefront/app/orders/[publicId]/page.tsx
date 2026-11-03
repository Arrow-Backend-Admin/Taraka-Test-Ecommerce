import Link from "next/link";
import { notFound } from "next/navigation";

import { getOrder, type Order } from "@/lib/orders";
import { OrderStatusPoller } from "./OrderStatusPoller";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Order — Sāntvana (concept)",
  description:
    "Order confirmation for the Sāntvana concept storefront. Payments are confirmed by a signed webhook, not the browser callback.",
  robots: { index: false, follow: false },
};

const inr = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

const paiseFmt = (paise: number) => inr.format(paise / 100);

const STATUS_LABELS: Record<string, string> = {
  created: "Created",
  awaiting_payment: "Awaiting payment",
  payment_failed: "Payment failed",
  expired: "Expired",
  paid: "Paid",
  refund_pending: "Refund pending",
  refunded: "Refunded",
  cancelled: "Cancelled",
};

const STATUS_COLORS: Record<string, string> = {
  paid: "border-[#2f6b4f]/30 bg-[#eaf4ee] text-[#22503b]",
  awaiting_payment: "border-[#b9892f]/40 bg-[#fff4d6] text-[#5c4317]",
  created: "border-[#b9892f]/40 bg-[#fff4d6] text-[#5c4317]",
  expired: "border-[#a62b22]/30 bg-[#fbeae7] text-[#7a1f18]",
  payment_failed: "border-[#a62b22]/30 bg-[#fbeae7] text-[#7a1f18]",
  refund_pending: "border-[#b9892f]/40 bg-[#fff4d6] text-[#5c4317]",
  refunded: "border-black/10 bg-white/60 text-muted",
  cancelled: "border-black/10 bg-white/60 text-muted",
};

export default async function OrderPage({
  params,
}: {
  params: Promise<{ publicId: string }>;
}) {
  const { publicId } = await params;
  const order = await getOrder(publicId);

  if (!order) notFound();

  return (
    <main className="min-h-screen bg-paper text-ink">
      <div className="mx-auto w-full max-w-4xl px-5 py-10 sm:px-8 lg:py-16">
        <header className="border-b border-black/10 pb-8">
          <p className="font-body text-[0.75rem] uppercase tracking-[0.14em] text-muted">
            Phase 4 · Milestone 3
          </p>
          <h1 className="mt-3 font-display text-4xl font-semibold tracking-[-0.035em] sm:text-5xl">
            Order
          </h1>
          <nav className="mt-5 flex flex-wrap gap-4 font-body text-sm">
            <Link
              className="underline decoration-black/20 underline-offset-4"
              href="/"
            >
              Home
            </Link>
            <Link
              className="underline decoration-black/20 underline-offset-4"
              href="/catalogue"
            >
              Catalogue
            </Link>
            <Link
              className="underline decoration-black/20 underline-offset-4"
              href="/checkout"
            >
              Checkout
            </Link>
          </nav>
        </header>

        <div className="mt-8 space-y-6">
          <OrderSummary order={order} />
          <OrderStatusPoller
            publicId={publicId}
            initialStatus={order.status}
            initialNextAction={order.next_action}
            initialMessage={order.message}
          />
        </div>

        <footer className="mt-12 border-t border-black/10 pt-6 font-body text-xs leading-5 text-muted">
          <p>
            Concept store. Payment is confirmed only by a signed Razorpay
            webhook. The browser callback is a UI hint, not a confirmation.
          </p>
        </footer>
      </div>
    </main>
  );
}

function OrderSummary({ order }: { order: Order }) {
  const statusColor =
    STATUS_COLORS[order.status] ?? "border-black/10 bg-white/60 text-muted";

  return (
    <>
      {/* Status banner */}
      <div className={`rounded-lg border p-5 ${statusColor}`}>
        <p className="font-body text-[0.75rem] uppercase tracking-[0.14em]">
          {STATUS_LABELS[order.status] ?? order.status}
        </p>
        <h2 className="mt-2 font-display text-2xl font-semibold">
          {order.public_id}
        </h2>
        <p className="mt-2 font-body text-sm leading-6">{order.message}</p>
        {order.reservation_expires_at ? (
          <p className="mt-1 font-body text-xs">
            Reservation expires{" "}
            {new Date(order.reservation_expires_at).toLocaleTimeString(
              "en-IN",
            )}
          </p>
        ) : null}
      </div>

      {/* Line items */}
      <section className="rounded-lg border border-black/10 bg-white/60 p-5">
        <h3 className="font-display text-xl font-semibold">Items</h3>
        <ul className="mt-4 divide-y divide-black/10">
          {order.items.map((item, index) => (
            <li key={`${item.sku}-${index}`} className="py-3 font-body text-sm">
              <div className="flex justify-between gap-3">
                <div>
                  <Link
                    className="font-medium underline decoration-black/20 underline-offset-4"
                    href={`/catalogue/${item.product_slug}`}
                  >
                    {item.product_name}
                  </Link>
                  <span className="block text-muted">
                    {item.size_uk} · {item.quantity} ×{" "}
                    {paiseFmt(item.unit_price_paise)}
                  </span>
                </div>
                <span className="whitespace-nowrap">
                  {paiseFmt(item.line_total_paise)}
                </span>
              </div>
              <div className="mt-1 text-xs text-muted">
                Taxable {paiseFmt(item.taxable_value_paise)} + GST{" "}
                {paiseFmt(item.gst_paise)} ({item.gst_rate_pct}%)
              </div>
            </li>
          ))}
        </ul>
        <div className="mt-2 space-y-1 border-t border-black/10 pt-3 font-body text-sm">
          <div className="flex justify-between gap-3 text-muted">
            <span>Subtotal (taxable value)</span>
            <span>{paiseFmt(order.subtotal_paise)}</span>
          </div>
          <div className="flex justify-between gap-3 text-muted">
            <span>GST (included in MRP)</span>
            <span>{paiseFmt(order.gst_paise)}</span>
          </div>
          <div className="flex justify-between gap-3 text-muted">
            <span>Shipping</span>
            <span>
              {order.shipping_paise === 0
                ? "Free"
                : paiseFmt(order.shipping_paise)}
            </span>
          </div>
          <div className="flex justify-between gap-3 font-display text-lg font-semibold">
            <span>Total</span>
            <span>{paiseFmt(order.total_paise)}</span>
          </div>
        </div>
      </section>

      {/* Address and contact */}
      <div className="grid gap-6 sm:grid-cols-2">
        <section className="rounded-lg border border-black/10 bg-white/60 p-5">
          <h3 className="font-display text-lg font-semibold">
            Delivery address
          </h3>
          <address className="mt-3 font-body text-sm leading-6 not-italic text-muted">
            <p>{order.customer_name}</p>
            <p>{order.address.line1}</p>
            {order.address.line2 ? <p>{order.address.line2}</p> : null}
            <p>
              {order.address.city}, {order.address.state}{" "}
              {order.address.pincode}
            </p>
            <p>{order.address.country}</p>
          </address>
        </section>

        <section className="rounded-lg border border-black/10 bg-white/60 p-5">
          <h3 className="font-display text-lg font-semibold">Contact</h3>
          <div className="mt-3 space-y-1 font-body text-sm text-muted">
            <p>{order.customer_email}</p>
            <p>{order.customer_phone}</p>
          </div>
          {order.paid_at ? (
            <p className="mt-3 font-body text-xs text-muted">
              Paid {new Date(order.paid_at).toLocaleString("en-IN")}
            </p>
          ) : null}
        </section>
      </div>

      {/* Seller details */}
      <section className="rounded-lg border border-black/10 bg-white/60 p-5">
        <h3 className="font-display text-lg font-semibold">Seller</h3>
        <div className="mt-3 font-body text-sm text-muted">
          <p>
            State: {order.seller.state}
            {order.seller.state.includes("[TO CONFIRM") ? (
              <span className="ml-2 text-xs italic">
                Placeholder — the founder has not confirmed this yet.
              </span>
            ) : null}
          </p>
          <p>
            GSTIN: {order.seller.gstin}
            {order.seller.gstin.includes("[TO CONFIRM") ? (
              <span className="ml-2 text-xs italic">
                Placeholder — the founder has not confirmed this yet.
              </span>
            ) : null}
          </p>
        </div>
      </section>
    </>
  );
}


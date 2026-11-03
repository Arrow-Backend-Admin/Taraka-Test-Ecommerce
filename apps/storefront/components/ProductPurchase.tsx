"use client";

import { useCallback, useEffect, useState } from "react";

import { getStock, type PublicVariant } from "@/lib/api";
import {
  addCartItem,
  createCart,
  fetchCart,
  removeCartItem,
  updateCartItem,
  type Cart,
  type CartItem,
} from "@/lib/cart";

const inr = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

const MAX_LINE = 5;

type Message = { kind: "info" | "error"; text: string } | null;

type ProductPurchaseProps = {
  slug: string;
  sizes: PublicVariant[];
};

export function ProductPurchase({ slug, sizes }: ProductPurchaseProps) {
  const initialAvailable = sizes.find((size) => size.available > 0)?.sku ?? null;
  const [stock, setStock] = useState<Record<string, number>>(() =>
    Object.fromEntries(sizes.map((size) => [size.sku, size.available])),
  );
  const [caps, setCaps] = useState<Record<string, number>>(() =>
    Object.fromEntries(sizes.map((size) => [size.sku, MAX_LINE])),
  );
  const [asOf, setAsOf] = useState<string | null>(null);
  const [selectedSku, setSelectedSku] = useState<string | null>(
    initialAvailable,
  );
  const [quantity, setQuantity] = useState(1);
  const [cart, setCart] = useState<Cart | null>(null);
  const [message, setMessage] = useState<Message>(null);
  const [busy, setBusy] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const refreshStock = useCallback(async () => {
    setRefreshing(true);
    const data = await getStock(slug);
    if (data) {
      setStock(
        Object.fromEntries(data.sizes.map((size) => [size.sku, size.available])),
      );
      setCaps(
        Object.fromEntries(
          data.sizes.map((size) => [size.sku, size.max_reservable]),
        ),
      );
      setAsOf(data.as_of);
    }
    setRefreshing(false);
  }, [slug]);

  useEffect(() => {
    void refreshStock();
    const timer = window.setInterval(() => {
      void refreshStock();
    }, 30_000);
    return () => window.clearInterval(timer);
  }, [refreshStock]);

  useEffect(() => {
    let cancelled = false;
    fetchCart()
      .then((next) => {
        if (!cancelled) setCart(next);
      })
      .catch(() => {
        if (!cancelled) setCart(null);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (selectedSku && (stock[selectedSku] ?? 0) > 0) return;
    const next =
      sizes.find((size) => (stock[size.sku] ?? 0) > 0)?.sku ?? null;
    setSelectedSku(next);
  }, [selectedSku, sizes, stock]);

  useEffect(() => {
    const available = selectedSku ? stock[selectedSku] ?? 0 : 0;
    const cap = selectedSku ? caps[selectedSku] ?? MAX_LINE : MAX_LINE;
    const max = Math.max(Math.min(MAX_LINE, available, cap), 1);
    if (quantity > max) setQuantity(max);
  }, [caps, quantity, selectedSku, stock]);

  const selected = sizes.find((size) => size.sku === selectedSku) ?? null;
  const selectedAvailable = selectedSku ? stock[selectedSku] ?? 0 : 0;
  const selectedCap = selectedSku ? caps[selectedSku] ?? MAX_LINE : MAX_LINE;
  const quantityMax = Math.max(
    Math.min(MAX_LINE, selectedAvailable, selectedCap),
    1,
  );

  async function handleAdd() {
    if (!selectedSku || selectedAvailable < 1 || busy) return;
    setBusy(true);
    setMessage(null);
    try {
      if (!cart || cart.status !== "active") {
        await createCart();
      }
      const next = await addCartItem(selectedSku, quantity);
      setCart(next);
      setMessage({
        kind: "info",
        text: `Reserved ${quantity} × ${selected?.size_uk ?? "selected size"} for ${next.reservation_minutes} minutes.`,
      });
      await refreshStock();
    } catch (error) {
      setMessage({
        kind: "error",
        text: error instanceof Error ? error.message : "Could not add to cart.",
      });
    } finally {
      setBusy(false);
    }
  }

  async function handleQuantity(item: CartItem, nextQuantity: number) {
    if (!cart || busy) return;
    setBusy(true);
    setMessage(null);
    try {
      const next = await updateCartItem(item.id, nextQuantity);
      setCart(next);
      await refreshStock();
    } catch (error) {
      setMessage({
        kind: "error",
        text:
          error instanceof Error ? error.message : "Could not update the cart.",
      });
    } finally {
      setBusy(false);
    }
  }

  async function handleRemove(item: CartItem) {
    if (!cart || busy) return;
    setBusy(true);
    setMessage(null);
    try {
      const next = await removeCartItem(item.id);
      setCart(next);
      await refreshStock();
    } catch (error) {
      setMessage({
        kind: "error",
        text:
          error instanceof Error ? error.message : "Could not remove the line.",
      });
    } finally {
      setBusy(false);
    }
  }

  if (sizes.length === 0) {
    return (
      <p className="mt-3 font-body leading-7 text-muted">
        Sizes are still to be confirmed.
      </p>
    );
  }

  return (
    <div className="mt-4 space-y-6">
      <fieldset>
        <legend className="font-body text-sm text-muted">
          Choose a UK size. Stock refreshes every 30 seconds.
        </legend>
        <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3">
          {sizes.map((size) => {
            const available = stock[size.sku] ?? 0;
            const isSelected = size.sku === selectedSku;
            return (
              <button
                key={size.sku}
                type="button"
                aria-pressed={isSelected}
                disabled={available < 1}
                onClick={() => {
                  setSelectedSku(size.sku);
                  setQuantity(1);
                }}
                className={`rounded-md border px-3 py-2 text-left font-body text-sm transition-colors ${
                  isSelected
                    ? "border-ink bg-ink text-paper"
                    : "border-black/15 bg-white/60 text-ink hover:border-black/35"
                } disabled:cursor-not-allowed disabled:border-black/10 disabled:bg-black/5 disabled:text-muted`}
              >
                <span className="block font-medium">{size.size_uk}</span>
                <span className="block text-xs opacity-80">
                  {available > 0 ? `${available} available` : "Unavailable"}
                </span>
              </button>
            );
          })}
        </div>
      </fieldset>

      {selected ? (
        <div className="rounded-md border border-black/10 bg-white/60 p-4 font-body text-sm leading-6 text-muted">
          <p>
            <span className="text-ink">Selected: </span>
            {selected.size_uk}
            {selected.size_eu ? ` · EU ${selected.size_eu}` : ""}
            {selected.foot_length_cm
              ? ` · ${selected.foot_length_cm} cm foot length`
              : ""}
          </p>
          <p className="mt-1">
            {selectedAvailable > 0
              ? `${selectedAvailable} available before your reservation.`
              : "This size is currently unavailable."}
          </p>
          {asOf ? (
            <p className="mt-1 text-xs">
              Stock checked {new Date(asOf).toLocaleTimeString("en-IN")}.
            </p>
          ) : null}
        </div>
      ) : null}

      <div className="flex flex-wrap items-end gap-3">
        <label className="font-body text-sm text-muted">
          <span className="block pb-1">Quantity</span>
          <select
            className="rounded-md border border-black/15 bg-white/70 px-3 py-2 text-ink"
            value={quantity}
            onChange={(event) => setQuantity(Number(event.target.value))}
            disabled={selectedAvailable < 1 || busy}
          >
            {Array.from({ length: quantityMax }, (_, index) => index + 1).map(
              (value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ),
            )}
          </select>
        </label>
        <button
          type="button"
          onClick={() => void handleAdd()}
          disabled={!selectedSku || selectedAvailable < 1 || busy}
          className="rounded-full bg-ink px-6 py-3 font-body text-sm text-paper transition-colors hover:bg-ground disabled:cursor-not-allowed disabled:bg-black/20"
        >
          {busy ? "Working…" : "Add to cart"}
        </button>
        <button
          type="button"
          onClick={() => void refreshStock()}
          disabled={refreshing}
          className="rounded-full border border-black/15 px-4 py-3 font-body text-sm transition-colors hover:bg-white/60 disabled:opacity-50"
        >
          {refreshing ? "Checking…" : "Refresh stock"}
        </button>
      </div>

      {message ? (
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
      ) : null}

      <section
        aria-labelledby="cart-heading"
        className="rounded-lg border border-black/10 bg-white/60 p-5"
      >
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <h3 className="font-display text-xl font-semibold" id="cart-heading">
            Guest cart
          </h3>
          {cart ? (
            <p className="font-body text-xs text-muted">
              {cart.status === "active" && cart.expires_at
                ? `Reserved until ${new Date(cart.expires_at).toLocaleTimeString("en-IN")}`
                : `Cart status: ${cart.status}`}
            </p>
          ) : null}
        </div>

        {!cart || cart.items.length === 0 ? (
          <p className="mt-3 font-body text-sm leading-6 text-muted">
            {cart && cart.status !== "active"
              ? "This reservation expired and its units were released. Add a size to start again."
              : "Your cart is empty. Adding a size reserves it for a short window; no payment is taken."}
          </p>
        ) : (
          <>
            <ul className="mt-4 divide-y divide-black/10">
              {cart.items.map((item) => (
                <li
                  key={item.id}
                  className="flex flex-wrap items-center justify-between gap-3 py-3"
                >
                  <div className="font-body text-sm">
                    <p className="font-medium">{item.name}</p>
                    <p className="text-muted">
                      {item.size_uk} · {inr.format(item.unit_price)} each
                    </p>
                  </div>
                  <div className="flex items-center gap-2 font-body text-sm">
                    <button
                      type="button"
                      aria-label={`Decrease quantity for ${item.size_uk}`}
                      onClick={() => void handleQuantity(item, item.quantity - 1)}
                      disabled={busy || item.quantity <= 1}
                      className="h-8 w-8 rounded-full border border-black/15 disabled:opacity-40"
                    >
                      −
                    </button>
                    <span className="w-6 text-center">{item.quantity}</span>
                    <button
                      type="button"
                      aria-label={`Increase quantity for ${item.size_uk}`}
                      onClick={() => void handleQuantity(item, item.quantity + 1)}
                      disabled={
                        busy ||
                        item.quantity >= MAX_LINE ||
                        item.quantity >= item.max_reservable ||
                        item.available < 1
                      }
                      className="h-8 w-8 rounded-full border border-black/15 disabled:opacity-40"
                    >
                      +
                    </button>
                    <button
                      type="button"
                      onClick={() => void handleRemove(item)}
                      disabled={busy}
                      className="ml-2 text-xs underline decoration-black/20 underline-offset-4"
                    >
                      Remove
                    </button>
                  </div>
                </li>
              ))}
            </ul>
            <div className="mt-4 flex flex-wrap items-baseline justify-between gap-2 border-t border-black/10 pt-3 font-body text-sm">
              <p>
                {cart.total_units} unit{cart.total_units === 1 ? "" : "s"}
              </p>
              <p className="font-display text-lg font-semibold">
                {inr.format(cart.subtotal_inr)}
              </p>
            </div>
            <p className="mt-3 font-body text-xs leading-5 text-muted">
              Reservations last {cart.reservation_minutes} minutes. Maximum{" "}
              {String(cart.rules.max_line_quantity)} per size,{" "}
              {String(cart.rules.max_total_units)} units and{" "}
              {String(cart.rules.max_lines)} lines per cart. One IP can hold at
              most {String(cart.rules.max_units_per_ip)} units, and at most 20%
              of a size&apos;s on-hand units. Checkout and payment are not
              available in this milestone.
            </p>
          </>
        )}
      </section>
    </div>
  );
}

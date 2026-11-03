"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import {
  getOrder,
  mockPay,
  retryPayment,
  type OrderCreated,
} from "@/lib/orders";
import { openRazorpayCheckout, type RazorpayResponse } from "@/lib/razorpay";

type Message = { kind: "info" | "error"; text: string } | null;

export function OrderStatusPoller({
  publicId,
  initialStatus,
  initialNextAction,
  initialMessage,
}: {
  publicId: string;
  initialStatus: string;
  initialNextAction: string;
  initialMessage: string;
}) {
  const [status, setStatus] = useState(initialStatus);
  const [nextAction, setNextAction] = useState(initialNextAction);
  const [orderMessage, setOrderMessage] = useState(initialMessage);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<Message>(null);

  const shouldPoll =
    status === "awaiting_payment" || status === "created";

  const poll = useCallback(async () => {
    const order = await getOrder(publicId);
    if (!order) return;
    setStatus(order.status);
    setNextAction(order.next_action);
    setOrderMessage(order.message);
  }, [publicId]);

  useEffect(() => {
    if (!shouldPoll) return;
    const timer = window.setInterval(() => {
      void poll();
    }, 4_000);
    return () => window.clearInterval(timer);
  }, [shouldPoll, poll]);

  // Refresh once on mount (catches webhook-before-redirect race)
  useEffect(() => {
    if (shouldPoll) {
      void poll();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleRetry() {
    if (busy) return;
    setBusy(true);
    setMessage(null);
    try {
      const updated: OrderCreated = await retryPayment(publicId);
      setStatus(updated.status);
      setNextAction(updated.next_action);
      setOrderMessage(updated.message);

      if (updated.checkout?.mock) {
        setBusy(false);
        setMessage({
          kind: "info",
          text: "New payment attempt created. Use the mock payment button below.",
        });
        return;
      }

      if (updated.checkout && updated.checkout.key_id) {
        try {
          await openRazorpayCheckout({
            checkout: updated.checkout,
            publicId,
            onPaid: (_response: RazorpayResponse) => {
              void poll();
            },
            onDismiss: () => {
              setBusy(false);
              setMessage({
                kind: "info",
                text: "The payment window closed. The reservation is held until it expires.",
              });
            },
            onFailed: () => {
              setMessage({
                kind: "error",
                text: "The payment did not complete.",
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
      } else {
        setBusy(false);
      }
    } catch (error) {
      setBusy(false);
      setMessage({
        kind: "error",
        text:
          error instanceof Error
            ? error.message
            : "Could not retry the payment.",
      });
    }
  }

  async function handleMockPay() {
    if (busy) return;
    setBusy(true);
    setMessage(null);
    try {
      await mockPay(publicId);
      await poll();
      setBusy(false);
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

  return (
    <div className="space-y-4">
      {/* Live status update */}
      {shouldPoll ? (
        <p className="font-body text-xs text-muted">
          Refreshing status every few seconds…
        </p>
      ) : null}

      {status === "paid" ? (
        <div className="rounded-lg border border-[#2f6b4f]/30 bg-[#eaf4ee] p-5">
          <p className="font-display text-xl font-semibold text-[#22503b]">
            Payment confirmed
          </p>
          <p className="mt-2 font-body text-sm leading-6 text-[#22503b]">
            {orderMessage}
          </p>
        </div>
      ) : null}

      {/* Retry button for failed/expired */}
      {nextAction === "retry" ? (
        <div className="rounded-md border border-black/10 bg-[#f4efe4] p-4">
          <p className="font-body text-sm leading-6 text-muted">
            {orderMessage}
          </p>
          <button
            type="button"
            onClick={() => void handleRetry()}
            disabled={busy}
            className="mt-3 rounded-full bg-ink px-6 py-3 font-body text-sm text-paper disabled:bg-black/20"
          >
            {busy ? "Working…" : "Retry payment"}
          </button>
        </div>
      ) : null}

      {/* Mock payment for local review */}
      {(status === "awaiting_payment" || status === "created") ? (
        <div className="rounded-md border border-black/10 bg-[#f4efe4] p-4">
          <p className="font-body text-sm leading-6 text-muted">
            Local review mode. This signs a fake webhook and runs the real
            confirmation path.
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
      ) : null}

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

      <p className="font-body text-sm">
        <Link
          className="underline decoration-black/20 underline-offset-4"
          href="/catalogue"
        >
          Continue shopping
        </Link>
      </p>
    </div>
  );
}


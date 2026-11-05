"use client";

import { useEffect, useState } from "react";

export function OfflineNotice() {
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    const update = () => setOffline(!navigator.onLine);
    update();
    window.addEventListener("online", update);
    window.addEventListener("offline", update);
    return () => {
      window.removeEventListener("online", update);
      window.removeEventListener("offline", update);
    };
  }, []);

  if (!offline) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className="border-b border-[#b9892f]/40 bg-[#fff4d6] px-5 py-3 text-center font-body text-sm text-[#5c4317]"
    >
      You are offline. Stock, totals and payment status may be out of date.
      Reconnect before paying.
    </div>
  );
}

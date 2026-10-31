import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-sm border px-2.5 py-1 text-[0.6875rem] font-semibold uppercase tracking-[0.12em]",
  {
    variants: {
      variant: {
        default: "border-transparent bg-ink text-paper",
        outline: "border-stone bg-transparent text-ink",
        clay: "border-transparent bg-clay text-paper",
        pass: "border-transparent bg-green text-paper",
        fail: "border-transparent bg-red text-paper",
        muted: "border-transparent bg-bone text-muted",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

function Badge({
  className,
  variant,
  ...props
}: React.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return (
    <span
      data-slot="badge"
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  );
}

export { Badge, badgeVariants };

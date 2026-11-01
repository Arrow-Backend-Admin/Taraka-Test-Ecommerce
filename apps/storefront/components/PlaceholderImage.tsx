import Image from "next/image";

import { safeText, type PublicImage } from "@/lib/api";

const PLACEHOLDER_NOTICE = "Placeholder image, not the actual product";

type PlaceholderImageProps = {
  image: PublicImage;
  priority?: boolean;
  sizes?: string;
  className?: string;
};

export function PlaceholderImage({
  image,
  priority = false,
  sizes = "(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw",
  className = "",
}: PlaceholderImageProps) {
  const alt =
    safeText(image.alt) ??
    (image.is_placeholder
      ? "Placeholder photograph of plain footwear."
      : "Product photograph.");
  const notice = image.is_placeholder
    ? safeText(image.placeholder_notice) ?? PLACEHOLDER_NOTICE
    : null;

  return (
    <div className={`relative overflow-hidden bg-[#e7e1d5] ${className}`}>
      {image.url ? (
        <Image
          src={image.url}
          alt={alt}
          width={800}
          height={1000}
          priority={priority}
          sizes={sizes}
          className="h-full w-full object-cover"
        />
      ) : (
        <div
          className="flex h-full w-full items-center justify-center px-4 text-center font-body text-xs text-muted"
          role="img"
          aria-label={alt}
        >
          Image unavailable
        </div>
      )}
      {notice ? (
        <p className="absolute inset-x-0 bottom-0 bg-ink/85 px-3 py-2 text-center font-body text-[0.65rem] uppercase leading-4 tracking-[0.08em] text-paper">
          {notice}
        </p>
      ) : null}
    </div>
  );
}

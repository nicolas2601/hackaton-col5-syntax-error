"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "relative inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-[8px] text-[14px] font-medium leading-none transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-electric-violet/40 disabled:pointer-events-none disabled:opacity-50 select-none overflow-hidden",
  {
    variants: {
      variant: {
        primary:
          "bg-electric-violet text-white hover:bg-electric-violet/92 active:scale-[0.99] shadow-[0_1px_0_0_rgba(255,255,255,0.18)_inset,0_8px_20px_-8px_rgba(94,76,255,0.5)]",
        ghost:
          "bg-transparent border border-midnight-ink text-midnight-ink hover:bg-ghost-fill",
        secondary:
          "bg-lavender-mist text-electric-violet hover:bg-lavender-mist/80",
        link:
          "bg-transparent text-electric-violet hover:underline underline-offset-4 px-0 py-0",
        outline:
          "bg-transparent border border-lava-cloud text-midnight-ink hover:bg-ghost-fill",
        destructive:
          "bg-destructive text-white hover:bg-destructive/90",
      },
      size: {
        sm: "h-8 px-3 text-[13px]",
        md: "h-10 px-5 py-3",
        lg: "h-12 px-6 py-3 text-[15px]",
        icon: "h-10 w-10 p-0",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  ripple?: boolean;
}

/** Button with optional ripple effect on click (used in primary CTAs). */
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ripple = true, onClick, children, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    const [ripples, setRipples] = React.useState<{ x: number; y: number; id: number }[]>([]);

    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
      if (ripple && variant === "primary") {
        const target = e.currentTarget;
        const rect = target.getBoundingClientRect();
        const id = Date.now() + Math.random();
        setRipples((r) => [...r, { x: e.clientX - rect.left, y: e.clientY - rect.top, id }]);
        setTimeout(() => setRipples((r) => r.filter((it) => it.id !== id)), 700);
      }
      onClick?.(e);
    };

    return (
      <Comp
        ref={ref}
        className={cn(buttonVariants({ variant, size, className }))}
        onClick={handleClick}
        {...props}
      >
        {children}
        {ripples.map((r) => (
          <span
            key={r.id}
            className="pointer-events-none absolute h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/40"
            style={{ left: r.x, top: r.y, animation: "ripple 0.6s ease-out forwards" }}
          />
        ))}
      </Comp>
    );
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };

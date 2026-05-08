import * as React from "react";
import { cn } from "@/lib/utils";

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { elevated?: boolean }
>(({ className, elevated = false, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "bg-canvas-white",
      elevated
        ? "rounded-[20px] p-6 shadow-[rgba(39,40,53,0.05)_0_0_0_1px,rgba(39,40,53,0.01)_0_50px_20px_0,rgba(39,40,53,0.02)_0_30px_18px_0,rgba(39,40,53,0.04)_0_13px_13px_0,rgba(39,40,53,0.05)_0_3px_7px_0]"
        : "rounded-[12px] p-6 shadow-[rgba(39,40,53,0.1)_0_0_0_1px]",
      className,
    )}
    {...props}
  />
));
Card.displayName = "Card";

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col gap-1.5 mb-4", className)}
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref as React.Ref<HTMLHeadingElement>}
    className={cn(
      "text-subheading font-medium tracking-[-0.010em] text-midnight-ink",
      className,
    )}
    {...(props as React.HTMLAttributes<HTMLHeadingElement>)}
  />
));
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref as React.Ref<HTMLParagraphElement>}
    className={cn("text-[13px] text-steel-gray leading-snug", className)}
    {...(props as React.HTMLAttributes<HTMLParagraphElement>)}
  />
));
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("text-deep-indigo", className)} {...props} />
));
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center mt-4 pt-4 border-t border-lava-cloud", className)}
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter };

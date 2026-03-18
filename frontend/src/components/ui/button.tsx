import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-input text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sw-blue disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-sw-blue text-white hover:bg-sw-blue/90",
        destructive: "bg-sw-red text-white hover:bg-sw-red/90",
        outline: "border border-sw-border bg-sw-surface hover:bg-sw-bg text-sw-text",
        secondary: "bg-sw-bg text-sw-text hover:bg-sw-border",
        ghost: "hover:bg-sw-bg text-sw-text",
        link: "text-sw-blue underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-input px-3",
        lg: "h-11 rounded-input px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }

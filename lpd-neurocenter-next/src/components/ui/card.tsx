import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const cardVariants = cva(
  'rounded-xl transition-all duration-200',
  {
    variants: {
      elevation: {
        none: 'border border-neutral-200 dark:border-neutral-800',
        sm: 'shadow-sm border border-neutral-200/50 dark:border-neutral-800/50',
        md: 'shadow-md border border-neutral-200/30 dark:border-neutral-800/30',
        lg: 'shadow-lg border border-neutral-200/20 dark:border-neutral-800/20',
      },
      variant: {
        default: 'bg-white dark:bg-neutral-900',
        glass: 'bg-white/80 dark:bg-neutral-900/80 backdrop-blur-sm',
        gradient: 'bg-gradient-to-br from-white to-neutral-50 dark:from-neutral-900 dark:to-neutral-950',
      },
    },
    defaultVariants: {
      elevation: 'md',
      variant: 'default',
    },
  }
)

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, elevation, variant, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(cardVariants({ elevation, variant }), className)}
      {...props}
    />
  )
)
Card.displayName = 'Card'

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    title?: React.ReactNode
    aside?: React.ReactNode
  }
>(({ className, title, aside, children, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'flex items-center justify-between p-6 border-b border-neutral-200 dark:border-neutral-800',
      className
    )}
    {...props}
  >
    {title || children ? (
      <>
        <div className="flex-1">
          {title && (
            <h3 className="text-lg font-heading font-semibold text-neutral-950 dark:text-neutral-0">
              {title}
            </h3>
          )}
          {children}
        </div>
        {aside && <div className="ml-4">{aside}</div>}
      </>
    ) : null}
  </div>
))
CardHeader.displayName = 'CardHeader'

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      'text-lg font-heading font-semibold text-neutral-950 dark:text-neutral-0',
      className
    )}
    {...props}
  />
))
CardTitle.displayName = 'CardTitle'

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-neutral-600 dark:text-neutral-400', className)}
    {...props}
  />
))
CardDescription.displayName = 'CardDescription'

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6', className)} {...props} />
))
CardContent.displayName = 'CardContent'

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'flex items-center p-6 pt-0 text-sm text-neutral-600 dark:text-neutral-400',
      className
    )}
    {...props}
  />
))
CardFooter.displayName = 'CardFooter'

export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter }
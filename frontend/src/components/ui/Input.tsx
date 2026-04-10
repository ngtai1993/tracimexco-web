import { cn } from '@/lib/utils'
import { forwardRef } from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, className, id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-')

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-medium text-fg"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            'w-full bg-surface border rounded-bento px-4 py-2.5 text-sm text-fg',
            'placeholder:text-fg-subtle',
            'transition-colors duration-150',
            'focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary',
            error
              ? 'border-danger focus:ring-danger/40 focus:border-danger'
              : 'border-border',
            className
          )}
          {...props}
        />
        {error && <p className="text-xs text-danger">{error}</p>}
        {hint && !error && <p className="text-xs text-fg-muted">{hint}</p>}
      </div>
    )
  }
)

Input.displayName = 'Input'

# Component Patterns — Compound, HOC, Render Props

## 1. Compound Component (React 19 với `use()`)

**Khi dùng:** Component có nhiều sub-parts hoạt động cùng nhau (Select, Modal, Tabs, Accordion, Dropdown).

```tsx
// features/ui/Select/Select.tsx
import { use, createContext, useState } from 'react'
import { cn } from '@/utils/cn'

interface SelectContextValue<T> {
  value: T | undefined
  onChange: (value: T) => void
  open: boolean
  setOpen: (open: boolean) => void
}

export interface SelectProps<T> {
  value?: T
  defaultValue?: T
  onChange?: (value: T) => void
  children: React.ReactNode
  className?: string
}

const SelectContext = createContext<SelectContextValue<unknown> | null>(null)

function useSelectContext() {
  const ctx = use(SelectContext)
  if (!ctx) throw new Error('Select sub-components must be used inside <Select>')
  return ctx
}

function Select<T>({ value, defaultValue, onChange, children, className }: SelectProps<T>) {
  const [internalValue, setInternalValue] = useState<T | undefined>(defaultValue)
  const [open, setOpen] = useState(false)

  const controlledValue = value ?? internalValue
  const handleChange = (val: T) => {
    setInternalValue(val)
    onChange?.(val)
    setOpen(false)
  }

  return (
    <SelectContext value={{ value: controlledValue, onChange: handleChange as any, open, setOpen }}>
      <div className={cn('relative inline-block', className)}>{children}</div>
    </SelectContext>
  )
}

function SelectTrigger({ children, className }: { children: React.ReactNode; className?: string }) {
  const { open, setOpen } = useSelectContext()
  return (
    <button
      type="button"
      onClick={() => setOpen(!open)}
      aria-expanded={open}
      className={cn(
        'flex items-center gap-2 rounded-md border px-3 py-2 text-sm',
        'border-border bg-bg hover:border-border-strong',
        className
      )}
    >
      {children}
    </button>
  )
}

function SelectOptions({ children, className }: { children: React.ReactNode; className?: string }) {
  const { open } = useSelectContext()
  if (!open) return null
  return (
    <ul className={cn('absolute z-10 mt-1 w-full rounded-md border border-border bg-bg py-1 shadow-md', className)}>
      {children}
    </ul>
  )
}

function SelectOption<T>({ value, children, className }: { value: T; children: React.ReactNode; className?: string }) {
  const ctx = useSelectContext()
  const isSelected = ctx.value === value
  return (
    <li
      role="option"
      aria-selected={isSelected}
      onClick={() => ctx.onChange(value)}
      className={cn(
        'cursor-pointer px-3 py-2 text-sm hover:bg-bg-muted',
        isSelected && 'bg-primary-light text-primary font-medium',
        className
      )}
    >
      {children}
    </li>
  )
}

Select.Trigger = SelectTrigger
Select.Options = SelectOptions
Select.Option = SelectOption

export { Select }

// Usage:
// <Select value={status} onChange={setStatus}>
//   <Select.Trigger>{status ?? 'Chọn trạng thái'}</Select.Trigger>
//   <Select.Options>
//     <Select.Option value="active">Hoạt động</Select.Option>
//     <Select.Option value="inactive">Vô hiệu</Select.Option>
//   </Select.Options>
// </Select>
```

---

## 2. Higher-Order Component (HOC)

**Khi dùng:** Cross-cutting concerns — auth guard, permissions, analytics, feature flags.

```tsx
// components/hoc/withAuth.tsx
import { Navigate } from 'react-router-dom'
import { useAuth } from '@/features/auth'
import { PageSkeleton } from '@/components/ui'

interface WithAuthOptions {
  requiredRole?: string
  redirectTo?: string
}

export function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options: WithAuthOptions = {}
) {
  const { requiredRole, redirectTo = '/login' } = options

  function WithAuth(props: P) {
    const { user, isLoading } = useAuth()

    if (isLoading) return <PageSkeleton />
    if (!user) return <Navigate to={redirectTo} replace />
    if (requiredRole && !user.roles.includes(requiredRole)) {
      return <Navigate to="/403" replace />
    }
    return <WrappedComponent {...props} />
  }

  WithAuth.displayName = `WithAuth(${WrappedComponent.displayName ?? WrappedComponent.name})`
  return WithAuth
}

// Usage:
// const AdminDashboard = withAuth(Dashboard, { requiredRole: 'admin' })
```

---

## 3. Controlled vs Uncontrolled — Input với forwardRef

```tsx
// components/ui/Input/Input.tsx
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, id, ...props }, ref) => {
    const inputId = id ?? React.useId()

    return (
      <div className="flex flex-col gap-1">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-fg">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            'rounded-md border px-3 py-2 text-sm outline-none bg-bg text-fg',
            'border-border focus:border-primary focus:ring-2 focus:ring-primary/20',
            error && 'border-danger focus:border-danger focus:ring-danger/20',
            className
          )}
          aria-invalid={!!error}
          aria-describedby={error ? `${inputId}-error` : undefined}
          {...props}
        />
        {error && (
          <p id={`${inputId}-error`} className="text-sm text-danger">
            {error}
          </p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'
```

---

## 4. Slot Pattern — Layout Components

```tsx
// components/ui/Card/Card.tsx
interface CardProps {
  header?: React.ReactNode
  footer?: React.ReactNode
  children: React.ReactNode
  className?: string
}

export function Card({ header, footer, children, className }: CardProps) {
  return (
    <div className={cn('rounded-xl border border-border bg-bg shadow-sm', className)}>
      {header && <div className="border-b border-border px-6 py-4">{header}</div>}
      <div className="px-6 py-4">{children}</div>
      {footer && <div className="border-t border-border px-6 py-4">{footer}</div>}
    </div>
  )
}
```

---

## Khi Nào Dùng Pattern Gì

| Tình huống | Pattern |
|-----------|---------|
| Component có trigger + content + options | Compound Component |
| Cần auth/permission check trước khi render | HOC with `withAuth` |
| Component nhận HTML props + ref | `React.forwardRef` + spread `...props` |
| Layout cần nhiều vùng nội dung | Slot Pattern (optional props) |

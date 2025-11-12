import React from 'react'
import { cn } from './cn'

const Button = React.forwardRef(({ className, variant = 'default', size = 'default', ...props }, ref) => {
  const variants = {
    default: 'bg-black text-white hover:bg-black/90',
    destructive: 'bg-red-500 text-white hover:bg-red-500/90',
    outline: 'border border-gray-300 hover:bg-gray-100',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-100/80',
    ghost: 'hover:bg-gray-100',
    link: 'text-black underline-offset-4 hover:underline',
  }
  const sizes = {
    default: 'h-10 px-4 py-2',
    sm: 'h-9 rounded-md px-3',
    lg: 'h-11 rounded-md px-8',
  }
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none',
        variants[variant],
        sizes[size],
        className
      )}
      ref={ref}
      {...props}
    />
  )
})

export default Button

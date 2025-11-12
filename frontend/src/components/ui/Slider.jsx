import React, { useEffect, useState } from 'react'
import { cn } from './cn'

const Slider = React.forwardRef(({ className, value, onValueChange, ...props }, ref) => {
  const [internalValue, setInternalValue] = useState(value)
  
  useEffect(() => {
    setInternalValue(value)
  }, [value])

  const handleChange = (event) => {
    const newValue = [parseFloat(event.target.value)]
    setInternalValue(newValue)
    if (onValueChange) {
      onValueChange(newValue)
    }
  }

  return (
    <div className="relative flex items-center w-full">
      <input
        type="range"
        ref={ref}
        value={internalValue}
        onChange={handleChange}
        className={cn('w-full h-2 bg-gray-200 rounded-full appearance-none cursor-pointer', className)}
        {...props}
      />
    </div>
  )
})

export default Slider

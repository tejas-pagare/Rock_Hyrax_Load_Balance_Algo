import React from 'react'
import Button from './ui/Button'
import { X } from 'lucide-react'

function Spinner() {
  return (
    <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
  )
}

export default function Modal({ title, content, onClose, isLoading }) {
  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 relative"
        onClick={(e) => e.stopPropagation()}
      >
        <Button 
          variant="ghost" 
          size="sm" 
          className="absolute top-3 right-3"
          onClick={onClose}
        >
          <X className="w-4 h-4" />
        </Button>
        <h3 className="text-lg font-semibold mb-4">{title}</h3>
        {isLoading ? (
          <div className="flex items-center justify-center h-24">
            <Spinner />
            <span className="ml-3 text-gray-600">Analyzing...</span>
          </div>
        ) : (
          <div 
            className="prose prose-sm max-w-none text-gray-700 max-h-[60vh] overflow-y-auto"
            dangerouslySetInnerHTML={{ __html: content }}
          />
        )}
      </div>
    </div>
  )
}

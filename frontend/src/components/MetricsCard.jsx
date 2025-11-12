import React from 'react'
import Button from './ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card'
import { Sparkles } from 'lucide-react'

export default function MetricsCard({ title, metrics, onExplainClick }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{title}</CardTitle>
          <Button variant="ghost" size="sm" onClick={onExplainClick} title="Explain these metrics">
            <Sparkles className="w-4 h-4 text-blue-500" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {Object.entries(metrics).map(([key, value]) => (
          <div key={key} className="flex justify-between items-baseline">
            <span className="text-sm text-gray-600">{key}</span>
            <span className="text-lg font-bold">{Number(value || 0).toFixed(2)}</span>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

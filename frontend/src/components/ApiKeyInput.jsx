import React, { useState } from 'react'
import Button from './ui/Button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/Card'
import { KeySquare } from 'lucide-react'

export default function ApiKeyInput({ apiKey, setApiKey }) {
  const [key, setKey] = useState(apiKey)

  const handleSave = () => {
    setApiKey(key)
  }

  return (
    <Card className="shadow-lg">
      <CardHeader>
        <div className="flex items-center space-x-2">
          <KeySquare className="w-6 h-6" />
          <CardTitle>Gemini API Key</CardTitle>
        </div>
        <CardDescription>
          Enter your Gemini API key to enable AI features. We do not store or share your key.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex space-x-2">
        <input
          type="password"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder="Enter your Gemini API key"
          className="flex-grow p-2 border rounded-md text-sm"
        />
        <Button onClick={handleSave}>{apiKey ? 'Update' : 'Save'} Key</Button>
      </CardContent>
    </Card>
  )
}

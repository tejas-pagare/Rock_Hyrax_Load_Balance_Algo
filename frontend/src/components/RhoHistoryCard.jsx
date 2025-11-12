import React, { useMemo, useState } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/Card'
import Button from './ui/Button'
import { cn } from './ui/cn'

function EntryRow({ entry, index }) {
  const [open, setOpen] = useState(false)

  const weights = entry.weights || { w1: 0, w2: 0 }
  const scores = entry.fitnessScores || []
  const normTime = entry.normTime || []
  const normEnergy = entry.normEnergy || []
  const efts = entry.efts || []
  const energyCosts = entry.energyCosts || []

  const sorted = useMemo(() => {
    return [...scores].sort((a, b) => a.score - b.score)
  }, [scores])

  const chosen = scores.find(s => s.isChosen)
  const alpha = scores.find(s => s.isAlpha)
  const runnerUp = sorted.find(s => s.vmId !== chosen?.vmId)

  const margin = runnerUp && chosen ? (runnerUp.score - chosen.score) : null

  const contrib = (vmId) => {
    const t = normTime?.[vmId]
    const e = normEnergy?.[vmId]
    const timePart = Number.isFinite(weights.w1) && Number.isFinite(t) ? weights.w1 * t : null
    const energyPart = Number.isFinite(weights.w2) && Number.isFinite(e) ? weights.w2 * e : null
    return { timePart, energyPart, eft: efts?.[vmId], energy: energyCosts?.[vmId] }
  }

  const chosenC = chosen ? contrib(chosen.vmId) : {}
  const runnerC = runnerUp ? contrib(runnerUp.vmId) : {}

  return (
    <div className="bg-white border border-gray-200 rounded-md p-2">
      <div className="flex flex-wrap items-center justify-between text-sm">
        <div className="space-x-2">
          <span className="font-semibold">Task {entry.taskId}</span>
          <span>Chosen: <span className="font-mono">VM {chosen?.vmId ?? '-'}</span></span>
          <span>Alpha: <span className="font-mono">VM {alpha?.vmId ?? '-'}</span></span>
          {margin != null && (
            <span className="ml-2 text-gray-600">Margin vs runner-up: <span className="font-mono">{margin.toFixed(4)}</span></span>
          )}
        </div>
        <Button size="sm" variant="outline" onClick={() => setOpen(o => !o)}>
          {open ? 'Hide Compare' : 'Compare Why Chosen'}
        </Button>
      </div>

      {open && (
        <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div className="border rounded-md p-2">
            <div className="font-semibold mb-1">Chosen vs Runner-up (Contributions)</div>
            <div className="grid grid-cols-5 gap-2 font-semibold">
              <span></span>
              <span className="text-right">Score</span>
              <span className="text-right">Time part</span>
              <span className="text-right">Energy part</span>
              <span className="text-right">EFT / Energy</span>
            </div>
            <div className="grid grid-cols-5 gap-2 items-center py-1 border-b">
              <span className="font-medium">Chosen (VM {chosen?.vmId ?? '-'})</span>
              <span className="font-mono text-right">{chosen ? chosen.score.toFixed(4) : '-'}</span>
              <span className="font-mono text-right">{chosenC.timePart != null ? chosenC.timePart.toFixed(4) : '-'}</span>
              <span className="font-mono text-right">{chosenC.energyPart != null ? chosenC.energyPart.toFixed(4) : '-'}</span>
              <span className="font-mono text-right">{Number.isFinite(chosenC.eft) ? chosenC.eft.toFixed(4) : '-' } / {Number.isFinite(chosenC.energy) ? chosenC.energy.toFixed(2) : '-'}</span>
            </div>
            <div className="grid grid-cols-5 gap-2 items-center py-1">
              <span className="font-medium">Runner-up (VM {runnerUp?.vmId ?? '-'})</span>
              <span className="font-mono text-right">{runnerUp ? runnerUp.score.toFixed(4) : '-'}</span>
              <span className="font-mono text-right">{runnerC.timePart != null ? runnerC.timePart.toFixed(4) : '-'}</span>
              <span className="font-mono text-right">{runnerC.energyPart != null ? runnerC.energyPart.toFixed(4) : '-'}</span>
              <span className="font-mono text-right">{Number.isFinite(runnerC.eft) ? runnerC.eft.toFixed(4) : '-' } / {Number.isFinite(runnerC.energy) ? runnerC.energy.toFixed(2) : '-'}</span>
            </div>
            {chosen && runnerUp && (
              <div className="text-gray-700 mt-2">
                <div>Delta (runner-up minus chosen):
                  <span className="ml-2 font-mono">
                    Δscore={ (runnerUp.score - chosen.score).toFixed(4) },
                    Δtime={ ( (runnerC.timePart ?? 0) - (chosenC.timePart ?? 0) ).toFixed(4) },
                    Δenergy={ ( (runnerC.energyPart ?? 0) - (chosenC.energyPart ?? 0) ).toFixed(4) }
                  </span>
                </div>
                <div className="text-gray-500">Lower is better. Negative contribution indicates the chosen VM was better on that component.</div>
              </div>
            )}
          </div>

          <div className="border rounded-md p-2">
            <div className="font-semibold mb-1">Top 5 Candidates</div>
            <div className="grid grid-cols-6 gap-2 font-semibold text-[11px]">
              <span>VM</span>
              <span className="text-right">Score</span>
              <span className="text-right">Time part</span>
              <span className="text-right">Energy part</span>
              <span className="text-right">EFT</span>
              <span className="text-right">Energy</span>
            </div>
            {(sorted.slice(0,5)).map(({ vmId, score, isAlpha, isChosen }) => {
              const c = contrib(vmId)
              return (
                <div key={vmId} className={cn(
                  'grid grid-cols-6 gap-2 items-center p-1 rounded border text-[12px] mt-1',
                  isChosen && 'bg-orange-100 border-orange-300',
                  isAlpha && 'ring-1 ring-blue-300'
                )}>
                  <span className="font-medium">VM {vmId}{isAlpha ? ' (α)' : ''}{isChosen ? ' (chosen)' : ''}</span>
                  <span className="font-mono text-right">{score.toFixed(4)}</span>
                  <span className="font-mono text-right">{c.timePart != null ? c.timePart.toFixed(4) : '-'}</span>
                  <span className="font-mono text-right">{c.energyPart != null ? c.energyPart.toFixed(4) : '-'}</span>
                  <span className="font-mono text-right">{Number.isFinite(c.eft) ? c.eft.toFixed(4) : '-'}</span>
                  <span className="font-mono text-right">{Number.isFinite(c.energy) ? c.energy.toFixed(2) : '-'}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default function RhoHistoryCard({ history, onClear }) {
  const [showAll, setShowAll] = useState(false)
  const entries = history || []
  const visible = showAll ? entries : entries.slice(-10)

  return (
    <Card className="shadow-lg col-span-1 md:col-span-3">
      <CardHeader className="flex items-center justify-between">
        <div>
          <CardTitle>RHO Decision History</CardTitle>
          <CardDescription>Track chosen VM and compare with runner-up to explain why.</CardDescription>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" onClick={() => setShowAll(v => !v)} disabled={entries.length <= 10}>
            {showAll ? 'Show Last 10' : 'Show All'}
          </Button>
          <Button size="sm" variant="destructive" onClick={() => onClear?.()} disabled={entries.length === 0}>
            Clear History
          </Button>
        </div>
      </CardHeader>
      <CardContent className="h-[400px] overflow-y-auto bg-gray-50 rounded-lg p-3 space-y-2">
        {entries.length === 0 && (
          <div className="h-full flex items-center justify-center text-gray-500 text-sm">No history yet. Start the simulation.</div>
        )}
        {visible.map((entry, idx) => (
          <EntryRow key={`${entry.taskId}-${idx}`} entry={entry} index={idx} />
        ))}
      </CardContent>
    </Card>
  )
}

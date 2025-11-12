import React, { useState } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './ui/Card'
import { cn } from './ui/cn'

export default function RhoInspectorCard({ data }) {
  if (!data) {
    return (
      <Card className="shadow-lg col-span-1 md:col-span-1">
        <CardHeader>
          <CardTitle>RHO Decision Inspector</CardTitle>
          <CardDescription>Waiting for simulation to start...</CardDescription>
        </CardHeader>
        <CardContent className="h-[400px] flex items-center justify-center">
          <p className="text-gray-500">Press Start</p>
        </CardContent>
      </Card>
    )
  }

  const { taskId, logReason, fitnessScores } = data

  const weights = data.weights || { w1: 0, w2: 0 }
  const efts = data.efts || []
  const energyCosts = data.energyCosts || []
  const normTime = data.normTime || []
  const normEnergy = data.normEnergy || []
  const minTime = data.minTime
  const maxTime = data.maxTime
  const minEnergy = data.minEnergy
  const maxEnergy = data.maxEnergy
  const decision = data.decision

  const [showDetails, setShowDetails] = useState(true)

  return (
    <Card className="shadow-lg col-span-1 md:col-span-1">
      <CardHeader>
        <CardTitle>RHO Decision Inspector</CardTitle>
        <CardDescription>
          Plan for <span className="font-bold text-black">Task {taskId}</span>:
          <br/>
          <span className="font-bold text-orange-600">{logReason}</span>
        </CardDescription>
      </CardHeader>
      <CardContent className="h-[400px] overflow-y-auto bg-gray-50 rounded-lg p-3 space-y-2">
        {/* Decision summary */}
        <div className="bg-white border border-gray-200 rounded-md p-2 text-xs">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <span className="font-semibold">Weights:</span>{' '}
              <span className="font-mono">w1 (time) = {weights.w1?.toFixed?.(2) ?? '-'}</span>,{' '}
              <span className="font-mono">w2 (energy) = {weights.w2?.toFixed?.(2) ?? '-'}</span>
            </div>
            <button
              className="text-blue-600 hover:underline"
              onClick={() => setShowDetails(v => !v)}
            >
              {showDetails ? 'Hide details' : 'Show details'}
            </button>
          </div>
          {decision && (
            <div className="mt-1 text-gray-700">
              <span className="font-semibold">Decision path:</span>{' '}
              <span className="font-mono">{decision.phase}</span>
              {Number.isFinite(decision.r1) && (
                <span className="ml-2 text-gray-500">r1={decision.r1.toFixed(2)}{Number.isFinite(decision.r2) ? `, r2=${decision.r2.toFixed(2)}` : ''}</span>
              )}
            </div>
          )}
          {showDetails && (Number.isFinite(minTime) || Number.isFinite(minEnergy)) && (
            <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2 text-gray-700">
              <div>
                <div className="font-semibold">Normalization ranges</div>
                <div className="font-mono">EFT: min={Number.isFinite(minTime) ? minTime.toFixed(4) : '-'}, max={Number.isFinite(maxTime) ? maxTime.toFixed(4) : '-'}</div>
                <div className="font-mono">Energy: min={Number.isFinite(minEnergy) ? minEnergy.toFixed(2) : '-'}, max={Number.isFinite(maxEnergy) ? maxEnergy.toFixed(2) : '-'}</div>
              </div>
              <div>
                <div className="font-semibold">Score formula</div>
                <div className="font-mono">scoreᵢ = w1 · normTimeᵢ + w2 · normEnergyᵢ</div>
              </div>
            </div>
          )}
        </div>

        {/* Table header */}
        <div className="grid grid-cols-6 gap-x-2 text-[11px] font-bold mb-1 sticky top-0 bg-gray-50 py-1">
          <span>VM</span>
          <span className="text-right">Score</span>
          <span className="text-right">Time part</span>
          <span className="text-right">Energy part</span>
          <span className="text-right">EFT</span>
          <span className="text-right">Energy</span>
        </div>

        {/* Rows */}
        {fitnessScores.map(({ vmId, score, isAlpha, isChosen }, idx) => {
          const t = normTime[idx] ?? null
          const e = normEnergy[idx] ?? null
          const timePart = Number.isFinite(t) && Number.isFinite(weights.w1) ? weights.w1 * t : null
          const energyPart = Number.isFinite(e) && Number.isFinite(weights.w2) ? weights.w2 * e : null
          const eftVal = efts[idx]
          const energyVal = energyCosts[idx]

          return (
            <div
              key={vmId}
              className={cn(
                'grid grid-cols-6 gap-x-2 items-center p-2 rounded-lg border text-xs',
                isAlpha && isChosen && 'bg-green-100 border-green-400 font-bold',
                isAlpha && !isChosen && 'bg-blue-100 border-blue-400',
                !isAlpha && isChosen && 'bg-orange-100 border-orange-400 font-bold',
                !isAlpha && !isChosen && 'bg-white border-gray-200'
              )}
            >
              <span className="font-medium">VM {vmId}</span>
              <span className="font-mono text-right">{score.toFixed(4)}</span>
              <span className="font-mono text-right">{timePart != null ? timePart.toFixed(4) : '-'}</span>
              <span className="font-mono text-right">{energyPart != null ? energyPart.toFixed(4) : '-'}</span>
              <span className="font-mono text-right">{Number.isFinite(eftVal) ? eftVal.toFixed(4) : '-'}</span>
              <span className="font-mono text-right">{Number.isFinite(energyVal) ? energyVal.toFixed(2) : '-'}</span>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}

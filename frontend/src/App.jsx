import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Play, Pause, RotateCcw, Rabbit, Turtle, Settings, ChevronDown, ChevronUp, BrainCircuit } from 'lucide-react'

import Button from './components/ui/Button'
import Slider from './components/ui/Slider'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './components/ui/Card'

import ApiKeyInput from './components/ApiKeyInput'
import MetricsCard from './components/MetricsCard'
import LoadChart from './components/charts/LoadChart'
import RhoInspectorCard from './components/RhoInspectorCard'
import RhoHistoryCard from './components/RhoHistoryCard'
import EnergyConsumptionChart from './components/charts/EnergyConsumptionChart'
import Modal from './components/Modal'

import {
  createVM, createTask,
  runRoundRobinStep, runRhoStep, runAcoStep,
  calculateLiveMetrics,
  getDefaultParams, getInitialBalancersState,
} from './lib/simulation'

function SimulationControls({ params, setParams, onStart, onReset, isSimulating, onPause }) {
  const [isOpen, setIsOpen] = useState(true)

  return (
    <Card className="shadow-lg">
      <CardHeader className="flex flex-row items-center justify-between cursor-pointer" onClick={() => setIsOpen(!isOpen)}>
        <div className="flex items-center space-x-2">
          <Settings className="w-6 h-6" />
          <CardTitle>Simulation Controls</CardTitle>
        </div>
        {isOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
      </CardHeader>
      {isOpen && (
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex flex-col space-y-4">
            <h4 className="font-medium">Actions</h4>
            <div className="flex space-x-2">
              {!isSimulating ? (
                <Button onClick={onStart} className="w-full">
                  <Play className="w-4 h-4 mr-2" /> Start
                </Button>
              ) : (
                <Button onClick={onPause} variant="destructive" className="w-full">
                  <Pause className="w-4 h-4 mr-2" /> Pause
                </Button>
              )}
              <Button onClick={onReset} variant="outline" className="w-full">
                <RotateCcw className="w-4 h-4 mr-2" /> Reset
              </Button>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Sim Speed (ms)</label>
              <div className="flex items-center space-x-2">
                <Turtle className="w-5 h-5" />
                <Slider
                  min={1}
                  max={500}
                  step={10}
                  value={[params.SIM_SPEED]}
                  onValueChange={([val]) => setParams(p => ({ ...p, SIM_SPEED: val }))}
                  disabled={isSimulating}
                />
                <Rabbit className="w-5 h-5" />
              </div>
              <span className="text-xs text-gray-500 text-center block">{params.SIM_SPEED}ms delay</span>
            </div>
          </div>

          <div className="flex flex-col space-y-4">
            <h4 className="font-medium">Environment</h4>
            <div className="space-y-2">
              <label className="text-sm font-medium">Number of VMs: {params.NUM_VMS}</label>
              <Slider
                min={5}
                max={50}
                step={1}
                value={[params.NUM_VMS]}
                onValueChange={([val]) => setParams(p => ({ ...p, NUM_VMS: val }))}
                disabled={isSimulating}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Number of Tasks: {params.NUM_TASKS}</label>
              <Slider
                min={100}
                max={2000}
                step={100}
                value={[params.NUM_TASKS]}
                onValueChange={([val]) => setParams(p => ({ ...p, NUM_TASKS: val }))}
                disabled={isSimulating}
              />
            </div>
          </div>

          <div className="flex flex-col space-y-4">
            <h4 className="font-medium">Algorithm Parameters</h4>
            <div className="space-y-2">
              <label className="text-sm font-medium">RHO Time Weight (w1): {params.RHO_WEIGHTS.w1.toFixed(1)}</label>

              <Slider
                min={0.1}
                max={0.9}
                step={0.1}
                value={[params.RHO_WEIGHTS.w1]}
                onValueChange={([val]) => setParams(p => ({ ...p, RHO_WEIGHTS: { w1: val, w2: 1 - val } }))}
                disabled={isSimulating}
              />
              <span className="text-xs text-gray-500 text-center block">
                Energy Weight (w2): {(1 - params.RHO_WEIGHTS.w1).toFixed(1)}
              </span>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">ACO Beta (Heuristic): {params.ACO_PARAMS.beta.toFixed(1)}</label>
              <Slider
                min={1}
                max={5}
                step={0.5}
                value={[params.ACO_PARAMS.beta]}
                onValueChange={([val]) => setParams(p => ({ ...p, ACO_PARAMS: { ...p.ACO_PARAMS, beta: val } }))}
                disabled={isSimulating}
              />
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  )
}

export default function App() {
  const [params, setParams] = useState(getDefaultParams())
  const [vms, setVms] = useState([])
  const [tasks, setTasks] = useState([])
  const [balancers, setBalancers] = useState(getInitialBalancersState(params.NUM_VMS, params.ACO_PARAMS))
  const [isSimulating, setIsSimulating] = useState(false)
  const [taskCounter, setTaskCounter] = useState(0)
  const [metrics, setMetrics] = useState({ rr: {}, rho: {}, aco: {} })
  const [metricsHistory, setMetricsHistory] = useState([])
  const [rhoInspectorData, setRhoInspectorData] = useState(null)
  const [rhoHistory, setRhoHistory] = useState([])

  // Gemini states
  const [apiKey, setApiKey] = useState('')
  const [modalContent, setModalContent] = useState(null) // { title, content }
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const simSpeedRef = useRef(params.SIM_SPEED)
  useEffect(() => {
    simSpeedRef.current = params.SIM_SPEED
  }, [params.SIM_SPEED])

  const initializeSimulation = useCallback(() => {
    const newVms = Array.from({ length: params.NUM_VMS }, (_, i) =>
      createVM(
        i,
        Math.floor(Math.random() * (params.VM_MIPS_RANGE[1] - params.VM_MIPS_RANGE[0] + 1)) + params.VM_MIPS_RANGE[0]
      )
    )
    const newTasks = Array.from({ length: params.NUM_TASKS }, (_, i) =>
      createTask(
        i,
        Math.floor(Math.random() * (params.TASK_LENGTH_RANGE[1] - params.TASK_LENGTH_RANGE[0] + 1)) + params.TASK_LENGTH_RANGE[0]
      )
    )

    setVms(newVms)
    setTasks(newTasks)
    setBalancers(getInitialBalancersState(params.NUM_VMS, params.ACO_PARAMS))
    setTaskCounter(0)
    setIsSimulating(false)
    setMetricsHistory([])
    setRhoInspectorData(null)
  }, [params])

  useEffect(() => {
    initializeSimulation()
  }, [initializeSimulation])

  const simulationStep = useCallback(() => {
    if (taskCounter >= tasks.length) {
      setIsSimulating(false)
      return
    }

    const task = tasks[taskCounter]

    setBalancers(currentBalancers => {
      const { newState: newRRState } = runRoundRobinStep(currentBalancers.rr, vms, task)
      const { newState: newRhoState, inspectorData: rhoData } = runRhoStep(currentBalancers.rho, vms, task, params.RHO_WEIGHTS)
      const { newState: newAcoState } = runAcoStep(currentBalancers.aco, vms, task)

      setRhoInspectorData(rhoData)
      setRhoHistory(prev => {
        const next = [...prev, rhoData]
        // cap to last 50 entries
        return next.length > 50 ? next.slice(next.length - 50) : next
      })

      return {
        rr: newRRState,
        rho: newRhoState,
        aco: newAcoState,
      }
    })

    setTaskCounter(c => c + 1)
  }, [taskCounter, tasks, vms, params.RHO_WEIGHTS])

  useEffect(() => {
    if (!isSimulating || taskCounter >= tasks.length) return

    const timerId = setTimeout(() => {
      simulationStep()
    }, simSpeedRef.current)
    return () => clearTimeout(timerId)
  }, [isSimulating, taskCounter, tasks.length, simulationStep])

  useEffect(() => {
    const rrMetrics = calculateLiveMetrics(balancers.rr, vms, taskCounter)
    const rhoMetrics = calculateLiveMetrics(balancers.rho, vms, taskCounter)
    const acoMetrics = calculateLiveMetrics(balancers.aco, vms, taskCounter)

    const newMetricsSet = { rr: rrMetrics, rho: rhoMetrics, aco: acoMetrics }
    setMetrics(newMetricsSet)

    if (taskCounter % 10 === 0 || taskCounter === 1 || taskCounter === params.NUM_TASKS) {
      setMetricsHistory(prevHistory => ([
        ...prevHistory,
        {
          task: taskCounter,
          rr_energy: rrMetrics['Energy (kJ)'],
          rho_energy: rhoMetrics['Energy (kJ)'],
          aco_energy: acoMetrics['Energy (kJ)'],
        }
      ]))
    }
  }, [balancers, vms, taskCounter, params.NUM_TASKS])

  const handleStart = () => setIsSimulating(true)
  const handlePause = () => setIsSimulating(false)
  const handleReset = () => initializeSimulation()
  const handleClearRhoHistory = () => setRhoHistory([])

  const callGemini = async (prompt) => {
    if (!apiKey) {
      setModalContent({ title: 'Error', content: 'Please enter your Gemini API key first.' })
      return null
    }

    setIsAnalyzing(true)
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`
    const systemPrompt = 'You are a helpful and concise assistant specializing in cloud computing and performance simulation. Your answers should be clear, easy to understand, and formatted in basic HTML (use <p>, <ul>, <li>, <strong>).'

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          systemInstruction: { parts: [{ text: systemPrompt }] },
        })
      })

      if (!response.ok) throw new Error(`API error: ${response.statusText}`)

      const result = await response.json()
      const text = result.candidates?.[0]?.content?.parts?.[0]?.text
      if (!text) throw new Error('Invalid response from API.')
      return text

    } catch (error) {
      console.error('Gemini API call failed:', error)
      return `<p><strong>Error:</strong> ${error.message}. Please check your API key and network connection.</p>`
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getExplanationPrompt = (metricTitle, metrics) => {
    return `
      Please explain all of the following metrics in the context of cloud load balancing simulation:
      <ul>
        ${Object.keys(metrics).map(key => `<li><strong>${key}</strong></li>`).join('')}
      </ul>
      For each one, briefly state what it measures and whether a higher or lower value is generally better.
    `
  }

  const handleExplainMetric = async (title, metrics) => {
    setModalContent({ title: `Explain: ${title}`, content: '', isLoading: true })
    const prompt = getExplanationPrompt(title, metrics)
    const explanation = await callGemini(prompt)
    setModalContent({ title: `Explain: ${title}`, content: explanation, isLoading: isAnalyzing })
  }

  const getAnalysisPrompt = () => {
    const finalMetrics = {
      'Round Robin': metrics.rr,
      'Rock Hyrax (RHO)': metrics.rho,
      'Ant Colony (ACO)': metrics.aco,
    }
    const promptMetrics = JSON.stringify(finalMetrics, (key, value) => 
      typeof value === 'number' ? value.toFixed(2) : value, 
      2
    )

    return `
      <p>Please act as a cloud performance analyst. I have just run a simulation comparing three load balancing algorithms. Here are the final results:</p>
      <pre>${promptMetrics}</pre>
      <p>Please provide a concise analysis. Answer the following:</p>
      <ul>
        <li><strong>Which algorithm performed best overall and why?</strong></li>
        <li><strong>What are the key trade-offs?</strong> (e.g., did one win on Makespan but lose on Energy?)</li>
        <li><strong>Give a brief recommendation</strong> based on these results.</li>
      </ul>
    `
  }

  const handleAnalyzeResults = async () => {
    setModalContent({ title: '✨ Simulation Analysis', content: '', isLoading: true })
    const prompt = getAnalysisPrompt()
    const analysis = await callGemini(prompt)
    setModalContent({ title: '✨ Simulation Analysis', content: analysis, isLoading: isAnalyzing })
  }

  const isSimulationDone = taskCounter >= params.NUM_TASKS

  return (
    <div className="min-h-screen bg-gray-100 p-4 md:p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-2 md:space-y-0">
          <h1 className="text-3xl font-bold text-gray-900">Real-Time Load Balancing Dashboard</h1>
          <div className="flex items-center space-x-4">
            {isSimulationDone && !isSimulating && (
              <Button onClick={handleAnalyzeResults} disabled={!apiKey || isAnalyzing}>
                <BrainCircuit className="w-4 h-4 mr-2" />
                ✨ Analyze Final Results
              </Button>
            )}
            <div className="flex items-center space-x-2">
              <div className={
                [
                  'w-3 h-3 rounded-full',
                  isSimulating ? 'bg-green-500 animate-pulse' : (isSimulationDone ? 'bg-blue-500' : 'bg-gray-400')
                ].join(' ')
              }/>
              <span className="text-sm text-gray-600">Tasks Processed: {taskCounter} / {params.NUM_TASKS}</span>
            </div>
          </div>
        </div>

        {/* <ApiKeyInput apiKey={apiKey} setApiKey={setApiKey} /> */}

        <SimulationControls 
          params={params}
          setParams={setParams}
          onStart={handleStart}
          onReset={handleReset}
          onPause={() => setIsSimulating(false)}
          isSimulating={isSimulating}
        />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <MetricsCard 
            title="Round Robin" 
            metrics={metrics.rr} 
            onExplainClick={() => handleExplainMetric('Round Robin Metrics', metrics.rr)} 
          />
          <MetricsCard 
            title="Rock Hyrax (RHO)" 
            metrics={metrics.rho} 
            onExplainClick={() => handleExplainMetric('Rock Hyrax (RHO) Metrics', metrics.rho)}
          />
          <MetricsCard 
            title="Ant Colony (ACO)" 
            metrics={metrics.aco} 
            onExplainClick={() => handleExplainMetric('Ant Colony (ACO) Metrics', metrics.aco)}
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <LoadChart vms={vms} balancers={balancers} />
          <RhoInspectorCard data={rhoInspectorData} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <RhoHistoryCard history={rhoHistory} onClear={handleClearRhoHistory} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <EnergyConsumptionChart data={metricsHistory} />
        </div>

        {modalContent && (
          <Modal 
            title={modalContent.title}
            content={modalContent.content}
            isLoading={isAnalyzing || modalContent.isLoading}
            onClose={() => setModalContent(null)}
          />
        )}

      </div>
    </div>
  )
}

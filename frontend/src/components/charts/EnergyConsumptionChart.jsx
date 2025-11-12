import React from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/Card'
import { ResponsiveContainer, LineChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Line } from 'recharts'

export default function EnergyConsumptionChart({ data }) {
  return (
    <Card className="shadow-lg col-span-1 md:col-span-3">
      <CardHeader>
        <CardTitle>Real-Time Energy Consumption</CardTitle>
        <CardDescription>Total cumulative energy (kJ) consumed by all VMs as tasks are processed.</CardDescription>
      </CardHeader>
      <CardContent className="h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="task" fontSize={12} unit=" tasks" />
            <YAxis fontSize={12} unit=" kJ" />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="rr_energy" name="Round Robin" stroke="#3b82f6" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="rho_energy" name="RHO" stroke="#f97316" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="aco_energy" name="ACO" stroke="#16a34a" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

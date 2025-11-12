import React, { useMemo } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/Card'
import { ResponsiveContainer, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Bar } from 'recharts'

export default function LoadChart({ vms, balancers }) {
  const chartData = useMemo(() => {
    return vms.map((vm, i) => ({
      name: `VM ${vm.id}`,
      'Round Robin': balancers.rr.vmLoads[i] / vm.mips,
      'RHO': balancers.rho.vmLoads[i] / vm.mips,
      'ACO': balancers.aco.vmLoads[i] / vm.mips,
    }))
  }, [vms, balancers])

  return (
    <Card className="shadow-lg col-span-1 md:col-span-2">
      <CardHeader>
        <CardTitle>Live Load Distribution</CardTitle>
        <CardDescription>Current finish time (in seconds) for each VM.</CardDescription>
      </CardHeader>
      <CardContent className="h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" fontSize={12} />
            <YAxis fontSize={12} />
            <Tooltip />
            <Legend />
            <Bar dataKey="Round Robin" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="RHO" fill="#f97316" radius={[4, 4, 0, 0]} />
            <Bar dataKey="ACO" fill="#16a34a" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

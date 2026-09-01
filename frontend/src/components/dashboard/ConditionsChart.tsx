"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type Point = { time: string; onda: number; vento: number };

export function ConditionsChart({ data }: { data: Point[] }) {
  return (
    <div className="conditions-chart" aria-label="Gráfico de tendência de ondas e vento">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 12, right: 6, bottom: 0, left: -24 }}>
          <defs>
            <linearGradient id="wave" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#45d4bd" stopOpacity={0.45}/><stop offset="1" stopColor="#45d4bd" stopOpacity={0}/></linearGradient>
            <linearGradient id="wind" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#f6d365" stopOpacity={0.25}/><stop offset="1" stopColor="#f6d365" stopOpacity={0}/></linearGradient>
          </defs>
          <CartesianGrid stroke="#173742" strokeDasharray="4 6" vertical={false} />
          <XAxis dataKey="time" tick={{ fill: "#82a0aa", fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "#82a0aa", fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip contentStyle={{ background: "#0c2833", border: "1px solid #244550", borderRadius: 12 }} />
          <Area type="monotone" dataKey="vento" stroke="#f6d365" fill="url(#wind)" strokeWidth={2} />
          <Area type="monotone" dataKey="onda" stroke="#45d4bd" fill="url(#wave)" strokeWidth={3} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

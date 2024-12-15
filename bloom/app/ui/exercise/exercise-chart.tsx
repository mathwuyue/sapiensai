import { Exercise, ExerciseType, ExerciseIntensity, ExerciseWithCalories } from "@/app/lib/definitions";

import { Bar, BarChart,CartesianGrid,XAxis,YAxis } from "recharts"
 
import { ChartContainer, ChartTooltipContent,type ChartConfig } from "@/components/ui/chart"
 
export const data:ExerciseWithCalories[] = [
    {
      user_id: "1",
      exercise: "run" as ExerciseType,
      calories: 100,
      start_time: "2024-01-01T08:00:00",
      duration: 30,
      intensity: "medium" as ExerciseIntensity,
      bpm: 120,
      remark: "今天感觉有点累",
      summary: "今天跑了30分钟，感觉有点累",
      advice: "建议适当休息，不要过度运动"
    },
    {
      user_id: "1",
      exercise: "run" as ExerciseType,
      calories: 30,
      start_time: "2024-01-01T09:00:00",
      duration: 30,
      intensity: "medium" as ExerciseIntensity,
      bpm: 120,
      remark: "今天感觉有点累",
      summary: "今天跑了30分钟，感觉有点累",
      advice: "建议适当休息，不要过度运动"
    },
    {
      user_id: "1",
      exercise: "run" as ExerciseType,
      calories: 120,
      start_time: "2024-01-02T09:00:00",
      duration: 30,
      intensity: "medium" as ExerciseIntensity,
      bpm: 120,
      remark: "今天感觉有点累",
      summary: "今天跑了30分钟，感觉有点累",
      advice: "建议适当休息，不要过度运动"
    },
    {
      user_id: "1",
      exercise: "run" as ExerciseType,
      calories: 250,
      start_time: "2024-01-03T09:00:00",
      duration: 30,
      intensity: "medium" as ExerciseIntensity,
      bpm: 120,
      remark: "今天感觉有点累",
      summary: "今天跑了30分钟，感觉有点累",
      advice: "建议适当休息，不要过度运动"
    }
  
  ]
  const chartConfig = {
    calories: {
      label: "Calories",
      color: "#2563eb",
    },
  } satisfies ChartConfig
  
export function ExerciseChart() {
  return (
    // <ChartContainer config={chartConfig} className="min-h-[200px] w-full">
    //   <BarChart accessibilityLayer data={data}>
    //     <Bar dataKey="calories" fill="var(--color-calories)" radius={4} />
    //   </BarChart>
    // </ChartContainer>
    <ChartContainer config={chartConfig} className="min-h-[200px] w-full">
      <BarChart accessibilityLayer data={data}>
        <>
          <XAxis dataKey="start_time" tickLine={false} tickMargin={10} axisLine={false} tickFormatter={(value) => value.slice(0, 3)} />
          <Bar dataKey="calories" fill="var(--color-calories)" radius={4} />
        </>
      </BarChart>
    </ChartContainer>
    
  )
}

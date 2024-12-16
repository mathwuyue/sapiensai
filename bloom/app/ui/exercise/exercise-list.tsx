import { fetchExerciseRecords } from "@/app/lib/actions/exercise";
import { useEffect, useState } from "react";
import { Exercise, ExerciseType, ExerciseIntensity, ExerciseWithCalories } from "@/app/lib/definitions";

import { Bar, BarChart,CartesianGrid,XAxis,YAxis } from "recharts"
 
import { ChartContainer, ChartTooltipContent,type ChartConfig } from "@/components/ui/chart"
 
// export function MyChart() {
//   return (
//     <ChartContainer>
//       <BarChart data={data}>
//         <Bar dataKey="value" />
//         <ChartTooltip content={<ChartTooltipContent />} />
//       </BarChart>
//     </ChartContainer>
//   )
// }

const chartConfig = {
  calories: {
    label: "Calories",
    color: "#2563eb",
  },
} satisfies ChartConfig



const data:ExerciseWithCalories[] = [
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

export function ExerciseList() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRecords() {
      try {
        const data = await fetchExerciseRecords();
        setRecords(data);
      } catch (error) {
        console.error('Failed to load records:', error);
      } finally {
        setLoading(false);
      }
    }

    loadRecords();
  }, []);

  if (loading) return <div>加载中...</div>;
  if (!records.length) return <div>暂无运动记录</div>;

  return (
    <>
    {/* <ChartContainer config={chartConfig} className="min-h-[200px] w-full">
      <BarChart accessibilityLayer data={data}>
        <>
          <XAxis dataKey="start_time" tickLine={false} tickMargin={10} axisLine={false} tickFormatter={(value) => value.slice(0, 3)} />
          <Bar dataKey="calories" fill="var(--color-calories)" radius={4} />
        </>
      </BarChart>
    </ChartContainer> */}
    
    <div className="space-y-4">
      {records.map((record: any) => (
        <div key={record.id} className="p-4 border rounded-lg">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-medium">{record.exercise}</h3>
              <p className="text-sm text-gray-500">
                {new Date(record.start_time).toLocaleString()}
              </p>
            </div>
            <div className="text-right">
              <p>Length: {record.duration} minutes</p>
              <p>Intensity: {record.intensity}</p>
            </div>
          </div>
          {record.bpm && (
            <p className="mt-2 text-sm">Heart Rate: {record.bpm}</p>
          )}
          {
            record.calories && (
              <p className="mt-2 text-sm">Calories: {record.calories}</p>
            )
          }
          {record.remark && (
            <p className="mt-2 text-sm text-gray-600">{record.remark}</p>
          )}
          {record.summary && (
            <div className="mt-3 p-3 bg-gray-50 rounded">
              <p className="text-sm">{record.summary}</p>
              {record.advice && (
                <p className="mt-2 text-sm text-blue-600">Advice: {record.advice}</p>
              )}
            </div>
          )}
        </div>
      ))}
      
    </div>
  
    </>
  );
}
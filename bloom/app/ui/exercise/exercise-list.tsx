import { fetchExerciseRecords, deleteExerciseRecord } from "@/app/lib/actions/exercise";
import { useEffect, useState } from "react";
import { Exercise, ExerciseType, ExerciseIntensity, ExerciseWithCalories } from "@/app/lib/definitions";

import { Bar, BarChart,CartesianGrid,XAxis,YAxis,Tooltip,ResponsiveContainer } from "recharts"
 
import { ChartContainer, ChartTooltipContent,type ChartConfig } from "@/components/ui/chart"
 


const chartConfig = {
  calories: {
    label: "Calories",
    color: "#2563eb",
  },
} satisfies ChartConfig




export function ExerciseList() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteId, setDeleteId] = useState<string | null>(null);

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

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this record?')) {
      try {
        await deleteExerciseRecord(id);
        setRecords(records.filter((record:any) => record.id !== id));
        //setDeleteId(null);
      } catch (error) {
        console.error('Delete failed:', error);
      }
    }
  };
  const caloriesData = records.map((record: any) => ({
    calories: Math.round(record.calories),
    start_time: record.start_time
  })).sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());

  if (loading) return <div>Loading...</div>;
  if (!records.length) return <div>No exercise records</div>;

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
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={caloriesData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="start_time" 
            tickFormatter={(value) => new Date(value).toLocaleDateString()}
          />
          <YAxis dataKey="calories" tickFormatter={(value) => `${value} kcal`} />
          <Tooltip />
          <Bar 
            dataKey="calories" 
            fill="#2563eb"
            radius={[4, 4, 0, 0]}
            maxBarSize={40}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
      {records.map((record: any) => (
        <div key={record.id} className="p-4 border rounded-lg">
          <div className="flex justify-between items-start">
          <button
          onClick={() => handleDelete(record.id)}
          className="text-red-600 hover:text-red-800"
          >
          Delete
          </button>
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
              <p className="mt-2 text-sm">Calories: {Math.round(record.calories)}</p>
            )
          }
          {record.remark && (
            <p className="mt-2 text-sm text-gray-600">{record.remark}</p>
          )}
         
          {(record.summary || record.advice) && (
        <div className="mt-3 p-3 bg-gray-50 rounded">
        {record.summary && (
          <p className="text-sm">Summary: {record.summary}</p>
        )}
        {record.advice && (
            <p className="mt-2 text-sm text-blue-600">
            Advice: {record.advice}
          </p>
        )}
      </div>
    )}
        </div>
      ))}
      
    </div>
  
    </>
  );
}
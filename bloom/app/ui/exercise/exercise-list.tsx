import { fetchExerciseRecords, deleteExerciseRecord } from "@/app/lib/actions/exercise";
import { useEffect, useState, useMemo } from "react";
import { Exercise, ExerciseType, ExerciseIntensity, ExerciseWithCalories } from "@/app/lib/definitions";

import { Bar, BarChart,CartesianGrid,XAxis,YAxis,Tooltip,ResponsiveContainer } from "recharts"
 
import { ChartContainer, ChartTooltipContent,type ChartConfig } from "@/components/ui/chart"
import { Trash, ChevronUp, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button"

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
  const [page, setPage] = useState(1);
  const [isExpanded, setIsExpanded] = useState(false);
  // const [records, setRecords] = useState([]);
  // 使用 Map 或对象来存储每个记录的展开状态
  const [expandedStates, setExpandedStates] = useState<Record<number, boolean>>({});

  const itemsPerPage = 3;
  const toggleExpand = (recordId: number) => {
    setExpandedStates(prev => ({
      ...prev,
      [recordId]: !prev[recordId]
    }));
  };

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



  const groupedRecords = useMemo(() => {
    const groups = records.reduce((acc, record:any) => {
      const date = new Date(record.start_time).toISOString().split('T')[0];
      if (!acc[date]) {
        acc[date] = [];
      }
      acc[date].push(record);
      return acc;
    }, {} as Record<string, Exercise[]>);

    // 每组内按时间正序
    Object.keys(groups).forEach(date => {
      groups[date].sort((a, b) => 
        new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
      );
    });

    return groups;
  }, [records]);

  const sortedDates = useMemo(() => 
    Object.keys(groupedRecords).sort((a, b) => 
      new Date(b).getTime() - new Date(a).getTime()
    ), [groupedRecords]
  );

  // 分页
  const paginatedDates = sortedDates.slice(
    (page - 1) * itemsPerPage,
    page * itemsPerPage
  );

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
      {/* {records.map((record: any) => (
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
      ))} */}
      
      {paginatedDates.map(date => (
        <div key={date} className="space-y-2">
          <h3 className="font-medium text-gray-900">
            {new Date(date).toLocaleDateString('zh-CN')}
          </h3>
          <div className="space-y-2">
            {groupedRecords[date].map((record:any) => (
              <div key={record.id} className="p-4 border rounded-lg relative">
                {/* 删除按钮 */}
                <button
                  onClick={() => handleDelete(record.id)}
                  className="absolute top-4 right-4 text-red-500 hover:text-red-700"
                >
                  <Trash className="h-5 w-5" />
                </button>
                <div className="pr-12">
                  <h4 className="font-medium">{record.exercise}</h4>
                  <p className="text-sm text-gray-500">
                    {new Date(record.start_time).toLocaleString()}
                  </p>
                  <div className="flex justify-between items-cente">
                    <p>Duration: {record.duration} minutes</p>
                    <p>Intensity: {record.intensity}</p>
                    {record.calories && (
                      <p>Calories: {Math.round(record.calories)}</p>
                    )}
                  </div>
                  <div className="flex justify-between items-center">

                  {record.bpm && (
            <p className="mt-2 text-sm">Heart Rate: {record.bpm}</p>
          )}
          {record.remark && (
            <p className="mt-2 text-sm text-gray-600">{record.remark}</p>
          )}
                    </div>
                        {/* <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
          >
            {isExpanded ? "Show less" : "Show more"}
            {isExpanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </button> */}
          <button
                  onClick={() => toggleExpand(record.id)}
                  className="mt-2 text-sm text-blue-600 hover:text-blue-800"
                >
                  {expandedStates[record.id] ? "Show less" : "Show more"}
                </button>
                </div>

                {/* {isExpanded && (
          <div className="mt-4 space-y-4 text-sm border-t pt-4">
            {record.summary && (
              <div>
                <h5 className="font-medium text-gray-900 mb-1">Summary</h5>
                <p className="text-gray-600 leading-relaxed">{record.summary}</p>
              </div>
            )}
            {record.advice && (
              <div>
                <h5 className="font-medium text-gray-900 mb-1">Advice</h5>
                <p className="text-gray-600 leading-relaxed">{record.advice}</p>
              </div>
            )}
          </div>
        )} */}
        {expandedStates[record.id] && (
                  <div className="mt-3 space-y-3 text-sm border-t pt-3">
                    {record.summary && (
                      <div>
                        <p className="font-medium">Summary</p>
                        <p className="text-gray-600">{record.summary}</p>
                      </div>
                    )}
                    {record.advice && (
                      <div>
                        <p className="font-medium">Advice</p>
                        <p className="text-gray-600">{record.advice}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
              ))}
<div className="flex items-center justify-between border-t pt-4">
        <div className="text-sm text-gray-500">
          Page {page} of {Math.ceil(sortedDates.length / itemsPerPage)}
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => p + 1)}
            disabled={page * itemsPerPage >= sortedDates.length}
          >
            Next
          </Button>
          </div>


    </div>
    </div>
  
    </>
  );
}
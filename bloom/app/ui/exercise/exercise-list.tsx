import { fetchExerciseRecords } from "@/app/lib/actions/exercise";
import { useEffect, useState } from "react";

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
              <p>时长: {record.duration}分钟</p>
              <p>强度: {record.intensity}</p>
            </div>
          </div>
          {record.bpm && (
            <p className="mt-2 text-sm">心率: {record.bpm}</p>
          )}
          {record.remark && (
            <p className="mt-2 text-sm text-gray-600">{record.remark}</p>
          )}
          {record.summary && (
            <div className="mt-3 p-3 bg-gray-50 rounded">
              <p className="text-sm">{record.summary}</p>
              {record.advice && (
                <p className="mt-2 text-sm text-blue-600">建议：{record.advice}</p>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
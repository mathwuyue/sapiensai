"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { createExerciseRecord } from "@/app/lib/actions/exercise";
import { PlusCircle, Trash2 } from "lucide-react";
import internal from "stream";
import { Exercise, ExerciseType, ExerciseIntensity, EXERCISE_TYPES, INTENSITY_TYPES } from "@/app/lib/definitions";
import { Textarea } from "@/components/ui/textarea";

interface ExerciseEntry {
    exercise: ExerciseType;
    intensity: ExerciseIntensity;
    duration: number;
    bpm?: number;
    start_time: string;
    remark?: string;
    customType?: string;  // 添加这行
  }
  
   



interface CreateExerciseModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CreateExerciseModal({ isOpen, onClose }: CreateExerciseModalProps) {
  const [entries, setEntries] = useState<ExerciseEntry[]>([
    {
        exercise: "walking",
        customType: '',
        intensity: "gentle",
        duration: 0,
        start_time: '', // 格式化为 "YYYY-MM-DD"
        remark: '',

    }
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{
    summary?: string;
    advice?: string;
  } | null>(null);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage(null);
    setFeedback(null); // 重置反馈

    try {
      for (const entry of entries) {
        if (!entry.exercise) {
            setMessage("Please select exercise type");
            return;
          }
          if (!entry.intensity) {
            setMessage("Please select exercise intensity");
            return;
          }
          if (!entry.duration || entry.duration <= 0) {
            setMessage("Please enter valid exercise duration");
            return;
          }
          if (!entry.start_time) {
            setMessage("Please select start time");
            return;
          }
    
        const form = new FormData();
        // console.log('提交的数据:', {
        //     exercise: entry.exercise,
        //     intensity: entry.intensity,
        //     duration: entry.duration,
        //     start_time: entry.start_time,
        //     bpm: entry.bpm,
        //     remark: entry.remark
        //   });
        const exerciseType = entry.exercise === 'other' ? entry.customType! : entry.exercise;
        form.append("exercise", exerciseType);
        form.append("intensity", String(entry.intensity));
        form.append("duration", String(entry.duration));
        form.append("start_time", new Date(entry.start_time).toISOString());
        if (entry.bpm && entry.bpm > 0) {
            form.append("bpm", String(entry.bpm));
          }
          
          if (entry.remark) {
            form.append("remark", String(entry.remark));
          }
          console.log('提交的数据:', {
            exercise: exerciseType,
            intensity: entry.intensity,
            duration: entry.duration,
            start_time: entry.start_time,
            bpm: entry.bpm,
            remark: entry.remark
          });
        const response = await createExerciseRecord({}, form);
        console.log('API 响应:', response);
        
        if (response.message === "Success") {
          setFeedback({
            summary: response.summary,
            advice: response.advice
          });
          setMessage("运动记录已添加成功！");
        } else {
          setMessage(response.message || "添加失败");
          return;
        }
      }
      
    //   setEntries([
    //     {
    //       exercise: "walking",
    //       intensity: "gentle",
    //       duration: 0,
    //       start_time: new Date().toISOString().split('T')[0]
    //     }
    //   ]);
      setMessage("Exercise record added");
      setTimeout(() => {
        onClose();
        setMessage(null);
        setFeedback(null);
        setEntries([{
            exercise: 'walking',
            intensity: 'gentle',
            duration: 0,
            bpm: undefined,
            start_time: new Date().toISOString().split('T')[0],
            remark: '',
            customType: ''
          }]);
      }, 10000);
    } catch (error) {
      setMessage("Failed to add exercise record");
    } finally {
      setIsSubmitting(false);
    }
  };

  const addEntry = () => {
    setEntries([
      ...entries,
      {
        exercise: "walking",
        intensity: "gentle",
        duration: 0,
        start_time: new Date().toISOString().split('T')[0]
      }
    ]);
  };

  const removeEntry = (index: number) => {
    setEntries(entries.filter((_, i) => i !== index));
  };

  const updateEntry = (index: number, field: keyof ExerciseEntry, value: string) => {
    const newEntries = [...entries];
    newEntries[index] = { ...newEntries[index], [field]: value };
    setEntries(newEntries);
  };

//   const updateEntry = (index: number, field: keyof ExerciseEntry, value: any) => {
//     const newEntries = [...entries];
//     if (field === 'duration') {
//       newEntries[index] = { 
//         ...entries[index], 
//         [field]: Number(value) // 确保转换为数字
//       };
//     } else {
//       newEntries[index] = { 
//         ...entries[index], 
//         [field]: value 
//       };
//     }
//     setEntries(newEntries);
//   };
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add Exercise Record</DialogTitle>
        </DialogHeader>

        {message && (
        <div className={`p-4 rounded-md ${
          message.includes('Failed') 
            ? 'bg-red-100 text-red-800' 
            : 'bg-green-100 text-green-800'
        }`}>
          {message}
        </div>
      )}

      {feedback && (
        <div className="mt-4 space-y-4">
          {feedback.summary && (
            <div className="p-4 rounded-md bg-blue-50">
              <h3 className="font-semibold text-blue-800 mb-2">Exercise Summary</h3>
              <p className="text-blue-700">{feedback.summary}</p>
            </div>
          )}
          
          {feedback.advice && (
            <div className="p-4 rounded-md bg-green-50">
              <h3 className="font-semibold text-green-800 mb-2">Advice</h3>
              <p className="text-green-700">{feedback.advice}</p>
            </div>
          )}
        </div>
      )}

        <form onSubmit={handleSubmit} className="space-y-4">
          
          {entries.map((entry, index) => (
            
            <div key={index} className="space-y-4 p-4 border rounded-lg relative">
                {entries.length > 1 && (
        <Button
        type="button"
        variant="ghost"
        size="icon"
        className="absolute top-2 right-2"
        onClick={() => removeEntry(index)}
      >
        <Trash2 className="h-4 w-4" />
              </Button>
            )}
              <div className="grid gap-4">
              <div className="grid gap-2">
                
              <label>Exercise Type</label>
              <Select
                value={entry.exercise}
                onValueChange={(value) => {
                  const newEntries = [...entries];
                  newEntries[index] = { ...entry, exercise: value as ExerciseType };
                  setEntries(newEntries);
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select Exercise Type" />
                </SelectTrigger>
                <SelectContent>
                  {EXERCISE_TYPES.map((type) => (
                    <SelectItem key={type} value={type}>
                      {type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
  
  {entry.exercise === 'other' && (
    <Input
      className="mt-2"
      placeholder="Please enter the exercise type"
      value={entry.customType || ''}
      onChange={(e) => updateEntry(index, "customType", e.target.value)}
      required
    />
  )}
</div>

  <div className="grid gap-2">
    <label>Intensity</label>
    <Select value={entry.intensity} onValueChange={(v) => updateEntry(index, "intensity", v)}>
      <SelectTrigger>
        <SelectValue placeholder="Select Intensity" />
      </SelectTrigger>
      <SelectContent>
                  {INTENSITY_TYPES.map((type) => (
                    <SelectItem key={type} value={type}>
                      {type}
                    </SelectItem>
                  ))}
            </SelectContent>
    </Select>
  </div>

  <div className="grid gap-2">
    <label>Duration(minutes)</label>
    <Input
      type="number"
      value={entry.duration}
      onChange={(e) => updateEntry(index, "duration", e.target.value)}
    />
  </div>

  <div className="grid gap-2">
    <label>Heart Rate(optional)</label>
    <Input
      type="number"
      value={entry.bpm || ''}
      onChange={(e) => updateEntry(index, "bpm", e.target.value)}
    />
  </div>

  <div className="grid gap-2">
    <label>Start Time</label>
    <Input
      type="datetime-local"
      value={entry.start_time}
      onChange={(e) => updateEntry(index, "start_time", e.target.value)}
    />
  </div>

  <div className="grid gap-2">
    <label>Remark(optional)</label>
    <Textarea
      value={entry.remark || ''}
      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => updateEntry(index, "remark", e.target.value)}
      placeholder="Feelings after exercise, body state, etc."
    />
  </div>
</div>

            </div>
          ))}

          {/* <Button
            type="button"
            variant="outline"
            className="w-full"
            onClick={addEntry}
          >
            <PlusCircle className="mr-2 h-4 w-4" />
            Add More Record
          </Button> */}

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Adding..." : "Save Record"}
            </Button>
          </div>
          
          
        </form>
        
      </DialogContent>
      
    </Dialog>
    
  );
}
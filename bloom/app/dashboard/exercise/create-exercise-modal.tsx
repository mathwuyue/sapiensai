"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { createExerciseRecord } from "@/app/lib/actions/exercise";
import { PlusCircle, Trash2 } from "lucide-react";
import internal from "stream";
import {
  Exercise,
  ExerciseType,
  ExerciseIntensity,
  EXERCISE_TYPES,
  INTENSITY_TYPES,
} from "@/app/lib/definitions";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/use-toast";
import { useTranslations } from "next-intl";

interface ExerciseEntry {
  exercise: ExerciseType;
  intensity: ExerciseIntensity;
  duration: number;
  bpm?: number;
  start_time: string;
  remark?: string;
  customType?: string; // 添加这行
}

interface CreateExerciseModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CreateExerciseModal({
  isOpen,
  onClose,
}: CreateExerciseModalProps) {
  const t = useTranslations("exercise");
  const [entries, setEntries] = useState<ExerciseEntry[]>([
    {
      exercise: "walking",
      customType: "",
      intensity: "gentle",
      duration: 0,
      start_time: "", // 格式化为 "YYYY-MM-DD"
      remark: "",
    },
  ]);

  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{
    summary?: string;
    advice?: string;
  } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // toast({
    //   title: "测试",
    //   description: "这是一个测试消息",
    //   duration: 3000,  // 3秒后自动关闭
    // });

    setIsSubmitting(true);
    setMessage(null);
    setFeedback(null); // 重置反馈

    try {
      for (const entry of entries) {
        if (!entry.exercise) {
          toast({
            title: "Please select exercise type",
            variant: "destructive",
          });
          return;
        }
        if (!entry.intensity) {
          toast({
            title: "Please select exercise intensity",
            variant: "destructive",
          });
          return;
        }
        if (!entry.duration || entry.duration <= 0) {
          toast({
            title: "Please enter valid exercise duration",
            variant: "destructive",
          });
          return;
        }
        if (!entry.start_time) {
          toast({
            title: "Please select start time",
            variant: "destructive",
          });
          return;
        }
        const form = new FormData();
        const exerciseType =
          entry.exercise === "other" ? entry.customType! : entry.exercise;
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

        console.log("提交的数据:", {
          exercise: exerciseType,
          intensity: entry.intensity,
          duration: entry.duration,
          start_time: entry.start_time,
          bpm: entry.bpm,
          remark: entry.remark,
        });
        const response = await createExerciseRecord({}, form);
        console.log("createExerciseRecord response:", response);
        // if (response && response.data && response.data.id) {  // 确保 id 存在
        //   await updateExerciseRecord(response.data.id,
        //     response.data.summary,
        //     response.data.advice
        //   );
        // }

        if (!response) {
          toast({
            title: "Failed",
            description: "Server not responding",
            variant: "destructive",
          });
          return;
        }

        if (response?.message === "Success") {
          toast({
            title: t("exercise_record_added_successfully"),
            description: (
              <div className="mt-2 space-y-2">
                {response.summary && (
                  <div className="p-2 rounded bg-blue-50">
                    <span className="font-semibold"> {t("summary")} </span>
                    <p>{response.summary}</p>
                  </div>
                )}
                {response.advice && (
                  <div className="p-2 rounded bg-green-50">
                    <span className="font-semibold"> {t("advice")} </span>
                    <p>{response.advice}</p>
                  </div>
                )}
              </div>
            ),
            duration: 8000, // 显示 8 秒
            className: "bg-white",
          });

          setTimeout(() => {
            onClose();
            setEntries([
              {
                exercise: "walking",
                intensity: "gentle",
                duration: 0,
                bpm: undefined,
                start_time: new Date().toISOString().split("T")[0],
                remark: "",
                customType: "",
              },
            ]);
          }, 1000);
        } else {
          toast({
            title: t("failed_to_add_exercise_record"),
            description: response.message || "Unknown error",
            variant: "destructive",
          });
        }
      }
    } catch (error) {
      toast({
        title: t("error"),
        description: t("failed_to_add_exercise_record"),
        variant: "destructive",
      });
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
        start_time: new Date().toISOString().split("T")[0],
      },
    ]);
  };

  const removeEntry = (index: number) => {
    setEntries(entries.filter((_, i) => i !== index));
  };

  const updateEntry = (
    index: number,
    field: keyof ExerciseEntry,
    value: string
  ) => {
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
      <DialogContent
        className="w-[90%] max-w-[400px] md:w-full p-4 md:p-6"
        aria-describedby="dialog-description"
      >
        <DialogHeader>
          <DialogTitle>{t("add_exercise_record")}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {entries.map((entry, index) => (
            <div
              key={index}
              className="space-y-4 p-4 border rounded-lg relative"
            >
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
                  <label>{t("exercise_type")}</label>
                  <Select
                    value={entry.exercise}
                    onValueChange={(value) => {
                      const newEntries = [...entries];
                      newEntries[index] = {
                        ...entry,
                        exercise: value as ExerciseType,
                      };
                      setEntries(newEntries);
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t("select_exercise_type")} />
                    </SelectTrigger>
                    <SelectContent>
                      {EXERCISE_TYPES.map((type) => (
                        <SelectItem key={type} value={type}>
                          {type}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  {entry.exercise === "other" && (
                    <Input
                      className="mt-2"
                      placeholder={t("please_enter_the_exercise_type")}
                      value={entry.customType || ""}
                      onChange={(e) =>
                        updateEntry(index, "customType", e.target.value)
                      }
                      required
                    />
                  )}
                </div>

                <div className="grid gap-2">
                  <label>{t("intensity")}</label>
                  <Select
                    value={entry.intensity}
                    onValueChange={(v) => updateEntry(index, "intensity", v)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t("select_intensity")} />
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
                  <label>
                    {t("duration")} ({t("minutes")})
                  </label>
                  <Input
                    type="number"
                    value={entry.duration}
                    onChange={(e) =>
                      updateEntry(index, "duration", e.target.value)
                    }
                  />
                </div>

                <div className="grid gap-2">
                  <label>
                    {t("heart_rate")} ({t("optional")})
                  </label>
                  <Input
                    type="number"
                    value={entry.bpm || ""}
                    onChange={(e) => updateEntry(index, "bpm", e.target.value)}
                  />
                </div>

                <div className="grid gap-2">
                  <label>{t("start_time")}</label>
                  <Input
                    type="datetime-local"
                    value={entry.start_time}
                    onChange={(e) =>
                      updateEntry(index, "start_time", e.target.value)
                    }
                  />
                </div>

                <div className="grid gap-2">
                  <label>
                    {t("remark")} ({t("optional")})
                  </label>
                  <Textarea
                    value={entry.remark || ""}
                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                      updateEntry(index, "remark", e.target.value)
                    }
                    placeholder={t("feel_after_exercise_body_state_etc")}
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
            {t("add_more_record")}
          </Button> */}

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isSubmitting}
            >
              {t("cancel")}
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? t("adding") : t("save_record")}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

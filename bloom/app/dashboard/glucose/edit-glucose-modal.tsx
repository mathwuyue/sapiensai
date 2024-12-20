"use client";

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
import { useState } from "react";
import { useTranslations } from "next-intl";

interface EditGlucoseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: { value: number; type: number; date: string }) => void;
  initialData: {
    id: string;
    value: number;
    type: number;
    date: string;
  };
  isLoading?: boolean; // 添加这行
}

export function EditGlucoseModal({
  isOpen,
  onClose,
  onSave,
  initialData,
}: EditGlucoseModalProps) {
  const t = useTranslations("glucose");
  const GLUCOSE_TYPES = {
    1: t("before_breakfast"),
    2: t("2h_after_breakfast"),
    3: t("before_lunch"),
    4: t("2h_after_lunch"),
    5: t("before_dinner"),
    6: t("2h_after_dinner"),
    7: t("before_bed"),
    8: t("midnight"),
  };
  const [value, setValue] = useState(initialData.value);
  const [type, setType] = useState(initialData.type);
  const [date, setDate] = useState(initialData.date);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({ value, type, date });
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent
        className="w-[90%] max-w-[400px] md:w-full p-4 md:p-6"
        aria-describedby="dialog-description"
      >
        <DialogHeader>
          <DialogTitle>{t("edit_glucose_reading")}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label>{t("glucose_value")} (mmol/L)</label>
            <Input
              type="number"
              step="0.1"
              value={value}
              onChange={(e) => setValue(Number(e.target.value))}
            />
          </div>
          <div className="space-y-2">
            <label>{t("measurement_type")}</label>
            <Select
              value={type.toString()}
              onValueChange={(val) => setType(Number(val))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(GLUCOSE_TYPES).map(([key, value]) => (
                  <SelectItem key={key} value={key}>
                    {value}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <label>{t("date")}</label>
            <Input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onClose}>
              {t("cancel")}
            </Button>
            <Button type="submit">{t("save")}</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

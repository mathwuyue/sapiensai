"use client";

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useState } from "react";
import { GLUCOSE_TYPES } from "@/app/ui/glucose/glucose-list";

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
  isLoading?: boolean;  // 添加这行

}

export function EditGlucoseModal({ isOpen, onClose, onSave, initialData }: EditGlucoseModalProps) {
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
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Glucose Reading</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label>Glucose value (mmol/L)</label>
            <Input
              type="number"
              step="0.1"
              value={value}
              onChange={(e) => setValue(Number(e.target.value))}
            />
          </div>
          <div className="space-y-2">
            <label>Measurement type</label>
            <Select value={type.toString()} onValueChange={(val) => setType(Number(val))}>
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
            <label>Date</label>
            <Input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">
              Save
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
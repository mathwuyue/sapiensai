"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { PlusCircle, Trash2 } from "lucide-react";
import { createGlucoseReadings, State } from "@/app/lib/actions/glucose";
import { useActionState } from "react";
import { formatLocalDate } from "@/app/lib/utils";

const GLUCOSE_TYPES = [
  { value: 1, label: "Before Breakfast" },
  { value: 2, label: "2h After Breakfast" },
  { value: 3, label: "Before Lunch" },
  { value: 4, label: "2h After Lunch" },
  { value: 5, label: "Before Dinner" },
  { value: 6, label: "2h After Dinner" },
  { value: 7, label: "Before Bed (10:00-11:00pm)" },
  { value: 8, label: "Midnight (2:00am)" },
];

interface GlucoseEntry {
  type: number;
  value: string;
  date: string;
}

export default function GlucoseCreatePage() {
  const initialState: State = { message: "", errors: {} };
  const [state, formAction] = useActionState(
    createGlucoseReadings,
    initialState
  );
  const [entries, setEntries] = useState<GlucoseEntry[]>([
    {
      type: 1,
      value: "",
      date: formatLocalDate(new Date()),
    },
  ]);

  // Add new glucose entry
  const addEntry = () => {
    setEntries([
      ...entries,
      {
        type: 1,
        value: "",
        date: formatLocalDate(new Date()),
      },
    ]);
  };

  // Remove glucose entry at specific index
  const removeEntry = (index: number) => {
    if (entries.length > 1) {
      const newEntries = entries.filter((_, i) => i !== index);
      setEntries(newEntries);
    }
  };

  // Update entry value at specific index
  const updateEntry = (
    index: number,
    field: keyof GlucoseEntry,
    value: number | string
  ) => {
    const newEntries = [...entries];
    newEntries[index] = { ...newEntries[index], [field]: value };
    setEntries(newEntries);
  };

  const wrappedFormAction = async (formData: FormData) => {
    const currentEntries = entries.map((entry) => ({
      ...entry,
      type: entry.type,
      value: entry.value,
      date: entry.date,
    }));

    try {
      await formAction(formData);
    } finally {
      setEntries(currentEntries);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Add New Glucose Reading</h1>

      <form action={wrappedFormAction}>
        {entries.map((entry, index) => (
          <div key={index} className="mb-4 p-4 border rounded-lg bg-white">
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <Input
                  type="date"
                  name="date"
                  value={entry.date}
                  onChange={(e) => updateEntry(index, "date", e.target.value)}
                  required
                />
              </div>
              <div className="flex-1">
                <Select
                  name="type"
                  value={entry.type.toString()}
                  onValueChange={(value) =>
                    updateEntry(index, "type", parseInt(value))
                  }
                  required
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a type" />
                  </SelectTrigger>
                  <SelectContent>
                    {GLUCOSE_TYPES.map((type) => (
                      <SelectItem
                        key={type.value}
                        value={type.value.toString()}
                        className="overflow-hidden"
                      >
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex-1 mt-2">
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    step="0.1"
                    name="value"
                    placeholder="Glucose Value"
                    value={entry.value}
                    required
                    onChange={(e) =>
                      updateEntry(
                        index,
                        "value",
                        e.target.value === "" ? "" : parseFloat(e.target.value)
                      )
                    }
                  />
                  <span className="text-sm text-gray-500">mmol/L</span>
                </div>
              </div>
              {entries.length > 1 && (
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => removeEntry(index)}
                >
                  <Trash2 className="h-5 w-5" />
                </Button>
              )}
            </div>
          </div>
        ))}

        <div className="flex gap-4 mt-6">
          <Button
            type="button"
            variant="outline"
            onClick={addEntry}
            className="flex items-center gap-2"
          >
            <PlusCircle className="h-5 w-5" />
            Add Another Reading
          </Button>

          <Button type="submit" className="ml-auto">
            Save Readings
          </Button>
        </div>
      </form>

      {state.errors && (
        <div className="text-red-500 mt-2">
          {Object.entries(state.errors).map(([key, errors]) => (
            <p key={key}>{errors.join(", ")}</p>
          ))}
        </div>
      )}
    </div>
  );
}

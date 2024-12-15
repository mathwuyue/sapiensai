"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  fetchPresetConditions,
  fetchPresetComplications,
} from "@/app/lib/data";
import {
  ProfileFormData,
  EXERCISE_LEVELS,
  PresetComplication,
  PresetCondition,
  CONDITION_LEVELS,
} from "@/app/lib/definitions";
import { createProfile, getProfile, State } from "@/app/lib/actions/profile";
import { useActionState } from "react";

interface SelectedCondition {
  id: string;
  severity: number;
}

export default function ProfileForm() {
  const [complications, setComplications] = useState<PresetComplication[]>([]);
  const [conditions, setConditions] = useState<PresetCondition[]>([]);
  const [selectedConditions, setSelectedConditions] = useState<
    SelectedCondition[]
  >([]);

  useEffect(() => {
    const loadComplications = async () => {
      const data = await fetchPresetComplications();
      setComplications(data);
    };
    const loadConditions = async () => {
      const data = await fetchPresetConditions();
      setConditions(data);
    };
    const loadProfile = async () => {
      const profile = await getProfile();
      if (profile) {
        setFormData(profile);
        if (profile.conditions) {
          const conditions = profile.conditions.map((condition) => ({
            id: condition.preset_condition_id.toString(),
            severity: condition.level,
          }));
          setSelectedConditions(conditions);
        }
      }
    };
    loadProfile();
    loadComplications();
    loadConditions();
  }, []);
  const initialState: State = { message: null, errors: {} };
  const [state, formAction] = useActionState(createProfile, initialState);
  const [formData, setFormData] = useState<ProfileFormData>({
    age: 0,
    pre_weight: 0,
    cur_weight: 0,
    height: 0,
    glucose: 0,
    hba1c: 0,
    blood_pressure_high: 0,
    blood_pressure_low: 0,
    gestational_age: 0,
    exercise_level: 1,
    conditions: [],
    conditions_severity: [],
    complications: [],
    prescription: undefined,
    dietary_advice: undefined,
  });

  const handleInputChange = (field: keyof ProfileFormData, value: any) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleConditionToggle = (conditionId: string, checked: boolean) => {
    if (checked) {
      setSelectedConditions((prev) => [
        ...prev,
        { id: conditionId, severity: 1 },
      ]);
    } else {
      setSelectedConditions((prev) => prev.filter((c) => c.id !== conditionId));
    }
  };

  const handleSeverityChange = (conditionId: string, severity: number) => {
    setSelectedConditions((prev) =>
      prev.map((c) => (c.id === conditionId ? { ...c, severity } : c))
    );
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Create Your Profile</h1>

      <form action={formAction}>
        {/* Basic Information */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-4">Basic Information</h2>
          <div className="space-y-4">
            <div className="p-4 border rounded-lg bg-white">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Age (years)
              </label>
              <Input
                type="number"
                name="age"
                value={formData.age}
                onChange={(e) => handleInputChange("age", e.target.value)}
                placeholder="Enter your age"
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 border rounded-lg bg-white">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Pre-pregnancy Weight (kg)
                </label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    step="0.1"
                    name="pre_weight"
                    value={formData.pre_weight}
                    onChange={(e) =>
                      handleInputChange("pre_weight", e.target.value)
                    }
                    placeholder="Enter weight"
                    required
                  />
                  <span className="text-sm text-gray-500">kg</span>
                </div>
              </div>

              <div className="p-4 border rounded-lg bg-white">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current Weight (kg)
                </label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    step="0.1"
                    name="cur_weight"
                    value={formData.cur_weight}
                    onChange={(e) =>
                      handleInputChange("cur_weight", e.target.value)
                    }
                    placeholder="Enter weight"
                    required
                  />
                  <span className="text-sm text-gray-500">kg</span>
                </div>
              </div>
            </div>

            <div className="p-4 border rounded-lg bg-white">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Height (cm)
              </label>
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  step="0.1"
                  name="height"
                  value={formData.height}
                  onChange={(e) => handleInputChange("height", e.target.value)}
                  placeholder="Enter height"
                  required
                />
                <span className="text-sm text-gray-500">cm</span>
              </div>
            </div>
          </div>
        </div>

        {/* Medical Information */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-4">Medical Information</h2>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 border rounded-lg bg-white">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fasting Glucose
                </label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    step="0.1"
                    name="glucose"
                    value={formData.glucose}
                    onChange={(e) =>
                      handleInputChange("glucose", e.target.value)
                    }
                    placeholder="Enter glucose"
                    required
                  />
                  <span className="text-sm text-gray-500">mmol/L</span>
                </div>
              </div>

              <div className="p-4 border rounded-lg bg-white">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  HbA1c
                </label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    step="0.1"
                    name="hba1c"
                    value={formData.hba1c}
                    onChange={(e) => handleInputChange("hba1c", e.target.value)}
                    placeholder="Enter hba1c"
                    required
                  />
                  <span className="text-sm text-gray-500">%</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 border rounded-lg bg-white">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Systolic Blood Pressure
                </label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    name="blood_pressure_high"
                    value={formData.blood_pressure_high}
                    onChange={(e) =>
                      handleInputChange("blood_pressure_high", e.target.value)
                    }
                    placeholder="Enter systolic blood pressure"
                    required
                  />
                  <span className="text-sm text-gray-500">mmHg</span>
                </div>
              </div>

              <div className="p-4 border rounded-lg bg-white">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Diastolic Blood Pressure
                </label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    name="blood_pressure_low"
                    value={formData.blood_pressure_low}
                    onChange={(e) =>
                      handleInputChange("blood_pressure_low", e.target.value)
                    }
                    placeholder="Enter diastolic blood pressure"
                    required
                  />
                  <span className="text-sm text-gray-500">mmHg</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Pregnancy Information */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-4">Pregnancy Information</h2>
          <div className="p-4 border rounded-lg bg-white">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Gestational Age (weeks)
            </label>
            <Input
              type="number"
              name="gestational_age"
              value={formData.gestational_age}
              onChange={(e) =>
                handleInputChange("gestational_age", e.target.value)
              }
              placeholder="Enter gestational age"
              required
            />
          </div>
        </div>

        {/* Exercise Level */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-4">Exercise Level</h2>
          <div className="p-4 border rounded-lg bg-white">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Exercise Frequency
            </label>
            <Select
              name="exercise_level"
              value={formData.exercise_level.toString()}
              onValueChange={(value) =>
                handleInputChange("exercise_level", parseInt(value))
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Select exercise level" />
              </SelectTrigger>
              <SelectContent>
                {EXERCISE_LEVELS.map((level) => (
                  <SelectItem key={level.value} value={level.value.toString()}>
                    {level.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Conditions Section */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-4">Basic Conditions</h2>
          <div className="grid gap-4">
            {conditions.map((condition) => {
              const isSelected = selectedConditions.some(
                (c) => c.id === condition.id
              );
              const selectedCondition = selectedConditions.find(
                (c) => c.id === condition.id
              );
              return (
                <div
                  key={condition.id}
                  className="p-4 border rounded-lg bg-white"
                >
                  <div className="flex items-center space-x-2 mb-2">
                    <input
                      type="checkbox"
                      name="conditions"
                      value={condition.id.toString()}
                      id={condition.id.toString()}
                      checked={isSelected}
                      onChange={(e) =>
                        handleConditionToggle(condition.id, e.target.checked)
                      }
                      className="h-4 w-4 rounded border-gray-300"
                    />
                    <label htmlFor={condition.id}>{condition.name}</label>
                  </div>

                  {isSelected && (
                    <div className="ml-6 mt-2">
                      <Select
                        name="conditions_severity"
                        value={selectedCondition?.severity.toString()}
                        onValueChange={(value) =>
                          handleSeverityChange(condition.id, parseInt(value))
                        }
                      >
                        <SelectTrigger className="w-[180px]">
                          <SelectValue placeholder="Please select severity" />
                        </SelectTrigger>
                        <SelectContent>
                          {CONDITION_LEVELS.map((level) => (
                            <SelectItem
                              key={level.value}
                              value={level.value.toString()}
                            >
                              {level.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Complications Section */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-4">Complications</h2>
          <div className="grid gap-4">
            {complications.map((complication) => (
              <div
                key={`complication-${complication.id}`}
                className="flex items-center space-x-2"
              >
                <input
                  type="checkbox"
                  name="complications"
                  value={complication.id.toString()}
                  id={`complication-${complication.id}`}
                  className="h-4 w-4 rounded border-gray-300"
                />
                <label htmlFor={`complication-${complication.id}`}>
                  {complication.name}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Prescription */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-4">Prescription</h2>
          <div className="p-4 border rounded-lg bg-white">
            <Input
              type="text"
              name="prescription"
              placeholder="Enter prescription"
            />
          </div>
        </div>

        {/* Dietary Advice */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold mb-4">Dietary Advice</h2>
          <div className="p-4 border rounded-lg bg-white">
            <Input
              type="text"
              name="dietary_advice"
              placeholder="Enter dietary advice"
            />
          </div>
        </div>

        <div id="status-error" aria-live="polite" aria-atomic="true">
          {state.errors && (
            <p className="mt-2 text-sm text-red-500">{state.message}</p>
          )}
        </div>

        <div className="flex gap-4 mt-6">
          <Button type="submit" className="ml-auto">
            Save Profile
          </Button>
        </div>
      </form>
    </div>
  );
}

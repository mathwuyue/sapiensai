export type Glucose = {
  id: string;
  user_id: string;
  glucose_value: number;
  glucose_date: Date;
  measurement_type: string;
  notes: string;
};

// Profile related types
export interface Profile {
  id: number;
  user_id: number;
  age: number;
  pre_weight: number;
  cur_weight: number;
  height: number;
  glucose?: number;
  hba1c?: number;
  blood_pressure_high?: number;
  blood_pressure_low?: number;
  gestational_age: number;
  exercise_level: number;
  conditions: UserCondition[];
  conditions_severity: typeof CONDITION_LEVELS[];
  complications: UserComplication[];
  prescription: string;
  dietary_advice: string;
  created_at: string;
  updated_at: string;
}

// Preset conditions (basic diseases)
export interface PresetCondition {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// User's conditions with severity level
export interface UserCondition {
  id: number;
  profile_id: number;
  preset_condition_id: number;
  level?: number; // 1-mild, 2-moderate, 3-severe
  preset_condition: PresetCondition;
}

// Preset complications
export interface PresetComplication {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// User's complications
export interface UserComplication {
  id: number;
  profile_id: number;
  preset_complication_id: number;
  preset_complication: PresetComplication;
}

// Form data types
export interface ProfileFormData {
  age?: number;
  pre_weight?: number;
  cur_weight?: number;
  height?: number;
  glucose?: number;
  hba1c?: number;
  blood_pressure_high?: number;
  blood_pressure_low?: number;
  gestational_age?: number;
  exercise_level?: number;
  conditions: {
    preset_condition_id: number;
    level?: number;
  }[];
  conditions_severity: {
    preset_condition_id: number;
    level?: number;
  }[];
  complications: {
    preset_complication_id: number;
  }[];
  prescription?: string;
  dietary_advice?: string;
}

// Condition severity levels
export const CONDITION_LEVELS = [
  { value: 1, label: "Mild" },
  { value: 2, label: "Moderate" },
  { value: 3, label: "Severe" },
] as const;

// Exercise levels
export const EXERCISE_LEVELS = [
  { value: 1, label: "No Exercise" },
  { value: 2, label: "Light Exercise" },
  { value: 3, label: "Regular Exercise" },
  { value: 4, label: "Heavy Exercise" },
] as const;

export type ExerciseType = "walking" | "running" | "cycling" | "swimming" | "jumping rope" | "aerobics" | "other" ;
export type ExerciseIntensity = "gentle" | "low" | "normal" | "high";

export interface Exercise {
  user_id: string;
  exercise: ExerciseType;
  intensity: ExerciseIntensity;
  duration: number;
  bpm?: number;
  start_time: string;
  remark?: string;
}

export const EXERCISE_TYPES = [
  "walking",
  "running",
  "cycling",
  "swimming",
  "jumping rope",
  "aerobics",
  "other"
] as const;

export const INTENSITY_TYPES = [
  'gentle',
  'low',
  'normal',
  'high'
] as const;

// 食物分析相关定义
export interface FoodItem {
  food: string;
  count: number;
}

export interface Nutrients {
  macro: {
    calories: number;
    protein: number;
    fat: number;
    carb: number;
  };
  micro: {
    fa: number;  // 膳食纤维
    vc: number;  // 维生素C
    vd: number;  // 维生素D
  };
  mineral: {
    calcium: number;  // 钙
    iron: number;    // 铁
    zinc: number;    // 锌
    iodine: number;  // 碘
  };
}

export interface FoodAnalysis {
  user_id: number;
  file_path: string;
  original_filename: string;
  foods: FoodItem[];
  nutrients: Nutrients;
  summary: string;
  advice: string;
  created_at: string;
}

export interface ExerciseWithCalories extends Exercise {
  calories: number;
  summary?: string;
  advice?: string;
}
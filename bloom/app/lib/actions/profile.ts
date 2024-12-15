"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";
import { auth } from "@/auth";
const URL = process.env.NEXT_PUBLIC_API_URL;

export type State = {
  errors?: {
    age?: string[];
    pre_weight?: string[];
    cur_weight?: string[];
    height?: string[];
    glucose?: string[];
    hba1c?: string[];
    blood_pressure_high?: string[];
    blood_pressure_low?: string[];
    gestational_age?: string[];
    exercise_level?: string[];
    prescription?: string[];
    dietary_advice?: string[];
  };
  message?: string | null;
};

const ProfileSchema = z.object({
  age: z.number().min(1, { message: "Age is required" }),
  pre_weight: z.number().min(1, { message: "Pre-pregnancy weight is required" }),
  cur_weight: z.number().min(1, { message: "Current weight is required" }),
  height: z.number().min(1, { message: "Height is required" }),
  glucose: z.number().min(1, { message: "Fasting glucose value is required" }),
  hba1c: z.number().min(1, { message: "HbA1c is required" }),
  blood_pressure_high: z.number().min(1, { message: "Blood pressure systolic is required" }),
  blood_pressure_low: z.number().min(1, { message: "Blood pressure diastolic is required" }),
  gestational_age: z.number().min(1, { message: "Gestational age is required" }),
  exercise_level: z.number().min(1, { message: "Exercise level is required" }),
  conditions: z.array(z.object({
    preset_condition_id: z.number(),
    level: z.number()
  })).min(1, { message: "At least one condition is required" }),
  complications: z.array(z.object({
    preset_complication_id: z.number()
  })).min(1, { message: "At least one complication is required" }),
  prescription: z.string().optional(),
  dietary_advice: z.string().optional(),
});

const CreateProfile = ProfileSchema.omit({
  prescription: true,
  dietary_advice: true,
});

export async function createProfile(prevState: State, formData: FormData) {
  const conditionIds = formData.get("conditions")?.toString().split(",").map(Number) || [];
  const severityLevels = formData.get("conditions_severity")?.toString().split(",").map(Number) || [];
  const complicationIds = formData.get("complications")?.toString().split(",").map(Number) || [];
  const conditions = conditionIds.map((id, index) => ({
    preset_condition_id: id,
    level: severityLevels[index]
  }));
  const complications = complicationIds.map((id) => ({
    preset_complication_id: id,
  }));
  const validatedFields = CreateProfile.safeParse({
    age: Number(formData.get("age")),
    pre_weight: Number(formData.get("pre_weight")),
    cur_weight: Number(formData.get("cur_weight")),
    height: Number(formData.get("height")),
    glucose: Number(formData.get("glucose")),
    hba1c: Number(formData.get("hba1c")),
    blood_pressure_high: Number(formData.get("blood_pressure_high")),
    blood_pressure_low: Number(formData.get("blood_pressure_low")),
    gestational_age: Number(formData.get("gestational_age")),
    exercise_level: Number(formData.get("exercise_level")),
    conditions: conditions,
    complications: complications,
    prescription: formData.get("prescription"),
    dietary_advice: formData.get("dietary_advice"),
  });

  if (!validatedFields.success) {
    console.log(validatedFields.error.flatten().fieldErrors);
    return {
      errors: validatedFields.error.flatten().fieldErrors,
      message: "Please correct the errors and try again."
    };
  }
  try {
    const session = await auth();
    const response = await fetch(`${URL}/profile`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${session?.accessToken}`,
      },
      body: JSON.stringify(validatedFields.data),
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Failed to save profile");
    }
  } catch (error) {
    console.error("Error creating profile:", error);
    return {
      message: "Failed to save profile"
    };
  }

  revalidatePath("/dashboard/profile");
  redirect("/dashboard/profile");
}

export async function getProfile() {
  const session = await auth();
  const response = await fetch(`${URL}/profile/me`, {
    headers: {
      "Authorization": `Bearer ${session?.accessToken}`,
    },
    credentials: "include",
  });
  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    throw new Error("Failed to fetch profile");
  }
  const data = await response.json();
  return data;
}

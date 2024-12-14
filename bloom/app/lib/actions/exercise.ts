'use server'

import { auth } from "@/auth";
import { revalidatePath } from "next/cache";
import { z } from "zod";
import { EXERCISE_TYPES, INTENSITY_TYPES } from "../definitions";
const URL = process.env.NEXT_PUBLIC_API_URL;

const BASE_URL = process.env.NEXT_PUBLIC_LLM_API_URL;
const WS_URL = process.env.NEXT_PUBLIC_LLM_WS_URL;
const LLM_API_TOKEN = process.env.LLM_API_TOKEN;

const ExerciseSchema = z.object({
    exercise: z.string(),
    intensity: z.enum(INTENSITY_TYPES),
    duration: z.number(),
    bpm: z.number().optional(),
    start_time: z.string(),
    remark: z.string().optional(),
});

export type State = {
    errors?: {
        exercise?: string[];
        intensity?: string[];
        duration?: string[];
        bpm?: string[];
        start_time?: string[];
        remark?: string[];
    };
    message?: string | null;
};

export async function createExerciseRecord(prevState: State, formData: FormData) {

  const validatedFields = ExerciseSchema.safeParse({
    exercise: formData.get("exercise"),
    intensity: formData.get("intensity"),
    duration: Number(formData.get("duration")),
    bpm: formData.get("bpm") ? Number(formData.get("bpm")) : undefined,
    start_time: formData.get("start_time")?.toString(), // 直接获取表单中的日期
    remark: formData.get("remark") || undefined
  });

  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
      message: "Invalid fields"
    };
  }

  try {
    const session = await auth();
    if (!session?.user) throw new Error("Unauthorized");
    // console.log("Session:", session);
    // console.log("Access Token:", session?.accessToken);
    console.log("API URL:", `${BASE_URL}/v1/emma/exercise`);

    const response = await fetch(`${BASE_URL}/v1/emma/exercise`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        "Authorization": `Bearer ${LLM_API_TOKEN}`,
        //'Authorization': `Bearer ${session.accessToken}`
      },
      body: JSON.stringify(
        {
          ...validatedFields.data,
          user_id: session.user.id 
        }
      )
    });

    if (!response.ok) {
        console.log("response", response);
      return {
        message: "Failed to create glucose readings"
          };
    }

    const data = await response.json();
    return { 
      message: "Success",
      data:data,
      summary: data.summary,
      advice: data.advice
    };  } catch (error) {
        console.log("error", error);
    return {
      message: "Failed to create exercise record again"
    };
  }
}



export async function updateExerciseRecord(
  id: string,
  data: {
    type: string;
    duration: number;
    calories: number;
    date: string;
  }
) {
  try {
    const session = await auth();
    const response = await fetch(`${URL}/exercise/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        "Authorization": `Bearer ${session?.accessToken}`,
      },
      body: JSON.stringify({
        exercise_type: data.type,
        duration: data.duration,
        calories: data.calories,
        exercise_date: data.date
      })
    });

    console.log("Response status:", response.status);
    if (!response.ok) {
      const errorText = await response.text();
      console.error("API Error:", errorText);
    }

    revalidatePath('/dashboard/exercise');
    return response.json();
  } catch (error) {
    console.error('更新失败:', error);
    throw error;
  }
}

export async function deleteExerciseRecord(id: string) {
  try {
    const session = await auth();
    const response = await fetch(`${URL}/exercise/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        "Authorization": `Bearer ${session?.accessToken}`,
      }
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    revalidatePath('/dashboard/exercise');
    return response.json();
  } catch (error) {
    console.error('删除失败:', error);
    throw error;
  }
}

export async function fetchExerciseRecords() {
  try {
    const session = await auth();
    const response = await fetch(`${BASE_URL}/v1/emma/exercise`, {
        method: 'GET',
        headers: {
        'Content-Type': 'application/json',
        "Authorization": `Bearer ${LLM_API_TOKEN}`,
      },
    });

    if (!response.ok) {
      console.error('获取失败:', response);

      throw new Error('获取运动记录失败');
    }

    return response.json();
  } catch (error) {
    console.error('获取失败:', error);
    return [];
  }
}
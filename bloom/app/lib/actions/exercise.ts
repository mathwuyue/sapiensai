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
    
    

    if (!response.ok) {
        console.log("response", response);
      return {
        message: "Failed to create glucose readings"
          };
    }
    
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
  summary: string,
  advice: string
) {
  try {
    const session = await auth();
    const response = await fetch(`${URL}/exercise/${id}/feedback`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        "Authorization": `Bearer ${session?.accessToken}`,
      },
      body: JSON.stringify({
        summary: summary,
        advice: advice
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


export async function deleteExerciseRecord(id: number) {
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
      const errorText = await response.text();
      console.error('Delete failed:', errorText);
      throw new Error(`Failed to delete exercise: ${errorText}`);
    }

    revalidatePath('/dashboard/exercise');
    return response.json();
  } catch (error) {
    console.error('删除失败:', error);
    throw error;
  }
}

// export async function fetchExerciseRecords() {
//   try {
//     const session = await auth();
//     const response = await fetch(`${BASE_URL}/v1/emma/exercise`, {
//         method: 'GET',
//         headers: {
//         'Content-Type': 'application/json',
//         "Authorization": `Bearer ${LLM_API_TOKEN}`,
//       },
//     });

//     if (!response.ok) {
//       console.error('获取失败:', response);

//       throw new Error('获取运动记录失败');
//     }

//     return response.json();
//   } catch (error) {
//     console.error('获取失败:', error);
//     return [];
//   }
// }

export async function fetchExerciseRecords(startDate?: Date, endDate?: Date) {
  let url = `${URL}/exercise`;
  //let url = `${LOCAL_API_URL}/v1/emma/exercise`; // 移除 /api 前缀

  const session = await auth();

  // const params = new URLSearchParams();
  // if (startDate) {
  //   params.append('start_date', startDate.toISOString());
  // }
  // if (endDate) {
  //   params.append('end_date', endDate.toISOString());
  // }
  
  // if (params.toString()) {
  //   url += `?${params.toString()}`;
  // }
  
  // const response = await fetch(url, {
  //   method: 'GET',
  //   headers: {
  //     'Content-Type': 'application/json',
  //     'Authorization': `Bearer ${session?.accessToken}`
  //   }
  // });
  
  // if (!response.ok) {
  //   const errorText = await response.text();
  //     console.error('API Error:', errorText); // 添加错误日志
  //   throw new Error('Failed to fetch exercises');
  // }
  
  try {
    console.log('Fetching URL:', url); // 添加日志
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session?.accessToken}`
      }
    });
    
    console.log('Response status:', response.status); // 添加日志
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('API Error:', errorText); // 添加错误日志
      throw new Error(`Failed to fetch exercises: ${response.status} ${errorText}`);
    }
    
    const data = await response.json();
    console.log('Response data:', data); // 添加日志
    return data.map((record: any) => {
      let emmaData = { summary: null, advice: null };
      if (record.emma) {
        try {
          emmaData = JSON.parse(record.emma);
        } catch (e) {
          console.error('Error parsing emma data:', e);
        }
      }

      return {
        ...record,
        summary: emmaData.summary,
        advice: emmaData.advice
      };
    });  
  } catch (error) {
    console.error('Fetch error:', error); // 添加错误日志
    throw error;
  }
}
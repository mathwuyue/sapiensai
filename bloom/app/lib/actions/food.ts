'use server'

import { revalidatePath } from 'next/cache'
import { auth } from "@/auth";

export async function getFoodAnalyses(params: { skip?: number; limit?: number } = {}) {
  const { skip = 0, limit = 10 } = params;
  
  try {
    const session = await auth();
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/food/analyses?skip=${skip}&limit=${limit}`,
      {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      console.error("API Error:", errorData);
      throw new Error(errorData.detail || "Failed to fetch food analyses");
    }

    const data = await response.json();
    return { data, error: null };
  } catch (error) {
    console.error("Failed to fetch food analyses:", error);
    return {
      data: null,
      error: "Failed to fetch food analyses",
    };
  }
}

export async function getFoodAnalysis(id: number) {
  try {
    const session = await auth();
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/food/analyses/${id}`,
      {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      console.error("API Error:", errorData);
      throw new Error(errorData.detail || "Failed to fetch food analysis");
    }

    const data = await response.json();
    return { data, error: null };
  } catch (error) {
    console.error("Failed to fetch food analysis:", error);
    return {
      data: null,
      error: "获取营养分析详情失败",
    };
  }
}

export async function analyzeFood(formData: FormData) {
  try {
    const session = await auth();
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/food/analyze`,
      {
        method: "POST",
        body: formData,
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      console.error("API Error:", errorData);
      throw new Error(errorData.detail || "Analysis failed");
    }

    const result = await response.json();
    revalidatePath('/dashboard/nutrition');
    return { data: result };
  } catch (error) {
    console.error("Analysis error:", error);
    return { error: error instanceof Error ? error.message : "Analysis failed" };
  }
}

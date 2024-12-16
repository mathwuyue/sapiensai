'use server'

import { revalidatePath } from 'next/cache'
import { auth } from "@/auth";

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

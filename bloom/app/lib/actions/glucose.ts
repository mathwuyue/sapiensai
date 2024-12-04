"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { z } from "zod";
import { auth } from "@/auth";
import { Glucose } from "@/app/lib/definitions"; // 确保路径正确

const GlucoseSchema = z.object({
  measurement_type: z.number().int().min(1).max(8),
  glucose_value: z.coerce.number().gt(0, {
    message: "Please enter a value greater than 0.",
  }),
  glucose_date: z.string().datetime()
});

const CreateGlucose = z.array(GlucoseSchema);

export type State = {
  errors?: {
    type?: string[];
    value?: string[];
    date?: string[];
  };
  message?: string | null;
};

const URL = process.env.NEXT_PUBLIC_API_URL;

export async function createGlucoseReadings(prevState: State, formData: FormData) {
  const dates = formData.getAll("date") as string[];
  const types = formData.getAll("type").map((type) => Number(type));
  const values = formData.getAll("value").map((value) => Number(value));
  const entries = dates.map((date, index) => ({
    glucose_date: new Date(date).toISOString(),
    measurement_type: types[index],
    glucose_value: values[index]
  }))
  const validatedFields = CreateGlucose.safeParse(entries);

  if (!validatedFields.success) {
    console.log(validatedFields.error)
    return {
      errors: {
        type: ["Validation failed"],
        value: ["Validation failed"],
        date: ["Validation failed"],
      },
      message: "Validation failed"
    };
  }
  try {
    const session = await auth();
    const response = await fetch(`${URL}/glucose`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${session?.accessToken}`,
      },
      body: JSON.stringify(validatedFields.data),
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Failed to create glucose readings");
    }
  } catch (error) {
    console.log(error)
    return {
      message: "Failed to create glucose readings"
    };
  }

  revalidatePath("/dashboard")
  redirect("/dashboard")
}

export async function fetchGlucoseReadings(): Promise<Glucose[]> {
  try {
    const session = await auth();
    const response = await fetch(`${URL}/glucose/`, {
      method: 'GET',
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${session?.accessToken}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch glucose readings");
      return [];

    }
    return response.json();

  } catch (error) {
    console.log(error);
    return []; 
  }
}

  //return response.json();
  //delete
  
  //put
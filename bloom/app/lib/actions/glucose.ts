'use server'

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
    const data = await response.json();
    console.log("data--------------------", data);
    return data;

  } catch (error) {
    console.log(error);
    return []; 
  }
}

  //return response.json();
  //delete
  
  //
  export async function deleteGlucoseReading(id: string) {
    try {
      const session = await auth();

      const fullUrl = `${URL}/glucose/${id}`;
      console.log({
        url: fullUrl,
        id: id,

        method: "DELETE",
        token: session?.accessToken?.substring(0, 10) + "..." 
      }); 
  
      const response = await fetch(`${URL}/glucose/${id}`, {
        method: "DELETE",  
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${session?.accessToken}`,
        },
        credentials: "include",
      });
      
  
      if (!response.ok) {
        const text = await response.text();
        console.log("Error response:", text);
        throw new Error(text || "Failed to delete glucose reading"); 
      }
      
      revalidatePath("/dashboard");

    } catch (error) {
      console.error("Error deleting glucose reading:", error);
      throw error;
    }
  }
  // export async function updateGlucoseReading( id: string, 
  //   data: { value: number; type: number; date: string }
  // ) {
  //   try {
  //     const session = await auth();

  //     const fullUrl = `${URL}/glucose/${id}`;
  //     console.log({
  //       url: fullUrl,
  //       id: id,
  //       method: "PUT",
  //       token: session?.accessToken?.substring(0, 10) + "..." // 只打印token的一部分
  //     }); 
  
  //     const response = await fetch(`${URL}/glucose/${id}`, {
  //       method: "PUT",  
  //       headers: {
  //         "Content-Type": "application/json",
  //         "Authorization": `Bearer ${session?.accessToken}`,
  //       },
  //       credentials: "include",
  //       body: JSON.stringify(data),

  //     });
      
  
  //     if (!response.ok) {
  //       const text = await response.text();
  //       console.log("Error response:", text);
  //       throw new Error(text || "Failed to update glucose reading"); 
  //     }
      
  //     revalidatePath("/dashboard/glucose");
  //     redirect("/dashboard/glucose");


  //   } catch (error) {
  //     console.error("Error updating glucose reading:", error);
  //     throw error;
  //   }
    
  // }
  export async function updateGlucoseReading(
    id: string, 
    
    data: { value: number; type: number; date: string }
  ) {
    const session = await auth();
    const response = await fetch(`${URL}/glucose/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        "Authorization": `Bearer ${session?.accessToken}`,

      },
      body: JSON.stringify({
        glucose_value: Number(data.value),      // 修改字段名以匹配后端
        measurement_type: Number(data.type),    // 修改字段名以匹配后端
      glucose_date: data.date
      })
    });
  
    if (!response.ok) {
      throw new Error(await response.text());
    }
  
    revalidatePath('/dashboard/glucose');
    //redirect('/dashboard/glucose');
    return response.json();

  }

  // const [glucoseData, setGlucoseData] = useState<FormattedGlucose[] | null>(null);
  // const [editingGlucose, setEditingGlucose] = useState<FormattedGlucose | null>(null);
  // const [editData, setEditData] = useState<{ value: number; type: number; date: string } | null>(null);
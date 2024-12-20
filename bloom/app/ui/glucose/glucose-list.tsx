"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { fetchGlucoseReadings, deleteGlucoseReading, updateGlucoseReading } from "@/app/lib/actions/glucose";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Edit, Trash } from "lucide-react";
import { EditGlucoseModal } from "@/app/dashboard/glucose/edit-glucose-modal";
interface FormattedGlucose {
  id: string;
  value: number;
  date: string;
  type: number;
}

export const GLUCOSE_TYPES: { [key: number]: string } = {
    1: "Before Breakfast",
    2: "2h After Breakfast",
    3: "Before Lunch",
    4: "2h After Lunch",
    5: "Before Dinner",
    6: "2h After Dinner",
    7: "Before Bed",
    8: "Midnight"
  };


export default function GlucoseList() {
  const [glucoseData, setGlucoseData] = useState<FormattedGlucose[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [editingGlucose, setEditingGlucose] = useState<FormattedGlucose | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);
  // const [page, setPage] = useState(1);

  // const itemsPerPage = 3;

  useEffect(() => {
    // if (dataFetchedRef.current) return;
    // dataFetchedRef.current = true;
    
    async function loadGlucoseData() {
      try {
        const data = await fetchGlucoseReadings();
        if (!data) {
          setGlucoseData([]);
          return;
        }

        const formattedData = data.map((reading) => ({
          id: reading.id,
          value: Number(reading.glucose_value),
          date: new Date(reading.glucose_date).toISOString().split('T')[0], 
          type: Number(reading.measurement_type)
        }));

        // 按日期和类型排序
        const sortedData = formattedData.sort((a, b) => {
            // 首先按日期排序
            const dateCompare = new Date(b.date).getTime() - new Date(a.date).getTime();
            if (dateCompare === 0) {
              return Number(a.type) - Number(b.type);
            }
            return dateCompare;
          });
  
        setGlucoseData(sortedData);

      } catch (error) {
        console.error('Error loading data:', error);
        setGlucoseData([]);
      } finally {
        setIsLoading(false);
      }
    }

    

    loadGlucoseData();


    
  }, []);
  




const deleteGlucoseData = (id: string) => {
    setDeleteId(id);
  };

  useEffect(() => {
    async function handleDelete() {
      if (!deleteId) return;
      try {
        await deleteGlucoseReading(deleteId);
        setGlucoseData((prevData) => 
          prevData ? prevData.filter(reading => reading.id !== deleteId) : null
        );
      } catch (error) {
        console.error('Fail to delete:', error);
      }
      setDeleteId(null);
    }

    handleDelete();
  }, [deleteId]);
//   useEffect(() => {
//     async function updateGlucose() {
//       if (!editingGlucose || !editData) return;
      
//       try {
//         await updateGlucoseReading(editingGlucose.id, editData);
//         setGlucoseData((prevData) => 
//           prevData?.map(reading => 
//             reading.id === editingGlucose.id 
//               ? { ...reading, ...editData }
//               : reading
//           ) ?? null
//         );
//         setEditingGlucose(null);
//       } catch (error) {
//         console.error('更新失败:', error);
//       }
//     }

//     updateGlucose();
//   }, [editData, editingGlucose]);
const handleEdit = async (data: { value: number; type: number; date: string }) => {
    if (!editingGlucose || isUpdating) return;
    
    try {
      setIsUpdating(true);
      await updateGlucoseReading(editingGlucose.id, data);
      
      // 本地状态更新
      setGlucoseData((prevData) => 
        prevData?.map(reading => 
          reading.id === editingGlucose.id 
            ? { ...reading, ...data }
            : reading
        ) ?? null
      );
      
      setEditingGlucose(null);
    } catch (error) {
      console.error('Update failed:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  // const paginatedData = glucoseData?.slice(
  //   (page - 1) * itemsPerPage,
  //   page * itemsPerPage
  // );

  if (isLoading || glucoseData === null) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Glucose History</CardTitle>
        </CardHeader>
        <CardContent>
          <div>Loading...</div>
        </CardContent>
      </Card>
    );
  }

  
  
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Glucose History</CardTitle>
        <CardDescription>Your blood glucose readings history</CardDescription>
      </CardHeader>
      <CardContent className="p-1">
        <Table className="w-full">
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Value (mmol/L)</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {glucoseData.map((reading) => (
              <TableRow key={reading.id}>
                <TableCell>
                  {new Date(reading.date).toLocaleDateString()}
                </TableCell>
                
                <TableCell>
                  {GLUCOSE_TYPES[reading.type]}
                </TableCell>
                <TableCell>{reading.value}</TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => {setEditingGlucose(reading);}}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <br />
                    <Button 
                      variant="destructive" 
                      size="sm"
                      onClick={() => {deleteGlucoseData(reading.id)}}
                    >
                      <Trash className="h-4 w-4" />
                    </Button>
                    {/* <GlucoseButtons id={reading.id} /> */}
                    {/* <span>{reading.id}</span> */}
                    {/* <form action={deleteGlucoseReading.bind(null, reading.id)}>
                      <button className="p-2 hover:bg-destructive/10 text-destructive rounded-md">
                        <Trash className="h-4 w-4" />
                      </button>
      </form> */}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
      {editingGlucose && (
                      <EditGlucoseModal
                      isOpen={!!editingGlucose}
                      onClose={() => !isUpdating && setEditingGlucose(null)}
                      onSave={handleEdit}
                      initialData={editingGlucose}
                      isLoading={isUpdating}
        />
                    )}
      <CardFooter>
      <Link className="w-full" href="/dashboard/glucose/create">
          <Button className="w-full">Add Glucose Reading</Button>
        </Link>
        <div className="flex items-center justify-between border-t pt-4">
        


    </div>
    

    {/* <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => p + 1)}
            disabled={page * itemsPerPage >= paginatedData?.length}
          >
            Next
          </Button>
          </div> */}
      </CardFooter>
    </Card>
  );
}
"use client";

import { useState } from "react";
 import { ExerciseList } from "@/app/ui/exercise/exercise-list";
//import { ExerciseStats } from "@/app/ui/exercise/exercise-stats";
import { Button } from "@/components/ui/button";
import { PlusCircle } from "lucide-react";
import { CreateExerciseModal } from "@/app/dashboard/exercise/create-exercise-modal";

export default function ExercisePage() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Exercise Record</h1>
        <Button onClick={() => setIsModalOpen(true)}>
          <PlusCircle className="mr-2 h-4 w-4" />
          Add Exercise
        </Button>
      </div>
      {/* <ExerciseStats /> */}
      <div className="mt-8">
        {/* <ExerciseList /> */}
      </div>

      <CreateExerciseModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
      <ExerciseList />
    </div>
  );
}
// 'use client';

// import { Pencil, Trash } from "lucide-react";
// import { deleteGlucoseReading } from "@/app/lib/actions/glucose";

// interface GlucoseButtonsProps {
//   id: number;
// }

// export function GlucoseButtons({ id }: GlucoseButtonsProps) {
//   return (
//     <div className="flex items-center gap-2">
//       <form action={`/dashboard/glucose/${id}/edit`} method="GET">
//         <button className="p-2 hover:bg-muted rounded-md">
//           <Pencil className="h-4 w-4" />
//         </button>
//       </form>

//       <form action={deleteGlucoseReading.bind(null, id)}>
//         <button className="p-2 hover:bg-destructive/10 text-destructive rounded-md">
//           <Trash className="h-4 w-4" />
//         </button>
//       </form>
//     </div>
//   );
// }
'use client';

import { Trash } from "lucide-react";
import { deleteGlucoseReading } from "@/app/lib/actions/glucose";
import { useTransition } from "react";

interface GlucoseButtonsProps {
  id: string;
}

export function GlucoseButtons({ id }: GlucoseButtonsProps) {
  const [isPending, startTransition] = useTransition();

  const handleDelete = () => {
    startTransition(async () => {
      try {
        console.log("Starting delete for ID:", id);
        await deleteGlucoseReading(id);
        console.log("Delete successful");
      } catch (error) {
        console.error("Delete failed:", error);
      }
    });
  };

  return (
    <div className="flex items-center gap-2">
      {/* <form action={`/dashboard/glucose/${id}/edit`} method="GET">
        <button className="p-2 hover:bg-muted rounded-md">
          <Pencil className="h-4 w-4" />
        </button>
      </form> */}

      <button 
        onClick={handleDelete}
        disabled={isPending}
        className="p-2 hover:bg-destructive/10 text-destructive rounded-md"
      >
        <Trash className="h-4 w-4" />
      </button>
    </div>
  );
}
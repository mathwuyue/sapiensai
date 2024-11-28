import IntakeCard from "@/app/ui/nutrition/intake_card";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Nutrition() {
  return (
    <div className="flex flex-col gap-4 h-full">
      <div className="p-5">
        <IntakeCard />
      </div>
      <div className="p-5 mt-auto">
        <Link href="/dashboard/nutrition/upload">
          <Button className="w-full">Upload My Nutrition Record</Button>
        </Link>
      </div>
    </div>
  );
}

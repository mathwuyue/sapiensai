import { auth } from "@/auth";
import { redirect } from "next/navigation";
import GlucoseCard from "@/app/ui/glucose/glucose-card";

export default async function DashboardPage() {
  const session = await auth();
  if (!session?.user) {
    redirect("/login");
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <GlucoseCard />
    </div>
  );
}

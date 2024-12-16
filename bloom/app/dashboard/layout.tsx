import { TabBar } from "@/app/ui/tabbar";
import { Toaster } from "@/components/ui/toaster";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen pb-[calc(3.5rem+env(safe-area-inset-bottom))]">
      {children}
      <TabBar />
      <Toaster />

    </div>
  );
}

import { TabBar } from "@/app/ui/tabbar";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen pb-[calc(3.5rem+env(safe-area-inset-bottom))]">
      {children}
      <TabBar />
    </div>
  );
}

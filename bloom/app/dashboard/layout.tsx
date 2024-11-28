import { TabBar } from "@/app/ui/tabbar";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen pb-14">
      {children}
      <TabBar />
    </div>
  );
}

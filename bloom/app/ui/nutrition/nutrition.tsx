import IntakeList from "@/app/ui/nutrition/intake_list";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useTranslations } from "next-intl";

export default function Nutrition() {
  const t = useTranslations("nutrition");
  return (
    <div className="flex flex-col h-full relative pb-16">
      {/* 主要内容区域 */}
      <div className="flex-1 overflow-hidden">
        <IntakeList />
      </div>

      {/* 固定在底部的按钮 */}
      <div className="fixed bottom-[80px] left-0 right-0 px-5 pb-4 bg-gradient-to-t from-background to-transparent pt-4">
        <Link href="/dashboard/nutrition/upload">
          <Button className="w-full shadow-lg">
            {t("upload_my_nutrition_record")}
          </Button>
        </Link>
      </div>
    </div>
  );
}

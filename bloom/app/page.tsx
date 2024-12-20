import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useTranslations } from "next-intl";

export default function Home() {
  const t = useTranslations("common");

  return (
    <div className="h-screen flex flex-col px-6">
      {/* Logo Section */}
      <div className="flex flex-1 items-center justify-center">
        <Image
          src="/logo.png"
          alt="Bloom Logo"
          width={212}
          height={183}
          priority
        />
      </div>

      {/* Bottom Section */}
      <div className="space-y-4 mb-[calc(env(safe-area-inset-bottom)+2.5rem)] pb-safe-bottom">
        <Link href="/login" className="block">
          <Button className="w-full text-white font-semibold text-lg h-12">
            {t("login")}
          </Button>
        </Link>

        <div className="flex items-center justify-center gap-2 text-gray-600">
          <span>{t("dont_have_an_account")}</span>
          <Link
            href="/signup"
            className="text-[#9EDA82] hover:underline font-bold"
          >
            {t("signup")}
          </Link>
        </div>
      </div>
    </div>
  );
}

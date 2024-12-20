"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useActionState } from "react";
import { authenticate } from "@/app/lib/actions";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { useTranslations } from "next-intl";

export default function LoginForm() {
  const t = useTranslations("common");
  const { toast } = useToast();
  const [errorMessage, formAction, isPending] = useActionState(
    authenticate,
    undefined
  );

  useEffect(() => {
    if (errorMessage) {
      toast({
        title: "Error",
        description: errorMessage,
      });
    }
  }, [errorMessage, toast]);

  return (
    <div className="w-full max-w-md p-6 space-y-6">
      <div className="flex items-center gap-2">
        <Link href="/">
          <ArrowLeft className="h-6 w-6" />
        </Link>
        <h1 className="text-2xl">{t("login")}</h1>
      </div>

      <form action={formAction} className="space-y-4">
        <div className="w-full">
          <Label htmlFor="email">{t("email")}</Label>
          <div className="relative">
            <Input
              type="email"
              name="email"
              id="email"
              placeholder={t("email")}
              required
            />
          </div>
        </div>
        <div className="relative">
          <Label htmlFor="password">{t("password")}</Label>
          <div className="relative">
            <Input
              type="password"
              name="password"
              id="password"
              placeholder={t("password")}
              required
              minLength={6}
            />
          </div>
        </div>
        <Button className="w-full text-white" disabled={isPending}>
          {isPending ? t("logging_in") : t("login")}
        </Button>
      </form>
    </div>
  );
}

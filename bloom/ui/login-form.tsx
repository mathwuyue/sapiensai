"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useActionState } from "react";
import { authenticate } from "@/lib/actions";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";

export default function LoginForm() {
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
        <h1 className="text-2xl">Log In</h1>
      </div>

      <form action={formAction} className="space-y-4">
        <div className="w-full">
          <Label htmlFor="email">Email</Label>
          <div className="relative">
            <Input
              type="email"
              name="email"
              id="email"
              placeholder="Email"
              required
            />
          </div>
        </div>
        <div className="relative">
          <Label htmlFor="password">Password</Label>
          <div className="relative">
            <Input
              type="password"
              name="password"
              id="password"
              placeholder="Password"
              required
              minLength={6}
            />
          </div>
        </div>
        <Button className="w-full text-white" disabled={isPending}>
          {isPending ? "Logging in..." : "Log in"}
        </Button>
      </form>
    </div>
  );
}

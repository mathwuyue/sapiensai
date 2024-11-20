import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col px-6">
      {/* Logo Section */}
      <div className="flex-1 flex items-center justify-center">
        <Image
          src="/logo.png"
          alt="Bloom Logo"
          width={212}
          height={183}
          priority
        />
      </div>

      {/* Bottom Section */}
      <div className="space-y-4 mb-10">
        <Link href="/login" className="block">
          <Button className="w-full text-white font-semibold text-lg h-12">
            Log in
          </Button>
        </Link>

        <div className="flex items-center justify-center gap-2 text-gray-600">
          <span>Don&apos;t have an account?</span>
          <Link
            href="/signup"
            className="text-[#9EDA82] hover:underline font-bold"
          >
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
}

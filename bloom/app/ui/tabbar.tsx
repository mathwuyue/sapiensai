"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import Image from "next/image";
import { useState } from "react";
import { AIChatModal } from "@/app/ui/chat/ai-chat-modal";

interface TabItem {
  label: string;
  href: string;
  icon: string;
  icon_selected: string;
}

const tabs: TabItem[] = [
  {
    label: "home",
    href: "/dashboard",
    icon: "/tabbar/tabbar_home.png",
    icon_selected: "/tabbar/tabbar_home_selected.png",
  },
  {
    label: "nutrition",
    href: "/dashboard/nutrition",
    icon: "/tabbar/tabbar_nutrition.png",
    icon_selected: "/tabbar/tabbar_nutrition_selected.png",
  },
  {
    label: "exercise",
    href: "/dashboard/exercise",
    icon: "/tabbar/tabbar_exercise.png",
    icon_selected: "/tabbar/tabbar_exercise_selected.png",
  },
  {
    label: "profile",
    href: "/dashboard/profile",
    icon: "/tabbar/tabbar_profile.png",
    icon_selected: "/tabbar/tabbar_profile_selected.png",
  },
];

export function TabBar() {
  const pathname = usePathname();
  const [isAIChatOpen, setIsAIChatOpen] = useState(false);

  const leftTabs = tabs.slice(0, 2);
  const rightTabs = tabs.slice(2);

  const handleAIChat = () => {
    setIsAIChatOpen(true);
  };

  return (
    <>
      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t">
        <div className="relative flex justify-between items-center h-14 px-4">
          {/* Left tabs */}
          <div className="flex flex-1 justify-around">
            {leftTabs.map((tab) => (
              <Link
                key={tab.href}
                href={tab.href}
                className={clsx(
                  "flex flex-col items-center justify-center",
                  pathname === tab.href ? "text-primary" : "text-gray-500"
                )}
              >
                <Image
                  src={pathname === tab.href ? tab.icon_selected : tab.icon}
                  alt={tab.label}
                  width={24}
                  height={24}
                />
                <span className="text-sm">{tab.label}</span>
              </Link>
            ))}
          </div>

          {/* Center AI Button */}
          <button
            onClick={handleAIChat}
            className="absolute left-1/2 -translate-x-1/2 -translate-y-6 w-14 h-14 rounded-full bg-primary flex items-center justify-center shadow-lg hover:bg-primary/90 transition-colors"
          >
            <Image
              src="/tabbar/ai_chat.png"
              alt="AI Chat"
              width={28}
              height={28}
            />
          </button>

          {/* Right tabs */}
          <div className="flex flex-1 justify-around">
            {rightTabs.map((tab) => (
              <Link
                key={tab.href}
                href={tab.href}
                className={clsx(
                  "flex flex-col items-center justify-center",
                  pathname === tab.href ? "text-primary" : "text-gray-500"
                )}
              >
                <Image
                  src={pathname === tab.href ? tab.icon_selected : tab.icon}
                  alt={tab.label}
                  width={24}
                  height={24}
                />
                <span className="text-sm">{tab.label}</span>
              </Link>
            ))}
          </div>
        </div>
        <div className="h-safe-bottom bg-white" />
      </nav>
      <AIChatModal
        isOpen={isAIChatOpen}
        onClose={() => setIsAIChatOpen(false)}
      />
    </>
  );
}

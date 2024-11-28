"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import Image from "next/image";

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

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t">
      <div className="flex justify-around items-center h-14">
        {tabs.map((tab) => (
          <Link
            key={tab.href}
            href={tab.href}
            className={clsx(
              "flex flex-col items-center justify-center flex-1 h-full",
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
    </nav>
  );
}

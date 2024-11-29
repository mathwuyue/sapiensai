"use client";

import { Area, AreaChart, CartesianGrid, XAxis } from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { Glucose } from "@/app/lib/definitions";
import { Button } from "@/components/ui/button";
import Link from "next/link";

const data: Glucose[] = [
  {
    id: 1,
    user_id: 1,
    glucose_value: 95,
    glucose_date: new Date("2024-01-01T08:00:00"),
    measurement_type: "fasting",
    notes: "Morning reading",
  },
  {
    id: 2,
    user_id: 1,
    glucose_value: 145,
    glucose_date: new Date("2024-01-01T13:00:00"),
    measurement_type: "after_meal",
    notes: "After lunch",
  },
  {
    id: 3,
    user_id: 1,
    glucose_value: 110,
    glucose_date: new Date("2024-01-02T08:00:00"),
    measurement_type: "fasting",
    notes: "Morning reading",
  },
  {
    id: 4,
    user_id: 1,
    glucose_value: 160,
    glucose_date: new Date("2024-01-02T19:00:00"),
    measurement_type: "after_meal",
    notes: "After dinner",
  },
];

const chartConfig = {
  glucose: {
    label: "Glucose",
    color: "hsl(var(--chart-1))",
  },
} satisfies ChartConfig;

export default function GlucoseCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Glucose</CardTitle>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <AreaChart
            accessibilityLayer
            data={data}
            margin={{
              left: 12,
              right: 12,
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="glucose_date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tickFormatter={(value) => value.toLocaleDateString()}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="line" />}
            />
            <Area
              dataKey="glucose_value"
              type="natural"
              fill="var(--color-glucose)"
              fillOpacity={0.4}
              stroke="var(--color-glucose)"
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
      <CardFooter>
        <Link className="w-full" href="/dashboard/glucose/create">
          <Button className="w-full">Add Glucose Reading</Button>
        </Link>
      </CardFooter>
    </Card>
  );
}

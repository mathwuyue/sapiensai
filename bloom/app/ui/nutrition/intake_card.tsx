"use client";

import * as React from "react";
import { Label, Pie, PieChart } from "recharts";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
const chartData = [
  { nutrient: "protein", calories: 1275, fill: "hsl(var(--chart-3))" },
  { nutrient: "carbs", calories: 200, fill: "hsl(var(--chart-1))" },
  { nutrient: "fat", calories: 287, fill: "hsl(var(--chart-2))" },
];

const chartConfig = {
  calories: {
    label: "Calories",
  },
  carbs: {
    label: "Carbs",
    color: "hsl(var(--chart-1))",
  },
  fat: {
    label: "Fat",
    color: "hsl(var(--chart-2))",
  },
  protein: {
    label: "Protein",
    color: "hsl(var(--chart-3))",
  },
} satisfies ChartConfig;

export default function IntakeCard() {
  const totalCalories = React.useMemo(() => {
    return chartData.reduce((acc, curr) => acc + curr.calories, 0);
  }, []);

  const getPercentage = (calories: number) => {
    return Math.round((calories / totalCalories) * 100);
  };

  return (
    <Card className="flex flex-col items-center bg-[#9EDA82] text-white">
      <CardHeader className="items-center pb-0">
        <CardTitle className="text-2xl font-bold">Intake</CardTitle>
        <CardDescription className="text-white">
          {new Date().toLocaleDateString("en-US", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-row items-center gap-4 p-4">
        <ChartContainer
          config={chartConfig}
          className="mx-auto aspect-square min-w-[150px] max-h-[250px]"
        >
          <PieChart>
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
            />
            <Pie
              data={chartData}
              dataKey="calories"
              nameKey="nutrient"
              innerRadius={45}
              outerRadius={70}
              strokeWidth={5}
            >
              <Label
                content={({ viewBox }) => {
                  if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                    return (
                      <text
                        x={viewBox.cx}
                        y={viewBox.cy}
                        textAnchor="middle"
                        dominantBaseline="middle"
                      >
                        <tspan
                          x={viewBox.cx}
                          y={viewBox.cy}
                          className="text-3xl font-bold text-white"
                        >
                          {totalCalories.toLocaleString()}
                        </tspan>
                        <tspan
                          x={viewBox.cx}
                          y={(viewBox.cy || 0) + 24}
                          className="text-white"
                        >
                          Calories
                        </tspan>
                      </text>
                    );
                  }
                }}
              />
            </Pie>
          </PieChart>
        </ChartContainer>
        <div className="flex-1 flex-col gap-6 pl-6">
          {chartData.map((item) => (
            <div key={item.nutrient} className="flex items-center gap-4 pb-3">
              <div
                className="h-12 w-1.5 rounded-full bg-opacity-100"
                style={{
                  backgroundColor: item.fill,
                }}
              />
              <div className="flex items-center gap-2 text-[#4E5969]">
                <div className="text-2xl font-medium capitalize">
                  {item.nutrient}
                </div>
                <div className="text-2xl">{getPercentage(item.calories)}%</div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

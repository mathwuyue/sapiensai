"use client";

import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts";
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
import { fetchGlucoseReadings,deleteGlucoseReading } from "@/app/lib/actions/glucose";
import { useEffect, useState, } from "react";
import { ArrowRight } from "lucide-react";
import React from "react";  

interface FormattedGlucose {
  value: number;
  date: string;
  type: number;

}

const data: Glucose[] = [
  {
    id: "1",
    user_id: "1",
    glucose_value: 95,
    glucose_date: new Date("2024-01-01T08:00:00"),
    measurement_type: "fasting",
    notes: "Morning reading",
  },
  {
    id: "2",
    user_id: "1",
    glucose_value: 145,
    glucose_date: new Date("2024-01-01T13:00:00"),
    measurement_type: "after_meal",
    notes: "After lunch",
  },
  {
    id: "3",
    user_id: "1",
    glucose_value: 110,
    glucose_date: new Date("2024-01-02T08:00:00"),
    measurement_type: "fasting",
    notes: "Morning reading",
  },
  {
    id: "4",
    user_id: "1",
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
  const [glucoseData, setGlucoseData] = useState<FormattedGlucose[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
  
    
    async function loadGlucoseData() {
      try {
        const data = await fetchGlucoseReadings();
        //console.log('Raw API data:', data); // 查看原始数据

        
        // 格式化数据用于图表显示
        const formattedData = data.map((reading: Glucose) => ({
          value: Number(reading.glucose_value),
          date: new Date(reading.glucose_date).toISOString().split('T')[0], 
          //type: reading.measurement_type === 'fasting' ? 1 : 2  // 或者使用其他数字映射逻辑
          type: Number(reading.measurement_type),
        }));      
        //console.log('Formatted data:', formattedData); // 调试日志


        const sortedData = formattedData.sort((a, b) => {
          // 首先按日期排序
          const dateCompare = new Date(a.date).getTime() - new Date(b.date).getTime();
          if (dateCompare === 0) {
            return a.type - b.type;
          }
          return dateCompare;
        });

        setGlucoseData(sortedData);

        //console.log('Final formatted data:', formattedData); // 查看最终数据

      } finally {
        setIsLoading(false);
      }
    }
    loadGlucoseData();
  }, []);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
      <CardTitle>Glucose</CardTitle>
      <div className="flex items-center gap-2">
          <div className="flex flex-col items-end">
            <span className="text-sm text-muted-foreground">All your glucose records</span>
            <div className="h-[1px] w-16 bg-border" /> {/* 添加横线 */}
          </div>
          <Link href="/dashboard/glucose">
            <Button variant="ghost" size="icon" className="hover:bg-primary/10 transition-all duration-200">
              <ArrowRight className="h-6 w-6 text-primary hover:translate-x-1" />
            </Button>
          </Link>
        </div>
      </CardHeader>
      
      <CardContent>
        <ChartContainer config={chartConfig}>
          <AreaChart
            accessibilityLayer
            data={glucoseData}
            margin={{
              left: 12,
              right: 12,
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              //tickFormatter={(value) => value.toLocaleDateString()}
            />
            <YAxis
              domain={[0, 'auto']}  // 设置最小值为 0，最大值自动计算
              tickLine={false}
              axisLine={false}
              tickMargin={8}
  />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="line" />}
            />
            <Area
              dataKey="value"
              type="monotone"
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
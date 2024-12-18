"use client";

import { useEffect, useState, useCallback } from "react";
import { FoodAnalysis } from "@/app/lib/definitions";
import { getFoodAnalyses } from "@/app/lib/actions/food";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { useInView } from "react-intersection-observer";

export default function IntakeList() {
  const [analyses, setAnalyses] = useState<FoodAnalysis[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(0);
  const limit = 10;

  const { ref, inView } = useInView({
    threshold: 0,
    rootMargin: "100px",
  });

  // 移除 loading 从依赖数组中
  const loadAnalyses = useCallback(async () => {
    if (loading) return; // 防止重复加载

    try {
      setLoading(true);
      const { data, error } = await getFoodAnalyses({
        skip: page * limit,
        limit,
      });

      if (error) {
        throw new Error(error);
      }

      if (data) {
        if (data.length < limit) {
          setHasMore(false);
        }
        setAnalyses((prev) => {
          // 防止重复数据
          const newData = data.filter(
            (item) => !prev.some((p) => p.created_at === item.created_at)
          );
          return [...prev, ...newData];
        });
        setPage((prev) => prev + 1);
      }
    } catch (error) {
      console.error("Failed to load food analyses:", error);
    } finally {
      setLoading(false);
    }
  }, [page, limit]); // 移除 loading 从依赖数组

  // 监听滚动加载更多
  useEffect(() => {
    if (inView && !loading && hasMore) {
      loadAnalyses();
    }
  }, [inView, loading, hasMore, loadAnalyses]);

  // 初始加载
  useEffect(() => {
    setPage(0); // 重置页码
    setAnalyses([]); // 清空数据
    setHasMore(true); // 重置加载状态
    loadAnalyses();
  }, []); // 移除 loadAnalyses 从依赖数组，只在组件挂载时执行一次

  return (
    <ScrollArea className="h-[calc(100vh-180px)] px-4">
      <div className="py-6">
        <h1 className="text-2xl font-bold mb-6">Intake List</h1>

        <div className="space-y-4">
          {analyses.map((analysis, index) => (
            <Card
              key={index}
              className="overflow-hidden hover:shadow-lg transition-shadow"
            >
              <CardHeader className="bg-primary/5 pb-3">
                <div className="flex justify-between items-center">
                  <h3 className="font-semibold text-lg">
                    {new Date(analysis.created_at).toLocaleDateString()}
                  </h3>
                  <span className="text-sm text-muted-foreground">
                    {analysis.nutrients.macro.calories.toFixed(0)} calories
                  </span>
                </div>
              </CardHeader>
              <CardContent className="pt-4">
                {/* 食物列表 */}
                <div className="mb-4">
                  <h4 className="font-medium mb-2">Food List</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {analysis.foods.map((food, idx) => (
                      <div key={idx} className="flex justify-between text-sm">
                        <span>{food.food}</span>
                        <span className="text-muted-foreground">
                          {food.count} portions
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 营养摘要 */}
                <div className="space-y-2">
                  <div className="grid grid-cols-4 gap-2 text-center">
                    <NutrientItem
                      label="Protein"
                      value={analysis.nutrients.macro.protein}
                      unit="g"
                    />
                    <NutrientItem
                      label="Fat"
                      value={analysis.nutrients.macro.fat}
                      unit="g"
                    />
                    <NutrientItem
                      label="Carbohydrate"
                      value={analysis.nutrients.macro.carb}
                      unit="g"
                    />
                    <NutrientItem
                      label="Fiber"
                      value={analysis.nutrients.micro.fa}
                      unit="g"
                    />
                  </div>
                </div>

                {/* 建议 */}
                <div className="mt-4 text-sm text-muted-foreground">
                  {analysis.advice}
                </div>
              </CardContent>
            </Card>
          ))}

          {/* 加载状态 */}
          {loading && (
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <Card key={i} className="overflow-hidden">
                  <CardHeader className="pb-3">
                    <Skeleton className="h-6 w-1/3" />
                  </CardHeader>
                  <CardContent className="pt-4">
                    <Skeleton className="h-24 w-full" />
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* 无限滚动触发器 */}
          <div ref={ref} className="h-4" />
        </div>
      </div>
    </ScrollArea>
  );
}

// NutrientItem 组件保持不变
function NutrientItem({
  label,
  value,
  unit,
}: {
  label: string;
  value: number;
  unit: string;
}) {
  return (
    <div className="bg-secondary/20 rounded p-2">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="font-medium">
        {value.toFixed(1)}
        <span className="text-xs ml-1">{unit}</span>
      </div>
    </div>
  );
}

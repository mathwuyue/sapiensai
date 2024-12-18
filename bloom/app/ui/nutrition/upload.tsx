"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import Image from "next/image";
import { ArrowLeft, Upload as UploadIcon, X, Loader2 } from "lucide-react";
import Link from "next/link";
import { analyzeFood } from "@/app/lib/actions/food";
import { toast } from "@/hooks/use-toast";

interface FoodItem {
  food: string;
  count: number;
}

interface Nutrients {
  macro: {
    calories: number;
    protein: number;
    fat: number;
    carb: number;
  };
  micro: {
    fa: number;
    vc: number;
    vd: number;
  };
  mineral: {
    calcium: number;
    iron: number;
    zinc: number;
    iodine: number;
  };
}

interface AnalysisResult {
  foods: FoodItem[];
  nutrients: Nutrients;
  summary: string;
  advice: string;
}

export default function Upload() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null
  );
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result as string);
        setAnalysisResult(null); // 清除之前的分析结果
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleAnalyze = async () => {
    if (!selectedImage) return;

    setIsAnalyzing(true);
    try {
      // 将 base64 字符串转换为 Blob
      const blob = await fetch(selectedImage).then((res) => res.blob());
      const formData = new FormData();
      formData.append("file", blob, "food.jpg");

      // 调用 server action
      const result = await analyzeFood(formData);

      if (result.error) {
        toast({
          title: "Error",
          description: result.error,
          variant: "destructive",
        });
        return;
      }

      if (result.data) {
        setAnalysisResult(result.data);
        toast({
          title: "Success",
          description: "Analysis completed successfully",
        });
      }
    } catch (error) {
      console.error("Analysis error:", error);
      toast({
        title: "Error",
        description: "Failed to analyze image",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex flex-col h-full p-4 gap-4">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard/nutrition">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-6 w-6" />
          </Button>
        </Link>
        <h1 className="text-2xl font-semibold">Upload a Photo</h1>
      </div>

      {/* Upload Area */}
      <Card
        className="flex-grow flex flex-col items-center justify-center p-6 bg-[#9EDA82]/20 border-dashed border-2 border-[#9EDA82] rounded-2xl cursor-pointer relative"
        onClick={handleUploadClick}
      >
        {selectedImage ? (
          <div className="w-full h-full flex flex-col">
            <div className="flex justify-end mb-2">
              <Button
                variant="ghost"
                size="icon"
                className="rounded-full bg-white/80 hover:bg-white"
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedImage(null);
                  setAnalysisResult(null);
                }}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex-grow relative min-h-[200px]">
              <Image
                src={selectedImage}
                alt="Selected food"
                fill
                className="object-contain rounded-xl"
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                unoptimized
              />
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4 text-gray-500">
            <div className="p-4 rounded-full bg-[#9EDA82]/20">
              <UploadIcon className="h-8 w-8 text-[#9EDA82]" />
            </div>
            <div className="text-center">
              <p className="text-lg font-medium">No photo uploaded yet.</p>
              <p className="text-sm">Tap here to add one!</p>
            </div>
          </div>
        )}
      </Card>

      {/* Analysis Results */}
      {analysisResult && (
        <div className="space-y-4">
          {/* Summary and Advice */}
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <h3 className="font-medium mb-2">Analysis Summary</h3>
            <p className="text-sm text-gray-600 mb-4">
              {analysisResult.summary}
            </p>
            <h4 className="font-medium mb-2">Recommendations</h4>
            <p className="text-sm text-gray-600">{analysisResult.advice}</p>
          </div>

          {/* Food Items */}
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <h3 className="font-medium mb-4">Food Items</h3>
            <div className="space-y-2">
              {analysisResult.foods.map((item, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="font-medium">{item.food}</span>
                  <span className="text-gray-600">{item.count} portions</span>
                </div>
              ))}
            </div>
          </div>

          {/* Nutritional Information */}
          <div className="bg-white rounded-xl p-4 shadow-sm">
            <h3 className="font-medium mb-4">Nutritional Information</h3>

            {/* Macronutrients */}
            <div className="mb-6">
              <h4 className="text-sm font-medium text-gray-500 mb-2">
                Macronutrients
              </h4>
              <div className="grid grid-cols-4 gap-2">
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-gray-500 text-sm">Calories</div>
                  <div className="font-medium">
                    {analysisResult.nutrients.macro.calories} kcal
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-gray-500 text-sm">Protein</div>
                  <div className="font-medium">
                    {analysisResult.nutrients.macro.protein}g
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-gray-500 text-sm">Carbs</div>
                  <div className="font-medium">
                    {analysisResult.nutrients.macro.carb}g
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-gray-500 text-sm">Fat</div>
                  <div className="font-medium">
                    {analysisResult.nutrients.macro.fat}g
                  </div>
                </div>
              </div>
            </div>

            {/* Micronutrients */}
            <div className="mb-6">
              <h4 className="text-sm font-medium text-gray-500 mb-2">
                Micronutrients
              </h4>
              <div className="grid grid-cols-3 gap-2">
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-gray-500 text-sm">Dietary Fiber</div>
                  <div className="font-medium">
                    {analysisResult.nutrients.micro.fa}g
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-gray-500 text-sm">Vitamin C</div>
                  <div className="font-medium">
                    {analysisResult.nutrients.micro.vc}mg
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-gray-500 text-sm">Vitamin D</div>
                  <div className="font-medium">
                    {analysisResult.nutrients.micro.vd}mcg
                  </div>
                </div>
              </div>
            </div>

            {/* Minerals */}
            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-2">
                Minerals
              </h4>
              <div className="grid grid-cols-4 gap-2">
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-gray-500 text-sm">Calcium</div>
                  <div className="font-medium">
                    {analysisResult.nutrients.mineral.calcium}mg
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-gray-500 text-sm">Iron</div>
                  <div className="font-medium">
                    {analysisResult.nutrients.mineral.iron}mg
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-gray-500 text-sm">Zinc</div>
                  <div className="font-medium">
                    {analysisResult.nutrients.mineral.zinc}mg
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-gray-500 text-sm">Iodine</div>
                  <div className="font-medium">
                    {analysisResult.nutrients.mineral.iodine}mcg
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Upload Button */}
      <Button
        className="w-full text-white"
        disabled={!selectedImage || isAnalyzing}
        onClick={handleAnalyze}
      >
        {isAnalyzing ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Analyzing...
          </>
        ) : (
          "Analyze Photo"
        )}
      </Button>

      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        className="hidden"
        accept="image/*"
        onChange={handleImageSelect}
      />
    </div>
  );
}

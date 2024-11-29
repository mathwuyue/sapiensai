"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import Image from "next/image";
import { ArrowLeft, Upload as UploadIcon, X, Loader2 } from "lucide-react";
import Link from "next/link";

interface FoodItem {
  name: string;
  calories: number;
  portion: string;
  protein: number;
  carbs: number;
  fat: number;
}

interface AnalysisResult {
  items: FoodItem[];
  total_calories: number;
  image_description: string;
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
      // 将 base64 字符串转换为文件
      const base64Data = selectedImage.split(",")[1];
      const blob = await fetch(`data:image/jpeg;base64,${base64Data}`).then(
        (res) => res.blob()
      );
      const file = new File([blob], "food.jpg", { type: "image/jpeg" });

      // 创建 FormData
      const formData = new FormData();
      formData.append("file", file);

      // send request
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/food/analyze`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) throw new Error("Analysis failed");

      const result = await response.json();
      setAnalysisResult(result);
    } catch (error) {
      console.error("Analysis error:", error);
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
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <h3 className="font-medium mb-2">Analysis Results</h3>
          <p className="text-sm text-gray-500 mb-4">
            {analysisResult.image_description}
          </p>

          {analysisResult.items.map((item, index) => (
            <div key={index} className="mb-4 last:mb-0">
              <div className="flex justify-between items-center mb-1">
                <span className="font-medium">{item.name}</span>
                <span>{item.calories} cal</span>
              </div>
              <div className="text-sm text-gray-500">
                <span className="mr-4">Protein : {item.protein}g</span>
                <span className="mr-4">Carbs: {item.carbs}g</span>
                <span>Fat: {item.fat}g</span>
              </div>
            </div>
          ))}

          <div className="mt-4 pt-4 border-t">
            <div className="flex justify-between items-center">
              <span className="font-medium">Total Calories</span>
              <span className="font-medium">
                {analysisResult.total_calories} cal
              </span>
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

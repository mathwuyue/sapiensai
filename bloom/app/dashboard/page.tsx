"use client";

import { useState } from "react";
import Link from "next/link";

export default function DashboardPage() {
  // Placeholder data - in real app would come from API/database
  const prenatalRecords = [
    { date: "2024-01-15", weight: 65, bloodPressure: "120/80" },
    { date: "2024-02-15", weight: 67, bloodPressure: "118/78" },
    // Add more data points
  ];

  const glucoseReadings = [
    { date: "2024-03-01", level: 95 },
    { date: "2024-03-02", level: 92 },
    // Add more readings
  ];

  const nutritionData = {
    carbs: 50,
    protein: 25,
    fats: 25,
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Prenatal Records Section */}
      <section className="mb-12">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">pregnancy test file</h2>
          <Link
            href="/prenatal/new"
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
          >
            upload new record
          </Link>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-lg">
          {/* Placeholder for prenatal records chart */}
          <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
            pregnancy test chart
          </div>
        </div>
      </section>

      {/* Blood Glucose Management Section */}
      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-6">blood glucose management</h2>
        <div className="bg-white p-6 rounded-lg shadow-lg">
          {/* Placeholder for glucose chart */}
          <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
            blood glucose trend chart
          </div>
        </div>
      </section>

      {/* Nutrition Management Section */}
      <section>
        <h2 className="text-2xl font-bold mb-6">nutrition management</h2>
        <div className="bg-white p-6 rounded-lg shadow-lg">
          {/* Placeholder for nutrition pie chart */}
          <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
            nutrition distribution pie chart
          </div>
        </div>
      </section>
    </div>
  );
}

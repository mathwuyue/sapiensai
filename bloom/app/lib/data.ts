import { PresetCondition, PresetComplication } from './definitions';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export async function fetchPresetConditions(): Promise<PresetCondition[]> {
  const response = await fetch(`${BASE_URL}/profile/conditions/preset`);
  if (!response.ok) {
    throw new Error("Failed to fetch preset conditions");
  }
  return response.json();
}

export async function fetchPresetComplications(): Promise<PresetComplication[]> {
  const response = await fetch(`${BASE_URL}/profile/complications/preset`);
  if (!response.ok) {
    throw new Error("Failed to fetch preset complications");
  }
  return response.json();
}

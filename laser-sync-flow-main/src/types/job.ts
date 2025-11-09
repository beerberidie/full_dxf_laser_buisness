export interface Job {
  id: string;
  projectName: string;
  parts: { name: string; quantity: number }[];
  rawPlateCount: number;
  estimatedCutTime: number; // in minutes
  drawingTime: number; // in minutes
  materialType: string;
  thickness: number;
  preset: string;
  dxfFiles: string[];
  status: "pending" | "running" | "paused" | "complete";
  actualCutTime?: number;
  startedAt?: Date;
  completedAt?: Date;
}

export interface Project {
  id: string;
  name: string;
  progress: number;
  missingData: string[];
  parts: { name: string; quantity: number }[];
  status: "incomplete" | "unscheduled";
  materialType?: string;
  thickness?: number;
  preset?: string;
  rawPlateCount?: number;
  estimatedCutTime?: number;
  drawingTime?: number;
  dxfFiles?: string[];
}

export interface JobFormData {
  projectName: string;
  materialType: string;
  thickness: number;
  rawPlateCount: number;
  estimatedCutTime: number;
  drawingTime: number;
  preset: string;
  parts: { name: string; quantity: number }[];
  dxfFiles: string[];
}

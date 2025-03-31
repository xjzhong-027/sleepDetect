export type Feature = 'posture' | 'emotion' | 'wake';

export interface FeatureState {
  features: {
    [key in Feature]: boolean;
  };
}

export interface MonitoringState {
  isMonitoring: boolean;
  currentEmotion: string;
  currentPosture: string;
  nightWakeCount: number;
  sleepDuration: number;
}

export interface ClockState {
  currentTime: Date;
} 
export interface Location {
  lat: number;
  lng: number;
}

export interface Provider {
  id: string;
  name: string;
  category: string;
  specializations: string[];
  basePrice: number;
  rating: number;
  cancellationRate: number;
  reliabilityScore: number;
  distanceVectors: Location;
  reviewRecency: number;
  isSynthetic: boolean;
}

export interface WorkingHours {
  start: string;
  end: string;
}

export interface ProviderSchedule {
  id: string;
  providerId: string;
  availableDates: string[];
  workingHours: WorkingHours;
  isSynthetic: boolean;
}

export interface Review {
  id: string;
  providerId: string;
  userId: string;
  rating: number;
  comment: string;
  timestamp: string;
  isSynthetic: boolean;
}

export interface TimelineEntry {
  state: string;
  timestamp: string;
  agent: string;
  reasoning?: string;
}

export interface Booking {
  id: string;
  providerId: string;
  userId: string;
  status: 'pending' | 'matched' | 'confirmed' | 'in_progress' | 'completed' | 'disputed' | 'resolved';
  timeline: TimelineEntry[];
  isSynthetic: boolean;
}

export interface AgentTrace {
  id: string;
  bookingId: string;
  agentName: string;
  reasoning: string;
  confidence: number;
  timestamp: string;
  isSynthetic: boolean;
}

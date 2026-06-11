export interface Destination {
  id: string
  name: string
  description: string | null
  source: string
  url: string
  city: string | null
  department: string | null
  country: string
  category: string | null
  rating: number | null
  estimated_days: number | null
  best_season: string | null
  latitude: number | null
  longitude: number | null
  tags: string[] | null
  created_at: string
  updated_at: string | null
}

export interface NearSearchRequest {
  latitude: number
  longitude: number
  radius_km: number
}

export interface GeneratePlanRequest {
  location: string
  days: number
  categories: string[] | null
  preferences: Record<string, string> | null
}

export interface GeneratePlanResponse {
  plan_id: string
  location: string
  days: number
  categories: string[] | null
  itinerary: Itinerary
}

export interface Itinerary {
  summary: string
  daily_plans: DailyPlan[]
  total_cost_estimate: string
  recommendations: string[]
}

export interface DailyPlan {
  day: number
  title: string
  activities: Activity[]
}

export interface Activity {
  time: string
  activity: string
  destination: string
  duration_hours: number
  notes: string
}

export interface SyncResponse {
  status: string
  count: number
}

export interface JobStatus {
  job_id: string
  status: string
  result: Record<string, unknown> | null
  error: string | null
}

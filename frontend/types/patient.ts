export interface Patient {
  id: string
  name: string
  dateOfBirth: string
  journalEntries: JournalEntry[]
  emergencyLogs: EmergencyLog[]
}

export interface JournalEntry {
  id: string
  date: string
  description: string
  type: "regular" | "emergency" | "followup"
  symptoms?: string[]
  medications?: string[]
  summary?: string
}

export interface EmergencyLog {
  id: string
  date: string
  caller: string
  description: string
  urgencyLevel: "low" | "medium" | "high"
  dispatchNotes?: string
  location?: string
  responseTime?: string
}

export interface ActionPoint {
  id: string
  priority: "immediate" | "high" | "medium" | "low"
  description: string
  status: "pending" | "in-progress" | "completed"
  category: "medical" | "safety" | "followup" | "medication"
}

export interface CaseAnalysis {
  summary: string
  actionPoints: ActionPoint[]
  riskLevel: "low" | "medium" | "high" | "critical"
  recommendations: string[]
}

export interface Message {
  id: string
  content: string
  role: "user" | "assistant"
  timestamp: Date
  context?: string
}


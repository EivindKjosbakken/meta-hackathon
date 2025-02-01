import type { Patient, CaseAnalysis } from "@/types/patient"

export const mockPatients: Patient[] = [
  {
    id: "1",
    name: "John Doe",
    dateOfBirth: "1965-03-15",
    journalEntries: [
      {
        id: "j1",
        date: "2024-01-28",
        description: "Patient reported chronic chest pain and shortness of breath. History of hypertension.",
        type: "regular",
        symptoms: ["chest pain", "shortness of breath"],
        medications: ["Lisinopril 10mg", "Aspirin 81mg"],
      },
      {
        id: "j2",
        date: "2024-01-15",
        description: "Follow-up after ER visit. Blood pressure remains elevated.",
        type: "followup",
        symptoms: ["high blood pressure"],
        medications: ["Lisinopril 20mg", "Aspirin 81mg"],
      },
    ],
    emergencyLogs: [
      {
        id: "e1",
        date: "2024-02-01T15:23:00Z",
        caller: "Spouse",
        description: "Patient experiencing severe chest pain and difficulty breathing",
        urgencyLevel: "high",
        dispatchNotes: "History of cardiac issues. Patient conscious but distressed.",
        location: "123 Main St, Apt 4B",
        responseTime: "4 minutes",
      },
      {
        id: "e2",
        date: "2024-01-15T08:45:00Z",
        caller: "Patient",
        description: "Severe hypertension symptoms",
        urgencyLevel: "medium",
        dispatchNotes: "BP 180/95, conscious and oriented",
        location: "123 Main St, Apt 4B",
        responseTime: "8 minutes",
      },
    ],
  },
  {
    id: "2",
    name: "Jane Smith",
    dateOfBirth: "1978-08-22",
    journalEntries: [
      {
        id: "j3",
        date: "2024-01-30",
        description: "Patient has Type 2 Diabetes. Regular check of blood sugar levels.",
        type: "regular",
        symptoms: ["fatigue", "increased thirst"],
        medications: ["Metformin 1000mg", "Glipizide 5mg"],
      },
    ],
    emergencyLogs: [
      {
        id: "e3",
        date: "2024-02-01T16:30:00Z",
        caller: "Patient",
        description: "Hypoglycemic episode, blood sugar 45mg/dL",
        urgencyLevel: "medium",
        dispatchNotes: "Patient conscious but confused. Has glucose tablets.",
        location: "456 Oak Ave",
        responseTime: "6 minutes",
      },
    ],
  },
]

export const mockAnalyzeCase = async (patientId: string, imageUrl: string, notes: string): Promise<CaseAnalysis> => {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 2000))

  return {
    summary:
      "Based on the image analysis and patient history, patient shows signs of acute cardiac distress with concurrent hypertension symptoms.",
    actionPoints: [
      {
        id: "ap1",
        priority: "immediate",
        description: "Administer sublingual nitroglycerin if prescribed",
        status: "pending",
        category: "medical",
      },
      {
        id: "ap2",
        priority: "immediate",
        description: "Monitor vital signs - BP, heart rate, O2 saturation",
        status: "pending",
        category: "medical",
      },
      {
        id: "ap3",
        priority: "high",
        description: "Prepare 12-lead ECG",
        status: "pending",
        category: "medical",
      },
      {
        id: "ap4",
        priority: "medium",
        description: "Review current medication list for interactions",
        status: "pending",
        category: "medication",
      },
    ],
    riskLevel: "high",
    recommendations: [
      "Consider immediate hospital transport",
      "Monitor for signs of acute MI",
      "Have defibrillator ready",
      "Establish IV access if possible",
    ],
  }
}

export const mockChatResponse = async (message: string): Promise<string> => {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1000))

  const responses = [
    "Based on the patient's history, this could indicate an acute cardiac event. Continue monitoring vital signs.",
    "The current symptoms align with previous episodes. Consider administering prescribed medication.",
    "Given the patient's age and medical history, these symptoms require immediate attention.",
    "Previous emergency logs show similar patterns. Recommend following established treatment protocol.",
  ]

  return responses[Math.floor(Math.random() * responses.length)]
}


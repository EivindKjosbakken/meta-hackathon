"use client"

import { useState } from "react"
import { PatientSearch } from "@/components/patient-search"
import { EmergencyBrief } from "@/components/emergency-brief"
import { CaseAssessment } from "@/components/case-assessment"
import { ChatInterface } from "@/components/chat-interface"
import type { Patient, CaseAnalysis } from "@/types/patient"

type Step = "brief" | "assessment" | "chat"

export default function PatientPortal() {
  const [currentStep, setCurrentStep] = useState<Step>("brief")
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null)
  const [analysis, setAnalysis] = useState<CaseAnalysis | null>(null)

  const handlePatientSelect = (patient: Patient) => {
    setSelectedPatient(patient)
  }

  const handleAnalysisComplete = (caseAnalysis: CaseAnalysis) => {
    setAnalysis(caseAnalysis)
    setCurrentStep("chat")
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-background to-ai-50/20">
      <div className="container max-w-lg mx-auto p-4 space-y-4">
        {/* Step indicator */}
        <div className="flex items-center justify-between mb-8 px-2">
          {(["brief", "assessment", "chat"] as Step[]).map((step, index) => (
            <div
              key={step}
              className={`flex flex-col items-center ${
                index < ["brief", "assessment", "chat"].indexOf(currentStep) + 1
                  ? "text-ai-500"
                  : "text-muted-foreground"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center mb-2 ${
                  index < ["brief", "assessment", "chat"].indexOf(currentStep) + 1 ? "bg-ai-500 text-white" : "bg-muted"
                }`}
              >
                {index + 1}
              </div>
              <span className="text-xs hidden sm:block capitalize">{step}</span>
            </div>
          ))}
        </div>

        {/* Main Content */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-glow via-glow-purple to-glow-teal opacity-10 blur-3xl -z-10" />

          {!selectedPatient && <PatientSearch onSelectPatient={handlePatientSelect} />}

          {selectedPatient && currentStep === "brief" && (
            <EmergencyBrief patient={selectedPatient} onContinue={() => setCurrentStep("assessment")} />
          )}

          {selectedPatient && currentStep === "assessment" && (
            <CaseAssessment patient={selectedPatient} onAnalysisComplete={handleAnalysisComplete} />
          )}

          {selectedPatient && currentStep === "chat" && analysis && (
            <ChatInterface patient={selectedPatient} analysis={analysis} />
          )}
        </div>
      </div>
    </main>
  )
}


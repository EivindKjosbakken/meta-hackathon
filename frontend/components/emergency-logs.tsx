"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { format } from "date-fns"
import type { Patient, EmergencyLog } from "@/types/patient"

// Mock emergency logs
const mockEmergencyLogs: EmergencyLog[] = [
  {
    id: "1",
    date: "2024-01-28T08:23:00Z",
    caller: "Family Member",
    description: "Patient experiencing severe chest pain",
    urgencyLevel: "high",
  },
  {
    id: "2",
    date: "2024-01-15T15:45:00Z",
    caller: "Patient",
    description: "Difficulty breathing after exercise",
    urgencyLevel: "medium",
  },
]

interface EmergencyLogsProps {
  patient: Patient
  onClose: () => void
}

export function EmergencyLogs({ patient, onClose }: EmergencyLogsProps) {
  const logs = patient.emergencyLogs || mockEmergencyLogs

  const getUrgencyColor = (level: EmergencyLog["urgencyLevel"]) => {
    switch (level) {
      case "high":
        return "bg-red-100 text-red-700 hover:bg-red-200"
      case "medium":
        return "bg-yellow-100 text-yellow-700 hover:bg-yellow-200"
      case "low":
        return "bg-green-100 text-green-700 hover:bg-green-200"
    }
  }

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Emergency Call Logs</DialogTitle>
        </DialogHeader>
        <ScrollArea className="h-[60vh] pr-4">
          <div className="space-y-4">
            {logs.map((log) => (
              <div key={log.id} className="p-4 rounded-lg border bg-card text-card-foreground">
                <div className="flex items-start justify-between mb-2">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{format(new Date(log.date), "PPP p")}</p>
                    <p className="text-sm text-muted-foreground">Caller: {log.caller}</p>
                  </div>
                  <Badge className={getUrgencyColor(log.urgencyLevel)}>{log.urgencyLevel}</Badge>
                </div>
                <p className="text-sm">{log.description}</p>
              </div>
            ))}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}


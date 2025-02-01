"use client"

import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Phone, AlertTriangle, Clock, FileText } from "lucide-react"
import { format } from "date-fns"
import type { Patient } from "@/types/patient"

interface EmergencyBriefProps {
  patient: Patient
  onContinue: () => void
}

export function EmergencyBrief({ patient, onContinue }: EmergencyBriefProps) {
  // Get the most recent emergency log
  const latestEmergency = patient.emergencyLogs[0]

  // Get recent journal entries (last 3)
  const recentEntries = patient.journalEntries.slice(0, 3)

  return (
    <div className="space-y-4">
      {/* Emergency Call Summary */}
      <Card className="border-red-200 bg-red-50">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-red-700 flex items-center gap-2">
              <Phone className="h-4 w-4" />
              Emergency Call Summary
            </CardTitle>
            <Badge variant="destructive">{latestEmergency.urgencyLevel}</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-red-600">
            <Clock className="h-4 w-4" />
            {format(new Date(latestEmergency.date), "PPp")}
          </div>
          <Alert variant="destructive" className="bg-red-100 border-red-200">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Dispatch Notes</AlertTitle>
            <AlertDescription>{latestEmergency.dispatchNotes}</AlertDescription>
          </Alert>
          <div className="text-sm">
            <strong>Location:</strong> {latestEmergency.location}
          </div>
          <div className="text-sm">
            <strong>Response Time:</strong> {latestEmergency.responseTime}
          </div>
        </CardContent>
      </Card>

      {/* Recent Medical History */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Recent Medical History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[200px] pr-4">
            <div className="space-y-4">
              {recentEntries.map((entry) => (
                <div key={entry.id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{format(new Date(entry.date), "PP")}</span>
                    <Badge variant="outline">{entry.type}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{entry.description}</p>
                  {entry.symptoms && (
                    <div className="flex flex-wrap gap-1">
                      {entry.symptoms.map((symptom) => (
                        <Badge key={symptom} variant="secondary">
                          {symptom}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
        <CardFooter>
          <Button onClick={onContinue} className="w-full bg-ai-500 hover:bg-ai-600">
            Continue to Assessment
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}


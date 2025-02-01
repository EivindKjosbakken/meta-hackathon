import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { X } from "lucide-react"
import type { Patient } from "@/types/patient"

interface PatientJournalProps {
  patient: Patient
}

export function PatientJournal({ patient }: PatientJournalProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-lg font-medium">Patient Journal</CardTitle>
        <Button variant="ghost" size="icon">
          <X className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {patient.journalEntries.map((entry, index) => (
          <div key={index} className="text-sm leading-relaxed">
            {entry}
          </div>
        ))}
      </CardContent>
    </Card>
  )
}


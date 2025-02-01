"use client"

import * as React from "react"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Button } from "@/components/ui/button"
import { Check, ChevronsUpDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { mockPatients } from "@/lib/mock-data"
import type { Patient } from "@/types/patient"

interface PatientSearchProps {
  onSelectPatient: (patient: Patient) => void
}

export function PatientSearch({ onSelectPatient }: PatientSearchProps) {
  const [open, setOpen] = React.useState(false)
  const [selectedPatient, setSelectedPatient] = React.useState<Patient | null>(null)
  const [searchQuery, setSearchQuery] = React.useState("")

  const filteredPatients = mockPatients.filter(
    (patient) => patient.name.toLowerCase().includes(searchQuery.toLowerCase()) || patient.id.includes(searchQuery),
  )

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-full justify-between bg-background/50 backdrop-blur-sm border-ai-100 hover:border-ai-200 hover:bg-ai-50/50 transition-colors"
        >
          {selectedPatient ? selectedPatient.name : "Search patient..."}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0 shadow-lg shadow-ai-500/10">
        <Command className="border-ai-100">
          <CommandInput
            placeholder="Search by name or ID..."
            onValueChange={setSearchQuery}
            className="border-b-ai-100"
          />
          <CommandList>
            <CommandEmpty>No patient found.</CommandEmpty>
            <CommandGroup>
              {filteredPatients.map((patient) => (
                <CommandItem
                  key={patient.id}
                  onSelect={() => {
                    setSelectedPatient(patient)
                    onSelectPatient(patient)
                    setOpen(false)
                  }}
                  className="hover:bg-ai-50"
                >
                  <Check
                    className={cn(
                      "mr-2 h-4 w-4 text-ai-500",
                      selectedPatient?.id === patient.id ? "opacity-100" : "opacity-0",
                    )}
                  />
                  <div className="flex flex-col">
                    <span>{patient.name}</span>
                    <span className="text-sm text-muted-foreground">
                      ID: {patient.id} • DOB: {patient.dateOfBirth}
                    </span>
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}


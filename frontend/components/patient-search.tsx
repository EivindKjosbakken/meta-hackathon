"use client"

import * as React from "react"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Button } from "@/components/ui/button"
import { Check, ChevronsUpDown } from "lucide-react"
import { cn } from "@/lib/utils"
import type { Patient } from "@/types/patient"

interface PatientSearchProps {
  onSelectPatient: (patient: Patient) => void
}

interface SearchResult {
  name: string
  score: number
}

export function PatientSearch({ onSelectPatient }: PatientSearchProps) {
  const [open, setOpen] = React.useState(false)
  const [selectedPatient, setSelectedPatient] = React.useState<Patient | null>(null)
  const [searchQuery, setSearchQuery] = React.useState("")
  const [searchResults, setSearchResults] = React.useState<SearchResult[]>([])
  const [error, setError] = React.useState<string | null>(null)

  const searchPatients = async (query: string) => {
    if (!query) {
      setSearchResults([])
      setError(null)
      return
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/search_patients?query=${encodeURIComponent(query)}`,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
          mode: 'cors',
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setSearchResults(data.matches || [])
      setError(null)
    } catch (error) {
      console.error("Error searching patients:", error)
      setSearchResults([])
      setError("Failed to search patients. Please try again.")
    }
  }

  // Debounce search to avoid too many API calls
  React.useEffect(() => {
    const timer = setTimeout(() => {
      searchPatients(searchQuery)
    }, 300)

    return () => clearTimeout(timer)
  }, [searchQuery])

  const handleSelect = (result: SearchResult) => {
    // Create a Patient object from the search result
    const patient: Patient = {
      id: result.name, // Using the full name as ID for now
      name: result.name.split(" – ")[0], // Extract just the name part
      dateOfBirth: result.name.split(" – ")[1]?.split(" ")[0] || "", // Extract DOB if available
      journalEntries: [],
      emergencyLogs: [],
    }

    setSelectedPatient(patient)
    onSelectPatient(patient)
    setOpen(false)
  }

  return (
    <div className="space-y-2">
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
              value={searchQuery}
              onValueChange={setSearchQuery}
              className="border-b-ai-100"
            />
            <CommandList>
              {error ? (
                <CommandEmpty className="py-6 text-center text-sm text-red-500">
                  {error}
                </CommandEmpty>
              ) : searchResults.length === 0 ? (
                <CommandEmpty>No patient found.</CommandEmpty>
              ) : (
                <CommandGroup>
                  {searchResults.map((result) => (
                    <CommandItem
                      key={result.name}
                      onSelect={() => handleSelect(result)}
                      className="hover:bg-ai-50"
                    >
                      <Check
                        className={cn(
                          "mr-2 h-4 w-4 text-ai-500",
                          selectedPatient?.id === result.name ? "opacity-100" : "opacity-0"
                        )}
                      />
                      <div className="flex flex-col">
                        <span>{result.name.split(" – ")[0]}</span>
                        <span className="text-sm text-muted-foreground">
                          Match score: {result.score}%
                        </span>
                      </div>
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  )
}


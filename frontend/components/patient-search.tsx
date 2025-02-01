"use client"

import * as React from "react"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Button } from "@/components/ui/button"
import { Check, ChevronsUpDown, Search, Loader2 } from "lucide-react"
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
  const [isSearching, setIsSearching] = React.useState(false)

  const searchPatients = async () => {
    if (!searchQuery) {
      setSearchResults([])
      setError(null)
      return
    }

    setIsSearching(true)
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/search_patients?query=${encodeURIComponent(searchQuery)}`,
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
      console.log('API Response:', data)
      if (data.matches && data.matches.length > 0) {
        setSearchResults(data.matches)
        setOpen(true)
      } else {
        setSearchResults([])
        setError("No matches found")
      }
    } catch (error) {
      console.error("Error searching patients:", error)
      setSearchResults([])
      setError("Failed to search patients. Please try again.")
    } finally {
      setIsSearching(false)
    }
  }

  const handleSelect = (result: SearchResult) => {
    // Parse "kari nordmann – 250795 67890" format
    const [namePart, idPart] = result.name.split(" – ")
    const [dateStr, personalNumber] = idPart ? idPart.split(" ") : ["", ""]
    
    // Format date from DDMMYY to a more readable format
    const formattedDate = dateStr ? 
      `${dateStr.slice(0,2)}.${dateStr.slice(2,4)}.${dateStr.slice(4)}` : ""

    const patient: Patient = {
      id: personalNumber || result.name, // Use personal number as ID if available
      name: namePart,
      dateOfBirth: formattedDate,
      journalEntries: [],
      emergencyLogs: [],
    }

    setSelectedPatient(patient)
    onSelectPatient(patient)
    setOpen(false)
  }

  return (
    <div className="space-y-2">
      <Popover 
        open={open} 
        onOpenChange={setOpen}
      >
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
        <PopoverContent className="w-[400px] p-0" align="start">
          <Command className="w-full">
            <div className="flex gap-2 p-2 border-b">
              <CommandInput
                placeholder="Search by name or ID..."
                value={searchQuery}
                onValueChange={(value) => {
                  setSearchQuery(value)
                  if (!value) {
                    setSearchResults([])
                    setError(null)
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    searchPatients()
                  }
                }}
                className="w-full"
              />
              <Button 
                size="sm"
                onClick={searchPatients}
                disabled={isSearching}
              >
                {isSearching ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
              </Button>
            </div>
            <CommandList className="max-h-[300px] overflow-y-auto p-2">
              <CommandEmpty className="py-6 text-center text-sm">
                {isSearching ? (
                  <div className="flex flex-col items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Searching...</span>
                  </div>
                ) : error ? (
                  <span className="text-red-500">{error}</span>
                ) : searchQuery ? (
                  "No results found"
                ) : (
                  "Type a name and press Enter or click Search"
                )}
              </CommandEmpty>
              {searchResults.length > 0 && (
                <CommandGroup>
                  {searchResults.map((result) => (
                    <CommandItem
                      key={result.name}
                      value={result.name}
                      onSelect={() => handleSelect(result)}
                      className="flex flex-col items-start gap-1 p-2 cursor-pointer hover:bg-ai-50"
                    >
                      <span className="font-medium">{result.name.split(" – ")[0]}</span>
                      <span className="text-sm text-muted-foreground">
                        Match score: {result.score}%
                      </span>
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


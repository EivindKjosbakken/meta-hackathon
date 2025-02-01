"use client"

import * as React from "react"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
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
  const [searchQuery, setSearchQuery] = React.useState("")
  const [searchResults, setSearchResults] = React.useState<SearchResult[]>([])
  const [error, setError] = React.useState<string | null>(null)
  const [isSearching, setIsSearching] = React.useState(false)
  const [hasSearched, setHasSearched] = React.useState(false)

  const searchPatients = async () => {
    if (!searchQuery) {
      setSearchResults([])
      setError(null)
      return
    }

    setIsSearching(true)
    setHasSearched(true)
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
      if (data.matches && data.matches.length > 0) {
        setSearchResults(data.matches)
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

  const handleSelect = async (result: SearchResult) => {
    // Parse both hyphen and en dash formats
    const [namePart, idPart] = result.name.split(/ - | – /)
    const [dateStr, personalNumber] = idPart ? idPart.split(" ") : ["", ""]
    
    // Format date from DDMMYY to a more readable format
    const formattedDate = dateStr ? 
      `${dateStr.slice(0,2)}.${dateStr.slice(2,4)}.${dateStr.slice(4)}` : ""

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/load_journal?patient_id=${encodeURIComponent(result.name)}`,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      const patient: Patient = {
        id: result.name,
        name: namePart,
        dateOfBirth: formattedDate,
        journalEntries: [{
          id: '1',
          date: new Date().toISOString(),
          description: data.text,
          type: 'regular',
          summary: data.summary
        }],
        emergencyLogs: [],
      }

      onSelectPatient(patient)
    } catch (error) {
      console.error('Error loading patient journal:', error)
    }
  }

  return (
    <div className="space-y-2">
      <Command className="border rounded-lg shadow-sm">
        <div className="flex items-center p-2 border-b">
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
            className="flex-1"
          />
          <Button 
            size="sm"
            onClick={searchPatients}
            disabled={isSearching}
            className="ml-auto pl-4 shrink-0"
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
            ) : hasSearched ? (
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
    </div>
  )
}


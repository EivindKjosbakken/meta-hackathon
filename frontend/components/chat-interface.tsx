"use client"

import { useState } from "react"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Send, AlertTriangle, Loader2 } from "lucide-react"
import { mockChatResponse } from "@/lib/mock-data"
import type { Patient, Message, CaseAnalysis, ActionPoint } from "@/types/patient"
import { TextToSpeech } from "@/components/text-to-speech"

interface ChatInterfaceProps {
  patient: Patient
  analysis: CaseAnalysis
}

export function ChatInterface({ patient, analysis }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      const response = await mockChatResponse(input)

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response,
        role: "assistant",
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error("Error getting response:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const getPriorityColor = (priority: ActionPoint["priority"]) => {
    switch (priority) {
      case "immediate":
        return "bg-red-100 text-red-700 border-red-200"
      case "high":
        return "bg-orange-100 text-orange-700 border-orange-200"
      case "medium":
        return "bg-yellow-100 text-yellow-700 border-yellow-200"
      case "low":
        return "bg-green-100 text-green-700 border-green-200"
    }
  }

  return (
    <div className="space-y-4">
      {/* Analysis Summary */}
      <Alert
        className={`
        ${
          analysis.riskLevel === "critical" || analysis.riskLevel === "high"
            ? "bg-red-50 border-red-200 text-red-700"
            : "bg-yellow-50 border-yellow-200 text-yellow-700"
        }
      `}
      >
        <div className="flex justify-between items-start gap-4">
          <AlertDescription className="text-sm">{analysis.summary}</AlertDescription>
          <TextToSpeech text={analysis.summary} />
        </div>
      </Alert>

      {/* Action Points */}
      <Card className="border-ai-100">
        <CardContent className="pt-6">
          <h3 className="text-sm font-medium mb-3">Action Points</h3>
          <ScrollArea className="h-[200px]">
            <div className="space-y-2 pr-4">
              {analysis.actionPoints.map((point) => (
                <div key={point.id} className={`p-3 rounded-lg border ${getPriorityColor(point.priority)}`}>
                  <div className="flex items-center justify-between mb-1">
                    <Badge variant="outline" className={getPriorityColor(point.priority)}>
                      {point.priority}
                    </Badge>
                    <Badge variant="outline">{point.category}</Badge>
                  </div>
                  <p className="text-sm">{point.description}</p>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Chat Interface */}
      <Card className="border-0 shadow-none relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-ai-50/20 to-transparent pointer-events-none" />
        <ScrollArea className="h-[300px] pr-4">
          <CardContent className="space-y-4">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`rounded-lg px-4 py-2 max-w-[80%] shadow-lg ${
                    message.role === "user" ? "bg-ai-500 text-white" : "bg-background border border-ai-100"
                  } ${message.role === "assistant" ? "relative overflow-hidden" : ""}`}
                >
                  {message.role === "assistant" && (
                    <div className="absolute inset-0 bg-gradient-to-r from-glow-purple/5 to-glow-teal/5" />
                  )}
                  <p className="text-sm relative">{message.content}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="rounded-lg px-4 py-2 bg-background border border-ai-100">
                  <Loader2 className="h-4 w-4 animate-spin" />
                </div>
              </div>
            )}
          </CardContent>
        </ScrollArea>
        <CardFooter className="flex gap-2 pt-4">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about the patient's condition..."
            className="min-h-[60px] bg-background/50 backdrop-blur-sm border-ai-100"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
          />
          <Button
            onClick={handleSend}
            size="icon"
            className="shrink-0 bg-ai-500 hover:bg-ai-600 text-white shadow-lg shadow-ai-500/25"
            disabled={isLoading}
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}


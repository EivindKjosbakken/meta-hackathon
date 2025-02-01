"use client"

import { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Camera, RotateCcw, Loader2 } from "lucide-react"
import { mockAnalyzeCase } from "@/lib/mock-data"
import type { Patient, CaseAnalysis } from "@/types/patient"

interface CaseAssessmentProps {
  patient: Patient
  onAnalysisComplete: (analysis: CaseAnalysis) => void
}

export function CaseAssessment({ patient, onAnalysisComplete }: CaseAssessmentProps) {
  const [imageUrl, setImageUrl] = useState<string | null>(null)
  const [notes, setNotes] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
    } catch (err) {
      console.error("Error accessing camera:", err)
    }
  }

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks()
      tracks.forEach((track) => track.stop())
    }
  }

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext("2d")
      if (context) {
        canvasRef.current.width = videoRef.current.videoWidth
        canvasRef.current.height = videoRef.current.videoHeight
        context.drawImage(videoRef.current, 0, 0)
        const imageUrl = canvasRef.current.toDataURL("image/jpeg")
        setImageUrl(imageUrl)
        stopCamera()
      }
    }
  }

  const analyzeCase = async () => {
    if (!imageUrl) return

    setIsAnalyzing(true)
    try {
      const analysis = await mockAnalyzeCase(patient.id, imageUrl, notes)
      onAnalysisComplete(analysis)
    } catch (error) {
      console.error("Error analyzing case:", error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  // Start camera when component mounts
  useEffect(() => {
    startCamera()
    return () => stopCamera()
  }, [])

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle className="text-lg font-medium">Patient Assessment</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="relative aspect-video rounded-lg overflow-hidden bg-black">
          {!imageUrl && (
            <>
              <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover" />
              <Button className="absolute bottom-4 left-1/2 transform -translate-x-1/2" onClick={captureImage}>
                <Camera className="w-4 h-4 mr-2" />
                Capture Image
              </Button>
            </>
          )}
          {imageUrl && (
            <img src={imageUrl || "/placeholder.svg"} alt="Captured" className="w-full h-full object-cover" />
          )}
          <canvas ref={canvasRef} className="hidden" />
        </div>

        {imageUrl && (
          <Button
            variant="outline"
            onClick={() => {
              setImageUrl(null)
              startCamera()
            }}
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Retake Photo
          </Button>
        )}

        <Textarea
          placeholder="Enter additional observations..."
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="min-h-[100px]"
        />
      </CardContent>
      <CardFooter>
        <Button className="w-full bg-ai-500 hover:bg-ai-600" onClick={analyzeCase} disabled={!imageUrl || isAnalyzing}>
          {isAnalyzing ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Analyzing...
            </>
          ) : (
            "Analyze Case"
          )}
        </Button>
      </CardFooter>
    </Card>
  )
}


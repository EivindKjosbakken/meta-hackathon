"use client"

import { useState, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Camera, RotateCcw } from "lucide-react"
import type { PatientImage } from "@/types/patient"

interface ImageCaptureProps {
  onCapture: (image: PatientImage) => void
}

export function ImageCapture({ onCapture }: ImageCaptureProps) {
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (err) {
      console.error("Error accessing camera:", err)
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop())
      setStream(null)
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
        setCapturedImage(imageUrl)
        stopCamera()
      }
    }
  }

  const retake = () => {
    setCapturedImage(null)
    startCamera()
  }

  const confirmImage = () => {
    if (capturedImage) {
      onCapture({
        id: Date.now().toString(),
        url: capturedImage,
        captureDate: new Date(),
      })
    }
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle className="text-lg font-medium">Capture Patient Photo</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="relative aspect-video rounded-lg overflow-hidden bg-black">
          {!stream && !capturedImage && (
            <Button
              className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
              onClick={startCamera}
            >
              <Camera className="w-4 h-4 mr-2" />
              Start Camera
            </Button>
          )}
          {stream && <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover" />}
          {capturedImage && (
            <img src={capturedImage || "/placeholder.svg"} alt="Captured" className="w-full h-full object-cover" />
          )}
          <canvas ref={canvasRef} className="hidden" />
        </div>

        <div className="flex justify-center gap-4">
          {stream && (
            <Button onClick={captureImage} className="bg-ai-500 hover:bg-ai-600">
              <Camera className="w-4 h-4 mr-2" />
              Capture
            </Button>
          )}
          {capturedImage && (
            <>
              <Button variant="outline" onClick={retake}>
                <RotateCcw className="w-4 h-4 mr-2" />
                Retake
              </Button>
              <Button className="bg-ai-500 hover:bg-ai-600" onClick={confirmImage}>
                Confirm & Continue
              </Button>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  )
}


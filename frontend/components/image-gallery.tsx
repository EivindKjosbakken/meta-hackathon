"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, X } from "lucide-react"
import type { Patient, PatientImage } from "@/types/patient"

interface ImageGalleryProps {
  patient: Patient
}

export function ImageGallery({ patient }: ImageGalleryProps) {
  const [images, setImages] = useState<PatientImage[]>([])

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files) return

    const newImages: PatientImage[] = Array.from(files).map((file) => ({
      id: Date.now().toString(),
      url: URL.createObjectURL(file),
    }))

    setImages([...images, ...newImages])
  }

  const removeImage = (id: string) => {
    setImages(images.filter((image) => image.id !== id))
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-lg font-medium">Images</CardTitle>
        <Button variant="outline" size="sm" className="gap-2">
          <Upload className="h-4 w-4" />
          <label htmlFor="image-upload" className="cursor-pointer">
            Upload
          </label>
          <input
            id="image-upload"
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={handleImageUpload}
          />
        </Button>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          {images.map((image) => (
            <div key={image.id} className="relative group">
              <img
                src={image.url || "/placeholder.svg"}
                alt="Patient"
                className="w-full h-32 object-cover rounded-lg"
              />
              <Button
                variant="destructive"
                size="icon"
                className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={() => removeImage(image.id)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}


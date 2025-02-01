import { Button } from "@/components/ui/button"
import { Volume2, VolumeX, Loader2 } from "lucide-react"
import { useState, useEffect } from "react"

interface TextToSpeechProps {
  text: string
}

export function TextToSpeech({ text }: TextToSpeechProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [speechSynthesis, setSpeechSynthesis] = useState<SpeechSynthesis | null>(null)

  useEffect(() => {
    if (typeof window !== 'undefined') {
      setSpeechSynthesis(window.speechSynthesis)
    }
  }, [])

  const speak = () => {
    if (!speechSynthesis) return

    if (isPlaying) {
      speechSynthesis.cancel()
      setIsPlaying(false)
      return
    }

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.onend = () => setIsPlaying(false)
    utterance.onerror = () => setIsPlaying(false)

    setIsPlaying(true)
    speechSynthesis.speak(utterance)
  }

  if (!speechSynthesis) {
    return null
  }

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={speak}
      className="gap-2"
    >
      {isPlaying ? (
        <>
          <VolumeX className="h-4 w-4" />
          Stop Reading
        </>
      ) : (
        <>
          <Volume2 className="h-4 w-4" />
          Read Aloud
        </>
      )}
    </Button>
  )
} 
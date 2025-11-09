"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send, Loader2, Sparkles } from "lucide-react"

interface ChatInputProps {
  onSendMessage: (message: string) => void
  isLoading: boolean
}

export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim())
      setInput("")
    }
  }

  return (
    <div className="border-t-2 border-[#FFC72C] bg-gradient-to-r from-white via-yellow-50 to-white dark:from-gray-900 dark:via-red-950 dark:to-gray-900 px-6 py-6 shadow-lg">
      <form onSubmit={handleSubmit} className="mx-auto max-w-4xl">
        <div className="flex gap-3 items-center p-2 bg-white dark:bg-gray-800 rounded-2xl border-3 border-[#FFC72C] focus-within:border-[#DA291C] focus-within:shadow-xl transition-all duration-200 shadow-lg">
          <div className="pl-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-[#DA291C] to-[#8B0000] flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-[#FFC72C]" />
            </div>
          </div>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tanyakan tentang menu McDonald's favoritmu..."
            disabled={isLoading}
            className={`flex-1 border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-base font-medium
              text-black dark:text-white
              placeholder:text-gray-400 focus:placeholder-transparent ${input ? 'placeholder-transparent' : ''}
              caret-[#DA291C]`}
          />
          <Button
            type="submit"
            size="icon"
            disabled={isLoading || !input.trim()}
            className="rounded-xl h-14 w-14 bg-gradient-to-br from-[#DA291C] to-[#8B0000] hover:from-[#8B0000] hover:to-[#DA291C] disabled:opacity-50 shadow-lg hover:shadow-xl transition-all duration-200 border-2 border-[#FFC72C]"
          >
            {isLoading ? (
              <Loader2 className="h-6 w-6 animate-spin text-[#FFC72C]" />
            ) : (
              <Send className="h-6 w-6 text-[#FFC72C]" />
            )}
          </Button>
        </div>
        <div className="flex items-center justify-center gap-2 mt-3">
          <span className="text-xs font-bold text-[#DA291C]">⚡</span>
          <p className="text-xs text-gray-600 dark:text-gray-400 font-medium">
            Tekan <kbd className="px-2 py-0.5 bg-[#FFC72C] text-[#DA291C] rounded font-bold">Enter</kbd> untuk mengirim
          </p>
        </div>
      </form>
    </div>
  )
}
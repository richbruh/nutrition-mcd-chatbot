"use client"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Bot, User } from "lucide-react"

interface ChatMessageProps {
  role: "user" | "assistant"
  content: string
}

export function ChatMessage({ role, content }: ChatMessageProps) {
  const isAssistant = role === "assistant"

  return (
    <div className={`flex gap-4 ${isAssistant ? 'justify-start' : 'justify-end'} animate-in fade-in slide-in-from-bottom-4 duration-300`}>
      {isAssistant && (
        <Avatar className="h-11 w-11 border-3 border-white shadow-xl bg-gradient-to-br from-[#DA291C] to-[#8B0000] flex-shrink-0">
          <AvatarFallback className="bg-transparent">
            <Bot className="h-6 w-6 text-[#FFC72C]" />
          </AvatarFallback>
        </Avatar>
      )}

      <div className={`flex flex-col gap-2 max-w-[75%] ${!isAssistant ? 'items-end' : ''}`}>
        <div
          className={`px-6 py-4 rounded-2xl shadow-lg transition-all duration-200 hover:shadow-xl ${
            isAssistant
              ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border-2 border-[#FFC72C]/30'
              : 'bg-gradient-to-br from-[#DA291C] to-[#8B0000] text-white border-2 border-white/20'
          }`}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap font-medium">{content}</p>
        </div>
        <div className="flex items-center gap-2 px-2">
          <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">
            {new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })}
          </span>
          {isAssistant && (
            <span className="text-xs bg-[#FFC72C] text-[#DA291C] px-2 py-0.5 rounded-full font-bold">
              AI
            </span>
          )}
        </div>
      </div>

      {!isAssistant && (
        <Avatar className="h-11 w-11 border-3 border-white shadow-xl bg-gradient-to-br from-blue-500 to-purple-600 flex-shrink-0">
          <AvatarFallback className="bg-transparent">
            <User className="h-6 w-6 text-white" />
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  )
}
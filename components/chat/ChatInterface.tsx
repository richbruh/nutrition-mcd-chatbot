"use client"

import { useState, useRef, useEffect } from "react"
import { ChatMessage } from "./ChatMessage"
import { ChatInput } from "./ChatInput"
import { Button } from "@/components/ui/button"
import { Plus, Menu, Sparkles, Utensils } from "lucide-react"

interface Message {
  role: "user" | "assistant"
  content: string
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "👋 Halo! Saya adalah asisten nutrisi McDonald's bertenaga AI. Saya siap membantu Anda mengetahui informasi nutrisi seperti kalori, gula, garam, dan lemak dari menu favorit Anda. Silakan tanyakan apa saja!"
    }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = { role: "user", content }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: content }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const responseText = await response.text()
      console.log("Raw response:", responseText)

      let data
      try {
        data = JSON.parse(responseText)
      } catch (parseError) {
        console.error("JSON parse error:", parseError)
        throw new Error("Invalid JSON response from server")
      }

      let assistantContent = ""
      
      if (typeof data === 'string') {
        assistantContent = data
      } else if (data.response) {
        assistantContent = data.response
      } else if (data.answer) {
        assistantContent = data.answer
      } else if (data.message) {
        assistantContent = data.message
      } else if (data.content) {
        assistantContent = data.content
      } else if (data.result) {
        assistantContent = data.result
      } else {
        assistantContent = JSON.stringify(data, null, 2)
      }

      const assistantMessage: Message = {
        role: "assistant",
        content: assistantContent,
      }
      
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error("Error details:", error)
      const errorMessage: Message = {
        role: "assistant",
        content: `⚠️ Maaf, terjadi kesalahan: ${error instanceof Error ? error.message : 'Unknown error'}\n\nPastikan backend server sudah berjalan di http://localhost:8000`,
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleNewChat = () => {
    setMessages([
      {
        role: "assistant",
        content: "👋 Halo! Saya adalah asisten nutrisi McDonald's bertenaga AI. Saya siap membantu Anda mengetahui informasi nutrisi seperti kalori, gula, garam, dan lemak dari menu favorit Anda. Silakan tanyakan apa saja!"
      }
    ])
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-red-50 via-yellow-50 to-orange-50 dark:from-gray-900 dark:via-red-950 dark:to-gray-900">
      {/* Sidebar dengan warna McDonald's */}
      <div className="hidden md:flex md:w-80 md:flex-col border-r border-[#DA291C]/20 bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl shadow-xl">
        <div className="p-6 bg-gradient-to-br from-[#DA291C] to-[#8B0000]">
          <div className="flex items-center gap-3 mb-6">
            <div className="h-12 w-12 rounded-2xl bg-[#FFC72C] flex items-center justify-center shadow-lg">
              <Utensils className="h-6 w-6 text-[#DA291C]" />
            </div>
            <div>
              <h2 className="font-bold text-xl text-white">McDonald's</h2>
              <p className="text-xs text-yellow-200">Nutrition Assistant AI</p>
            </div>
          </div>
          
          <Button 
            onClick={handleNewChat}
            className="w-full justify-start gap-3 h-12 bg-[#FFC72C] hover:bg-[#FFD700] text-[#DA291C] font-bold shadow-lg hover:shadow-xl transition-all duration-200"
          >
            <Plus className="h-5 w-5" />
            <span>Chat Baru</span>
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-6">
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-bold text-[#DA291C] mb-3 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[#FFC72C]"></span>
                Fitur Unggulan
              </h3>
              <div className="space-y-2">
                {[
                  { icon: "🔥", text: "Informasi kalori lengkap", color: "from-red-500 to-orange-500" },
                  { icon: "🍬", text: "Kandungan gula & garam", color: "from-yellow-500 to-amber-500" },
                  { icon: "💪", text: "Rekomendasi menu sehat", color: "from-green-500 to-emerald-500" },
                  { icon: "⚖️", text: "Perbandingan nutrisi", color: "from-blue-500 to-cyan-500" }
                ].map((item, idx) => (
                  <div 
                    key={idx} 
                    className="flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-white to-red-50 dark:from-gray-800 dark:to-gray-700 border-2 border-transparent hover:border-[#FFC72C] transition-all duration-200 group"
                  >
                    <div className={`text-2xl flex items-center justify-center h-10 w-10 rounded-lg bg-gradient-to-br ${item.color} shadow-md group-hover:scale-110 transition-transform`}>
                      {item.icon}
                    </div>
                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">{item.text}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-6 p-4 rounded-xl bg-gradient-to-br from-[#DA291C] to-[#8B0000] text-white">
              <p className="text-xs leading-relaxed">
                💡 <strong>Tips:</strong> Tanyakan tentang menu favorit Anda untuk mendapatkan informasi nutrisi yang akurat dan rekomendasi yang sesuai dengan kebutuhan Anda!
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex flex-1 flex-col">
        {/* Header dengan McDonald's branding */}
        <div className="border-b-2 border-[#FFC72C] bg-gradient-to-r from-[#DA291C] to-[#8B0000] px-6 py-5 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" className="md:hidden text-white hover:bg-white/20">
                <Menu className="h-6 w-6" />
              </Button>
              <div>
                <h1 className="font-black text-2xl text-white drop-shadow-lg">
                  McDonald's Nutrition AI
                </h1>
                <p className="text-sm text-yellow-200 font-medium">
                  Powered by RAG Technology
                </p>
              </div>
            </div>
            <Button
              onClick={handleNewChat}
              className="gap-2 bg-[#FFC72C] hover:bg-[#FFD700] text-[#DA291C] font-bold border-2 border-white/50"
            >
              <Plus className="h-4 w-4" />
              <span className="hidden sm:inline">Chat Baru</span>
            </Button>
          </div>
        </div>

        {/* Messages area */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message, index) => (
              <ChatMessage key={index} role={message.role} content={message.content} />
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-center gap-3 px-6 py-4 rounded-2xl bg-white dark:bg-gray-800 shadow-lg border-2 border-[#FFC72C]">
                  <div className="flex gap-1.5">
                    <div className="h-3 w-3 bg-gradient-to-r from-[#DA291C] to-[#FFC72C] rounded-full animate-bounce"></div>
                    <div className="h-3 w-3 bg-gradient-to-r from-[#DA291C] to-[#FFC72C] rounded-full animate-bounce [animation-delay:0.2s]"></div>
                    <div className="h-3 w-3 bg-gradient-to-r from-[#DA291C] to-[#FFC72C] rounded-full animate-bounce [animation-delay:0.4s]"></div>
                  </div>
                  <span className="text-sm font-semibold text-[#DA291C]">AI sedang berpikir...</span>
                </div>
              </div>
            )}
          </div>
        </div>

        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  )
}
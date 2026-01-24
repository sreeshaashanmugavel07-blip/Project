import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'https://web-production-fa9c4.up.railway.app'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [initialized, setInitialized] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Initialize session by sending empty message to get greeting from backend
    if (!initialized && !sessionId) {
      setInitialized(true)
      const initSession = async () => {
        try {
          const response = await axios.post(`${API_URL}/chat`, {
            message: "",
            session_id: null
          }, {
            timeout: 5000 // 5 second timeout
          })
          if (response.data.session_id) {
            setSessionId(response.data.session_id)
          }
          if (response.data.reply) {
            setMessages([{ role: 'assistant', content: response.data.reply }])
          }
        } catch (error) {
          console.error('Error initializing session:', error)
          // Fallback greeting if backend fails
          setMessages([{ 
            role: 'assistant', 
            content: 'Hello! I am the Community Helpdesk Assistant. What type of issue are you reporting? Please choose from: Garbage, Water, Road, Streetlight, Drainage, or Others.' 
          }])
        }
      }
      initSession()
    }
  }, [initialized, sessionId])

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const requestBody = {
        message: userMessage
      }
      // Only include session_id if we have one
      if (sessionId) {
        requestBody.session_id = sessionId
      }
      
      const response = await axios.post(`${API_URL}/chat`, requestBody)

      // Update session ID if provided
      if (response.data.session_id) {
        setSessionId(response.data.session_id)
      }

      // Check if this is the success message
      const isSuccessMessage = response.data.reply.includes("successfully registered")
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.reply
      }])

      // If complaint was registered, show confirmation
      if (isSuccessMessage) {
        setTimeout(() => {
          setMessages(prev => [...prev, {
            role: 'system',
            content: 'Your complaint has been successfully registered.'
          }])
        }, 500)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm py-4 px-6">
        <h1 className="text-2xl font-bold text-indigo-600">
          🏛️ Community Helpdesk Assistant
        </h1>
        <p className="text-sm text-gray-600 mt-1">
          Report your community issues here
        </p>
      </header>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] md:max-w-[70%] rounded-2xl px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-indigo-600 text-white'
                  : msg.role === 'system'
                  ? 'bg-green-100 text-green-800 border-2 border-green-300'
                  : 'bg-white text-gray-800 shadow-md'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-2xl px-4 py-3 shadow-md">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={sendMessage} className="bg-white border-t border-gray-200 p-4">
        <div className="flex gap-2 max-w-4xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-indigo-600 text-white rounded-full font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  )
}

export default App

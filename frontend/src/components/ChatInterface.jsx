/**
 * CHAT INTERFACE COMPONENT (ChatInterface.jsx)
 * --------------------------------------------
 * This component handles user interactions with the AI.
 * 
 * How to explain it:
 * - It maintains an array of `messages` representing the chat history.
 * - When a user types a question and clicks "Send", it sends a POST request to our Backend (`/api/chat`).
 * - While waiting for the Groq AI to process the SQL, it displays a bouncing loading animation.
 * - It auto-scrolls to the bottom whenever a new message appears.
 */
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function ChatInterface() {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hi! I can help you analyze the Order to Cash process. Ask me anything about the data.", isBot: true }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef();

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { id: Date.now(), text: input, isBot: false };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await axios.post(`${API_BASE_URL}/api/chat`, { query: userMsg.text });
      const botMsg = { id: Date.now() + 1, text: res.data.response, isBot: true };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      const errorMsg = { id: Date.now() + 1, text: "Network error trying to reach the context graph API.", isBot: true };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white text-slate-800">
      {/* Header */}
      <div className="px-6 py-5 border-b border-slate-100">
        <h2 className="text-[14px] font-bold text-slate-900 border-b-2 border-slate-900 pb-1 inline-block">Analysis Assistant</h2>
        <p className="text-[12px] text-slate-500 mt-1">LLM powered query interface</p>
      </div>      

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6 text-[14px]" ref={scrollRef}>
        {messages.map((m, i) => (
          <div key={m.id} className={`flex flex-col ${m.isBot ? 'items-start' : 'items-end'} w-full`}>
            {/* Avatar Header */}
            <div className={`flex items-center gap-2 mb-2 ${m.isBot ? 'flex-row' : 'flex-row-reverse'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${m.isBot ? 'bg-slate-900 text-white' : 'bg-slate-200 text-slate-500'}`}>
                {m.isBot ? <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 2a10 10 0 1 0 10 10H12V2z"></path></svg> : <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>}
              </div>
              <div>
                <span className="font-bold text-slate-900 text-[13px]">{m.isBot ? 'Nexus AI' : 'You'}</span>
                {m.isBot && <span className="block text-[11px] text-slate-400 mt-[-2px]">Graph Agent</span>}
              </div>
            </div>
            
            {/* Bubble */}
            <div className={`px-4 py-3 rounded-2xl max-w-[90%] shadow-sm ${
              m.isBot ? 'bg-white border border-slate-100 text-slate-700 rounded-tl-none' : 'bg-slate-900 text-white rounded-tr-none'
            }`}>
              <p className="whitespace-pre-wrap leading-relaxed">{m.text}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex flex-col items-start w-full">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center shrink-0">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 2a10 10 0 1 0 10 10H12V2z"></path></svg>
              </div>
            </div>
            <div className="px-4 py-4 rounded-2xl bg-white border border-slate-100 rounded-tl-none flex gap-1.5 shadow-sm">
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></span>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-6 pt-0">
        <div className="bg-slate-50 border border-slate-200 rounded-2xl p-1 relative shadow-sm">
          <div className="absolute top-2 left-3 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Agent awaiting input</span>
          </div>
          <form onSubmit={handleSend} className="mt-6 flex bg-white rounded-xl overflow-hidden border border-slate-100 shadow-[inset_0_2px_4px_rgba(0,0,0,0.02)]">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Analyze anything..." 
              className="flex-1 bg-transparent px-4 py-3.5 text-[14px] text-slate-800 focus:outline-none placeholder-slate-400"
            />
            <div className="p-1.5 flex items-center justify-center">
              <button 
                type="submit" 
                disabled={!input.trim() || isLoading}
                className="bg-slate-500 hover:bg-slate-700 disabled:bg-slate-300 disabled:text-slate-100 transition-colors text-white text-[13px] font-semibold px-4 py-2 rounded-lg"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

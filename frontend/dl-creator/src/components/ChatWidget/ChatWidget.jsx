import React, { useState, useRef, useEffect } from 'react';
import './ChatWidget.css';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your driving license assistant. How can I help you today?",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [userId, setUserId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    // Get user ID from localStorage or generate one
    const storedUserId = localStorage.getItem('userId');
    if (storedUserId) {
      setUserId(storedUserId);
    } else {
      const newUserId = 'user_' + Date.now();
      localStorage.setItem('userId', newUserId);
      setUserId(newUserId);
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const sendMessageToRasa = async (message) => {
    try {
      const token = localStorage.getItem('jwt'); // Get JWT token
      // Use Vite's import.meta.env instead of process.env
      const rasaUrl = import.meta.env.VITE_RASA_URL || 'http://localhost:5005';
      
      const response = await fetch(`${rasaUrl}/webhooks/rest/webhook`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` // Include JWT in headers too
        },
        body: JSON.stringify({
          sender: userId || 'user',
          message: message,
          metadata: { token } // Token in metadata as requested
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error sending message to Rasa:', error);
      // Return a fallback response if Rasa is unavailable
      return [{
        recipient_id: userId,
        text: "I'm having trouble connecting right now. Please try again later or contact support."
      }];
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      // Send message to Rasa and get response
      const rasaResponse = await sendMessageToRasa(inputMessage);
      
      if (rasaResponse && rasaResponse.length > 0) {
        // Process Rasa responses
        rasaResponse.forEach((response, index) => {
          if (response.text) {
            setTimeout(() => {
              const botMessage = {
                id: Date.now() + index,
                text: response.text,
                sender: 'bot',
                timestamp: new Date()
              };
              setMessages(prev => [...prev, botMessage]);
            }, index * 500); // Stagger multiple responses
          }
        });
      } else {
        // Fallback response if no response from Rasa
        setTimeout(() => {
          const fallbackMessage = {
            id: Date.now(),
            text: "I understand you're asking about: '" + inputMessage + "'. I can help with license status, renewals, address updates, vehicle modifications, and general license information. What specific assistance do you need?",
            sender: 'bot',
            timestamp: new Date()
          };
          setMessages(prev => [...prev, fallbackMessage]);
        }, 1000);
      }
    } catch (error) {
      console.error('Error in chat:', error);
      // Error fallback message
      setTimeout(() => {
        const errorMessage = {
          id: Date.now(),
          text: "Sorry, I'm experiencing some technical difficulties. Please try again or contact support if the issue persists.",
          sender: 'bot',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }, 1000);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Floating Chat Button */}
      <button 
        className={`chat-widget-button ${isOpen ? 'hidden' : ''}`}
        onClick={toggleChat}
        aria-label="Open chat"
      >
        <div className="chat-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
          </svg>
        </div>
        <span className="chat-label">Need Help?</span>
      </button>

      {/* Chat Popup */}
      {isOpen && (
        <div className="chat-widget-popup">
          <div className="chat-header">
            <div className="chat-header-info">
              <div className="chat-avatar">🤖</div>
              <div className="chat-title">
                <h3>License Assistant</h3>
                <span className="chat-status">Online</span>
              </div>
            </div>
            <button 
              className="close-button"
              onClick={toggleChat}
              aria-label="Close chat"
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
              </svg>
            </button>
          </div>

          <div className="chat-messages">
            {messages.map((message) => (
              <div 
                key={message.id} 
                className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
              >
                <div className="message-content">
                  <p>{message.text}</p>
                  <span className="message-time">{formatTime(message.timestamp)}</span>
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="message bot-message">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input">
            <div className="input-container">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message here..."
                rows="1"
                className="message-input"
              />
              <button 
                className="send-button"
                onClick={handleSendMessage}
                disabled={!inputMessage.trim()}
                aria-label="Send message"
              >
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
              </button>
            </div>
            <div className="chat-suggestions">
              <button 
                className="suggestion-chip"
                onClick={() => setInputMessage("Check my license status")}
              >
                Check Status
              </button>
              <button 
                className="suggestion-chip"
                onClick={() => setInputMessage("I have not received my license")}
              >
                My license hasn't arrived Yet
              </button>
              <button 
                className="suggestion-chip"
                onClick={() => setInputMessage("Renew my license")}
              >
                Renew License
              </button>
              <button 
                className="suggestion-chip"
                onClick={() => setInputMessage("Update my address")}
              >
                Update Address
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatWidget;

"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { useChat } from "ai/react";
import Image from "next/image";
import { X, Send, Image as ImageIcon, Loader2 } from "lucide-react";
import clsx from "clsx";
import {
  initChatSession,
  getAuthInfo,
  getChatHistory,
} from "@/app/lib/actions/chat";

interface AIChatModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface MessageContent {
  type: "text" | "image_url";
  text?: string;
  image_url?: {
    url: string;
    detail?: "high" | "low";
  };
}

interface Message {
  id: string;
  role: "user" | "system" | "assistant" | "data";
  content: string | MessageContent | MessageContent[];
  createdAt?: string | Date;
}

type JSONValue =
  | string
  | number
  | boolean
  | { [x: string]: JSONValue }
  | Array<JSONValue>
  | null;

const suggestions = [
  "Recommend a recipe that works for me!",
  "What's my pregnancy status?",
];

function ThinkingIndicator() {
  return (
    <div className="flex items-center gap-2 text-gray-500 p-4">
      <Loader2 className="w-4 h-4 animate-spin" />
      <span>Thinking...</span>
    </div>
  );
}

const LLM_API_TOKEN = process.env.LLM_API_TOKEN;

interface HistoryMessage {
  id: string;
  role: "user" | "assistant";
  message: string | MessageContent[];
  created_at?: string;
}

interface HistoryResponse {
  history: HistoryMessage[];
}

export function AIChatModal({ isOpen, onClose }: AIChatModalProps) {
  const [authInfo, setAuthInfo] = useState<{
    accessToken: string;
    userId: string;
  } | null>(null);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    messages,
    input,
    handleInputChange,
    handleSubmit: handleChatSubmit,
    isLoading,
    setMessages,
  } = useChat({
    api: "/api/chat",
    body: {
      user_id: authInfo?.userId,
      session_id: sessionId,
      app_id: "emmabloom",
      temperature: 0.1,
      stream: true,
    },
    headers: {
      Authorization: `Bearer ${LLM_API_TOKEN}`,
    },
    experimental_prepareRequestBody: (options: { messages: Message[] }) => {
      const formattedMessages = options.messages.map((msg) => ({
        role: msg.role,
        content:
          typeof msg.content === "string"
            ? [{ type: "text" as const, text: msg.content }]
            : Array.isArray(msg.content)
            ? msg.content
            : [msg.content],
      }));

      const requestBody = {
        model: "gpt4o-1.5-turbo",
        user_id: authInfo?.userId || "",
        user_meta: {
          name: "user",
          email: "user@example.com",
          address: "123 Main St",
        },
        session_id: sessionId,
        app_id: "emmabloom",
        temperature: 0.1,
        stream: true,
        messages: formattedMessages,
      };

      console.log("Sending request:", requestBody);
      return requestBody as unknown as JSONValue;
    },
    initialMessages: [],
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // 当消息列表更新时滚动到底部
  useEffect(() => {
    if (messages.length > 0) {
      scrollToBottom();
    }
  }, [messages]);

  const fetchChatHistory = async (sid: string) => {
    try {
      const data = await getChatHistory(sid);

      // 获取历史消息数组
      const historyArray = (data as HistoryResponse)?.history || [];

      if (historyArray.length > 0) {
        const formattedMessages = historyArray.map((msg: HistoryMessage) => {
          let messageContent: string;

          // 处理消息内容
          if (typeof msg.message === "string") {
            messageContent = msg.message;
          } else if (Array.isArray(msg.message)) {
            // 确保每个内容项都被正确处理
            messageContent = msg.message
              .filter(
                (item) => item && typeof item === "object" && "type" in item
              )
              .map((item) => {
                if (item.type === "text" && item.text) {
                  return item.text;
                }
                return "";
              })
              .join("");
          } else {
            messageContent = "";
          }

          const formattedMessage = {
            id: msg.id || `msg_${Date.now()}_${Math.random()}`,
            role: msg.role,
            content: messageContent,
            createdAt: msg.created_at ? new Date(msg.created_at) : new Date(),
          };
          return formattedMessage;
        });
        setMessages(formattedMessages);
      }
    } catch (error) {
      console.error("Failed to fetch chat history:", error);
    }
  };

  const initSession = async () => {
    try {
      const data = await initChatSession();
      const newSessionId = data.session_id;
      setSessionId(newSessionId);
      await fetchChatHistory(newSessionId);
    } catch (error) {
      console.error("Failed to initialize chat session:", error);
    }
  };

  useEffect(() => {
    if (sessionId) {
      fetchChatHistory(sessionId);
    }
  }, [sessionId]);

  useEffect(() => {
    const fetchAuthInfo = async () => {
      try {
        const info = await getAuthInfo();
        if (info.accessToken) {
          setAuthInfo(info as { accessToken: string; userId: string });
        }
      } catch (error) {
        console.error("Failed to get auth info:", error);
      }
    };

    if (isOpen) {
      fetchAuthInfo();
    }
  }, [isOpen]);

  useEffect(() => {
    if (isOpen && !sessionId && authInfo) {
      initSession();
    }
  }, [isOpen, authInfo]);

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setIsUploading(true);
      setSelectedImage(file);

      // Convert file to base64
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = reader.result as string;
        setImageUrl(base64String);
        setIsUploading(false);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleInputChange({
      target: {
        value: suggestion,
      },
    } as React.ChangeEvent<HTMLInputElement>);

    const message = {
      role: "user",
      type: "text",
      content: [
        {
          type: "text",
          text: suggestion,
        },
      ],
    };
    handleChatSubmit(null as any, { messages: [message] });
  };

  const handleSubmit = useCallback(
    async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      if (!sessionId) return;

      const messageContent = [];

      if (input) {
        messageContent.push({
          type: "text",
          text: input,
        });
      }

      if (imageUrl) {
        messageContent.push({
          type: "image_url",
          image_url: {
            url: imageUrl,
            detail: "high",
          },
        });
      }

      const message = {
        role: "user",
        content: messageContent,
      };

      handleChatSubmit(e, { messages: [message] });

      // setSelectedImage(null);
      // setImageUrl(null);
    },
    [sessionId, input, imageUrl, handleChatSubmit]
  );

  // const handleRating = async (messageId: string, rating: number) => {
  //   try {
  //     await submitRating(messageId, rating);
  //   } catch (error) {
  //     console.error("Failed to submit rating:", error);
  //   }
  // };

  if (!isOpen || !authInfo) return null;

  return (
    <div
      className={clsx(
        "fixed inset-0 bg-black/50 z-50 flex items-center justify-center",
        isOpen ? "opacity-100" : "opacity-0 pointer-events-none"
      )}
    >
      <div className="bg-white w-full max-w-2xl h-[600px] rounded-lg flex flex-col">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">Chat with AI</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={clsx(
                "flex",
                message.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              <div
                className={clsx(
                  "max-w-[80%] rounded-lg p-4",
                  message.role === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-100"
                )}
              >
                {message.content}
              </div>
            </div>
          ))}
          {isLoading && <ThinkingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <div className="flex-1 flex">
              <input
                type="text"
                value={input}
                onChange={handleInputChange}
                placeholder="Type your message..."
                className="flex-1 px-4 py-2 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {/* <label
                htmlFor="image-upload"
                className="px-4 py-2 bg-gray-100 border-y border-r hover:bg-gray-200 cursor-pointer flex items-center"
              >
                <ImageIcon className="w-5 h-5" />
                <input
                  id="image-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
              </label> */}
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className={clsx(
                "px-4 py-2 bg-blue-500 text-white rounded-lg",
                "hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500",
                "disabled:bg-gray-300 disabled:cursor-not-allowed"
              )}
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

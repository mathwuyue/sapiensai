"use client";

import { useState, useCallback, useEffect } from "react";
import { useChat } from "ai/react";
import Image from "next/image";
import { X, Send, Image as ImageIcon, Loader2 } from "lucide-react";
import clsx from "clsx";
import {
  initChatSession,
  submitRating,
  getAuthInfo,
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

export function AIChatModal({ isOpen, onClose }: AIChatModalProps) {
  const [authInfo, setAuthInfo] = useState<{
    accessToken: string;
    userId: string;
  } | null>(null);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const initSession = async () => {
    try {
      const data = await initChatSession();
      setSessionId(data.session_id);
    } catch (error) {
      console.error("Failed to initialize chat session:", error);
    }
  };

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
      app_id: "wz0001",
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
    onResponse: async (response: Response) => {
      console.log("Response received:", response);
      const reader = response.body?.getReader();
      let currentMessageId: string | null = null;
      let accumulatedContent = "";
      const uniqueMessageId = `msg_${Date.now()}_${Math.random()
        .toString(36)
        .substr(2, 9)}`;

      if (reader) {
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = new TextDecoder().decode(value);
            console.log("Chunk received:", chunk);

            const lines = chunk.split("\n");
            for (const line of lines) {
              if (line.startsWith("data: ")) {
                const jsonStr = line.slice(6).trim();
                if (!jsonStr || jsonStr === "[DONE]") continue;

                try {
                  const data = JSON.parse(jsonStr);
                  console.log("Parsed data:", data);

                  // 只处理增量更新
                  if (data.choices?.[0]?.delta?.content) {
                    const deltaContent = data.choices[0].delta.content;

                    if (!currentMessageId) {
                      currentMessageId = uniqueMessageId;
                      accumulatedContent = deltaContent;
                    } else {
                      accumulatedContent += deltaContent;
                    }

                    setMessages((currentMessages) => {
                      const newMessage = {
                        id: currentMessageId!,
                        role: "assistant" as const,
                        content: accumulatedContent,
                        createdAt: new Date(data.created * 1000),
                      };

                      // 检查是否已经有这个消息ID的消息
                      const existingMessageIndex = currentMessages.findIndex(
                        (msg) => msg.id === currentMessageId
                      );

                      if (existingMessageIndex >= 0) {
                        // 更新现有消息的内容
                        const updatedMessages = [...currentMessages];
                        updatedMessages[existingMessageIndex] = newMessage;
                        return updatedMessages;
                      } else {
                        // 添加新消息
                        return [...currentMessages, newMessage];
                      }
                    });
                  }
                } catch (parseError) {
                  console.error("JSON parse error:", parseError);
                }
              }
            }
          }
        } catch (e) {
          console.error("Error reading response:", e);
        } finally {
          reader.releaseLock();
        }
      }
    },
    onFinish: (message) => {
      console.log("Message finished:", message);
    },
    onError: (error) => {
      console.error("Chat error:", error);
    },
    initialMessages: [
      {
        id: "welcome",
        role: "assistant",
        content: "How can I help you?",
        createdAt: new Date(),
      },
    ],
  });

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

      setSelectedImage(null);
      setImageUrl(null);
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-white rounded-2xl w-full max-w-lg h-[600px] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">AI Assistant</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-full"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Chat content */}
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
        </div>

        {/* Suggestions */}
        {messages.length === 1 && (
          <div className="px-4 space-y-2">
            {suggestions.map((suggestion) => (
              <button
                key={suggestion}
                className="w-full text-left p-3 rounded-lg border hover:bg-gray-50 transition-colors"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}

        {/* Selected Image Preview */}
        {selectedImage && (
          <div className="px-4 py-2 border-t">
            <div className="relative w-20 h-20">
              <Image
                src={URL.createObjectURL(selectedImage)}
                alt="Selected"
                fill
                className="object-cover rounded-lg"
              />
              <button
                onClick={() => {
                  setSelectedImage(null);
                  setImageUrl(null);
                }}
                className="absolute -top-2 -right-2 bg-white rounded-full p-1 shadow-md hover:bg-gray-100"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Input area */}
        <form
          onSubmit={handleSubmit}
          className="p-4 border-t flex items-end gap-2"
        >
          <label className="cursor-pointer text-gray-500 hover:text-gray-700">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
            <ImageIcon className="w-6 h-6" />
          </label>
          <input
            value={input}
            onChange={handleInputChange}
            placeholder="Type your message..."
            className="flex-1 resize-none rounded-xl border p-2 focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <button
            type="submit"
            disabled={isLoading || isUploading || !sessionId}
            className="bg-primary text-white p-2 rounded-xl hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading || isUploading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

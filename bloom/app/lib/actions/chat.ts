"use server";

import { auth } from "@/auth";
import WebSocket from 'ws';

const BASE_URL = process.env.NEXT_PUBLIC_LLM_API_URL;
const WS_URL = process.env.NEXT_PUBLIC_LLM_WS_URL;
const LLM_API_TOKEN = process.env.LLM_API_TOKEN;

export async function initChatSession() {
  try {
    const session = await auth();
    if (!session?.user) throw new Error("Unauthorized");
    const response = await fetch(`${BASE_URL}/v1/chat/session`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${LLM_API_TOKEN}`,
      },
      body: JSON.stringify({
        user_id: session.user.id,
      }),
    });
    
    if (!response.ok) {
      console.error("Failed to create session:", response);
      throw new Error("Failed to create session");
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Failed to initialize chat session:", error);
    throw error;
  }
}

export async function chat(req: Request) {
  try {
    const session = await auth();
    if (!session?.user) {
      return new Response('Unauthorized', { status: 401 });
    }

    const body = await req.json();

    const stream = new ReadableStream({
      async start(controller) {
        const ws = new WebSocket(`${WS_URL}/v1/chat/completions`);

        ws.onopen = () => {
          console.log('WebSocket connected');
          console.log("body", body);
          ws.send(JSON.stringify({
            ...body,
            user_id: session.user.id,
          }));
        };

        ws.onmessage = (event) => {
          controller.enqueue(event.data);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          controller.error(error);
        };

        ws.onclose = () => {
          controller.close();
        };
      }
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });

  } catch (error) {
    console.error('Chat API error:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
} 

export async function submitRating(messageId: string, rating: number) {
  try {
    const session = await auth();
    if (!session?.user) throw new Error("Unauthorized");

    const response = await fetch(`${BASE_URL}/v1/chat/rating`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session.accessToken}`,
      },
      body: JSON.stringify({
        id: messageId,
        rating: [{ index: 0, index_rating: rating }],
      }),
    });

    if (!response.ok) throw new Error("Failed to submit rating");
    return await response.json();
  } catch (error) {
    console.error("Failed to submit rating:", error);
    throw error;
  }
}

export async function getAuthInfo() {
  const session = await auth();
  if (!session?.user) throw new Error("Unauthorized");
  
  return {
    accessToken: session.accessToken,
    userId: session.user.id
  };
}

export async function getChatHistory(sessionId: string) {
  const session = await auth();
  if (!session?.user) {
    throw new Error("Unauthorized");
  }

  const queryParams = new URLSearchParams({
    user_id: session.user.id,
    session_id: sessionId,
  });

  const response = await fetch(`${BASE_URL}/v1/chat/history?${queryParams}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${LLM_API_TOKEN}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch chat history");
  }

  return response.json();
}
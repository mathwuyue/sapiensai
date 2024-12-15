import { auth } from "@/auth";
import WebSocket from 'ws';

const WS_URL = process.env.NEXT_PUBLIC_LLM_API_URL?.replace('http', 'ws') || '';

export async function POST(req: Request) {
  try {
    const session = await auth();
    if (!session?.user) {
      return new Response('Unauthorized', { status: 401 });
    }

    const body = await req.json();
    console.log('Request body:', body);

    const stream = new ReadableStream({
      async start(controller) {
        const ws = new WebSocket(`${WS_URL}/v1/chat/completions`);
        let accumulatedContent = '';
        let currentMessageId: string | null = null;

        ws.onopen = () => {
          console.log('WebSocket connected');
          const requestData = {
            ...body,
            user_id: session.user.id,
          };
          console.log('Sending to WebSocket:', requestData);
          ws.send(JSON.stringify(requestData));
        };

        ws.onmessage = (event) => {
          const data = typeof event.data === 'string' 
            ? JSON.parse(event.data)
            : JSON.parse(new TextDecoder().decode(event.data as ArrayBuffer));
          
          console.log('WebSocket received data:', data);

          // 处理增量更新
          if (data.choices?.[0]?.delta?.content) {
            const deltaContent = data.choices[0].delta.content;

            if (!currentMessageId) {
              currentMessageId = data.id;
              accumulatedContent = deltaContent;
            } else {
              accumulatedContent += deltaContent;
            }

            const deltaMessage = {
              id: currentMessageId,
              role: 'assistant',
              content: accumulatedContent,
              createdAt: new Date(data.created * 1000).toISOString()
            };

            const sseData = `data: ${JSON.stringify(deltaMessage)}\n\n`;
            controller.enqueue(new TextEncoder().encode(sseData));
          }
          // 处理完整消息
          else if (data.choices?.[0]?.message?.content) {
            const content = data.choices[0].message.content;
            
            const message = {
              id: data.id,
              role: 'assistant',
              content: content,
              createdAt: new Date(data.created * 1000).toISOString()
            };

            const sseData = `data: ${JSON.stringify(message)}\n\n`;
            controller.enqueue(new TextEncoder().encode(sseData));
          }

          // 检查是否是结束消息
          if (data.choices?.[0]?.finish_reason === 'stop') {
            console.log('Received stop signal');
            // 如果有累积的内容，发送最终消息
            if (accumulatedContent && currentMessageId) {
              const finalMessage = {
                id: currentMessageId,
                role: 'assistant',
                content: accumulatedContent,
                createdAt: new Date(data.created * 1000).toISOString()
              };
              const finalSSE = `data: ${JSON.stringify(finalMessage)}\n\n`;
              console.log('Sending final message:', finalMessage);
              controller.enqueue(new TextEncoder().encode(finalSSE));
            }
            controller.close();
            return;
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          controller.error(error);
        };

        ws.onclose = (e) => {
          console.log('WebSocket closed with code:', e.code, 'reason:', e.reason);
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
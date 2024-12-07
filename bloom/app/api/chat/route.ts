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

    const stream = new ReadableStream({
      async start(controller) {
        const ws = new WebSocket(`${WS_URL}/v1/chat/completions`);
        let accumulatedContent = '';

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

          // 检查是否是结束消息
          if (data.choices?.[0]?.finish_reason === 'stop') {
            console.log('Received stop signal');
            // 发送累积的内容
            if (accumulatedContent) {
              const finalMessage = {
                id: data.id,
                role: 'assistant',
                content: accumulatedContent,
                createdAt: new Date(data.created * 1000).toISOString()
              };
              const finalSSE = `data: ${JSON.stringify(finalMessage)}\n\n`;
              controller.enqueue(new TextEncoder().encode(finalSSE));
            }
            controller.close();
            return;
          }

          // 提取实际的消息内容
          if (data.choices?.[0]?.delta?.content) {
            const content = data.choices[0].delta.content;
            accumulatedContent += content;
            
            // 直接发送增量更新
            const deltaMessage = {
              id: data.id,
              choices: [{
                delta: {
                  content: content
                },
                finish_reason: null,
                index: 0
              }],
              created: Math.floor(Date.now() / 1000)
            };

            const sseData = `data: ${JSON.stringify(deltaMessage)}\n\n`;
            controller.enqueue(new TextEncoder().encode(sseData));
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          controller.error(error);
        };

        ws.onclose = (e) => {
          console.log('WebSocket closed', e);
          controller.close();
          // return new Response('Internal Server Error', { status: 500 });
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
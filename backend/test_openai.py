import asyncio
from openai import AsyncOpenAI

async def test():
  
    try:
        response = await client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': 'Hi'}],
            max_tokens=5
        )
        print('SUCCESS:', response.choices[0].message.content)
    except Exception as e:
        print('ERROR:', type(e).__name__, str(e)[:200])

if __name__ == '__main__':
    asyncio.run(test())

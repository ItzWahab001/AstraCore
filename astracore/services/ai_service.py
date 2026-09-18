import aiohttp
from config import settings
async def ask(prompt,system='You are AstraCore, a helpful Discord assistant.'):
    if not settings.ai_api_key or not settings.ai_base_url or not settings.ai_model:
        raise RuntimeError('AI provider is not configured. Set AI_API_KEY, AI_BASE_URL and AI_MODEL.')
    url=settings.ai_base_url.rstrip('/')+'/chat/completions'
    payload={'model':settings.ai_model,'messages':[{'role':'system','content':system},{'role':'user','content':prompt}]}
    timeout=aiohttp.ClientTimeout(total=45)
    async with aiohttp.ClientSession(timeout=timeout) as s:
        for attempt in range(2):
            try:
                async with s.post(url,json=payload,headers={'Authorization':f'Bearer {settings.ai_api_key}'}) as r:
                    if r.status in (429,500,502,503,504) and attempt==0: continue
                    r.raise_for_status(); data=await r.json(); return data['choices'][0]['message']['content']
            except (aiohttp.ClientError,KeyError,IndexError):
                if attempt: raise
    raise RuntimeError('AI provider did not return a usable response.')

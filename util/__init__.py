import asyncio
def run_async_function(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(coro)
    loop.close()
    return result




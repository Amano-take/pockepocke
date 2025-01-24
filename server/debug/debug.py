import asyncio
import time


async def awaitable():
    while True:
        print("this is not mainloop")
        await asyncio.sleep(1)

# not awaitable but need to call awaitable function
def not_awaitable(loop):
    def _not_awaitable():
        asyncio.run_coroutine_threadsafe(
            awaitable(),
            loop
        )
    return _not_awaitable
    

    

async def main():
    # main loop
    # make another thread to run not_awaitable function
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, not_awaitable(loop))
    while True:
        print("this is mainloop")
        await asyncio.sleep(1)
    
    
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    # set main
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()
    
import asyncio

import uvicorn
from game_server import app

if __name__ == "__main__":
    # Initialize event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Run server
    uvicorn.run(
        "server.game_server:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        reload=False,  # Disable auto-reload for Windows compatibility
    )

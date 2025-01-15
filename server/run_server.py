import uvicorn
from game_server import app

if __name__ == "__main__":
    print("ポケモンカードゲーム マルチプレイヤーサーバーを起動します...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

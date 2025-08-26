import asyncio
import websockets
import os

# 接続している全てのクライアントを保持するセット
connected_clients = set()

async def handler(websocket, path):
    print(f"新しい接続がありました。Path: '{path}'")
    
    connected_clients.add(websocket)
    print(f"クライアント接続成功。現在 {len(connected_clients)} 人。")

    try:
        async for message in websocket:
            print(f"受信: {message}")
            
            # 全てのクライアントにメッセージをブロードキャスト
            for client in connected_clients:
                if client.open:
                    await client.send(message)
                
    finally:
        connected_clients.remove(websocket)
        print(f"クライアント切断。現在 {len(connected_clients)} 人。")

async def main():
    port = int(os.environ.get("PORT", 10000)) # Renderのデフォルトポート10000を明記
    
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
    # ★ これが最後の魔法です！
    # ★ origins=None を追加することで、どのオリジンからの接続も受け入れる
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
    async with websockets.serve(handler, "0.0.0.0", port, origins=None):
        print(f"サーバーがポート {port} で起動しました。（全てのオリジンを許可）")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

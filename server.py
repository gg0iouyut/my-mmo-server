import asyncio
import websockets
import os

# 接続している全てのクライアントを保持するセット
connected_clients = set()

async def handler(websocket, path):
    # ★重要なデバッグ情報：どのパスで接続しようとしているかを表示★
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
    port = int(os.environ.get("PORT", 8080))
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"サーバーがポート {port} で起動しました。")
        await asyncio.Future()  # サーバーを永久に実行

if __name__ == "__main__":
    asyncio.run(main())

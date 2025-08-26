import asyncio
import websockets
import json
import os

# 接続している全てのクライアントを保持するセット
connected_clients = set()

async def handler(websocket, path):
    # 新しいクライアントが接続したら、セットに追加
    connected_clients.add(websocket)
    print(f"新しいクライアントが接続しました。現在 {len(connected_clients)} 人。")

    try:
        # クライアントからメッセージを待ち受けるループ
        async for message in websocket:
            print(f"受信したメッセージ: {message}")
            
            # 全てのクライアントにメッセージをブロードキャスト（一斉送信）
            # （メッセージを送った本人にも送り返すシンプルな形）
            for client in connected_clients:
                await client.send(message)
                
    finally:
        # クライアントの接続が切れたら、セットから削除
        connected_clients.remove(websocket)
        print(f"クライアントの接続が切れました。現在 {len(connected_clients)} 人。")

async def main():
    # Renderが指定するポート番号を取得する。ローカルテスト用には8080をデフォルトに。
    port = int(os.environ.get("PORT", 8080))
    # '0.0.0.0' は、どのネットワークからでも接続を受け付けるという意味
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"サーバーがポート {port} で起動しました。")
        await asyncio.Future()  # サーバーを永久に実行

if __name__ == "__main__":
    asyncio.run(main())

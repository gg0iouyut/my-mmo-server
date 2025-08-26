import asyncio
import websockets
import json
import os
from websockets.server import serve

# 接続している全てのクライアントを保持するセット
connected_clients = set()

async def ws_handler(websocket, path):
    # 新しいクライアントが接続したら、セットに追加
    connected_clients.add(websocket)
    print(f"新しいクライアントが接続しました。現在 {len(connected_clients)} 人。")

    try:
        # クライアントからメッセージを待ち受けるループ
        async for message in websocket:
            print(f"受信したメッセージ: {message}")
            
            # 全てのクライアントにメッセージをブロードキャスト
            for client in connected_clients:
                # エラーハンドリングを追加
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    # 送信に失敗したクライアントは既に切断されているので無視
                    pass
                
    finally:
        # クライアントの接続が切れたら、セットから削除
        connected_clients.remove(websocket)
        print(f"クライアントの接続が切れました。現在 {len(connected_clients)} 人。")

# ★ここからが新しい部分：HTTPリクエストを処理する部分★
async def http_handler(path, request_headers):
    # もし、WebSocketへのアップグレードリクエストなら、何もしない（ws_handlerに任せる）
    if "Upgrade" in request_headers and request_headers["Upgrade"].lower() == "websocket":
        return

    # それ以外のHTTPリクエスト（Renderのヘルスチェックなど）が来た場合
    # 「私は元気ですよ」という意味で、ステータスコード200 OKを返す
    return (200, {"Content-Type": "text/plain"}, b"This is a WebSocket server.")

async def main():
    port = int(os.environ.get("PORT", 8080))
    # ★ここを変更：WebSocketハンドラとHTTPハンドラの両方を設定★
    async with serve(ws_handler, "0.0.0.0", port, process_request=http_handler):
        print(f"サーバーがポート {port} で起動しました。")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

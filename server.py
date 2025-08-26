import asyncio
import websockets
import os
from websockets.server import serve

# 接続している全てのクライアントを保持するセット
connected_clients = set()

# WebSocketのメインハンドラ
async def ws_handler(websocket, path):
    # ★デバッグ用：接続してきたパスを表示する★
    print(f"新しいWebSocket接続試行 on path: '{path}'")
    
    connected_clients.add(websocket)
    print(f"クライアント接続成功。現在 {len(connected_clients)} 人。")

    try:
        async for message in websocket:
            print(f"受信: {message}")
            
            # ブロードキャスト処理
            # asyncio.gatherを使うと、複数の送信処理を効率的に並行実行できる
            tasks = [client.send(message) for client in connected_clients if client.open]
            await asyncio.gather(*tasks, return_exceptions=True) # return_exceptions=Trueでエラーを無視
                
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"接続が正常にクローズされました: {e}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
    finally:
        connected_clients.remove(websocket)
        print(f"クライアント切断。現在 {len(connected_clients)} 人。")

# HTTPリクエストのハンドラ
async def http_handler(path, request_headers):
    if "Upgrade" in request_headers and request_headers["Upgrade"].lower() == "websocket":
        return None  # WebSocketへのアップグレードリクエストなら、ws_handlerに処理を渡す

    # ヘルスチェックなど、それ以外のHTTPリクエストへの応答
    print(f"HTTPリクエスト受信 on path: '{path}'")
    return (200, {"Content-Type": "text/plain"}, b"WebSocket server is running.")

async def main():
    port = int(os.environ.get("PORT", 8080))
    # ★重要：websockets.serveからserveに変更し、process_requestを使う★
    async with serve(ws_handler, "0.0.0.0", port, process_request=http_handler):
        print(f"サーバーがポート {port} で起動しました。")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

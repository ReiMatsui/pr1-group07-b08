import qrcode

SERVER_IP = "172.20.10.7"         
URL = f"http://{SERVER_IP}:8000/qr/trigger?from=qr"

img = qrcode.make(URL)
img.save("fastapi_trigger_qr.png")  # カレントディレクトリに出力
print("QR 画像を生成しました:", URL)
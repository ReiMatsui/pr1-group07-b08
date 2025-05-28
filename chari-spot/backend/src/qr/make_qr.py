import qrcode

SERVER_IP = "172.20.10.7"
SPOT_ID = 1
SLOT_ID = 3

URL = f"http://{SERVER_IP}:8000/qr/trigger?from=qr&spot_id={SPOT_ID}&slot_id={SLOT_ID}"

img = qrcode.make(URL)
img.save("fastapi_trigger_qr.png")
print("QR 画像を生成しました:", URL)
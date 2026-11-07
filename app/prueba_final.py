import requests


TOKEN = "EAAP1RCHVIkMBS33U4SZAvvtBSD6pyIMb5pVxVb0haUnaFyJGBm9DBo96Wp3lmYI8WQ6Ne9pFEktNZCD8C3dmFpPZB2JvYZCZCg3WMXCVSBkGP05i9fRlDZCrmZAzAf2mys851uuEBTcSZCmmW5mGqkrr0Lhq791QfvBFuIhADiyCT1vF94LcqyZCZBc7yl55zJZAxNuFgZDZD"
IG_ID = "17841406744590581"

print(f" Probando conexión con Instagram ID: {IG_ID}")
print(f"Token (primeros 30 chars): {TOKEN[:30]}...")

url = f"https://graph.facebook.com/v21.0/{IG_ID}"
params = {
    "fields": "username,biography,followers_count,media_count",
    "access_token": TOKEN
}

response = requests.get(url, params=params)
data = response.json()

print("\nResultado:")
print(data)

if "username" in data:
    print(f"\n ¡FUNCIONA PERFECTAMENTE!")
    print(f" Usuario: {data['username']}")
else:
    print("\n Error:")
    print(data)
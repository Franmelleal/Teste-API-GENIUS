# app.py
import os
import uuid
import json
from flask import Flask, request, jsonify
import requests
import boto3
import redis
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

GENIUS_TOKEN = os.getenv("GENIUS_TOKEN")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Configurar Flask
app = Flask(__name__)

# Conectar DynamoDB
dynamodb = boto3.resource(
    "dynamodb",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)
table_name = "GeniusTransactions"
table = dynamodb.Table(table_name)

# Conectar Redis
cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Função para buscar músicas do Genius
def buscar_musicas(artista):
    headers = {"Authorization": f"Bearer {GENIUS_TOKEN}"}
    search_url = f"https://api.genius.com/search?q={artista}"
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        return None
    data = response.json()
    hits = data["response"]["hits"]
    # Pegar 10 músicas mais populares
    musicas = []
    for hit in hits[:10]:
        song = hit["result"]
        musicas.append({
            "id": song["id"],
            "title": song["title"],
            "url": song["url"],
            "artist": song["primary_artist"]["name"]
        })
    return musicas

# Rota principal
@app.route("/musicas", methods=["GET"])
def listar_musicas():
    artista = request.args.get("artista")
    cache_option = request.args.get("cache", "true").lower() != "false"

    if not artista:
        return jsonify({"error": "Informe o parâmetro 'artista'"}), 400

    transaction_id = str(uuid.uuid4())

    # Verificar cache Redis
    cached_data = cache.get(artista)
    if cached_data and cache_option:
        return jsonify({"from_cache": True, "musicas": json.loads(cached_data)})

    # Buscar músicas no Genius
    musicas = buscar_musicas(artista)
    if musicas is None:
        return jsonify({"error": "Erro ao consultar Genius"}), 500

    # Salvar no Redis se cache=True
    if cache_option:
        cache.setex(artista, 7*24*3600, json.dumps(musicas))  # 7 dias

    # Salvar no DynamoDB
    table.put_item(
        Item={
            "transaction_id": transaction_id,
            "artist": artista,
            "musicas": musicas
        }
    )

    return jsonify({"transaction_id": transaction_id, "musicas": musicas})

if __name__ == "__main__":
    app.run(debug=True)

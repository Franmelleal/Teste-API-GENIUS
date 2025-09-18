# Teste Genius API

Este projeto é um teste de integração com a API do Genius, utilizando Python e AWS DynamoDB para armazenar resultados de buscas de músicas.

>**Aviso:** O arquivo `Dados Token Teste Genius.env` contém tokens e chaves apenas para teste. Não use esses dados em produção.

## Estrutura do projeto

- `app.py` - Código principal que realiza buscas na API Genius e salva os resultados no DynamoDB.
- `Dados Token Teste Genius.env` - Arquivo de ambiente com tokens e chaves para teste.
- `venv/` - Ambiente virtual Python (não é necessário enviar, pode ser recriado com `python -m venv venv`).

## Instalação

1. Clone o repositório:

```bash
git clone https://github.com/Franmelleal/Teste-API-GENIUS.git
cd Teste-API-GENIUS

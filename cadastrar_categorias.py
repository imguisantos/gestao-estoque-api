"""
Script para cadastrar varias categorias de uma vez na API de Gestao de Estoque.

Como usar:
1. Preencha EMAIL e SENHA abaixo com um usuario ADMIN
2. Ajuste a lista CATEGORIAS se quiser outros nomes/descricoes
3. Com a API rodando (uvicorn) e o venv ativado, rode:
   python cadastrar_categorias.py
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

# Troque pelas credenciais do seu usuario admin
EMAIL = "user@teste.com"
SENHA = "123456"

CATEGORIAS = [
    {"nome": "Notebooks", "descricao": "Computadores portáteis para uso doméstico, profissional e gamer."},
    {"nome": "Monitores", "descricao": "Monitores LED, IPS, OLED e UltraWide para produtividade e jogos."},
    {"nome": "Placas de Vídeo", "descricao": "GPUs dedicadas para jogos, edição de vídeo, modelagem 3D e inteligência artificial."},
    {"nome": "Processadores", "descricao": "CPUs Intel e AMD para computadores de diferentes níveis de desempenho."},
    {"nome": "Memórias RAM", "descricao": "Módulos de memória DDR4 e DDR5 para desktops e notebooks."},
    {"nome": "SSDs", "descricao": "Unidades de armazenamento SATA e NVMe de alta velocidade."},
]


def login() -> str:
    resposta = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "senha": SENHA})
    resposta.raise_for_status()
    return resposta.json()["access_token"]


def criar_categorias(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    for categoria in CATEGORIAS:
        resposta = requests.post(f"{BASE_URL}/categorias/", json=categoria, headers=headers)
        if resposta.status_code == 201:
            print(f"OK   - {categoria['nome']} (id {resposta.json()['id']})")
        elif resposta.status_code == 400:
            print(f"SKIP - {categoria['nome']} (já existe)")
        else:
            print(f"ERRO - {categoria['nome']}: {resposta.status_code} - {resposta.text}")


if __name__ == "__main__":
    print("Fazendo login...")
    token = login()
    print("Login ok. Cadastrando categorias...\n")
    criar_categorias(token)
    print("\nConcluído.")

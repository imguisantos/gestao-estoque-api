"""
Script para popular a API com um catalogo realista de fornecedores e
produtos de informatica, vinculados as categorias ja existentes.

Como usar:
1. Preencha EMAIL e SENHA com um usuario ADMIN
2. Com a API rodando (uvicorn) e o venv ativado, rode:
   python seed_fornecedores_e_produtos.py

E' seguro rodar mais de uma vez: fornecedores e produtos ja existentes
(mesmo nome) sao pulados, nao duplicados.
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

EMAIL = "user@teste.com"
SENHA = "123456"

CATEGORIAS = [
    {"nome": "Notebooks", "descricao": "Computadores portáteis para uso doméstico, profissional e gamer."},
    {"nome": "Monitores", "descricao": "Monitores LED, IPS, OLED e UltraWide para produtividade e jogos."},
    {"nome": "Placas de Vídeo", "descricao": "GPUs dedicadas para jogos, edição de vídeo, modelagem 3D e inteligência artificial."},
    {"nome": "Processadores", "descricao": "CPUs Intel e AMD para computadores de diferentes níveis de desempenho."},
    {"nome": "Memórias RAM", "descricao": "Módulos de memória DDR4 e DDR5 para desktops e notebooks."},
    {"nome": "SSDs", "descricao": "Unidades de armazenamento SATA e NVMe de alta velocidade."},
    {"nome": "Teclados", "descricao": "Teclados mecânicos e de membrana, com e sem fio."},
    {"nome": "Mouses", "descricao": "Mouses ópticos e a laser, gamer e de escritório."},
]

FORNECEDORES = [
    {"nome": "Kingston Technology", "cnpj": "12.345.678/0001-99", "email": "comercial@kingston.com", "telefone": "(11) 4000-1234"},
    {"nome": "Samsung Eletrônica", "cnpj": "23.456.789/0001-11", "email": "b2b@samsung.com.br", "telefone": "(11) 4000-2345"},
    {"nome": "Corsair Memory", "cnpj": "34.567.890/0001-22", "email": "sales@corsair.com", "telefone": "(11) 4000-3456"},
    {"nome": "Logitech do Brasil", "cnpj": "45.678.901/0001-33", "email": "comercial@logitech.com.br", "telefone": "(11) 4000-4567"},
    {"nome": "Intel Semicondutores", "cnpj": "56.789.012/0001-44", "email": "vendas@intel.com.br", "telefone": "(11) 4000-5678"},
    {"nome": "Advanced Micro Devices (AMD)", "cnpj": "67.890.123/0001-55", "email": "sales@amd.com", "telefone": "(11) 4000-6789"},
    {"nome": "NVIDIA Brasil", "cnpj": "78.901.234/0001-66", "email": "comercial@nvidia.com", "telefone": "(11) 4000-7890"},
    {"nome": "Seagate Technology", "cnpj": "89.012.345/0001-77", "email": "vendas@seagate.com", "telefone": "(11) 4000-8901"},
    {"nome": "Western Digital", "cnpj": "90.123.456/0001-88", "email": "comercial@wd.com", "telefone": "(11) 4000-9012"},
    {"nome": "Cooler Master Brasil", "cnpj": "01.234.567/0001-10", "email": "sales@coolermaster.com", "telefone": "(11) 4001-0123"},
    {"nome": "ASUSTeK Computer", "cnpj": "11.222.333/0001-44", "email": "comercial@asus.com.br", "telefone": "(11) 4001-1234"},
    {"nome": "Gigabyte Technology", "cnpj": "22.333.444/0001-55", "email": "vendas@gigabyte.com", "telefone": "(11) 4001-2345"},
    {"nome": "Micro-Star International (MSI)", "cnpj": "33.444.555/0001-66", "email": "comercial@msi.com", "telefone": "(11) 4001-3456"},
    {"nome": "Razer Inc.", "cnpj": "44.555.666/0001-77", "email": "sales@razer.com", "telefone": "(11) 4001-4567"},
    {"nome": "HyperX (HP Inc.)", "cnpj": "55.666.777/0001-88", "email": "comercial@hyperx.com", "telefone": "(11) 4001-5678"},
    {"nome": "Redragon Gaming", "cnpj": "66.777.888/0001-99", "email": "vendas@redragon.com.br", "telefone": "(11) 4001-6789"},
    {"nome": "Multilaser Industrial", "cnpj": "77.888.999/0001-10", "email": "comercial@multilaser.com.br", "telefone": "(11) 4001-7890"},
    {"nome": "Positivo Tecnologia", "cnpj": "88.999.000/0001-21", "email": "vendas@positivo.com.br", "telefone": "(11) 4001-8901"},
    {"nome": "TP-Link do Brasil", "cnpj": "99.000.111/0001-32", "email": "comercial@tp-link.com.br", "telefone": "(11) 4001-9012"},
    {"nome": "Lenovo Tecnologia", "cnpj": "10.111.222/0001-43", "email": "b2b@lenovo.com", "telefone": "(11) 4002-0123"},
]

# categoria e fornecedor referenciam os "nome" das listas acima
PRODUTOS = [
    # Notebooks
    {"nome": "Lenovo IdeaPad 3i", "categoria": "Notebooks", "fornecedor": "Lenovo Tecnologia", "preco": 3299.00, "estoque_inicial": 15, "estoque_minimo": 5},
    {"nome": "ASUS Vivobook 15", "categoria": "Notebooks", "fornecedor": "ASUSTeK Computer", "preco": 3799.90, "estoque_inicial": 12, "estoque_minimo": 5},
    {"nome": "Positivo Motion C4128F", "categoria": "Notebooks", "fornecedor": "Positivo Tecnologia", "preco": 2199.00, "estoque_inicial": 20, "estoque_minimo": 8},
    # Monitores
    {"nome": "Samsung Odyssey G5 27\"", "categoria": "Monitores", "fornecedor": "Samsung Eletrônica", "preco": 1899.00, "estoque_inicial": 18, "estoque_minimo": 6},
    {"nome": "LG UltraWide 29\"", "categoria": "Monitores", "fornecedor": "Samsung Eletrônica", "preco": 1599.00, "estoque_inicial": 10, "estoque_minimo": 4},
    {"nome": "ASUS TUF Gaming 24\"", "categoria": "Monitores", "fornecedor": "ASUSTeK Computer", "preco": 1299.00, "estoque_inicial": 22, "estoque_minimo": 8},
    # Placas de Vídeo
    {"nome": "NVIDIA GeForce RTX 4060", "categoria": "Placas de Vídeo", "fornecedor": "NVIDIA Brasil", "preco": 2599.00, "estoque_inicial": 8, "estoque_minimo": 3},
    {"nome": "AMD Radeon RX 7600", "categoria": "Placas de Vídeo", "fornecedor": "Advanced Micro Devices (AMD)", "preco": 2199.00, "estoque_inicial": 6, "estoque_minimo": 3},
    {"nome": "Gigabyte GeForce RTX 4070", "categoria": "Placas de Vídeo", "fornecedor": "Gigabyte Technology", "preco": 4299.00, "estoque_inicial": 5, "estoque_minimo": 2},
    # Processadores
    {"nome": "Intel Core i5-13400F", "categoria": "Processadores", "fornecedor": "Intel Semicondutores", "preco": 1399.00, "estoque_inicial": 25, "estoque_minimo": 10},
    {"nome": "AMD Ryzen 5 7600", "categoria": "Processadores", "fornecedor": "Advanced Micro Devices (AMD)", "preco": 1599.00, "estoque_inicial": 20, "estoque_minimo": 10},
    {"nome": "Intel Core i7-13700K", "categoria": "Processadores", "fornecedor": "Intel Semicondutores", "preco": 2899.00, "estoque_inicial": 10, "estoque_minimo": 4},
    # Memórias RAM
    {"nome": "Corsair Vengeance 16GB DDR4", "categoria": "Memórias RAM", "fornecedor": "Corsair Memory", "preco": 349.90, "estoque_inicial": 40, "estoque_minimo": 15},
    {"nome": "Kingston Fury 32GB DDR5", "categoria": "Memórias RAM", "fornecedor": "Kingston Technology", "preco": 799.00, "estoque_inicial": 18, "estoque_minimo": 6},
    # SSDs
    {"nome": "Kingston NV2 1TB", "categoria": "SSDs", "fornecedor": "Kingston Technology", "preco": 399.90, "estoque_inicial": 35, "estoque_minimo": 10},
    {"nome": "Samsung 980 PRO 1TB", "categoria": "SSDs", "fornecedor": "Samsung Eletrônica", "preco": 599.00, "estoque_inicial": 25, "estoque_minimo": 8},
    {"nome": "Western Digital Blue 500GB", "categoria": "SSDs", "fornecedor": "Western Digital", "preco": 259.90, "estoque_inicial": 30, "estoque_minimo": 10},
    {"nome": "Seagate Barracuda 2TB", "categoria": "SSDs", "fornecedor": "Seagate Technology", "preco": 749.00, "estoque_inicial": 14, "estoque_minimo": 5},
    # Teclados
    {"nome": "Logitech G213 Prodigy", "categoria": "Teclados", "fornecedor": "Logitech do Brasil", "preco": 299.90, "estoque_inicial": 28, "estoque_minimo": 10},
    {"nome": "Redragon Kumara K552", "categoria": "Teclados", "fornecedor": "Redragon Gaming", "preco": 189.90, "estoque_inicial": 32, "estoque_minimo": 12},
    {"nome": "HyperX Alloy Origins", "categoria": "Teclados", "fornecedor": "HyperX (HP Inc.)", "preco": 449.00, "estoque_inicial": 15, "estoque_minimo": 5},
    # Mouses
    {"nome": "Logitech G203 Lightsync", "categoria": "Mouses", "fornecedor": "Logitech do Brasil", "preco": 129.90, "estoque_inicial": 45, "estoque_minimo": 15},
    {"nome": "Razer DeathAdder V2", "categoria": "Mouses", "fornecedor": "Razer Inc.", "preco": 279.00, "estoque_inicial": 20, "estoque_minimo": 8},
    {"nome": "Multilaser Classic USB", "categoria": "Mouses", "fornecedor": "Multilaser Industrial", "preco": 39.90, "estoque_inicial": 60, "estoque_minimo": 20},
]


def login() -> str:
    resposta = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "senha": SENHA})
    resposta.raise_for_status()
    return resposta.json()["access_token"]


def criar_categorias(headers) -> dict:
    print("Categorias:")
    for categoria in CATEGORIAS:
        resposta = requests.post(f"{BASE_URL}/categorias/", json=categoria, headers=headers)
        status = "OK" if resposta.status_code == 201 else "SKIP"
        print(f"  {status:4} - {categoria['nome']}")
    return _mapear_por_nome(f"{BASE_URL}/categorias/", headers)


def criar_fornecedores(headers) -> dict:
    print("\nFornecedores:")
    for fornecedor in FORNECEDORES:
        resposta = requests.post(f"{BASE_URL}/fornecedores/", json=fornecedor, headers=headers)
        status = "OK" if resposta.status_code == 201 else "SKIP/ERRO"
        print(f"  {status:10} - {fornecedor['nome']}")
    return _mapear_por_nome(f"{BASE_URL}/fornecedores/", headers)


def criar_produtos(headers, categorias_map: dict, fornecedores_map: dict) -> dict:
    print("\nProdutos:")
    for produto in PRODUTOS:
        categoria_id = categorias_map.get(produto["categoria"])
        fornecedor_id = fornecedores_map.get(produto["fornecedor"])
        if categoria_id is None or fornecedor_id is None:
            print(f"  ERRO - {produto['nome']}: categoria ou fornecedor não encontrado")
            continue

        payload = {
            "nome": produto["nome"],
            "preco": produto["preco"],
            "estoque_minimo": produto["estoque_minimo"],
            "categoria_id": categoria_id,
            "fornecedor_id": fornecedor_id,
            "quantidade_estoque": 0,  # começa zerado; a entrada inicial vira uma movimentação real
        }
        resposta = requests.post(f"{BASE_URL}/produtos/", json=payload, headers=headers)
        status = "OK" if resposta.status_code == 201 else "SKIP/ERRO"
        print(f"  {status:10} - {produto['nome']}")
    return _mapear_por_nome(f"{BASE_URL}/produtos/", headers)


def _mapear_por_nome(url: str, headers) -> dict:
    """Busca todos os itens (paginando) e monta um dict nome -> id."""
    mapa = {}
    skip = 0
    limit = 100
    while True:
        resposta = requests.get(url, params={"skip": skip, "limit": limit}, headers=headers)
        resposta.raise_for_status()
        corpo = resposta.json()
        for item in corpo["itens"]:
            mapa[item["nome"]] = item["id"]
        if len(corpo["itens"]) < limit:
            break
        skip += limit
    return mapa


if __name__ == "__main__":
    print("Fazendo login...")
    token = login()
    headers = {"Authorization": f"Bearer {token}"}
    print("Login ok.\n")

    categorias_map = criar_categorias(headers)
    fornecedores_map = criar_fornecedores(headers)
    produtos_map = criar_produtos(headers, categorias_map, fornecedores_map)

    print(f"\nConcluído: {len(categorias_map)} categorias, {len(fornecedores_map)} fornecedores, {len(produtos_map)} produtos.")
    print("Agora rode: python seed_movimentacoes.py")

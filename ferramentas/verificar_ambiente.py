"""
Verifica se o computador está pronto para rodar o jogo.

Uso (a partir da pasta do projeto):
    python ferramentas/verificar_ambiente.py

Mostra [OK], [AVISO] ou [ERRO] para cada item e diz como resolver.
Só usa a biblioteca padrão do Python, então roda mesmo sem nada instalado.
"""
import importlib.util
import json
import os
import platform
import struct
import sys

PASTA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_MINIMO = (3, 10)
PYTHON_TESTADO_MAX = (3, 14)
IMAGENS = ["passaro_1.png", "passaro_2.png", "passaro_3.png", "coluna.png",
           "chao.png", "fundo_dia.png", "fundo_tarde.png", "fundo_noite.png"]

erros = 0
avisos = 0


def ok(msg):
    print(f"[OK]    {msg}")


def aviso(msg, solucao=""):
    global avisos
    avisos += 1
    print(f"[AVISO] {msg}")
    if solucao:
        print(f"        -> {solucao}")


def erro(msg, solucao=""):
    global erros
    erros += 1
    print(f"[ERRO]  {msg}")
    if solucao:
        print(f"        -> {solucao}")


def versao_pacote(nome):
    try:
        from importlib.metadata import version
        return version(nome)
    except Exception:
        return None


print(f"Sistema: {platform.system()} {platform.release()} ({platform.machine()})")
print(f"Python:  {sys.executable}\n")

# 1. Versão do Python
v = sys.version_info
texto_versao = f"{v.major}.{v.minor}.{v.micro}"
if (v.major, v.minor) < PYTHON_MINIMO:
    erro(f"Python {texto_versao} é antigo demais (mínimo 3.10).",
         "Instale o Python 3.12: winget install Python.Python.3.12")
elif (v.major, v.minor) > PYTHON_TESTADO_MAX:
    aviso(f"Python {texto_versao} é mais novo que as versões testadas (até 3.14).",
          "Se algo falhar, use o Python 3.12.")
else:
    ok(f"Python {texto_versao}")

# 2. 64 bits
if struct.calcsize("P") * 8 != 64:
    aviso("Python de 32 bits. Algumas bibliotecas não têm instalador para 32 bits.",
          "Instale a versão de 64 bits do Python.")

# 3. Rodando dentro de um ambiente virtual?
if sys.prefix != getattr(sys, "base_prefix", sys.prefix):
    ok("Ambiente virtual ativo")

# 4. pygame (obrigatório)
pygame_oficial = versao_pacote("pygame")
pygame_ce = versao_pacote("pygame-ce")
if pygame_oficial and pygame_ce:
    erro(f"pygame ({pygame_oficial}) e pygame-ce ({pygame_ce}) instalados ao mesmo tempo.",
         "Remova os dois e reinstale, um comando de cada vez:\n"
         "           python -m pip uninstall -y pygame pygame-ce\n"
         "           python -m pip install -r requirements.txt")
elif importlib.util.find_spec("pygame") is None:
    solucao = "python -m pip install -r requirements.txt"
    if (v.major, v.minor) >= (3, 14):
        solucao += "  (no Python 3.14+ ele instala o pygame-ce)"
    erro("pygame não está instalado.", solucao)
else:
    nome = "pygame-ce" if pygame_ce else "pygame"
    ok(f"{nome} {pygame_ce or pygame_oficial}")

# 5. matplotlib (opcional)
if importlib.util.find_spec("matplotlib") is None:
    aviso("matplotlib não está instalado: o jogo roda, mas sem os gráficos da IA.",
          "python -m pip install matplotlib")
else:
    ok(f"matplotlib {versao_pacote('matplotlib')}")

# 6. Imagens
pasta_imagens = os.path.join(PASTA, "assets", "imagens")
faltando = [n for n in IMAGENS if not os.path.exists(os.path.join(pasta_imagens, n))]
if faltando:
    aviso(f"Imagens faltando: {', '.join(faltando)}. O jogo usa formas simples no lugar.",
          "python ferramentas/gerar_imagens.py")
else:
    ok(f"{len(IMAGENS)} imagens em assets/imagens")

# 7. Pasta de dados com permissão de escrita
pasta_dados = os.path.join(PASTA, "dados")
try:
    os.makedirs(pasta_dados, exist_ok=True)
    teste = os.path.join(pasta_dados, ".teste_escrita")
    with open(teste, "w") as f:
        f.write("ok")
    os.remove(teste)
    ok("Pasta dados/ com permissão de escrita (recorde e treino da IA)")
except OSError:
    erro("Sem permissão para gravar em dados/. O recorde e o treino não serão salvos.",
         "Mova o projeto para uma pasta sua (ex.: Área de Trabalho ou Documentos).")

# 8. Tabela Q existente
arquivo_q = os.path.join(pasta_dados, "tabela_q.json")
if os.path.exists(arquivo_q):
    try:
        with open(arquivo_q) as f:
            dados = json.load(f)
        if dados.get("formato") == 2:
            ok(f"Tabela Q com {dados.get('episodios', 0)} partidas de treino "
               f"(recorde {dados.get('recorde', 0)})")
        else:
            aviso("Tabela Q de uma versão anterior: será ignorada e a IA começa do zero.")
    except (json.JSONDecodeError, OSError):
        aviso("Tabela Q corrompida: será ignorada e a IA começa do zero.")

print()
if erros:
    print(f"{erros} erro(s) e {avisos} aviso(s). Corrija os erros antes de rodar o jogo.")
    sys.exit(1)
print(f"Pronto para jogar! ({avisos} aviso(s))  ->  python main.py")

# Flappy Bird com modo jogador e IA (Q-Learning)

Projeto de estágio. Equipe: Pedro Arthur, Leone, Davi Marques, Paulo.

Jogo no estilo Flappy Bird feito em Python com Pygame. Tem dois modos: um em que
a pessoa joga e outro em que o pássaro aprende a jogar sozinho com Q-Learning.
Todas as imagens são geradas por código pela própria equipe
(`ferramentas/gerar_imagens.py`).

A parte de IA partiu do projeto de Stalone Augusto
(https://github.com/HardWareGCR/FlappyBirdQLearning-01656165-StaloneAugusto),
com correções e mudanças descritas no fim deste arquivo.

## Como rodar

    pip install -r requirements.txt
    python ferramentas/gerar_imagens.py   # só na primeira vez
    python main.py

Treinar a IA sem abrir janela (bem mais rápido):

    python main.py --treinar 20000

## Controles

| Tela | Tecla | Ação |
|---|---|---|
| Menu | 1 / 2 / ESC | Jogar / ver a IA / sair |
| Jogar | ESPAÇO, seta pra cima ou clique | Voar |
| Jogar | ESC | Voltar ao menu |
| IA | T | Turbo: treina várias partidas sem desenhar cada frame |
| IA | G | Gráfico da evolução dos pontos |
| IA | I | Mostrar/esconder informações |
| IA | ESC | Salvar e voltar ao menu |

## Estrutura do projeto

    flappy_bird/
    ├── main.py                  ponto de entrada (menu ou --treinar)
    ├── requirements.txt
    ├── assets/
    │   └── imagens/             PNGs gerados pelo script abaixo
    ├── ferramentas/
    │   └── gerar_imagens.py     desenha todas as imagens por código
    ├── jogo/
    │   ├── config.py            todas as constantes (tela, física, dificuldade, pastas)
    │   ├── imagens.py           carrega os PNGs
    │   ├── entidades.py         Passaro e Coluna
    │   ├── mundo.py             regras do jogo (movimento, colisão, pontos)
    │   ├── ciclo.py             ciclo do dia: troca o fundo entre dia, tarde e noite
    │   └── telas.py             menu, modo jogador e modo IA
    ├── ia/
    │   ├── agente.py            AgenteQLearning (estado, ação, tabela Q)
    │   └── treino.py            partidas da IA e treino sem janela
    └── dados/                   recorde e tabela Q salvos (fora do git)

A ideia da separação: `jogo/mundo.py` não sabe nada de teclado nem de IA, só
recebe "pula ou não pula" a cada frame. O modo jogador manda o comando vindo do
teclado e a IA manda o comando vindo da tabela Q. Assim as duas usam exatamente
as mesmas regras.

## Funcionalidades exigidas

| Funcionalidade | Onde está |
|---|---|
| F1 - Subir ao clicar/tocar | `Passaro.pular()` em `jogo/entidades.py`, `ler_comando_jogador()` em `jogo/telas.py` |
| F2 - Gravidade | `Passaro.mover()` em `jogo/entidades.py` |
| F3 - Gerar obstáculos automaticamente | `Jogo.atualizar_colunas()` em `jogo/mundo.py` |
| F4 - Colisão com obstáculo ou chão | `Jogo.verificar_colisao()` em `jogo/mundo.py` |
| F5 - Contador de pontos | `Jogo.atualizar_colunas()` em `jogo/mundo.py` |

## Imagens

`ferramentas/gerar_imagens.py` desenha as 6 imagens em pixel art e salva em
`assets/imagens`. O jogo amplia 2x ao carregar.

| Arquivo | Tamanho | Conteúdo |
|---|---|---|
| passaro_1/2/3.png | 34x24 | pássaro azul com topete, asa em 3 posições (animação) |
| coluna.png | 52x320 | coluna de metal com faixas laranjas (virada para a de cima) |
| fundo_dia.png | 288x512 | céu azul, sol, nuvens e morros verdes |
| fundo_tarde.png | 288x512 | céu de pôr do sol, primeiras estrelas, sol baixo |
| fundo_noite.png | 288x512 | céu escuro, muitas estrelas, lua com crateras |
| chao.png | 336x112 | grama e terra, emenda nas bordas para rolar sem corte |

Para mudar o visual basta editar as cores em `PALETA` (pássaro, coluna, chão)
ou em `TEMAS_FUNDO` (céus) ou as funções de desenho
e rodar o script de novo. Se as imagens não existirem, o jogo roda com formas
simples no lugar.

## Ciclo do dia

O fundo passa por dia, tarde e noite enquanto o jogo roda, e depois volta ao
dia. Cada período dura 20 segundos e, nos últimos 4, o fundo seguinte vai
aparecendo por cima até substituir o atual (transição suave com transparência).

- O tempo conta frames desenhados, não frames de jogo, então o turbo da IA não
  faz o céu piscar.
- Existe um ciclo só para o programa inteiro (`ciclo` em `jogo/ciclo.py`), então
  o céu continua de onde parou ao reiniciar a partida ou trocar de tela.
- Durações e ordem dos períodos ficam em `jogo/config.py`
  (`PERIODOS`, `DURACAO_PERIODO`, `DURACAO_TRANSICAO`).

## Diferenças em relação ao projeto base

Organização:

| Projeto base | Este projeto |
|---|---|
| Tudo em `FlappyBird.py` | Separado em `jogo/` e `ia/`, entrada em `main.py` |
| Pasta `imgs/` com imagens prontas | `assets/imagens/`, geradas por `ferramentas/gerar_imagens.py` |
| `bird1.png`, `pipe.png`, `base.png`, `bg.png` | `passaro_1.png`, `coluna.png`, `chao.png`, `fundo_dia/tarde/noite.png` |
| Fundo fixo | Fundo muda entre dia, tarde e noite |
| Classe `Cano` | Classe `Coluna` |
| Constantes espalhadas nas classes | Todas em `jogo/config.py` |
| Nada salvo entre execuções | Recorde e tabela Q em `dados/` |

Jogo:

- Modo jogador (no projeto base só a IA joga), com tela de game over e recorde.
- Dificuldade progressiva: acelera a cada 10 pontos.
- Física por velocidade (`v += g; y += v`) no lugar da fórmula por tempo.
- Colunas seguidas não mudam de altura bruscamente, para ser sempre possível passar.

IA:

- **Punição da morte chega na tabela Q.** No original a atualização era pulada
  no frame da batida (`if rodando:`), então o -1000 nunca era aprendido.
- **Aprendizado de trás pra frente.** No fim de cada partida a tabela é
  atualizada do último frame para o primeiro. Se o pássaro bateu por cima, o
  último pulo leva a culpa.
- **Estado independente da velocidade.** A distância até a coluna é medida em
  frames, então o que a IA aprende continua valendo quando o jogo acelera.
- **Tabela Q salva em arquivo** e treino sem janela.

## Resultados

| Partidas de treino | Média de pontos | Recorde |
|---|---|---|
| 1.000 | ~0 | 4 |
| 3.000 | ~9 | 38 |
| 5.000 | ~10 | 41 |
| ~20.000 | ~50 | 342 |

O projeto base relata recorde entre 15 e 30 pontos. A IA melhora bastante mas
não fica perfeita: com tabela Q ela ainda erra de vez em quando. Um próximo passo
seria Deep Q-Learning (rede neural no lugar da tabela).

# Flappy Bird com modo jogador e IA (Q-Learning)

Projeto de estágio. Equipe: Pedro Arthur, Leone, Davi Marques, Paulo.

Baseado no projeto de Stalone Augusto:
https://github.com/HardWareGCR/FlappyBirdQLearning-01656165-StaloneAugusto

## Como rodar

    pip install -r requirements.txt
    python flappy_bird.py

Para usar as imagens do jogo, copie a pasta `imgs` do projeto base para esta
pasta. Sem ela o jogo roda com formas simples no lugar das imagens.

## Modos

1. **Jogar**: ESPAÇO, seta pra cima ou clique para voar. A cada 10 pontos os
   canos ficam mais rápidos. O recorde fica salvo em `recorde.txt`.
2. **IA**: o pássaro aprende sozinho. Teclas: T liga/desliga o turbo (treina
   sem desenhar cada frame), G mostra o gráfico de evolução, I esconde as
   informações, ESC volta ao menu. O aprendizado fica salvo em `tabela_q.json`
   e continua de onde parou.

Treino rápido sem janela:

    python flappy_bird.py --treinar 20000

## Funcionalidades exigidas

| Funcionalidade | Onde está no código |
|---|---|
| Subir ao clicar/tocar | `Passaro.pular()`, `tratar_eventos_jogador()` |
| Gravidade | `Passaro.mover()` |
| Gerar canos automaticamente | `Jogo.atualizar_canos()`, `Cano.__init__` |
| Colisão com cano ou chão | `Jogo.verificar_colisao()` |
| Contador de pontos | `Jogo.atualizar_canos()` |

## O que mudou em relação ao projeto base

- **Modo jogador**: no projeto base só a IA joga.
- **Punição da morte chega na tabela Q**: no original a atualização era pulada
  no frame da batida (`if rodando:`), então o -1000 nunca era aprendido.
- **Aprendizado de trás pra frente**: no fim de cada partida a tabela é
  atualizada do último frame para o primeiro, e se o pássaro bateu por cima o
  último pulo leva a culpa. Isso acelera muito o aprendizado.
- **Estado independente da velocidade**: a distância até o cano é medida em
  frames, não em pixels, então o que a IA aprende vale quando o jogo acelera.
- **Física por velocidade** (`v += g; y += v`) no lugar da fórmula por tempo.
- **Canos justos**: a altura de um cano não varia demais em relação ao anterior.
- **Tabela Q salva em arquivo** e treino sem janela para rodar milhares de
  partidas em segundos.

## Resultados nos nossos testes

| Partidas de treino | Média de pontos | Recorde |
|---|---|---|
| 1.000 | ~0 | 3 |
| 3.000 | ~9 | 33 |
| 8.000 | ~20 | 55 |
| ~20.000 | ~50 | 342 |

Para comparação, o projeto base relata recorde entre 15 e 30 pontos.
A IA melhora bastante mas não fica perfeita: com tabela Q ainda erra de vez
em quando. Um próximo passo seria Deep Q-Learning (rede neural).

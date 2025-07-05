# Chess_Senai
Jogo de Xadrez interativo desenvolvido em Python com interface gráfica usando Pygame. Permite jogar contra outro jogador, contra a IA ou assistir uma partida entre IAs. Inclui animações, promoção de peão, roque, en passant, salvamento e carregamento de partidas.

## Requisitos

- Python 3.8+
- Pygame

Instale o Pygame com:
```bash
pip install pygame
```

## Como jogar

1. Execute o arquivo principal:

2. O menu inicial aparecerá com as opções:
- **1**: Jogador vs Jogador
- **2**: Jogador vs IA
- **3**: IA vs IA
- **S**: Salvar jogo
- **L**: Carregar jogo
- **M**: Voltar ao jogo
- **ESC**: Sair

3. No modo Jogador vs IA, use a tecla **C** para trocar a cor do jogador (brancas/pretas).
4. Use as setas **↑/↓** para ajustar a dificuldade da IA (profundidade de busca).
5. Clique nas peças para selecionar e movê-las. Movimentos válidos são destacados.
6. Quando um peão chega ao final do tabuleiro, escolha a peça para promoção clicando na opção desejada.

## Funcionalidades

- **Modos de jogo**: Jogador vs Jogador, Jogador vs IA, IA vs IA
- **IA**: Algoritmo Minimax com Alpha-Beta Pruning
- **Movimentos especiais**: Roque, en passant, promoção de peão
- **Animações**: Movimentação das peças animada
- **Salvar/Carregar**: Permite salvar e retomar partidas
- **Detecção de xeque, xeque-mate e empate**

## Observações

- O arquivo salvo é `xadrez_salvo.json` na mesma pasta do programa.

## Créditos

Desenvolvido para trabalho acadêmico na Faculdade Senai de Taubaté.
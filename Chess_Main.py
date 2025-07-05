# implantação de Roque e El passante ok (roque para peças pretas não esta funcionando)

import pygame
import sys
import copy
import random
import json
import time
from pygame.locals import *

# Inicialização do Pygame
pygame.init()
pygame.font.init()

# Constantes
LARGURA, ALTURA = 800, 700

TAMANHO_CASA = 70
TABULEIRO_TAM = TAMANHO_CASA * 8
MARGEM_X = (LARGURA - TABULEIRO_TAM) // 2
MARGEM_Y = (ALTURA - TABULEIRO_TAM) // 2
FPS = 60

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CASA_CLARA = (230, 192, 130)
CASA_ESCURA = (181, 136, 99)
DESTAQUE = (247, 220, 111)
DESTAQUE_MOVIMENTO = (88, 214, 141)
TEXTO = (50, 50, 50)
FUNDO = (40, 40, 40)
VERMELHO = (220, 60, 60)
VERDE = (60, 180, 60)
AZUL_CLARO = (173, 216, 230)

# Peças
PECA_BRANCA = 'b'
PECA_PRETA = 'w'
VAZIO = '--'

# Símbolos Unicode para as peças
SIMBOLOS_PECAS = {
    'wR': '♜', 'wN': '♞', 'wB': '♝', 'wQ': '♛', 'wK': '♚', 'wP': '♟',
    'bR': '♖', 'bN': '♘', 'bB': '♗', 'bQ': '♕', 'bK': '♔', 'bP': '♙',
    '--': ''
}

# Carregar fontes
fonte_pecas = pygame.font.SysFont('segoeuisymbol', 70)
fonte_ui = pygame.font.SysFont('Arial', 24)
fonte_titulo = pygame.font.SysFont('Arial', 36, bold=True)
fonte_status = pygame.font.SysFont('Arial', 28)

def criar_tabuleiro_inicial():
    return [
        ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
        [VAZIO]*8,
        [VAZIO]*8,
        [VAZIO]*8,
        [VAZIO]*8,
        ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
        ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
    ]

def coord_para_indice(coord_str):
    if len(coord_str) != 2:
        raise ValueError("Coordenada inválida. Use formato 'a1' a 'h8'.")
    coluna = ord(coord_str[0].lower()) - ord('a')
    linha = 8 - int(coord_str[1])
    if not (0 <= linha < 8 and 0 <= coluna < 8):
        raise ValueError("Coordenada fora do tabuleiro.")
    return linha, coluna

def indice_para_coord(linha, coluna):
    coluna_str = chr(ord('a') + coluna)
    linha_str = str(8 - linha)
    return coluna_str + linha_str

def obter_movimentos_peao(tabuleiro, linha, coluna, cor_jogador, en_passant_target):
    movimentos = []
    direcao = -1 if cor_jogador == PECA_BRANCA else 1
    nova_linha = linha + direcao
    
    # Movimento para frente
    if 0 <= nova_linha < 8 and tabuleiro[nova_linha][coluna] == VAZIO:
        movimentos.append(((linha, coluna), (nova_linha, coluna)))
        
        # Movimento duplo do peão
        if (cor_jogador == PECA_BRANCA and linha == 6) or (cor_jogador == PECA_PRETA and linha == 1):
            nova_linha_dupla = linha + 2 * direcao
            if tabuleiro[nova_linha_dupla][coluna] == VAZIO:
                movimentos.append(((linha, coluna), (nova_linha_dupla, coluna)))
    
    # Capturas normais
    for dc in [-1, 1]:
        nova_coluna = coluna + dc
        if 0 <= nova_linha < 8 and 0 <= nova_coluna < 8:
            peca_alvo = tabuleiro[nova_linha][nova_coluna]
            if peca_alvo != VAZIO and peca_alvo[0] != cor_jogador:
                movimentos.append(((linha, coluna), (nova_linha, nova_coluna)))
    
    # Captura En Passant
    if en_passant_target:
        ep_linha, ep_coluna = en_passant_target
        if (cor_jogador == PECA_BRANCA and linha == 3 and ep_linha == 2 and abs(coluna - ep_coluna) == 1) or \
           (cor_jogador == PECA_PRETA and linha == 4 and ep_linha == 5 and abs(coluna - ep_coluna) == 1):
            
            # Verificar se o alvo en passant é válido para este peão
            if (ep_linha == nova_linha) and (abs(coluna - ep_coluna) == 1):
                # O movimento real do peão que captura vai para a casa ep_linha, ep_coluna
                movimentos.append(((linha, coluna), (ep_linha, ep_coluna)))
                
    return movimentos

def obter_movimentos_torre(tabuleiro, linha, coluna, cor_jogador):
    movimentos = []
    direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for dr, dc in direcoes:
        for i in range(1, 8):
            nova_linha, nova_coluna = linha + dr * i, coluna + dc * i
            if 0 <= nova_linha < 8 and 0 <= nova_coluna < 8:
                peca_alvo = tabuleiro[nova_linha][nova_coluna]
                if peca_alvo == VAZIO:
                    movimentos.append(((linha, coluna), (nova_linha, nova_coluna)))
                elif peca_alvo[0] != cor_jogador:
                    movimentos.append(((linha, coluna), (nova_linha, nova_coluna)))
                    break
                else:
                    break
            else:
                break
    return movimentos

def obter_movimentos_cavalo(tabuleiro, linha, coluna, cor_jogador):
    movimentos = []
    saltos = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
              (1, -2), (1, 2), (2, -1), (2, 1)]
    
    for dr, dc in saltos:
        nova_linha, nova_coluna = linha + dr, coluna + dc
        if 0 <= nova_linha < 8 and 0 <= nova_coluna < 8:
            peca_alvo = tabuleiro[nova_linha][nova_coluna]
            if peca_alvo == VAZIO or peca_alvo[0] != cor_jogador:
                movimentos.append(((linha, coluna), (nova_linha, nova_coluna)))
    return movimentos

def obter_movimentos_bispo(tabuleiro, linha, coluna, cor_jogador):
    movimentos = []
    direcoes = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    
    for dr, dc in direcoes:
        for i in range(1, 8):
            nova_linha, nova_coluna = linha + dr * i, coluna + dc * i
            if 0 <= nova_linha < 8 and 0 <= nova_coluna < 8:
                peca_alvo = tabuleiro[nova_linha][nova_coluna]
                if peca_alvo == VAZIO:
                    movimentos.append(((linha, coluna), (nova_linha, nova_coluna)))
                elif peca_alvo[0] != cor_jogador:
                    movimentos.append(((linha, coluna), (nova_linha, nova_coluna)))
                    break
                else:
                    break
            else:
                break
    return movimentos

def obter_movimentos_rainha(tabuleiro, linha, coluna, cor_jogador):
    movimentos = obter_movimentos_torre(tabuleiro, linha, coluna, cor_jogador) + \
                 obter_movimentos_bispo(tabuleiro, linha, coluna, cor_jogador)
    return movimentos

def obter_movimentos_rei(tabuleiro, linha, coluna, cor_jogador, game_state):
    movimentos = []
    saltos = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 1),
              (1, -1), (1, 0), (1, 1)]
    
    for dr, dc in saltos:
        nova_linha, nova_coluna = linha + dr, coluna + dc
        if 0 <= nova_linha < 8 and 0 <= nova_coluna < 8:
            peca_alvo = tabuleiro[nova_linha][nova_coluna]
            if peca_alvo == VAZIO or peca_alvo[0] != cor_jogador:
                movimentos.append(((linha, coluna), (nova_linha, nova_coluna)))

    # Roque (Castling)
    if cor_jogador == PECA_BRANCA:
        if linha == 7 and coluna == 4 and not game_state.castling_rights['wK']:
            # Kingside Castling (short roque)
            if not game_state.castling_rights['wR_kingside'] and \
               tabuleiro[7][5] == VAZIO and tabuleiro[7][6] == VAZIO and \
               tabuleiro[7][7][1] == 'R' and tabuleiro[7][7][0] == PECA_BRANCA: # Check if rook is there
                # Check if king's path is not attacked
                if not esta_em_xeque(tabuleiro, cor_jogador):
                   # Temporarily move king to intermediate square to check for check
                   temp_board, _ = fazer_movimento(copy.deepcopy(tabuleiro), (7,4), (7,5), copy.deepcopy(game_state))
                   if not esta_em_xeque(temp_board, cor_jogador):
                       temp_board2, _ = fazer_movimento(copy.deepcopy(tabuleiro), (7,4), (7,6), copy.deepcopy(game_state))
                       if not esta_em_xeque(temp_board2, cor_jogador):
                           movimentos.append(((linha, coluna), (7, 6))) # King's destination

            # Queenside Castling (long roque)
            if not game_state.castling_rights['wR_queenside'] and \
               tabuleiro[7][1] == VAZIO and tabuleiro[7][2] == VAZIO and tabuleiro[7][3] == VAZIO and \
               tabuleiro[7][0][1] == 'R' and tabuleiro[7][0][0] == PECA_BRANCA: # Check if rook is there
                # Check if king's path is not attacked
                if not esta_em_xeque(tabuleiro, cor_jogador):
                    temp_board, _ = fazer_movimento(copy.deepcopy(tabuleiro), (7,4), (7,3), copy.deepcopy(game_state))
                    if not esta_em_xeque(temp_board, cor_jogador):
                        temp_board2, _ = fazer_movimento(copy.deepcopy(tabuleiro), (7,4), (7,2), copy.deepcopy(game_state))
                        if not esta_em_xeque(temp_board2, cor_jogador):
                            movimentos.append(((linha, coluna), (7, 2))) # King's destination

    elif cor_jogador == PECA_PRETA:
        if linha == 0 and coluna == 4 and not game_state.castling_rights['bK']:
            # Kingside Castling (short roque)
            if not game_state.castling_rights['bR_kingside'] and \
               tabuleiro[0][5] == VAZIO and tabuleiro[0][6] == VAZIO and \
               tabuleiro[0][7][1] == 'R' and tabuleiro[0][7][0] == PECA_PRETA: # Check if rook is there
                # Check if king's path is not attacked
                if not esta_em_xeque(tabuleiro, cor_jogador):
                    temp_board, _ = fazer_movimento(copy.deepcopy(tabuleiro), (0,4), (0,5), copy.deepcopy(game_state))
                    if not esta_em_xeque(temp_board, cor_jogador):
                        temp_board2, _ = fazer_movimento(copy.deepcopy(tabuleiro), (0,4), (0,6), copy.deepcopy(game_state))
                        if not esta_em_xeque(temp_board2, cor_jogador):
                            movimentos.append(((linha, coluna), (0, 6))) # King's destination

            # Queenside Castling (long roque)
            if not game_state.castling_rights['bR_queenside'] and \
               tabuleiro[0][1] == VAZIO and tabuleiro[0][2] == VAZIO and tabuleiro[0][3] == VAZIO and \
               tabuleiro[0][0][1] == 'R' and tabuleiro[0][0][0] == PECA_PRETA: # Check if rook is there
                # Check if king's path is not attacked
                if not esta_em_xeque(tabuleiro, cor_jogador):
                    temp_board, _ = fazer_movimento(copy.deepcopy(tabuleiro), (0,4), (0,3), copy.deepcopy(game_state))
                    if not esta_em_xeque(temp_board, cor_jogador):
                        temp_board2, _ = fazer_movimento(copy.deepcopy(tabuleiro), (0,4), (0,2), copy.deepcopy(game_state))
                        if not esta_em_xeque(temp_board2, cor_jogador):
                            movimentos.append(((linha, coluna), (0, 2))) # King's destination

    return movimentos

def aplicar_movimento_no_tabuleiro(tabuleiro, origem, destino, game_state):
    linha_orig, col_orig = origem
    linha_dest, col_dest = destino
    
    peca = tabuleiro[linha_orig][col_orig]
    tabuleiro[linha_orig][col_orig] = VAZIO
    tabuleiro[linha_dest][col_dest] = peca
    
    # Reset en_passant_target a cada movimento, a menos que seja um movimento de peão duplo.
    game_state.en_passant_target = None

    # Roque (Castling) - Move the rook
    if peca[1] == 'K' and abs(col_dest - col_orig) == 2: # King moved two squares
        if col_dest == 6: # Kingside castling
            rook = tabuleiro[linha_dest][7]
            tabuleiro[linha_dest][7] = VAZIO
            tabuleiro[linha_dest][5] = rook
        elif col_dest == 2: # Queenside castling
            rook = tabuleiro[linha_dest][0]
            tabuleiro[linha_dest][0] = VAZIO
            tabuleiro[linha_dest][3] = rook
    
    # En Passant - If pawn moved to an empty square and it was an en passant target
    # This implies a pawn was captured "behind" the landing square
    elif peca[1] == 'P' and abs(linha_dest - linha_orig) == 1 and col_orig != col_dest and tabuleiro[linha_dest][col_dest] == peca:
        # Check if the destination was an en_passant_target.
        # The piece at destination is the moving pawn, so we need to check if the square
        # "behind" the destination (where the captured pawn was) is empty.
        # This means the target pawn was actually removed.
        # This check is a bit tricky here because the board is already updated.
        # A more robust check might be needed if issues arise.
        # For now, let's assume if it was a diagonal move to an empty square by a pawn, it was en passant.
        
        # Determine where the captured pawn should be based on the destination
        if peca[0] == PECA_BRANCA: # White pawn moved down
            # If white moved from (3, X) to (2, Y), captured pawn was at (3, Y)
            if linha_orig == 3 and linha_dest == 2:
                tabuleiro[linha_orig][col_dest] = VAZIO # Remove the captured black pawn
        elif peca[0] == PECA_PRETA: # Black pawn moved up
            # If black moved from (4, X) to (5, Y), captured pawn was at (4, Y)
            if linha_orig == 4 and linha_dest == 5:
                tabuleiro[linha_orig][col_dest] = VAZIO # Remove the captured white pawn


    # Update en_passant_target if pawn moved two squares
    if peca[1] == 'P' and abs(linha_dest - linha_orig) == 2:
        game_state.en_passant_target = ((linha_orig + linha_dest) // 2, col_orig)
    
    # Update castling rights
    if peca == 'wK':
        game_state.castling_rights['wK'] = True
    elif peca == 'bK':
        game_state.castling_rights['bK'] = True
    elif peca == 'wR':
        if origem == (7, 0):
            game_state.castling_rights['wR_queenside'] = True
        elif origem == (7, 7):
            game_state.castling_rights['wR_kingside'] = True
    elif peca == 'bR':
        if origem == (0, 0):
            game_state.castling_rights['bR_queenside'] = True
        elif origem == (0, 7):
            game_state.castling_rights['bR_kingside'] = True
    
    pass


def fazer_movimento(tabuleiro, origem, destino, game_state):
    novo_tabuleiro = copy.deepcopy(tabuleiro)
    novo_game_state = copy.deepcopy(game_state) # Ensure game_state is also copied
    
    # Antes de aplicar o movimento no tabuleiro copiado,
    # capture a peça que está na casa de destino para verificar se uma torre é capturada.
    peca_no_destino_antes_do_movimento = novo_tabuleiro[destino[0]][destino[1]]

    # Temporariamente remove a peça de origem para aplicar o movimento na cópia
    peca_movendo = novo_tabuleiro[origem[0]][origem[1]]
    novo_tabuleiro[origem[0]][origem[1]] = VAZIO
    novo_tabuleiro[destino[0]][destino[1]] = peca_movendo

    # Lógica de Roque para a simulação: mover a torre
    if peca_movendo[1] == 'K' and abs(destino[1] - origem[1]) == 2:
        if destino[1] == 6: # Roque curto
            rook = novo_tabuleiro[destino[0]][7]
            novo_tabuleiro[destino[0]][7] = VAZIO
            novo_tabuleiro[destino[0]][5] = rook
        elif destino[1] == 2: # Roque longo
            rook = novo_tabuleiro[destino[0]][0]
            novo_tabuleiro[destino[0]][0] = VAZIO
            novo_tabuleiro[destino[0]][3] = rook
    
    # Lógica de En Passant para a simulação: remover o peão capturado
    # Condição para En Passant: peão movendo, destino vazio, e diferença de coluna
    is_en_passant_move = (peca_movendo[1] == 'P' and 
                           peca_no_destino_antes_do_movimento == VAZIO and 
                           origem[1] != destino[1])

    if is_en_passant_move:
        # Se for um movimento en passant, remove o peão capturado
        if peca_movendo[0] == PECA_BRANCA: # Peão branco capturou peão preto
            novo_tabuleiro[destino[0] + 1][destino[1]] = VAZIO
        else: # Peão preto capturou peão branco
            novo_tabuleiro[destino[0] - 1][destino[1]] = VAZIO
            
    # Atualiza o en_passant_target para o NOVO game_state simulado
    novo_game_state.en_passant_target = None # Por padrão, reseta

    if peca_movendo[1] == 'P' and abs(destino[0] - origem[0]) == 2:
        # Se o peão moveu duas casas, define o novo en_passant_target
        novo_game_state.en_passant_target = ((origem[0] + destino[0]) // 2, origem[1])
        
    # Update castling rights in the simulated game state
    if peca_movendo == 'wK':
        novo_game_state.castling_rights['wK'] = True
    elif peca_movendo == 'bK':
        novo_game_state.castling_rights['bK'] = True
    elif peca_movendo == 'wR':
        if origem == (7, 0): novo_game_state.castling_rights['wR_queenside'] = True
        elif origem == (7, 7): novo_game_state.castling_rights['wR_kingside'] = True
    elif peca_movendo == 'bR':
        if origem == (0, 0): novo_game_state.castling_rights['bR_queenside'] = True
        elif origem == (0, 7): novo_game_state.castling_rights['bR_kingside'] = True

    # Verifica se uma torre foi capturada na posição inicial e atualiza os direitos
    # Esta verificação é mais robusta se feita antes de sobrescrever 'destino'.
    # Como já sobrescrevemos, precisamos do 'peca_no_destino_antes_do_movimento'
    if peca_no_destino_antes_do_movimento != VAZIO and peca_no_destino_antes_do_movimento[1] == 'R':
        if destino == (7, 0): novo_game_state.castling_rights['wR_queenside'] = True
        elif destino == (7, 7): novo_game_state.castling_rights['wR_kingside'] = True
        elif destino == (0, 0): novo_game_state.castling_rights['bR_queenside'] = True
        elif destino == (0, 7): novo_game_state.castling_rights['bR_kingside'] = True

    return novo_tabuleiro, novo_game_state

def encontrar_rei(tabuleiro, cor_rei):
    for r in range(8):
        for c in range(8):
            peca = tabuleiro[r][c]
            if peca == cor_rei + 'K':
                return r, c
    return None

def esta_em_xeque(tabuleiro, cor_jogador_checado):
    rei_pos = encontrar_rei(tabuleiro, cor_jogador_checado)
    if rei_pos is None:
        return False # Should not happen in a valid game
    
    cor_oponente = PECA_BRANCA if cor_jogador_checado == PECA_PRETA else PECA_PRETA
    
    for r_op in range(8):
        for c_op in range(8):
            peca_op = tabuleiro[r_op][c_op]
            if peca_op != VAZIO and peca_op[0] == cor_oponente:
                tipo_peca_op = peca_op[1]
                
                # Special handling for pawns and kings (their "attacks" are different from their moves)
                if tipo_peca_op == 'P':
                    direcao_ataque = -1 if cor_oponente == PECA_BRANCA else 1
                    for dc in [-1, 1]:
                        nova_linha_ataque = r_op + direcao_ataque
                        nova_coluna_ataque = c_op + dc
                        if 0 <= nova_linha_ataque < 8 and 0 <= nova_coluna_ataque < 8:
                            if (nova_linha_ataque, nova_coluna_ataque) == rei_pos:
                                return True
                    continue # Already handled pawn attacks

                elif tipo_peca_op == 'K':
                    # King attacks one square around, check directly
                    for dr_k, dc_k in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                        k_attack_r, k_attack_c = r_op + dr_k, c_op + dc_k
                        if (k_attack_r, k_attack_c) == rei_pos:
                            return True
                    continue # Already handled king attacks
                
                movs_op = []
                # For other pieces, their "moves" are their "attacks"
                if tipo_peca_op == 'R':
                    movs_op = obter_movimentos_torre(tabuleiro, r_op, c_op, cor_oponente)
                elif tipo_peca_op == 'N':
                    movs_op = obter_movimentos_cavalo(tabuleiro, r_op, c_op, cor_oponente)
                elif tipo_peca_op == 'B':
                    movs_op = obter_movimentos_bispo(tabuleiro, r_op, c_op, cor_oponente)
                elif tipo_peca_op == 'Q':
                    movs_op = obter_movimentos_rainha(tabuleiro, r_op, c_op, cor_oponente)
                
                for _, destino_op in movs_op:
                    if destino_op == rei_pos:
                        return True
    return False

def obter_todos_movimentos_validos(tabuleiro, cor_jogador, game_state):
    todos_movimentos = []
    
    for r in range(8):
        for c in range(8):
            peca = tabuleiro[r][c]
            if peca != VAZIO and peca[0] == cor_jogador:
                tipo_peca = peca[1]
                movs = []
                
                if tipo_peca == 'P':
                    movs = obter_movimentos_peao(tabuleiro, r, c, cor_jogador, game_state.en_passant_target)
                elif tipo_peca == 'R':
                    movs = obter_movimentos_torre(tabuleiro, r, c, cor_jogador)
                elif tipo_peca == 'N':
                    movs = obter_movimentos_cavalo(tabuleiro, r, c, cor_jogador)
                elif tipo_peca == 'B':
                    movs = obter_movimentos_bispo(tabuleiro, r, c, cor_jogador)
                elif tipo_peca == 'Q':
                    movs = obter_movimentos_rainha(tabuleiro, r, c, cor_jogador)
                elif tipo_peca == 'K':
                    movs = obter_movimentos_rei(tabuleiro, r, c, cor_jogador, game_state) # Pass game_state for castling

                for mov in movs:
                    novo_tabuleiro, novo_game_state_simulado = fazer_movimento(copy.deepcopy(tabuleiro), mov[0], mov[1], copy.deepcopy(game_state))
                    if not esta_em_xeque(novo_tabuleiro, cor_jogador):
                        todos_movimentos.append(mov)
    
    return todos_movimentos

def is_game_over(tabuleiro, cor_jogador_atual, game_state):
    movimentos_validos = obter_todos_movimentos_validos(tabuleiro, cor_jogador_atual, game_state)
    
    if len(movimentos_validos) == 0:
        if esta_em_xeque(tabuleiro, cor_jogador_atual):
            return "CHECKMATE"
        else:
            return "STALEMATE"
    return None

class Animacao:
    def __init__(self, peca, origem_pos, destino_pos, duracao=0.3): # Duração da animação em segundos
        self.peca = peca
        self.origem_x = MARGEM_X + origem_pos[1] * TAMANHO_CASA + TAMANHO_CASA // 2
        self.origem_y = MARGEM_Y + origem_pos[0] * TAMANHO_CASA + TAMANHO_CASA // 2
        self.destino_x = MARGEM_X + destino_pos[1] * TAMANHO_CASA + TAMANHO_CASA // 2
        self.destino_y = MARGEM_Y + destino_pos[0] * TAMANHO_CASA + TAMANHO_CASA // 2
        self.tempo_inicio = time.time()
        self.duracao = duracao
        self.origem_pos_tabuleiro = origem_pos # Guarda a posição real no tabuleiro
        self.destino_pos_tabuleiro = destino_pos # Guarda a posição real no tabuleiro

    def obter_posicao_atual(self):
        tempo_decorrido = time.time() - self.tempo_inicio
        progresso = min(1, tempo_decorrido / self.duracao)

        x = self.origem_x + (self.destino_x - self.origem_x) * progresso
        y = self.origem_y + (self.destino_y - self.origem_y) * progresso
        return (x, y)

    def esta_completa(self):
        return (time.time() - self.tempo_inicio) >= self.duracao

class ChessAI:
    def __init__(self, cor_ia, profundidade_maxima):
        self.cor_ia = cor_ia
        self.profundidade_maxima = profundidade_maxima
        self.cor_oponente = PECA_BRANCA if cor_ia == PECA_PRETA else PECA_PRETA

    def avaliar_tabuleiro(self, tabuleiro):
        valor = 0
        valores_pecas = {'P': 10, 'N': 30, 'B': 30, 'R': 50, 'Q': 90, 'K': 900}
        
        for r in range(8):
            for c in range(8):
                peca = tabuleiro[r][c]
                if peca != VAZIO:
                    tipo_peca = peca[1]
                    if peca[0] == self.cor_ia:
                        valor += valores_pecas.get(tipo_peca, 0)
                    else:
                        valor -= valores_pecas.get(tipo_peca, 0)
        
        centro = [(3,3), (3,4), (4,3), (4,4)]
        for r, c in centro:
            peca = tabuleiro[r][c]
            if peca != VAZIO:
                if peca[0] == self.cor_ia:
                    valor += 3
                else:
                    valor -= 3
                    
        return valor

    def minimax(self, tabuleiro, profundidade, is_maximizando_jogador, alpha, beta, game_state):
        if profundidade == self.profundidade_maxima:
            return self.avaliar_tabuleiro(tabuleiro)
        
        cor_atual = self.cor_ia if is_maximizando_jogador else self.cor_oponente
        game_status = is_game_over(tabuleiro, cor_atual, game_state)
        
        if game_status == "CHECKMATE":
            return float('-inf') if not is_maximizando_jogador else float('inf')
        elif game_status == "STALEMATE":
            return 0

        movimentos_possiveis = obter_todos_movimentos_validos(tabuleiro, cor_atual, game_state)
        if not movimentos_possiveis:
            return self.avaliar_tabuleiro(tabuleiro)

        if is_maximizando_jogador:
            melhor_valor = float('-inf')
            for origem, destino in movimentos_possiveis:
                # Pass game_state to fazer_movimento and minimax
                novo_tabuleiro, novo_game_state = fazer_movimento(copy.deepcopy(tabuleiro), origem, destino, copy.deepcopy(game_state))
                valor = self.minimax(novo_tabuleiro, profundidade + 1, False, alpha, beta, novo_game_state)
                melhor_valor = max(melhor_valor, valor)
                alpha = max(alpha, melhor_valor)
                if beta <= alpha:
                    break
            return melhor_valor
        else:
            melhor_valor = float('inf')
            for origem, destino in movimentos_possiveis:
                # Pass game_state to fazer_movimento and minimax
                novo_tabuleiro, novo_game_state = fazer_movimento(copy.deepcopy(tabuleiro), origem, destino, copy.deepcopy(game_state))
                valor = self.minimax(novo_tabuleiro, profundidade + 1, True, alpha, beta, novo_game_state)
                melhor_valor = min(melhor_valor, valor)
                beta = min(beta, melhor_valor)
                if beta <= alpha:
                    break
            return melhor_valor

    def escolher_melhor_movimento(self, tabuleiro, game_state):
        melhor_movimento = None
        melhor_valor = float('-inf')
        movimentos_possiveis = obter_todos_movimentos_validos(tabuleiro, self.cor_ia, game_state)
        random.shuffle(movimentos_possiveis) # Adicionado shuffle para diversificar as escolhas da IA

        if not movimentos_possiveis:
            return None
        
        for origem, destino in movimentos_possiveis:
            # Pass game_state to fazer_movimento and minimax
            novo_tabuleiro, novo_game_state = fazer_movimento(copy.deepcopy(tabuleiro), origem, destino, copy.deepcopy(game_state))
            # Simular promoção de peão para a IA (sem escolha para simplificar a IA)
            if novo_tabuleiro[destino[0]][destino[1]][1] == 'P' and (destino[0] == 0 or destino[0] == 7):
                novo_tabuleiro[destino[0]][destino[1]] = novo_tabuleiro[destino[0]][destino[1]][0] + 'Q' # IA sempre promove para rainha
            
            valor = self.minimax(novo_tabuleiro, 1, False, float('-inf'), float('inf'), novo_game_state)
            
            if valor > melhor_valor:
                melhor_valor = valor
                melhor_movimento = (origem, destino)
        
        return melhor_movimento

class JogoXadrez:
    def __init__(self):
        self.tabuleiro = criar_tabuleiro_inicial()
        self.turno = PECA_BRANCA
        self.peca_selecionada = None
        self.movimentos_validos = []
        self.jogo_ativo = True
        self.modo_jogo = None
        self.ia_branca = None
        self.ia_preta = None
        self.ultimo_movimento = None
        self.mensagem = "Escolha um modo de jogo"
        self.menu_visivel = True
        self.profundidade_ia = 2
        self.cor_jogador = PECA_BRANCA
        self.peca_animacao = None
        self.tempo_ultimo_movimento_ia_iniciado = 0
        self.tabuleiro_para_desenhar = None 
        self.castling_rights = {
            'wK': False, 'wR_kingside': False, 'wR_queenside': False,
            'bK': False, 'bR_kingside': False, 'bR_queenside': False
        } # Tracks if king/rooks have moved
        self.en_passant_target = None # (linha, coluna) of the square a pawn skipped over

        self.promocao_ativa = False
        self.posicao_promocao = None # (linha, coluna) onde o peão será promovido
        self.cor_peao_promovendo = None # Nova variável para guardar a cor do peão que está promovendo

    def desenhar_tabuleiro(self, tela):
        # Desenhar fundo
        tela.fill(FUNDO)
        
        # Desenhar título
        titulo = fonte_titulo.render("JOGO DE XADREZ", True, VERDE)
        tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 15))
        
        # Desenhar as casas do tabuleiro
        for linha in range(8):
            for coluna in range(8):
                x = MARGEM_X + coluna * TAMANHO_CASA
                y = MARGEM_Y + linha * TAMANHO_CASA
                
                if (linha + coluna) % 2 == 0:
                    cor = CASA_CLARA
                else:
                    cor = CASA_ESCURA
                
                pygame.draw.rect(tela, cor, (x, y, TAMANHO_CASA, TAMANHO_CASA))
                
                if self.peca_selecionada == (linha, coluna):
                    pygame.draw.rect(tela, DESTAQUE, (x, y, TAMANHO_CASA, TAMANHO_CASA), 4)
                
                for origem, destino in self.movimentos_validos:
                    if destino == (linha, coluna):
                        pygame.draw.circle(tela, DESTAQUE_MOVIMENTO, 
                                          (x + TAMANHO_CASA//2, y + TAMANHO_CASA//2), 
                                          10, 3)
        
        # Determine qual tabuleiro usar para o desenho estático das peças
        # Se houver uma animação ativa, desenhamos um tabuleiro "vazio" nas posições de origem/destino
        tabuleiro_atual_para_desenho = self.tabuleiro
        if self.peca_animacao:
            # Criamos uma cópia temporária para o desenho durante a animação
            tabuleiro_temp_desenho = copy.deepcopy(self.tabuleiro)
            
            # Removemos a peça da origem no tabuleiro temporário
            tabuleiro_temp_desenho[self.peca_animacao.origem_pos_tabuleiro[0]][self.peca_animacao.origem_pos_tabuleiro[1]] = VAZIO
            
            # Se for um movimento de captura en passant, também remove o peão capturado
            peca_animada_info = self.peca_animacao.peca
            origem_anim = self.peca_animacao.origem_pos_tabuleiro
            destino_anim = self.peca_animacao.destino_pos_tabuleiro

            if peca_animada_info[1] == 'P' and abs(destino_anim[0] - origem_anim[0]) == 1 and origem_anim[1] != destino_anim[1]:
                # É uma captura diagonal de peão para uma casa vazia: En Passant
                if peca_animada_info[0] == PECA_BRANCA: # Peão branco
                    tabuleiro_temp_desenho[destino_anim[0] + 1][destino_anim[1]] = VAZIO
                else: # Peão preto
                    tabuleiro_temp_desenho[destino_anim[0] - 1][destino_anim[1]] = VAZIO

            # Se for um roque, limpa a posição original da torre também para o desenho
            if peca_animada_info[1] == 'K' and abs(destino_anim[1] - origem_anim[1]) == 2:
                if destino_anim[1] == 6: # Kingside castling
                    tabuleiro_temp_desenho[destino_anim[0]][7] = VAZIO
                elif destino_anim[1] == 2: # Queenside castling
                    tabuleiro_temp_desenho[destino_anim[0]][0] = VAZIO
            
            tabuleiro_atual_para_desenho = tabuleiro_temp_desenho

        # Desenhar as peças estáticas do tabuleiro
        for linha in range(8):
            for coluna in range(8):
                peca = tabuleiro_atual_para_desenho[linha][coluna]
                
                if peca != VAZIO:
                    x = MARGEM_X + coluna * TAMANHO_CASA + TAMANHO_CASA//2
                    y = MARGEM_Y + linha * TAMANHO_CASA + TAMANHO_CASA//2
                    
                    cor_texto = BRANCO if peca[0] == PECA_BRANCA else PRETO
                    texto = fonte_pecas.render(SIMBOLOS_PECAS[peca], True, cor_texto)
                    rect = texto.get_rect(center=(x, y))
                    tela.blit(texto, rect)

        # Desenhar a peça em animação por cima de tudo
        if self.peca_animacao:
            if not self.peca_animacao.esta_completa():
                x_anim, y_anim = self.peca_animacao.obter_posicao_atual()
                peca_animada_info = self.peca_animacao.peca
                cor_texto_anim = BRANCO if peca_animada_info[0] == PECA_BRANCA else PRETO
                texto_anim = fonte_pecas.render(SIMBOLOS_PECAS[peca_animada_info], True, cor_texto_anim)
                rect_anim = texto_anim.get_rect(center=(x_anim, y_anim))
                tela.blit(texto_anim, rect_anim)
            else:
                # Animação concluída, aplicar movimento final ao tabuleiro e resetar
                aplicar_movimento_no_tabuleiro(self.tabuleiro, self.peca_animacao.origem_pos_tabuleiro, self.peca_animacao.destino_pos_tabuleiro, self)
                
                # *** NOVA LÓGICA DE PROMOÇÃO APÓS ANIMAÇÃO ***
                peca_movida_animacao = self.tabuleiro[self.peca_animacao.destino_pos_tabuleiro[0]][self.peca_animacao.destino_pos_tabuleiro[1]]
                if peca_movida_animacao[1] == 'P' and (self.peca_animacao.destino_pos_tabuleiro[0] == 0 or self.peca_animacao.destino_pos_tabuleiro[0] == 7):
                    # É um peão que chegou à última fileira
                    self.promocao_ativa = True
                    self.posicao_promocao = self.peca_animacao.destino_pos_tabuleiro
                    # Armazena a cor do peão que está promovendo (a cor da peça que acabou de se mover)
                    self.cor_peao_promovendo = peca_movida_animacao[0] 
                    self.peca_animacao = None # Para parar a animação e aguardar a escolha
                    self.mensagem = "Escolha a peça para promoção (Q, R, B, N)"
                else:
                    self.turno = PECA_PRETA if self.turno == PECA_BRANCA else PECA_BRANCA
                    self.verificar_fim_jogo()
                    self.peca_animacao = None # Limpa a animação para o próximo turno

        # Desenhar informações do jogo
        if self.jogo_ativo:
            status_text = f"Turno: {'Brancas' if self.turno == PECA_BRANCA else 'Pretas'}"
            if esta_em_xeque(self.tabuleiro, self.turno):
                status_text += " (XEQUE!)"
        else:
            status_text = self.mensagem
        
        status = fonte_status.render(status_text, True, BRANCO)
        tela.blit(status, (20, ALTURA - 40))
        
        # Desenhar coordenadas
        letras = "abcdefgh"
        numeros = "87654321"
        
        for i in range(8):
            texto = fonte_ui.render(letras[i], True, BRANCO)
            tela.blit(texto, (MARGEM_X + i * TAMANHO_CASA + TAMANHO_CASA//2 - texto.get_width()//2, 
                             MARGEM_Y + TABULEIRO_TAM + 5))
            
            texto = fonte_ui.render(numeros[i], True, BRANCO)
            tela.blit(texto, (MARGEM_X - 20, 
                             MARGEM_Y + i * TAMANHO_CASA + TAMANHO_CASA//2 - texto.get_height()//2))

    def desenhar_menu(self, tela):
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        tela.blit(s, (0, 0))
        
        titulo = fonte_titulo.render("MENU DE XADREZ", True, VERDE)
        tela.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 100))
        
        opcoes = [
            "1 - Jogador vs Jogador",
            "2 - Jogador vs IA",
            "3 - IA vs IA",
            "S - Salvar jogo",
            "L - Carregar jogo",
            "M - Voltar ao jogo",
            "ESC - Sair"
        ]
        
        for i, opcao in enumerate(opcoes):
            texto = fonte_ui.render(opcao, True, BRANCO)
            tela.blit(texto, (LARGURA//2 - texto.get_width()//2, 200 + i * 40))
        
        texto = fonte_ui.render(f"Profundidade da IA: {self.profundidade_ia} (Setas para Cima/Baixo)", True, BRANCO)
        tela.blit(texto, (LARGURA//2 - texto.get_width()//2, 200 + len(opcoes) * 40 + 20))
        
        if self.modo_jogo == 'pvia':
            cor_text = "Brancas" if self.cor_jogador == PECA_BRANCA else "Pretas"
            texto = fonte_ui.render(f"Jogando como: {cor_text} (C - Trocar)", True, BRANCO)
            tela.blit(texto, (LARGURA//2 - texto.get_width()//2, 200 + (len(opcoes) + 1) * 40 + 20))

    def desenhar_menu_promocao(self, tela):
        if not self.promocao_ativa:
            return

        # Overlay escuro
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        tela.blit(s, (0, 0))

        # Centralizar menu
        menu_largura = 4 * TAMANHO_CASA + 3 * 10 # 4 peças + 3 espaços de 10px
        menu_altura = TAMANHO_CASA + 20 # altura da casa + margem
        menu_x = (LARGURA - menu_largura) // 2
        menu_y = (ALTURA - menu_altura) // 2

        pygame.draw.rect(tela, FUNDO, (menu_x - 10, menu_y - 10, menu_largura + 20, menu_altura + 20), 0, 10)
        pygame.draw.rect(tela, VERDE, (menu_x - 10, menu_y - 10, menu_largura + 20, menu_altura + 20), 3, 10)

        tipos_promocao = ['Q', 'R', 'B', 'N']
        
        # A cor da peça promovendo é a que foi salva quando o peão chegou à última fileira.
        cor_da_peca_promovendo = self.cor_peao_promovendo 

        for i, tipo in enumerate(tipos_promocao):
            peca_str = cor_da_peca_promovendo + tipo
            simbolo = SIMBOLOS_PECAS[peca_str]
            cor_texto = BRANCO if cor_da_peca_promovendo == PECA_BRANCA else PRETO # 'w' é preto, 'b' é branco no Pygame Unicode

            texto_peca = fonte_pecas.render(simbolo, True, cor_texto)
            
            # Posição de desenho da peça na UI de promoção
            pos_x = menu_x + i * (TAMANHO_CASA + 10) + TAMANHO_CASA // 2
            pos_y = menu_y + TAMANHO_CASA // 2
            
            rect_peca = texto_peca.get_rect(center=(pos_x, pos_y))
            
            # Adicionar um retângulo clicável para cada opção
            click_rect = pygame.Rect(menu_x + i * (TAMANHO_CASA + 10), menu_y, TAMANHO_CASA, TAMANHO_CASA)
            pygame.draw.rect(tela, AZUL_CLARO, click_rect, 0, 5) # Fundo para a opção
            pygame.draw.rect(tela, DESTAQUE_MOVIMENTO, click_rect, 2, 5) # Borda

            tela.blit(texto_peca, rect_peca)

    def lidar_clique_promocao(self, x, y):
        if not self.promocao_ativa:
            return False

        menu_largura = 4 * TAMANHO_CASA + 3 * 10
        menu_altura = TAMANHO_CASA + 20
        menu_x = (LARGURA - menu_largura) // 2
        menu_y = (ALTURA - menu_altura) // 2

        tipos_promocao = ['Q', 'R', 'B', 'N']
        cor_da_peca_promovendo = self.cor_peao_promovendo # Usa a cor salva do peão que promove

        for i, tipo in enumerate(tipos_promocao):
            click_rect = pygame.Rect(menu_x + i * (TAMANHO_CASA + 10), menu_y, TAMANHO_CASA, TAMANHO_CASA)
            if click_rect.collidepoint(x, y):
                # O jogador clicou em uma opção de promoção
                linha, coluna = self.posicao_promocao
                self.tabuleiro[linha][coluna] = cor_da_peca_promovendo + tipo
                
                self.promocao_ativa = False
                self.posicao_promocao = None
                self.cor_peao_promovendo = None # Limpa a variável
                self.mensagem = "Peão promovido!"
                
                # Agora que a promoção foi feita, é a vez do próximo jogador
                # O turno já foi atualizado em desenhar_tabuleiro. Não é necessário inverter aqui.
                # O turno já está correto para o PRÓXIMO jogador.
                self.verificar_fim_jogo()
                return True
        return False


    def clique_casa(self, linha, coluna):
        if self.promocao_ativa: # Bloqueia interações do tabuleiro durante a promoção
            return
            
        if not self.jogo_ativo or self.menu_visivel or self.peca_animacao:
            return
            
        peca = self.tabuleiro[linha][coluna]
        
        if not self.peca_selecionada:
            if peca != VAZIO and peca[0] == self.turno:
                if (self.turno == PECA_BRANCA and self.ia_branca is None) or \
                   (self.turno == PECA_PRETA and self.ia_preta is None): # Só permite selecionar se não for turno da IA
                    self.peca_selecionada = (linha, coluna)
                    self.movimentos_validos = [mov for mov in obter_todos_movimentos_validos(self.tabuleiro, self.turno, self) 
                                              if mov[0] == (linha, coluna)]
        elif self.peca_selecionada:
            movimento_encontrado = False
            for origem, destino in self.movimentos_validos:
                if destino == (linha, coluna):
                    self.iniciar_animacao_movimento(origem, destino)
                    movimento_encontrado = True
                    break
            
            if movimento_encontrado:
                self.peca_selecionada = None
                self.movimentos_validos = []
            else:
                if peca != VAZIO and peca[0] == self.turno:
                    self.peca_selecionada = (linha, coluna)
                    self.movimentos_validos = [mov for mov in obter_todos_movimentos_validos(self.tabuleiro, self.turno, self) 
                                              if mov[0] == (linha, coluna)]
                else:
                    self.peca_selecionada = None
                    self.movimentos_validos = []

    def iniciar_animacao_movimento(self, origem, destino):
        # Captura a peça que será animada do tabuleiro lógico
        peca_a_animar = self.tabuleiro[origem[0]][origem[1]]
        self.peca_animacao = Animacao(peca_a_animar, origem, destino)
        
        origem_coord = indice_para_coord(origem[0], origem[1])
        destino_coord = indice_para_coord(destino[0], destino[1])
        self.mensagem = f"Movimento: {origem_coord} → {destino_coord}"

    def verificar_fim_jogo(self):
        game_status = is_game_over(self.tabuleiro, self.turno, self)
        if game_status == "CHECKMATE":
            vencedor = "Brancas" if self.turno == PECA_PRETA else "Pretas"
            self.mensagem = f"XEQUE-MATE! {vencedor} venceram!"
            self.jogo_ativo = False
        elif game_status == "STALEMATE":
            self.mensagem = "EMPATE! (Afogamento)"
            self.jogo_ativo = False

    def executar_movimento_ia(self):
        if not self.jogo_ativo or self.menu_visivel or self.peca_animacao or self.promocao_ativa:
            return
            
        ia_para_mover = None
        if self.turno == PECA_BRANCA and self.ia_branca:
            ia_para_mover = self.ia_branca
        elif self.turno == PECA_PRETA and self.ia_preta:
            ia_para_mover = self.ia_preta

        if ia_para_mover:
            if time.time() - self.tempo_ultimo_movimento_ia_iniciado > 1.0: # Dá um tempo para o jogador ver o tabuleiro antes da IA mover
                self.mensagem = "IA pensando..."
                pygame.display.flip() # Força a atualização da tela para mostrar "IA pensando..."
                
                movimento = ia_para_mover.escolher_melhor_movimento(self.tabuleiro, self)
                
                if movimento:
                    # IA sempre promove para rainha para simplificar
                    # A animação e a aplicação real do movimento são as mesmas.
                    # A promoção para a IA não precisa de um menu de escolha.
                    self.iniciar_animacao_movimento(movimento[0], movimento[1])
                    # A atualização do turno e verificação de fim de jogo
                    # ocorrem APÓS a animação ser concluída (no desenhar_tabuleiro)
                self.tempo_ultimo_movimento_ia_iniciado = time.time()
            else:
                self.mensagem = "Aguardando IA..."

    def salvar_jogo(self):
        data = {
            "tabuleiro": self.tabuleiro,
            "turno": self.turno,
            "modo_jogo": self.modo_jogo,
            "profundidade_ia": self.profundidade_ia,
            "cor_jogador": self.cor_jogador,
            "castling_rights": self.castling_rights,
            "promocao_ativa": self.promocao_ativa,
            "posicao_promocao": self.posicao_promocao,
            "cor_peao_promovendo": self.cor_peao_promovendo,
            "en_passant_target": self.en_passant_target
        }
        try:
            with open("xadrez_salvo.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.mensagem = "Jogo salvo com sucesso!"
        except Exception as e:
            self.mensagem = f"Erro ao salvar: {str(e)}"

    def carregar_jogo(self):
        try:
            with open("xadrez_salvo.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.tabuleiro = data.get("tabuleiro", criar_tabuleiro_inicial())
            self.turno = data.get("turno", PECA_BRANCA)
            self.modo_jogo = data.get("modo_jogo", None)
            self.profundidade_ia = data.get("profundidade_ia", 2)
            self.cor_jogador = data.get("cor_jogador", PECA_BRANCA)
            self.castling_rights = data.get("castling_rights", {
                'wK': False, 'wR_kingside': False, 'wR_queenside': False,
                'bK': False, 'bR_kingside': False, 'bR_queenside': False
            })
            self.en_passant_target = tuple(data.get("en_passant_target")) if data.get("en_passant_target") else None
            self.promocao_ativa = data.get("promocao_ativa", False)
            self.posicao_promocao = tuple(data.get("posicao_promocao")) if data.get("posicao_promocao") else None # Tupla
            self.cor_peao_promovendo = data.get("cor_peao_promovendo", None)


            self.ia_branca = None
            self.ia_preta = None
            if self.modo_jogo == 'pvia':
                if self.cor_jogador == PECA_BRANCA:
                    self.ia_preta = ChessAI(PECA_PRETA, self.profundidade_ia)
                else:
                    self.ia_branca = ChessAI(PECA_BRANCA, self.profundidade_ia)
            elif self.modo_jogo == 'iavia':
                self.ia_branca = ChessAI(PECA_BRANCA, self.profundidade_ia)
                self.ia_preta = ChessAI(PECA_PRETA, self.profundidade_ia)
            
            self.jogo_ativo = True
            self.peca_selecionada = None
            self.movimentos_validos = []
            self.peca_animacao = None
            self.mensagem = "Jogo carregado com sucesso!"
        except FileNotFoundError:
            self.mensagem = "Nenhum jogo salvo encontrado."
        except Exception as e:
            self.mensagem = f"Erro ao carregar: {str(e)}"

def main():
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Jogo de Xadrez")
    relogio = pygame.time.Clock()
    
    jogo = JogoXadrez()
    
    executando = True
    while executando:
        for evento in pygame.event.get():
            if evento.type == QUIT:
                executando = False
            
            elif evento.type == KEYDOWN:
                if evento.key == K_ESCAPE:
                    executando = False
                elif evento.key == K_m:
                    jogo.menu_visivel = not jogo.menu_visivel
                elif jogo.menu_visivel:
                    if evento.key == K_1:
                        jogo.modo_jogo = 'pvp'
                        jogo.ia_branca = None
                        jogo.ia_preta = None
                        jogo.tabuleiro = criar_tabuleiro_inicial()
                        jogo.turno = PECA_BRANCA
                        jogo.jogo_ativo = True
                        jogo.menu_visivel = False
                        jogo.mensagem = "Modo: Jogador vs Jogador"
                        # Reset castling rights, en passant and promotion state
                        jogo.castling_rights = {
                            'wK': False, 'wR_kingside': False, 'wR_queenside': False,
                            'bK': False, 'bR_kingside': False, 'bR_queenside': False
                        }
                        jogo.en_passant_target = None
                        jogo.promocao_ativa = False
                        jogo.posicao_promocao = None
                        jogo.cor_peao_promovendo = None
                    elif evento.key == K_2:
                        jogo.modo_jogo = 'pvia'
                        jogo.tabuleiro = criar_tabuleiro_inicial()
                        jogo.turno = PECA_BRANCA
                        if jogo.cor_jogador == PECA_BRANCA:
                            jogo.ia_branca = None
                            jogo.ia_preta = ChessAI(PECA_PRETA, jogo.profundidade_ia)
                        else:
                            jogo.ia_branca = ChessAI(PECA_BRANCA, jogo.profundidade_ia)
                            jogo.ia_preta = None
                        jogo.jogo_ativo = True
                        jogo.menu_visivel = False
                        jogo.mensagem = "Modo: Jogador vs IA"
                        # Reset castling rights, en passant and promotion state
                        jogo.castling_rights = {
                            'wK': False, 'wR_kingside': False, 'wR_queenside': False,
                            'bK': False, 'bR_kingside': False, 'bR_queenside': False
                        }
                        jogo.en_passant_target = None
                        jogo.promocao_ativa = False
                        jogo.posicao_promocao = None
                        jogo.cor_peao_promovendo = None
                    elif evento.key == K_3:
                        jogo.modo_jogo = 'iavia'
                        jogo.ia_branca = ChessAI(PECA_BRANCA, jogo.profundidade_ia)
                        jogo.ia_preta = ChessAI(PECA_PRETA, jogo.profundidade_ia)
                        jogo.tabuleiro = criar_tabuleiro_inicial()
                        jogo.turno = PECA_BRANCA
                        jogo.jogo_ativo = True
                        jogo.menu_visivel = False
                        jogo.mensagem = "Modo: IA vs IA"
                        # Reset castling rights, en passant and promotion state
                        jogo.castling_rights = {
                            'wK': False, 'wR_kingside': False, 'wR_queenside': False,
                            'bK': False, 'bR_kingside': False, 'bR_queenside': False
                        }
                        jogo.en_passant_target = None
                        jogo.promocao_ativa = False
                        jogo.posicao_promocao = None
                        jogo.cor_peao_promovendo = None
                    elif evento.key == K_s:
                        jogo.salvar_jogo()
                    elif evento.key == K_l:
                        jogo.carregar_jogo()
                    elif evento.key == K_UP:
                        jogo.profundidade_ia = min(jogo.profundidade_ia + 1, 4)
                    elif evento.key == K_DOWN:
                        jogo.profundidade_ia = max(jogo.profundidade_ia - 1, 1)
                    elif evento.key == K_c:
                        if jogo.modo_jogo == 'pvia':
                            jogo.cor_jogador = PECA_PRETA if jogo.cor_jogador == PECA_BRANCA else PECA_BRANCA
                            if jogo.cor_jogador == PECA_BRANCA:
                                jogo.ia_branca = None
                                jogo.ia_preta = ChessAI(PECA_PRETA, jogo.profundidade_ia)
                            else:
                                jogo.ia_branca = ChessAI(PECA_BRANCA, jogo.profundidade_ia)
                                jogo.ia_preta = None
            
            elif evento.type == MOUSEBUTTONDOWN and evento.button == 1:
                x, y = pygame.mouse.get_pos()
                if jogo.promocao_ativa:
                    # Lidar com o clique no menu de promoção
                    if jogo.lidar_clique_promocao(x, y):
                        pass # Clique tratado pelo menu de promoção
                else:
                    # Lidar com o clique normal no tabuleiro
                    if (MARGEM_X <= x < MARGEM_X + TABULEIRO_TAM and 
                        MARGEM_Y <= y < MARGEM_Y + TABULEIRO_TAM):
                        coluna = (x - MARGEM_X) // TAMANHO_CASA
                        linha = (y - MARGEM_Y) // TAMANHO_CASA
                        jogo.clique_casa(linha, coluna)
        
        # A IA só deve se mover se não houver animação ou promoção ativa
        if jogo.jogo_ativo and not jogo.menu_visivel and not jogo.peca_animacao and not jogo.promocao_ativa:
            jogo.executar_movimento_ia()
        
        jogo.desenhar_tabuleiro(tela)
        if jogo.menu_visivel:
            jogo.desenhar_menu(tela)
        
        # Desenhar menu de promoção APÓS o tabuleiro, para ficar por cima
        jogo.desenhar_menu_promocao(tela) 

        pygame.display.flip()
        relogio.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
import pygame
import random
from collections import deque

# --- CONFIGURAÇÕES ---
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
AZUL = (25, 25, 166)
AMARELO = (255, 255, 0)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
LARANJA = (255, 165, 0)

TAMANHO_BLOCO = 20
LARGURA_MAPA = 30
ALTURA_MAPA = 20
LARGURA_TELA = LARGURA_MAPA * TAMANHO_BLOCO
ALTURA_TELA = ALTURA_MAPA * TAMANHO_BLOCO + 80 

# Mapa 20x30 
MAPA_LAYOUT = [
    "111111111111111111111111111111",
    "100000000000001100000000000001",
    "101111011111101101111110111101",
    "101111011111101101111110111101",
    "100000000000000000000000000001",
    "101111011011111111110110111101",
    "100000011000001100000110000001",
    "111111011111101101111110111111",
    "111111011000000000000110111111",
    "100000000011119911110000000001",
    "101111011019999999910110111101",
    "101111011019111111910110111101",
    "100000000010111111010000000001",
    "111111011110000000011110111111",
    "111111011110111111011110111111",
    "100000000000001100000000000001",
    "101111011111101101111110111101",
    "100000011000000000000110000001",
    "101111111111111111111111111101",
    "111111111111111111111111111111"
]

class Jogo:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption("Pac-Man")
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.SysFont('Arial', 18)
        self.fonte_grande = pygame.font.SysFont('Arial', 24)
        
         
        self.fonte_gigante = pygame.font.SysFont('Arial', 50, bold=True) 
        
        self.menu_ativo = True
        self.contador_frames = 0
        
        self.menu_inicial()

    def resetar_jogo(self, dificuldade):
        self.dificuldade = dificuldade
        self.pontos = 0
        self.tempo_inicio = pygame.time.get_ticks()
        self.game_over = False
        self.vitoria = False # Variável para controlar vitória
        self.mapa_atual = [list(linha) for linha in MAPA_LAYOUT]
        self.contador_frames = 0
        self.pacman_pos = [1, 1]
        
        # Total de pontos disponíveis no início
        self.total_pontos = sum(linha.count('0') for linha in MAPA_LAYOUT)

        if dificuldade == "FACIL":
            cor_fantasma = VERDE
            self.probabilidade_inteligencia = 0.25 
            self.delay_fantasma = 4 
        elif dificuldade == "MEDIA":
            cor_fantasma = LARANJA
            self.probabilidade_inteligencia = 0.60 
            self.delay_fantasma = 3 
        else: # DIFICIL
            cor_fantasma = VERMELHO
            self.probabilidade_inteligencia = 0.90
            self.delay_fantasma = 3 

        self.fantasmas = [Fantasma(14, 10, cor_fantasma)]

    def menu_inicial(self):
        while self.menu_ativo:
            self.tela.fill(PRETO)
            titulo = self.fonte_grande.render("SELECIONE A DIFICULDADE", True, AMARELO)
            op1 = self.fonte.render("1 - FÁCIL", True, VERDE)
            op2 = self.fonte.render("2 - MÉDIO", True, LARANJA)
            op3 = self.fonte.render("3 - DIFÍCIL", True, VERMELHO)
            
            self.tela.blit(titulo, (LARGURA_TELA//2 - 150, 100))
            self.tela.blit(op1, (LARGURA_TELA//2 - 100, 200))
            self.tela.blit(op2, (LARGURA_TELA//2 - 100, 250))
            self.tela.blit(op3, (LARGURA_TELA//2 - 100, 300))
            
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: self.resetar_jogo("FACIL"); self.menu_ativo = False
                    if event.key == pygame.K_2: self.resetar_jogo("MEDIA"); self.menu_ativo = False
                    if event.key == pygame.K_3: self.resetar_jogo("DIFICIL"); self.menu_ativo = False
        
        self.rodar_jogo()

    def desenhar_painel(self):
        y_pos = ALTURA_MAPA * TAMANHO_BLOCO
        pygame.draw.rect(self.tela, (30, 30, 30), (0, y_pos, LARGURA_TELA, 80))
        
        tempo_total_segundos = (pygame.time.get_ticks() - self.tempo_inicio) // 1000
        minutos = tempo_total_segundos // 60
        segundos = tempo_total_segundos % 60
        texto_tempo = f"{minutos:02}:{segundos:02}"
        
        txt_dif = self.fonte.render(f"Modo: {self.dificuldade}", True, BRANCO)
        txt_pts = self.fonte.render(f"Pontos: {self.pontos}", True, AMARELO)
        txt_time = self.fonte.render(f"Tempo: {texto_tempo}", True, BRANCO)
        
        self.tela.blit(txt_dif, (20, y_pos + 10))
        self.tela.blit(txt_pts, (20, y_pos + 40))
        self.tela.blit(txt_time, (300, y_pos + 25))

    # Função unificada para fim de jogo
    def tela_fim_de_jogo(self, venceu):
        self.tela.fill(PRETO)
        
        if venceu:
            texto_msg = "PARABÉNS! VOCÊ GANHOU!"
            cor_msg = VERDE
        else:
            texto_msg = "VOCÊ PERDEU!"
            cor_msg = VERMELHO

        texto = self.fonte_gigante.render(texto_msg, True, cor_msg)
        rect_texto = texto.get_rect(center=(LARGURA_TELA//2, ALTURA_TELA//2))
        
        self.tela.blit(texto, rect_texto)
        pygame.display.update()
        pygame.time.wait(4000) # Espera 4 segundos

    def rodar_jogo(self):
        while not self.game_over:
            self.relogio.tick(15) 
            self.contador_frames += 1

            self.tela.fill(PRETO)
            
            # 1. Captura de Entrada
            movimento = [0, 0]
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); exit()
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: movimento = [-1, 0]
            elif keys[pygame.K_RIGHT]: movimento = [1, 0]
            elif keys[pygame.K_UP]: movimento = [0, -1]
            elif keys[pygame.K_DOWN]: movimento = [0, 1]

            # 2. Atualizar Pacman
            nx, ny = self.pacman_pos[0] + movimento[0], self.pacman_pos[1] + movimento[1]
            if self.mapa_atual[ny][nx] != '1':
                self.pacman_pos = [nx, ny]
                if self.mapa_atual[ny][nx] == '0':
                    self.mapa_atual[ny][nx] = '9'
                    self.pontos += 10
            
            # [NOVO] Verifica Vitória 
           
            pontos_restantes = sum(linha.count('0') for linha in self.mapa_atual)
            if pontos_restantes == 0:
                self.game_over = True
                self.vitoria = True

            # 3. Atualizar Fantasma
            if self.contador_frames % self.delay_fantasma == 0:
                for f in self.fantasmas:
                    f.mover(self.mapa_atual, self.pacman_pos, self.probabilidade_inteligencia)
            
            # Colisão
            for f in self.fantasmas:
                if f.x == self.pacman_pos[0] and f.y == self.pacman_pos[1]:
                    self.game_over = True
                    self.vitoria = False # Define derrota

            # 4. Desenhar tudo
            for y in range(len(self.mapa_atual)):
                for x in range(len(self.mapa_atual[y])):
                    r = pygame.Rect(x*TAMANHO_BLOCO, y*TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO)
                    if self.mapa_atual[y][x] == '1': pygame.draw.rect(self.tela, AZUL, r, 1)
                    elif self.mapa_atual[y][x] == '0': pygame.draw.circle(self.tela, BRANCO, r.center, 3)
            
            px, py = self.pacman_pos[0]*TAMANHO_BLOCO, self.pacman_pos[1]*TAMANHO_BLOCO
            pygame.draw.circle(self.tela, AMARELO, (px+10, py+10), 8)
            
            for f in self.fantasmas:
                fx, fy = f.x*TAMANHO_BLOCO, f.y*TAMANHO_BLOCO
                pygame.draw.circle(self.tela, f.cor, (fx+10, fy+10), 8)

            self.desenhar_painel()
            pygame.display.update()

        # Exibe tela de fim de jogo
        self.tela_fim_de_jogo(self.vitoria)
        
        self.menu_ativo = True
        self.menu_inicial()

class Fantasma:
    def __init__(self, x, y, cor):
        self.x = x
        self.y = y
        self.cor = cor

    def mover(self, mapa, alvo, chance_inteligencia):
        decisao = random.random()
        if decisao < chance_inteligencia:
            proximo_passo = self.calcular_bfs(mapa, alvo)
            if proximo_passo:
                self.x += proximo_passo[0]
                self.y += proximo_passo[1]
                return
        self.mover_aleatorio(mapa)

    def mover_aleatorio(self, mapa):
        vizinhos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        opcoes_validas = []
        for dx, dy in vizinhos:
            nx, ny = self.x + dx, self.y + dy
            if mapa[ny][nx] != '1':
                opcoes_validas.append((dx, dy))
        if opcoes_validas:
            escolha = random.choice(opcoes_validas)
            self.x += escolha[0]
            self.y += escolha[1]

    def calcular_bfs(self, mapa, alvo):
        fila = deque([(self.x, self.y, [])])
        visitados = set([(self.x, self.y)])
        while fila:
            cx, cy, caminho = fila.popleft()
            if cx == alvo[0] and cy == alvo[1]:
                return caminho[0] if caminho else None
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < LARGURA_MAPA and 0 <= ny < ALTURA_MAPA:
                    if mapa[ny][nx] != '1' and (nx, ny) not in visitados:
                        visitados.add((nx, ny))
                        novo_caminho = list(caminho)
                        novo_caminho.append((dx, dy))
                        fila.append((nx, ny, novo_caminho))
        return None

if __name__ == "__main__":
    Jogo()


    
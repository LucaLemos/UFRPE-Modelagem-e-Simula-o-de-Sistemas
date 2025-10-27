import pygame
from entities.computador import Computador
from entities.gerador import GeradorProcessos
from entities.processo import Processo
from utils.grid_helper import GridHelper
from config import FREQUENCIAS, BRANCO, AMARELO, VERDE, VERMELHO, CINZA, PRETO, POS_UI, POS_INSTRUCOES

class QueueSimulator:
    def __init__(self):
        self.computador = Computador()
        self.gerador = GeradorProcessos()
        self.processos = []
        self.fila_espera = []  # Nova: processos aguardando na fila
        self.proximo_id = 1
        self.tempo_ultimo_processo = 0
        
        self.frequencia_atual = 2
        self.intervalo_geracao = FREQUENCIAS[self.frequencia_atual]["valor"]
        self.geracao_automatica = True
        
        # Posições da fila baseadas no grid
        self.fila_positions = self._calcular_posicoes_fila()
    
    def _calcular_posicoes_fila(self):
        """Calcula as posições onde os processos ficam na fila"""
        posicoes = []
        coluna_inicio = 4  # Coluna onde começa a fila
        linha = 4          # Linha da fila
        
        for i in range(5):  # 5 posições na fila
            x, y = GridHelper.centro_pixels(coluna_inicio + i, linha)
            posicoes.append((x, y))
        
        return posicoes
    
    def obter_frequencia_atual(self):
        return FREQUENCIAS[self.frequencia_atual]
    
    def aumentar_frequencia(self):
        if self.frequencia_atual < len(FREQUENCIAS) - 1:
            self.frequencia_atual += 1
            self.intervalo_geracao = FREQUENCIAS[self.frequencia_atual]["valor"]
    
    def diminuir_frequencia(self):
        if self.frequencia_atual > 0:
            self.frequencia_atual -= 1
            self.intervalo_geracao = FREQUENCIAS[self.frequencia_atual]["valor"]
    
    def toggle_geracao_automatica(self):
        self.geracao_automatica = not self.geracao_automatica
    
    def gerar_processo(self):
        x, y = self.gerador.get_centro()
        novo_processo = Processo(self.proximo_id, x, y)
        self.processos.append(novo_processo)
        self.fila_espera.append(novo_processo)  # Adiciona à fila
        self.proximo_id += 1
        return novo_processo
    
    def atualizar(self):
        # Geração automática
        if self.geracao_automatica:
            self.tempo_ultimo_processo += 1
            if self.tempo_ultimo_processo >= self.intervalo_geracao:
                self.gerar_processo()
                self.tempo_ultimo_processo = 0
        
        # Atualiza posições dos processos na fila
        for i, processo in enumerate(self.fila_espera):
            if i < len(self.fila_positions):
                alvo_x, alvo_y = self.fila_positions[i]
                processo.mover_para(alvo_x, alvo_y)
                processo.em_fila = True
        
        # Move o primeiro da fila para a CPU se estiver ociosa
        if self.fila_espera and self.computador.processor_ocioso:
            processo = self.fila_espera.pop(0)
            processo.em_fila = False
        
        # Processa movimento dos processos
        for processo in self.processos[:]:
            if processo.ativo:
                if not processo.em_fila and processo.mover_para_computador(self.computador):
                    self.computador.processor_ocioso = False
                    processo.ativo = False
            else:
                self.processos.remove(processo)
        
        # Atualiza status da CPU
        self.computador.processor_ocioso = len(self.fila_espera) == 0
    
    def desenhar(self, tela):
        # Limpa a tela
        tela.fill(PRETO)
        
        # Desenha grid (opcional - pode remover depois)
        GridHelper.desenhar_grid(tela)
        
        # Desenha seta de conexão
        gerador_x, gerador_y = self.gerador.get_centro()
        computador_x, computador_y = self.computador.get_centro()
        pygame.draw.line(tela, BRANCO, (gerador_x, gerador_y), (computador_x, computador_y), 3)
        
        # Desenha área da fila
        self._desenhar_area_fila(tela)
        
        # Desenha componentes
        self.gerador.desenhar(tela)
        self.computador.desenhar(tela)
        
        # Desenha processos
        for processo in self.processos:
            processo.desenhar(tela)
        
        # Desenha UI
        self._desenhar_ui(tela)
    
    def _desenhar_area_fila(self, tela):
        """Desenha a área visual da fila de espera"""
        if self.fila_positions:
            # Desenha base da fila
            primeira_x, primeira_y = self.fila_positions[0]
            ultima_x, ultima_y = self.fila_positions[-1]
            
            pygame.draw.rect(tela, (40, 40, 40), 
                           (primeira_x - 20, primeira_y - 25, 
                            ultima_x - primeira_x + 40, 50))
            
            # Texto "Fila de Espera"
            fonte = pygame.font.SysFont(None, 20)
            texto = fonte.render("Fila de Espera", True, CINZA)
            tela.blit(texto, (primeira_x - 15, primeira_y - 20))
    
    def _desenhar_ui(self, tela):
        fonte_info = pygame.font.SysFont(None, 24)
        
        # Converte posições do grid para pixels
        ui_x, ui_y, _, _ = GridHelper.para_pixels(*POS_UI, 4, 2)
        inst_x, inst_y, _, _ = GridHelper.para_pixels(*POS_INSTRUCOES, 4, 2)
        
        # Informações do sistema
        freq_atual = self.obter_frequencia_atual()
        info_frequencia = fonte_info.render(f"Frequência: {freq_atual['nome']}", True, AMARELO)
        tela.blit(info_frequencia, (ui_x, ui_y))
        
        info_processos = fonte_info.render(f"Processos ativos: {len(self.processos)}", True, BRANCO)
        tela.blit(info_processos, (ui_x, ui_y + 30))
        
        info_fila = fonte_info.render(f"Fila: {len(self.fila_espera)} processos", True, BRANCO)
        tela.blit(info_fila, (ui_x, ui_y + 60))
        
        status_auto = "LIGADA" if self.geracao_automatica else "DESLIGADA"
        cor_status = VERDE if self.geracao_automatica else VERMELHO
        info_auto = fonte_info.render(f"Auto: {status_auto}", True, cor_status)
        tela.blit(info_auto, (ui_x, ui_y + 90))
        
        # Instruções
        instrucoes = [
            "ESPACO: Gerar processo",
            "A: + Frequência", 
            "Z: - Frequência",
            "G: Toggle Auto",
            "ESC: Sair"
        ]
        
        for i, instrucao in enumerate(instrucoes):
            texto_inst = fonte_info.render(instrucao, True, CINZA)
            tela.blit(texto_inst, (inst_x, inst_y + i * 25))
# Batata Tower (Batata vs Banana Defense)

Um jogo simples e divertido de *Tower Defense* feito em Python usando a biblioteca Pygame. 
Defenda seu caminho plantando torres de batata carismáticas que disparam contra as hordas infinitas de bananas malignas!

## Funcionalidades Dinâmicas V1.0
- **Menu Completo:** O jogo agora possui tela inicial interativa com escolha de Campanha (Nível 1 seguido do Nível 2), modo Arcade (Level Selecionado) e tela de Configurações de som independentes.
- **3 Tipos de Torres (Batatas):**
  - **Normal (Tecla 1):** R$ 40 - Balanceada.
  - **Fritas (Tecla 2):** R$ 60 - Alcance curto mas dano constante na área próxima.
  - **Doce Sniper (Tecla 3):** R$ 80 - Alvo de longa distância com alto dano.
- **Evolução de Torres:** Clique em qualquer torre existente com dinheiro suficiente para upá-la para o Nível 2, ganhando habilidades extras (Penetração e Splah Damage).
- **Habilidades Globais:** Use as teclas **Q** (Purê Lento - R$150) ou **W** (Bomba Ketchup - R$200) para ganhar vantagem em momentos de aperto.
- **Inimigos Habilidosos (Bananas):** Surgem Bananas normais, corredoras Verdes com baixo HP e Bananas-da-Terra extremamente lentas e parrudas.

## Requisitos

- Python 3.x
- [Pygame](https://www.pygame.org/wiki/GettingStarted)

## Instalação e Execução

1. Certifique-se de ter o Python instalado em seu sistema.
2. Instale o Pygame executando o comando no terminal:
   ```bash
   pip install pygame
   ```
3. Antes de começar a jogar, primeiro você deve executar os dois scripts de Download de Áudio incluídos para adquirir trilhas sonoras profissionais (Open-Source KenneyNL):
   ```bash
   python download_assets.py
   python download_music.py
   ```
4. Em seguida, execute o script principal do jogo:
   ```bash
   python batata_tower.py
   ```

## Como Jogar
- A navegação através do Menu é totalmente baseada no mouse (`Hover` e clique intuitivo).
- Na partida, use as **Teclas 1, 2, 3** do seu teclado para selecionar qual a torre você deseja equipar, e então clique na Grama/Areia para plantá-la.
- O jogo te avisará visualmente circulando o mouse com vermelho caso você **não tenha fundos** ou esteja **em cima do caminho** de passagem.
- Para invocar feitiços globais de emergência, pressione a tecla **Q** no seu teclado a qualquer momento para retardar as hordas, ou pressione a tecla **W** e clique num local específico do mapa para causar uma Explosão vermelha enorme.

## Créditos
Projeto original: *Studio Kaplun!*

import pygame
import math
import random

# Inicialização
import os
import wave
import struct

pygame.init()
pygame.font.init()
pygame.mixer.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Batata Tower - Defense")
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 220, 80)
ORANGE = (255, 140, 30)
BROWN = (180, 100, 40)
GREEN = (80, 220, 80)

# Carregamento de Efeitos Sonoros Profissionais
try:
    fx_shoot = pygame.mixer.Sound("assets/sounds/snd_shoot.wav")
    fx_hit = pygame.mixer.Sound("assets/sounds/snd_hit.wav")
    fx_buy = pygame.mixer.Sound("assets/sounds/snd_buy.wav")
    fx_ketchup = pygame.mixer.Sound("assets/sounds/snd_ketchup.wav")
    fx_slow = pygame.mixer.Sound("assets/sounds/snd_slow.wav")
    
    fx_shoot.set_volume(0.25)
    fx_hit.set_volume(0.35)
    fx_buy.set_volume(0.6)
    fx_ketchup.set_volume(0.8)
    fx_slow.set_volume(0.8)
except Exception as e:
    print(f"Erro carregando sons: {e}")
    class DummySound:
        def play(self): pass
try:
    pygame.mixer.music.load("assets/music/bgm_action.ogg")
    pygame.mixer.music.set_volume(0.35)
    pygame.mixer.music.play(loops=-1) # Infinite loop
except Exception as e:
    print(f"Erro carregando musica: {e}")

global_music_vol = 0.35
global_sfx_vol = 0.5

def update_volumes():
    pygame.mixer.music.set_volume(global_music_vol)
    fx_shoot.set_volume(global_sfx_vol * 0.5)
    fx_hit.set_volume(global_sfx_vol * 0.7)
    fx_buy.set_volume(global_sfx_vol * 1.2)
    fx_ketchup.set_volume(global_sfx_vol * 1.6)
    fx_slow.set_volume(global_sfx_vol * 1.6)
    fx_over.set_volume(global_sfx_vol * 1.6)

# Sintetizador apenas para o Game Over 
def create_over_sound(filename, frequency, duration, volume=0.5):
    sample_rate = 44100
    num_samples = int(duration * sample_rate)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for i in range(num_samples):
            t = float(i) / sample_rate
            val = 1.0 if (t * frequency) % 1.0 > 0.5 else -1.0 # square
            packed_value = struct.pack('h', int(val * volume * 32767.0))
            wav_file.writeframesraw(packed_value)

create_over_sound("snd_over.wav", 150, 1.5, 0.8)
fx_over = pygame.mixer.Sound("snd_over.wav")

# ----------------- GERAÇÃO DE SPRITES (PIXEL ART) -----------------
SPRITES = {}

PIXEL_COLORS = {
    'B': BLACK, 'W': WHITE, 'R': BROWN, 'C': (220, 40, 40), 
    'F': (255, 210, 80), 'D': (160, 60, 140), 'O': ORANGE,
    'N': YELLOW, 'G': (150, 255, 100), 'P': (200, 150, 40), '.': None
}

PAT_BANANA = [
    [
        "....XXXX....",
        "...XXXXXX...",
        "..XXXBXXBX..",
        "..XXXXXXXX..",
        "..XXXXXXXX..",
        "...XXXXXX...",
        "...XX..XX...",
        "...BB..BB..."
    ],
    [
        "....XXXX....",
        "...XXXXXX...",
        "..XXXBXXBX..",
        "..XXXXXXXX..",
        "..XXXXXXXX..",
        "...XXXXXX...",
        "....XXXX....",
        "....BBBB...."
    ]
]

PAT_POTATO = {
    "normal": [
        "....RRRR....",
        "...RRRRRR...",
        "..RRRRRRRR..",
        "..RRBBRRBB..",
        "..RRRRRRRR..",
        "...RRRBB....",
        "....RRRR...."
    ],
    "normal_2": [
        "....BBBB....",
        "...BBBBBB...",
        "..BBBBBBBB..",
        "..BBWWBWWB..",
        "..BBBBBBBB..",
        "...BBBW.....",
        "....BBBB...."
    ],
    "sniper": [
        "....DDDD....",
        "...DDDDDD...",
        "..DDBBDDBB..",
        "..DDDDDDDD..",
        "..DDDDDDDD..",
        "...DDDDB....",
        "....DDDD...."
    ],
    "sniper_2": [
        "....RRRR....", # Batata vermelha pimenta
        "...RRRRRR...",
        "..RWWBRWWB..",
        "..RRRRRRRR..",
        "..RRRRRRRR..",
        "...RRBWBR...",
        "....RRRR...."
    ],
    "fries": [
        "...F....F...",
        "..FFF..FFF..",
        "...F....F...",
        "..CCCCCCCC..",
        "..CBBCCBBC..",
        "..CCCCCCCC..",
        "..CCCCCCCC..",
        "...CCCCCC..."
    ],
    "fries_2": [
        "...F.FF.F...",
        "..FFFFFFFF..",
        "...F.FF.F...",
        "..BBBBBBBB..", # Caixa preta
        "..BWWBBWWB..",
        "..BBBBBBBB..",
        "..BBBBBBBB..",
        "...BBBBBB..."
    ]
}

PAT_BULLET = [
    ".OO.",
    "OOOO",
    "OOOO",
    ".OO."
]

def create_pixel_sprite(pattern, colors_dict, scale=4):
    height = len(pattern)
    width = len(pattern[0])
    surface = pygame.Surface((width * scale, height * scale), pygame.SRCALPHA)
    for y, row in enumerate(pattern):
        for x, char in enumerate(row):
            if char in colors_dict and colors_dict[char] is not None:
                pygame.draw.rect(surface, colors_dict[char], (x * scale, y * scale, scale, scale))
    return surface

def init_sprites():
    # Bananas
    for b_type, char in [("normal", "N"), ("green", "G"), ("plantain", "P")]:
        for frame in [0, 1]:
            pattern = [row.replace('X', char) for row in PAT_BANANA[frame]]
            SPRITES[f"banana_{b_type}_{frame}"] = create_pixel_sprite(pattern, PIXEL_COLORS, scale=4)
            
    # Potatoes
    for p_type in ["normal", "normal_2", "sniper", "sniper_2", "fries", "fries_2"]:
        SPRITES[f"potato_{p_type}"] = create_pixel_sprite(PAT_POTATO[p_type], PIXEL_COLORS, scale=4)
        
    # Bullet
    SPRITES["bullet"] = create_pixel_sprite(PAT_BULLET, PIXEL_COLORS, scale=3)
    SPRITES["bullet_sniper"] = create_pixel_sprite([row.replace('O', 'W') for row in PAT_BULLET], PIXEL_COLORS, scale=4)
    SPRITES["bullet_fire"] = create_pixel_sprite([row.replace('O', 'C') for row in PAT_BULLET], PIXEL_COLORS, scale=4)

init_sprites()
# ------------------------------------------------------------------

# Caminho que as bananas seguem (curvinha pra ficar mais engraçado)
PATHS = {
    1: [
        (0, 180), (120, 180), (120, 320), (300, 320), (300, 140),
        (520, 140), (520, 400), (720, 400), (720, 220), (900, 220)
    ],
    2: [
        (0, 50), (180, 50), (180, 500), (380, 500), (380, 150),
        (600, 150), (600, 450), (820, 450), (820, 250), (900, 250)
    ]
}

current_path = PATHS[1]

# Sistema de Partículas para Dano
class DamageNumber:
    def __init__(self, x, y, amount):
        self.x = x
        self.y = y
        self.amount = amount
        self.lifetime = 45
        self.font = pygame.font.SysFont("arialrounded", 20, bold=True)
        self.vy = -1.5

    def update(self):
        self.y += self.vy
        self.lifetime -= 1
        return self.lifetime <= 0

    def draw(self):
        if self.lifetime > 0:
            alpha = min(255, self.lifetime * 8)
            text_surf = self.font.render(f"-{self.amount}", True, (255, 50, 50))
            text_surf.set_alpha(alpha)
            screen.blit(text_surf, (self.x - 10, self.y - 15))

class Banana:
    def __init__(self, b_type="normal", hp_multiplier=1.0, speed_multiplier=1.0):
        self.x, self.y = current_path[0]
        self.path_index = 0
        self.type = b_type
        
        base_hp = 8
        base_speed = 1.6
        self.reward = 6
        self.color = YELLOW
        
        if b_type == "green": # Fast runner
            base_hp = 5
            base_speed = 2.4
            self.reward = 4
            self.color = (150, 255, 100)
        elif b_type == "plantain": # Slow tank
            base_hp = 25
            base_speed = 1.0
            self.reward = 12
            self.color = (200, 150, 40)
            
        self.max_health = base_hp * hp_multiplier
        self.health = self.max_health
        self.speed = base_speed * speed_multiplier
        self.angle = 0
        self.dying = False
        self.die_timer = 0

    def move(self):
        if self.dying:
            self.die_timer += 1
            self.angle += 12
            return self.die_timer > 35

        if self.path_index >= len(current_path) - 1:
            return True  # chegou no final → player perde vida

        target_x, target_y = current_path[self.path_index + 1]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < 3:
            self.path_index += 1
            return False

        current_speed = self.speed * 0.5 if slow_spell_timer > 0 else self.speed
        self.x += dx / dist * current_speed
        self.y += dy / dist * current_speed

        # Balanço engraçado enquanto anda
        self.angle = math.sin(pygame.time.get_ticks() * 0.008 + self.x) * 25
        return False

    def draw(self):
        # Animação de caminhada
        frame = (pygame.time.get_ticks() // 200) % 2
        sprite_name = f"banana_{self.type}_{frame}"
        surf = SPRITES[sprite_name]

        if self.dying:
            alpha = max(0, 255 - self.die_timer * 7)
            surf = surf.copy() # Copia para poder alterar alpha independente
            surf.set_alpha(alpha)

        rotated = pygame.transform.rotate(surf, -self.angle)
        rect = rotated.get_rect(center=(int(self.x), int(self.y - 8)))
        screen.blit(rotated, rect.topleft)

        # Barra de vida
        if not self.dying:
            bar_width = 40
            bar_height = 6
            fill = (self.health / self.max_health) * bar_width
            pygame.draw.rect(screen, (220, 40, 40), (self.x - 20, self.y - 35, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (self.x - 20, self.y - 35, fill, bar_height))


class PotatoTower:
    def __init__(self, x, y, t_type="normal"):
        self.x = x
        self.y = y
        self.type = t_type
        self.level = 1
        self.angle = 0
        self.cooldown = 0
        
        self.pierce = 0 # Inimigos atravessados por tiro
        self.splash = 0 # Dano em área do tiro
        
        self._apply_stats()

    def _apply_stats(self):
        if self.type == "normal":
            self.range = 110
            self.cooldown_max = 28
            self.damage = 2
            self.cost = 40
            self.upgrade_cost = 50
            self.bullet_color = ORANGE
            if self.level == 2:
                self.cooldown_max = 18
                self.pierce = 1
                self.bullet_color = YELLOW
                
        elif self.type == "sniper":
            self.range = 230
            self.cooldown_max = 70
            self.damage = 6
            self.cost = 80
            self.upgrade_cost = 100
            self.bullet_color = (255, 100, 200)
            if self.level == 2:
                self.damage = 18
                self.splash = 30
                self.bullet_color = (255, 60, 60)
                
        elif self.type == "fries":
            self.range = 85
            self.cooldown_max = 10
            self.damage = 1
            self.cost = 60
            self.upgrade_cost = 80
            self.bullet_color = (255, 255, 100)
            if self.level == 2:
                self.range = 145
                self.damage = 2

    def upgrade(self):
        if self.level == 1:
            self.level = 2
            self._apply_stats()
            return True
        return False

    def find_target(self, bananas):
        for b in bananas:
            if b.dying:
                continue
            dist = math.hypot(b.x - self.x, b.y - self.y)
            if dist <= self.range:
                return b
        return None

    def update(self, bananas):
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        target = self.find_target(bananas)
        if target:
            # Olhar pro alvo (pra batata ficar mais expressiva)
            dx = target.x - self.x
            dy = target.y - self.y
            self.angle = math.degrees(math.atan2(dy, dx))

            # Atira!
            bullets.append(Bullet(self.x, self.y, target, self.damage, self.bullet_color, self.pierce, self.splash))
            self.cooldown = self.cooldown_max
            fx_shoot.play()

    def draw(self):
        sprite_name = f"potato_{self.type}" + ("_2" if self.level == 2 else "")
        surf = SPRITES[sprite_name]
        rotated = pygame.transform.rotate(surf, -self.angle)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated, rect.topleft)


class Bullet:
    def __init__(self, x, y, target, damage=2, color=ORANGE, pierce=0, splash=0):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.color = color
        self.pierce = pierce
        self.splash = splash
        self.speed = 7
        self.alive = True
        self.hit_targets = set()

    def update(self):
        if not self.alive or self.target.dying:
            # Se estava indo na direção de alguém que morreu, e tem pierce, pode continuar voadora.
            # No momento, vamos só morrer se não tem alvo.
            if self.pierce == 0:
                return True
            else:
                self.alive = False
                return True

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)

        if dist < 12 and self.target not in self.hit_targets:
            self.target.health -= self.damage
            damage_numbers.append(DamageNumber(self.target.x, self.target.y, self.damage))
            fx_hit.play()
            self.hit_targets.add(self.target)
            
            if self.target.health <= 0:
                self.target.dying = True
                self.target.die_timer = 0
                
            if self.splash > 0:
                # Dano para todo mundo perto do alvo (explosão)
                for b in bananas:
                    if b != self.target and not b.dying:
                        if math.hypot(b.x - self.x, b.y - self.y) < self.splash:
                            b.health -= self.damage // 2
                            damage_numbers.append(DamageNumber(b.x, b.y, self.damage // 2))
                            if b.health <= 0:
                                b.dying = True
                                b.die_timer = 0

            if self.pierce > 0:
                self.pierce -= 1
                # Encontrar novo alvo próximo pra perfurar
                new_target = None
                for b in bananas:
                    if b not in self.hit_targets and not b.dying and math.hypot(b.x - self.x, b.y - self.y) < 80:
                        new_target = b
                        break
                if new_target:
                    self.target = new_target
                else:
                    self.alive = False
                    return True
            else:
                self.alive = False
                return True

        self.x += dx / dist * self.speed
        self.y += dy / dist * self.speed

        # Rotação maluca da batata voadora
        self.angle = (pygame.time.get_ticks() // 8) % 360
        return False

    def draw(self):
        if self.splash > 0:
            surf = SPRITES["bullet_fire"]
        elif self.damage > 2:
            surf = SPRITES["bullet_sniper"]
        else:
            surf = SPRITES["bullet"]
            
        rotated = pygame.transform.rotate(surf, -self.angle)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated, rect.topleft)


# Grupos
towers = []
bananas = []
bullets = []
damage_numbers = []

# Variáveis do jogo
money = 120
lives = 15
font = pygame.font.SysFont("arialrounded", 32)
large_font = pygame.font.SysFont("arialrounded", 64, bold=True)
medium_font = pygame.font.SysFont("arialrounded", 40)
small_font = pygame.font.SysFont("arialrounded", 24)

selected_tower = "normal"  # normal, fries, sniper
TOWER_COSTS = {"normal": 40, "fries": 60, "sniper": 80}

# Sistema de Waves
# Formato: [Quantidade de Bananas, HP Multiplier, Speed Multiplier, Spawn Rate (frames), Probabilidades (Normal, Green, Plantain)]
WAVES = [
    [10, 1.0, 1.0, 80, [1.0, 0.0, 0.0]],  # Wave 1: Só normal
    [15, 1.1, 1.0, 70, [0.8, 0.2, 0.0]],  # Wave 2: Algumas greens
    [20, 1.2, 1.1, 60, [0.7, 0.2, 0.1]],  # Wave 3: Apresenta plantain
    [30, 1.4, 1.1, 50, [0.5, 0.3, 0.2]],  # Wave 4: Misturado
    [40, 1.7, 1.2, 40, [0.3, 0.4, 0.3]],  # Wave 5: Mais rápidas e fortes
    [50, 2.2, 1.2, 35, [0.2, 0.3, 0.5]]   # Wave 6: Muitas plantains pra aguentar tiro
]
current_wave = 0
bananas_spawned = 0
spawn_timer = 0
wave_delay_timer = 300 # Tempo antes da primeira wave e entre waves
state = "MAIN_MENU" # Estados: MAIN_MENU, LEVEL_SELECT, SETTINGS, PLAYING, GAMEOVER, LEVEL_TRANSITION
slow_spell_timer = 0
explosions = []
campaign_mode = False

def get_random_banana_type(probs):
    r = random.random()
    if r < probs[0]: return "normal"
    elif r < probs[0] + probs[1]: return "green"
    else: return "plantain"

def reset_game(level=1):
    global towers, bananas, bullets, damage_numbers, money, lives, current_wave, bananas_spawned, wave_delay_timer, spawn_timer, state, selected_tower, slow_spell_timer, explosions, current_path, WAVES
    current_path = PATHS[level]
    # Torna a onda base mais dificil se for level 2
    if level == 2:
        for w in WAVES:
            w[1] += 0.5  # HP base maior
    
    towers = [PotatoTower(240, 240, "normal")]
    bananas = []
    bullets = []
    damage_numbers = []
    explosions = []
    slow_spell_timer = 0
    money = 120
    lives = 15
    current_wave = 0
    bananas_spawned = 0
    spawn_timer = 0
    wave_delay_timer = 180
    selected_tower = "normal"
    state = "PLAYING"

running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if state == "PLAYING":
                if event.key == pygame.K_1: selected_tower = "normal"
                elif event.key == pygame.K_2: selected_tower = "fries"
                elif event.key == pygame.K_3: selected_tower = "sniper"
                elif event.key == pygame.K_q: # Purê Lento
                    if money >= 150 and slow_spell_timer <= 0:
                        money -= 150
                        slow_spell_timer = 180 # 3 segundos
                        fx_slow.play()
                elif event.key == pygame.K_w: # Bomba de Ketchup
                    selected_tower = "ketchup"
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state == "MAIN_MENU":
                x, y = pygame.mouse.get_pos()
                btn_w, btn_h = 240, 50
                start_x = WIDTH//2 - btn_w//2
                start_y = HEIGHT//2 - 40
                
                # Botões: Campanha, Níveis, Config, Sair
                if start_x <= x <= start_x + btn_w:
                    if start_y <= y <= start_y + btn_h:
                        campaign_mode = True
                        reset_game(level=1)
                    elif start_y + 70 <= y <= start_y + 70 + btn_h:
                        campaign_mode = False
                        state = "LEVEL_SELECT"
                    elif start_y + 140 <= y <= start_y + 140 + btn_h:
                        state = "SETTINGS"
                    elif start_y + 210 <= y <= start_y + 210 + btn_h:
                        running = False
                        
            elif state == "LEVEL_SELECT":
                x, y = pygame.mouse.get_pos()
                btn_w, btn_h = 180, 50
                b1_x, b1_y = WIDTH//2 - 200, HEIGHT//2 - 20
                b2_x, b2_y = WIDTH//2 + 20, HEIGHT//2 - 20
                b_voltar_x, b_voltar_y = WIDTH//2 - 90, HEIGHT//2 + 80
                
                if b1_x <= x <= b1_x + btn_w and b1_y <= y <= b1_y + btn_h:
                    reset_game(level=1)
                elif b2_x <= x <= b2_x + btn_w and b2_y <= y <= b2_y + btn_h:
                    reset_game(level=2)
                elif b_voltar_x <= x <= b_voltar_x + 180 and b_voltar_y <= y <= b_voltar_y + 50:
                    state = "MAIN_MENU"

            elif state == "SETTINGS":
                x, y = pygame.mouse.get_pos()
                # Botões de Voltar
                if WIDTH//2 - 90 <= x <= WIDTH//2 + 90 and HEIGHT//2 + 150 <= y <= HEIGHT//2 + 200:
                    state = "MAIN_MENU"
                
                # Sliders simplificados
                # Music: Y = HEIGHT//2 - 20
                if WIDTH//2 - 100 <= x <= WIDTH//2 + 100 and HEIGHT//2 - 25 <= y <= HEIGHT//2 - 5:
                    global_music_vol = (x - (WIDTH//2 - 100)) / 200.0
                    global_music_vol = max(0.0, min(1.0, global_music_vol))
                    update_volumes()
                    
                # SFX: Y = HEIGHT//2 + 80
                if WIDTH//2 - 100 <= x <= WIDTH//2 + 100 and HEIGHT//2 + 75 <= y <= HEIGHT//2 + 95:
                    global_sfx_vol = (x - (WIDTH//2 - 100)) / 200.0
                    global_sfx_vol = max(0.0, min(1.0, global_sfx_vol))
                    update_volumes()
                    fx_shoot.play() # test sound

            elif state == "LEVEL_TRANSITION":
                x, y = pygame.mouse.get_pos()
                if WIDTH//2 - 100 <= x <= WIDTH//2 + 100 and HEIGHT//2 + 50 <= y <= HEIGHT//2 + 100:
                    # Mudar para level 2 mantendo recursos
                    current_path = PATHS[2]
                    for w in WAVES: w[1] += 0.5 # Aumento de dificildade
                    towers.clear()
                    bananas.clear()
                    bullets.clear()
                    damage_numbers.clear()
                    explosions.clear()
                    current_wave = 0
                    bananas_spawned = 0
                    wave_delay_timer = 180
                    state = "PLAYING"

            elif state == "GAMEOVER":
                state = "MAIN_MENU"
                fx_shoot.play() # Feedback sonoro menu
            elif state == "PLAYING":
                x, y = pygame.mouse.get_pos()
                if y < 80: continue # Área da UI
                
                # Check se clicou em torre existente (Upgrade)
                clicked_tower = None
                for t in towers:
                    if math.hypot(t.x - x, t.y - y) < 25:
                        clicked_tower = t
                        break
                
                if clicked_tower:
                    if clicked_tower.level == 1 and money >= clicked_tower.upgrade_cost:
                        clicked_tower.upgrade()
                        money -= clicked_tower.upgrade_cost
                        fx_buy.play()
                    continue # não planta torre em cima

                # Senão tenta plantar torre ou castar magia
                if selected_tower == "ketchup":
                    if money >= 200:
                        money -= 200
                        explosions.append([x, y, 0]) # x, y, raio inicial
                        # Dano massivo em área
                        for b in bananas:
                            if not b.dying and math.hypot(b.x - x, b.y - y) < 150:
                                b.health -= 50
                                damage_numbers.append(DamageNumber(b.x, b.y, 50))
                                if b.health <= 0:
                                    b.dying = True
                                    b.die_timer = 0
                        fx_ketchup.play() # Feedback sonoro profissional para bomba de ketchup
                        selected_tower = "normal" # reseta ferramenta
                    continue

                cost = TOWER_COSTS.get(selected_tower, 40)
                if money >= cost:
                    too_close = False
                    for px, py in current_path:
                        if math.hypot(px - x, py - y) < 60:
                            too_close = True
                            break
                    for t in towers:
                        if math.hypot(t.x - x, t.y - y) < 40:
                            too_close = True
                            break
                            
                    if not too_close:
                        towers.append(PotatoTower(x, y, selected_tower))
                        money -= cost
                        fx_buy.play()

    if state in ["MAIN_MENU", "LEVEL_SELECT", "SETTINGS"]:
        screen.fill((40, 120, 40))
        
        # Título com Sombra
        title = large_font.render("BATATA TOWER", True, YELLOW)
        title_shadow = large_font.render("BATATA TOWER", True, (20, 60, 20))
        screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 4, 60 + 4))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        
        mx, my = pygame.mouse.get_pos()
        
        if state == "MAIN_MENU":
            btn_w, btn_h = 240, 50
            start_x = WIDTH//2 - btn_w//2
            start_y = HEIGHT//2 - 40
            
            buttons = [
                ("Jogar Campanha", start_y),
                ("Escolher Nível", start_y + 70),
                ("Configurações", start_y + 140),
                ("Sair", start_y + 210)
            ]
            
            for text, by in buttons:
                hover = start_x <= mx <= start_x + btn_w and by <= my <= by + btn_h
                col = (100, 230, 100) if hover else (80, 200, 80)
                if text == "Sair": col = (230, 100, 100) if hover else (200, 80, 80)
                
                pygame.draw.rect(screen, col, (start_x, by, btn_w, btn_h), border_radius=8)
                pygame.draw.rect(screen, (30, 100, 30), (start_x, by, btn_w, btn_h), 3, border_radius=8)
                txt = font.render(text, True, BLACK)
                screen.blit(txt, (start_x + btn_w//2 - txt.get_width()//2, by + btn_h//2 - txt.get_height()//2))

        elif state == "LEVEL_SELECT":
            btn_w, btn_h = 180, 50
            b1_x, b1_y = WIDTH//2 - 200, HEIGHT//2 - 20
            b2_x, b2_y = WIDTH//2 + 20, HEIGHT//2 - 20
            b_voltar_x, b_voltar_y = WIDTH//2 - 90, HEIGHT//2 + 80
            
            # Hover Nível 1 & 2
            col1 = (100, 230, 100) if b1_x <= mx <= b1_x + btn_w and b1_y <= my <= b1_y + btn_h else (80, 200, 80)
            col2 = (230, 190, 100) if b2_x <= mx <= b2_x + btn_w and b2_y <= my <= b2_y + btn_h else (200, 160, 80)
            col3 = (150, 150, 150) if b_voltar_x <= mx <= b_voltar_x + btn_w and b_voltar_y <= my <= b_voltar_y + btn_h else (100, 100, 100)
            
            pygame.draw.rect(screen, col1, (b1_x, b1_y, btn_w, btn_h), border_radius=8)
            pygame.draw.rect(screen, col2, (b2_x, b2_y, btn_w, btn_h), border_radius=8)
            pygame.draw.rect(screen, col3, (b_voltar_x, b_voltar_y, btn_w, btn_h), border_radius=8)
            
            pygame.draw.rect(screen, (30, 100, 30), (b1_x, b1_y, btn_w, btn_h), 3, border_radius=8)
            pygame.draw.rect(screen, (100, 80, 40), (b2_x, b2_y, btn_w, btn_h), 3, border_radius=8)
            pygame.draw.rect(screen, (50, 50, 50), (b_voltar_x, b_voltar_y, btn_w, btn_h), 3, border_radius=8)
            
            lvl1_txt = font.render("GRAMA (Lvl 1)", True, BLACK)
            lvl2_txt = font.render("DESERTO (Lvl 2)", True, BLACK)
            volt_txt = font.render("Voltar", True, WHITE)
            
            screen.blit(lvl1_txt, (b1_x + btn_w//2 - lvl1_txt.get_width()//2, b1_y + btn_h//2 - lvl1_txt.get_height()//2))
            screen.blit(lvl2_txt, (b2_x + btn_w//2 - lvl2_txt.get_width()//2, b2_y + btn_h//2 - lvl2_txt.get_height()//2))
            screen.blit(volt_txt, (b_voltar_x + btn_w//2 - volt_txt.get_width()//2, b_voltar_y + btn_h//2 - volt_txt.get_height()//2))

        elif state == "SETTINGS":
            # Textos de Configuração
            mus_txt = medium_font.render("Volume da Música", True, WHITE)
            sfx_txt = medium_font.render("Volume dos Efeitos", True, WHITE)
            screen.blit(mus_txt, (WIDTH//2 - mus_txt.get_width()//2, HEIGHT//2 - 60))
            screen.blit(sfx_txt, (WIDTH//2 - sfx_txt.get_width()//2, HEIGHT//2 + 40))
            
            # Trilhos
            pygame.draw.rect(screen, BLACK, (WIDTH//2 - 100, HEIGHT//2 - 20, 200, 10))
            pygame.draw.rect(screen, BLACK, (WIDTH//2 - 100, HEIGHT//2 + 80, 200, 10))
            
            # Barras preenchidas
            pygame.draw.rect(screen, YELLOW, (WIDTH//2 - 100, HEIGHT//2 - 20, int(200 * global_music_vol), 10))
            pygame.draw.rect(screen, YELLOW, (WIDTH//2 - 100, HEIGHT//2 + 80, int(200 * global_sfx_vol), 10))
            
            # Botões/Bolinhas
            pygame.draw.circle(screen, WHITE, (int(WIDTH//2 - 100 + 200 * global_music_vol), HEIGHT//2 - 15), 10)
            pygame.draw.circle(screen, WHITE, (int(WIDTH//2 - 100 + 200 * global_sfx_vol), HEIGHT//2 + 85), 10)
            
            # Botão Voltar
            btn_w, btn_h = 180, 50
            b_voltar_x, b_voltar_y = WIDTH//2 - 90, HEIGHT//2 + 150
            hover = b_voltar_x <= mx <= b_voltar_x + btn_w and b_voltar_y <= my <= b_voltar_y + btn_h
            col3 = (150, 150, 150) if hover else (100, 100, 100)
            
            pygame.draw.rect(screen, col3, (b_voltar_x, b_voltar_y, btn_w, btn_h), border_radius=8)
            pygame.draw.rect(screen, (50, 50, 50), (b_voltar_x, b_voltar_y, btn_w, btn_h), 3, border_radius=8)
            volt_txt = font.render("Voltar", True, WHITE)
            screen.blit(volt_txt, (b_voltar_x + btn_w//2 - volt_txt.get_width()//2, b_voltar_y + btn_h//2 - volt_txt.get_height()//2))

        pygame.display.flip()
        continue

    elif state == "GAMEOVER":
        screen.fill((40, 40, 40))
        gameover_txt = large_font.render("GAME OVER", True, (255, 80, 80))
        stats_txt = medium_font.render(f"Você sobreviveu até a Wave {current_wave + 1}", True, WHITE)
        restart_txt = font.render("Clique para voltar ao menu", True, YELLOW)
        
        screen.blit(gameover_txt, (WIDTH//2 - gameover_txt.get_width()//2, HEIGHT//2 - 80))
        screen.blit(stats_txt, (WIDTH//2 - stats_txt.get_width()//2, HEIGHT//2))
        screen.blit(restart_txt, (WIDTH//2 - restart_txt.get_width()//2, HEIGHT//2 + 60))
        pygame.display.flip()
        continue

    elif state == "LEVEL_TRANSITION":
        screen.fill((60, 100, 60))
        trans_txt = large_font.render("NÍVEL 1 CONCLUÍDO!", True, YELLOW)
        aviso_txt = medium_font.render("As bananas do deserto estão atacando!", True, WHITE)
        
        mx, my = pygame.mouse.get_pos()
        btn_w, btn_h = 200, 50
        bt_x, bt_y = WIDTH//2 - 100, HEIGHT//2 + 50
        
        hover = bt_x <= mx <= bt_x + btn_w and bt_y <= my <= bt_y + btn_h
        col = (100, 230, 100) if hover else (80, 200, 80)
        
        pygame.draw.rect(screen, col, (bt_x, bt_y, btn_w, btn_h), border_radius=8)
        pygame.draw.rect(screen, (30, 100, 30), (bt_x, bt_y, btn_w, btn_h), 3, border_radius=8)
        
        bt_txt = font.render("Ir para o Deserto", True, BLACK)
        
        screen.blit(trans_txt, (WIDTH//2 - trans_txt.get_width()//2, HEIGHT//2 - 80))
        screen.blit(aviso_txt, (WIDTH//2 - aviso_txt.get_width()//2, HEIGHT//2))
        screen.blit(bt_txt, (bt_x + btn_w//2 - bt_txt.get_width()//2, bt_y + btn_h//2 - bt_txt.get_height()//2))
        pygame.display.flip()
        continue

    elif state == "PLAYING":
        if slow_spell_timer > 0:
            slow_spell_timer -= 1

        # Lógica de Waves
        if wave_delay_timer > 0:
            wave_delay_timer -= 1
        else:
            wave_info = WAVES[min(current_wave, len(WAVES)-1)]
            target_bananas = wave_info[0]
            hp_mult = wave_info[1]
            speed_mult = wave_info[2]
            spawn_rate = wave_info[3]
            probs = wave_info[4]
            
            # Ajuste endless após wave 6
            if current_wave >= len(WAVES):
                target_bananas += (current_wave - len(WAVES) + 1) * 15
                hp_mult += (current_wave - len(WAVES) + 1) * 0.4
                spawn_rate = max(8, spawn_rate - 2)
                probs = [0.2, 0.4, 0.4]

            if bananas_spawned < target_bananas:
                spawn_timer += 1
                if spawn_timer >= spawn_rate:
                    spawn_timer = 0
                    b_type = get_random_banana_type(probs)
                    bananas.append(Banana(b_type, hp_mult, speed_mult))
                    bananas_spawned += 1
            elif len(bananas) == 0:
                if campaign_mode and current_path == PATHS[1] and current_wave == 5:
                    # Venceu o nível 1 na campanha (6 waves)
                    state = "LEVEL_TRANSITION"
                    money += 200
                else:
                    # Wave acabou limpinha!
                    current_wave += 1
                    bananas_spawned = 0
                    wave_delay_timer = 300 # 5 segundos de paz
                    money += 50 + (current_wave * 10) # Bônus de fim de wave

    # Atualizações
    to_remove_bananas = []
    for b in bananas:
        if b.move():
            to_remove_bananas.append(b)
            if not b.dying:
                lives -= 1
                fx_hit.play()
                if lives <= 0:
                    state = "GAMEOVER"
                    fx_over.play()

    for b in to_remove_bananas:
        if b in bananas:
            bananas.remove(b)
            if b.dying:
                money += b.reward

    for t in towers:
        t.update(bananas)

    bullets[:] = [b for b in bullets if not b.update()]
    damage_numbers[:] = [dn for dn in damage_numbers if not dn.update()]

    # Desenho
    if current_path == PATHS[1]:
        screen.fill((40, 120, 40))  # fundo verde musgo
        road_color1 = (180, 140, 60)
        road_color2 = (160, 120, 50)
    else:
        screen.fill((200, 180, 100)) # fundo areia deserto
        road_color1 = (160, 100, 60)
        road_color2 = (140, 80, 50)

    # Caminho
    pygame.draw.lines(screen, road_color1, False, current_path, 36)
    pygame.draw.lines(screen, road_color2, False, current_path, 28)

    for t in towers:
        t.draw()

    for b in bananas:
        b.draw()

    for bullet in bullets:
        bullet.draw()
        
    for dn in damage_numbers:
        dn.draw()

    for exp in explosions:
        exp[2] += 8 # aumenta o raio
        thickness = max(1, 15 - exp[2]//10)
        pygame.draw.circle(screen, (255, 80, 50), (int(exp[0]), int(exp[1])), int(exp[2]), thickness)
    explosions[:] = [exp for exp in explosions if exp[2] < 150]

    # Interface Superior Direita
    pygame.draw.rect(screen, (30, 90, 30), (0, 0, WIDTH, 40))
    pygame.draw.line(screen, (20, 60, 20), (0, 40), (WIDTH, 40), 3)

    money_text = font.render(f"R$ {money}", True, YELLOW)
    lives_text = font.render(f"Vidas: {lives}", True, (255, 100, 100))
    wave_text = font.render(f"Wave: {current_wave+1}", True, (100, 200, 255))
    
    screen.blit(lives_text, (20, 5))
    screen.blit(money_text, (150, 5))
    screen.blit(wave_text, (WIDTH - 140, 5))
    
    # Barra de Seleção de Torres na UI
    pygame.draw.rect(screen, (50, 50, 50), (280, 5, 450, 30), border_radius=6)
    
    towers_ui = [
        ("1: Normal ($40)", "normal", 290),
        ("2: Frita ($60)", "fries", 440),
        ("3: Doce ($80)", "sniper", 580)
    ]
    
    for text, t_type, tx in towers_ui:
        color = YELLOW if selected_tower == t_type else (150, 150, 150)
        ui_txt = small_font.render(text, True, color)
        screen.blit(ui_txt, (tx, 10))

    # Magias UI
    pygame.draw.rect(screen, (60, 40, 60), (330, 40, 140, 26), border_radius=6)
    q_color = (150, 255, 100) if money >= 150 and slow_spell_timer <= 0 else (150, 150, 150)
    q_txt = small_font.render("Q: Lento ($150)", True, q_color)
    screen.blit(q_txt, (340, 43))
    
    pygame.draw.rect(screen, (80, 40, 40), (480, 40, 145, 26), border_radius=6)
    w_color = YELLOW if selected_tower == "ketchup" else (255, 100, 100) if money >= 200 else (150, 150, 150)
    w_txt = small_font.render("W: Bomba ($200)", True, w_color)
    screen.blit(w_txt, (490, 43))

    # Efeito visual de Purê Lento ativo
    if slow_spell_timer > 0:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((150, 255, 100, 20)) # Verde transparente na tela toda
        screen.blit(overlay, (0, 0))
        slow_txt = font.render(f"PURÊ LENTO: {(slow_spell_timer//60)+1}s", True, (150, 255, 100))
        screen.blit(slow_txt, (WIDTH//2 - slow_txt.get_width()//2, 100))

    # Mouse interact preview (Preço da torre ou Upgrade ou Bomba)
    mx, my = pygame.mouse.get_pos()
    if my > 80: # Se não tiver mouse na UI
        if selected_tower == "ketchup":
            if money >= 200:
                cost_txt = pygame.font.SysFont("arialrounded", 18).render(f"BOMBA! (R$200)", True, (255, 100, 100))
                pygame.draw.circle(screen, (255, 100, 100, 100), (mx, my), 150, 2)
            else:
                cost_txt = pygame.font.SysFont("arialrounded", 18).render(f"Sem dinheiro", True, (255, 80, 80))
            screen.blit(cost_txt, (mx + 15, my + 15))
        else:
            hovered_tower = None
            for t in towers:
                if math.hypot(t.x - mx, t.y - my) < 25:
                    hovered_tower = t
                    break
                    
            if hovered_tower:
                if hovered_tower.level == 1:
                    cost = hovered_tower.upgrade_cost
                    pygame.draw.circle(screen, YELLOW, (hovered_tower.x, hovered_tower.y), 30, 2)
                    if money >= cost:
                        txt = pygame.font.SysFont("arialrounded", 18).render(f"UP Lvl 2 (R${cost})", True, (150, 255, 100))
                    else:
                        txt = pygame.font.SysFont("arialrounded", 18).render(f"Pobre (R${cost})", True, (255, 80, 80))
                    screen.blit(txt, (mx + 15, my + 15))
            else:
                # Comprando torre nova
                cost = TOWER_COSTS.get(selected_tower, 40)
                tower_range = 110
                if selected_tower == "sniper": tower_range = 230
                elif selected_tower == "fries": tower_range = 85
                
                if money >= cost:
                    cost_txt = pygame.font.SysFont("arialrounded", 18).render(f"Plantar (R${cost})", True, WHITE)
                    pygame.draw.circle(screen, (255, 255, 255, 100), (mx, my), tower_range, 1)
                    screen.blit(cost_txt, (mx + 15, my + 15))
                else:
                    cost_txt = pygame.font.SysFont("arialrounded", 18).render(f"Sem dinheiro", True, (255, 80, 80))
                    pygame.draw.circle(screen, (255, 80, 80, 100), (mx, my), tower_range, 1)
                    screen.blit(cost_txt, (mx + 15, my + 15))

    # Anúncio de Wave
    if wave_delay_timer > 0:
        delay_sec = wave_delay_timer // 60
        if delay_sec > 0:
            msg = f"Wave {current_wave + 1} começa em {delay_sec}..."
            msg_txt = medium_font.render(msg, True, WHITE)
            # Fundo escuro atrás do texto para dar contraste
            rect = msg_txt.get_rect(center=(WIDTH//2, 80))
            pygame.draw.rect(screen, (0, 0, 0, 150), rect.inflate(20, 10), border_radius=8)
            screen.blit(msg_txt, rect)

    pygame.display.flip()

# Limpar arquivos temporários de som
pygame.quit()
try: os.remove("snd_over.wav")
except: pass
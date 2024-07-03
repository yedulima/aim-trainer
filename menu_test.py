import pygame as pg
from random import randint
import sys

pg.init()
pg.font.init()

# == Colors ==
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# == Screen sets ==
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 640

BACKGROUND_COLOR: tuple = (105, 105, 105)
BACKGROUND_IMAGE = pg.image.load('Background.jpeg')

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Aim Trainer")

clock = pg.time.Clock()

running: bool = True

# == Menu settings ==
font = pg.font.Font(None, 36)

option1 = font.render('JOGAR', True, WHITE)
option1_rect = option1.get_rect(center=(SCREEN_WIDTH//2, 150))

option2 = font.render('SAIR', True, WHITE)
option2_rect = option2.get_rect(center=(SCREEN_WIDTH//2, 200))

# == Game settings ==
timer: int = 60

# == Font sets ==
game_title_font = pg.font.SysFont('Helvetica', 70)
sub_title_font = pg.font.SysFont('Helvatica', 40)
default_font = pg.font.SysFont('Helvetica', 30)

# == Targets sets ==
TARGET_WIDTH: int = 70
TARGET_HEIGHT: int = 70

TARGET_IMAGE = pg.image.load('target.png')
BOW_SFX = pg.mixer.Sound('BowSFX.mp3')

targets: dict = {}

LIFE_TIME: int = 600  # Tempo que o alvo passará na tela (em frames)
MAX_TARGETS: int = 10  # Número de alvos máximos que poderão aparecer na tela de uma só vez

clicks: int = 0 # Cliques do jogador
points: int = 0  # Pontuação do jogador
misses: int = 0  # Erros do jogador

def getNumOfTargets() -> int:
    """
    Retorna o número de alvos na tela.
    """
    return len(targets)

def generateRandomPos() -> tuple:
    """
    Gera uma posição aleatória.
    """
    target_x: int = randint(50, SCREEN_WIDTH - (TARGET_WIDTH + 50))
    target_y: int = randint(130, SCREEN_HEIGHT - (TARGET_HEIGHT + 50))
    return target_x, target_y

def isOverlapping(new_rect) -> bool:
    """
    Verifica se o novo retângulo colide com algum dos retângulos existentes.
    """
    rect = new_rect.get_rect()
    for target in targets.values():
        if rect.colliderect(target[0].get_rect()):
            return True
    return False

def createTarget() -> None:
    """
    Faz um objeto, retângulo, com base na posição gerada no
    generateRandomPos e nas dimensões presetadas.
    Garante que o novo alvo não se sobreponha a outros alvos.
    """
    while True:
        target_x, target_y = generateRandomPos()
        new_target = pg.transform.scale(TARGET_IMAGE, (TARGET_WIDTH, TARGET_HEIGHT))

        appendTarget(new_target, (target_x, target_y), [TARGET_WIDTH, TARGET_HEIGHT])

        break
        
        if not isOverlapping(new_target):
            appendTarget(new_target, (target_x, target_y), [TARGET_WIDTH, TARGET_HEIGHT])
            break

def appendTarget(new_target, pos, scale) -> None:
    """
    Cria um alvo dentro do dicionário targets.
    """
    targets[pos] = [new_target, LIFE_TIME, scale]

def updateAndDrawTargets() -> None:
    """
    Atualiza o tempo de vida dos alvos e desenha os alvos na tela.
    Remove alvos cujo tempo de vida chegou a zero.
    """
    global misses
    for pos in list(targets.keys()):
        target, time_left, scale = targets[pos]
        time_left -= 1
        
        if time_left <= 150:
            del targets[pos]
            misses += 1
        else:
            targets[pos][1] = time_left
            
            # Calcula o novo tamanho do alvo com base no tempo de vida restante
            shrink_factor = time_left / LIFE_TIME
            new_width = int(TARGET_WIDTH * shrink_factor)
            new_height = int(TARGET_HEIGHT * shrink_factor)
            
            # Atualiza a posição do alvo para mantê-lo centrado
            new_x = pos[0] + (TARGET_WIDTH - new_width) // 2
            new_y = pos[1] + (TARGET_HEIGHT - new_height) // 2
            scale[0] = new_width
            scale[1] = new_height

            # Imagem reescalada
            scaled_target = pg.transform.scale(target, (new_width, new_height))

            # Desenha o alvo redimensionado
            screen.blit(scaled_target, (new_x, new_y))

def handleMouseClick(pos) -> None:
    """
    Verifica se o clique do mouse está dentro de algum alvo.
    Se sim, aumenta os pontos e remove o alvo.
    """
    global points
    for target_pos, (target, _, _) in list(targets.items()):
        rect = target.get_rect()
        rect.x, rect.y = target_pos  # Define a posição correta do retângulo do alvo
        
        if rect.collidepoint(pos):
            points += 1
            del targets[target_pos]
            break

# == Code ==

in_game = False

while running:
    clock.tick(30)

    screen.fill(BACKGROUND_COLOR)
    screen.blit(BACKGROUND_IMAGE, (0, 0))

    if in_game:
        # Text
        game_title_text = game_title_font.render("AIM TRAINER", True, (255, 255, 255))
        #sub_title_text = sub_title_font.render("I M P R O V E  Y O U R  A I M", True, (255, 0, 0))
        clicks_text = default_font.render(f"Clicks: {clicks}", True, (255, 255, 255))
        points_text = default_font.render(f"Points: {points}", True, (255, 255, 255))
        misses_text = default_font.render(f"Misses: {misses}", True, (255, 255, 255))
        screen.blit(game_title_text, (45, 40))
        #screen.blit(sub_title_text, (40, 100))
        screen.blit(clicks_text, (SCREEN_WIDTH - 150, 20))
        screen.blit(points_text, (SCREEN_WIDTH - 150, 50))
        screen.blit(misses_text, (SCREEN_WIDTH - 150, 80))

        # Targets
        if getNumOfTargets() < MAX_TARGETS:
            createTarget()

        updateAndDrawTargets()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                pg.mixer.Sound.play(BOW_SFX)
                clicks += 1
                handleMouseClick(event.pos)
        
    else:
        screen.blit(option1, option1_rect)
        screen.blit(option2, option2_rect)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.MOUSEBUTTONDOWN:
                # Verifica se o clique do mouse foi em alguma opção
                pos = pg.mouse.get_pos()
                
                # Exemplo: clique na "Opção 1"
                if option1_rect.collidepoint(pos):
                    in_game = True
                    
                # Exemplo: clique na "Opção 2"
                elif option2_rect.collidepoint(pos):
                    running = False

    pg.display.update()

pg.quit()
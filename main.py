import pygame as pg
from random import randint

pg.init()
pg.font.init()

# == Screen sets ==
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 640

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Aim Trainer")

clock = pg.time.Clock()

running: bool = True

# == Game settings ==
timer: int = 60

# == Font sets ==
game_title_font = pg.font.SysFont('Helvetica', 70)
sub_title_font = pg.font.SysFont('Helvatica', 40)
default_font = pg.font.SysFont('Helvetica', 30)

# == Targets sets ==
targets: dict = {}

life_time: int = 600  # Tempo que o alvo passará na tela (em frames)
max_targets: int = 10  # Número de alvos máximos que poderão aparecer na tela de uma só vez

initial_target_width: int = 50
initial_target_height: int = 50

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
    target_x: int = randint(50, SCREEN_WIDTH - (initial_target_width + 50))
    target_y: int = randint(130, SCREEN_HEIGHT - (initial_target_height + 50))
    return target_x, target_y

def isOverlapping(new_rect) -> bool:
    """
    Verifica se o novo retângulo colide com algum dos retângulos existentes.
    """
    for target in targets.values():
        if new_rect.colliderect(target[0]):
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
        new_target = pg.Rect(target_x, target_y, initial_target_width, initial_target_height)
        
        if not isOverlapping(new_target):
            appendTarget(new_target, (target_x, target_y))
            break

def appendTarget(new_target, pos) -> None:
    """
    Cria um alvo dentro do dicionário targets.
    """
    targets[pos] = [new_target, life_time]

def updateAndDrawTargets() -> None:
    """
    Atualiza o tempo de vida dos alvos e desenha os alvos na tela.
    Remove alvos cujo tempo de vida chegou a zero.
    """
    global misses
    for pos in list(targets.keys()):
        target, time_left = targets[pos]
        time_left -= 1
        
        if time_left <= 150:
            del targets[pos]
            misses += 1
        else:
            targets[pos][1] = time_left
            
            # Calcula o novo tamanho do alvo com base no tempo de vida restante
            shrink_factor = time_left / life_time
            new_width = int(initial_target_width * shrink_factor)
            new_height = int(initial_target_height * shrink_factor)
            
            # Atualiza a posição do alvo para mantê-lo centrado
            target.x = pos[0] + (initial_target_width - new_width) // 2
            target.y = pos[1] + (initial_target_height - new_height) // 2
            target.width = new_width
            target.height = new_height

            # Desenha o alvo redimensionado
            pg.draw.rect(screen, (255, 255, 255), target)

def handleMouseClick(pos) -> None:
    """
    Verifica se o clique do mouse está dentro de algum alvo.
    Se sim, aumenta os pontos e remove o alvo.
    """
    global points
    for target_pos, (target, _) in list(targets.items()):
        if target.collidepoint(pos):
            points += 1
            del targets[target_pos]
            break

# == Code ==

while running:
    clock.tick(30)

    screen.fill((105, 105, 105))

    # Text
    game_title_text = game_title_font.render("AIM TRAINER", True, (255, 255, 255))
    sub_title_text = sub_title_font.render("I M P R O V E  Y O U R  A I M", True, (255, 0, 0))
    clicks_text = default_font.render(f"Clicks: {clicks}", True, (255, 255, 255))
    points_text = default_font.render(f"Points: {points}", True, (255, 255, 255))
    misses_text = default_font.render(f"Misses: {misses}", True, (255, 255, 255))
    screen.blit(game_title_text, (45, 30))
    screen.blit(sub_title_text, (40, 100))
    screen.blit(clicks_text, (SCREEN_WIDTH - 150, 20))
    screen.blit(points_text, (SCREEN_WIDTH - 150, 50))
    screen.blit(misses_text, (SCREEN_WIDTH - 150, 80))

    # Targets
    if getNumOfTargets() < max_targets:
        createTarget()

    updateAndDrawTargets()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            clicks += 1
            handleMouseClick(event.pos)

    pg.display.update()

pg.quit()
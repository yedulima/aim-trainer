import pygame as pg
from random import randint

pg.init()
pg.font.init()

# == Screen sets ==
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 640

BACKGROUND_COLOR: tuple = (105, 105, 105)
BACKGROUND_IMAGE = pg.image.load('Background.jpeg')

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Aim Trainer")

clock = pg.time.Clock()

running: bool = True

# == Player sets
PLAYER_IMAGE = pg.image.load('Megumin.png')
RESIZED_PLAYER = pg.transform.scale(PLAYER_IMAGE, (70, 70))

# == Game sets ==
timer: int = 60
accuracy: float = 100.00

# == Font sets ==
game_title_font = pg.font.SysFont('Helvetica', 70)
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
            decreaseAccuracy()

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

def decreaseAccuracy() -> None:
    """
    Reduz a accurancy se o jogador errar um clique ou um alvo desaparecer.
    """
    global accuracy
    if clicks > 0:
        accuracy -= 1.0 * ((misses + points / clicks) * 2.0)
        if accuracy < 0:
            accuracy = 0
    else:
        accuracy -= 1.0

def increaseAccuracy() -> None:
    """
    Aumenta minimamente a accurancy se o jogador acertar um clique.
    """
    global accuracy
    if accuracy + 0.1 < 100.0:
        accuracy += (clicks / points)
        if accuracy > 100.0:
            accuracy = 100.0
    
def handleMouseClick(pos) -> None:
    """
    Verifica se o clique do mouse está dentro de algum alvo.
    Se sim, aumenta os pontos e remove o alvo.
    """
    global points, misses, accuracy

    found: bool = False
    
    for target_pos, (target, _, _) in list(targets.items()):
        rect = target.get_rect()
        rect.x, rect.y = target_pos  # Define a posição correta do retângulo do alvo
        
        if rect.collidepoint(pos):
            points += 1
            increaseAccuracy()
            del targets[target_pos]
            found = True
            break

    if not found:
        misses += 1
        decreaseAccuracy()

# == Code ==

while running:
    clock.tick(30)

    screen.fill(BACKGROUND_COLOR)
    screen.blit(BACKGROUND_IMAGE, (0, 0))

    # Text
    game_title_text = game_title_font.render("AIM TRAINER", True, (255, 255, 255))
    accuracy_text = default_font.render(f"Accuracy: {accuracy:.2f}", True, (255, 255, 255))
    #screen.blit(game_title_text, (45, 40))
    screen.blit(accuracy_text, (SCREEN_WIDTH - 250, 40))

    # Player
    screen.blit(RESIZED_PLAYER, (int(SCREEN_WIDTH / 2) - 10, SCREEN_HEIGHT - 60))

    # Targets
    if getNumOfTargets() < MAX_TARGETS:
        createTarget()

    updateAndDrawTargets()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            clicks += 1
            pg.mixer.Sound.play(BOW_SFX)
            handleMouseClick(event.pos)

    pg.display.update()

pg.quit()
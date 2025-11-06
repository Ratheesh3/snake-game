# snake_game_pro.py
import pygame
import sys
import random
import time
import os
import math

# ---------------- Configuration ----------------
CELL_SIZE = 20
CELL_NUMBER = 30
WIDTH = CELL_SIZE * CELL_NUMBER
HEIGHT = CELL_SIZE * CELL_NUMBER
FPS = 12

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (255, 60, 60)
GRAY = (40, 40, 40)
YELLOW = (250, 250, 50)
BLUE = (0, 150, 255)
ORANGE = (255, 160, 50)
PURPLE = (180, 0, 255)

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game Pro - Ratheesh")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 24)

# ---------------- Sound Setup ----------------
# Load optional background music
background_music_loaded = False
try:
    if os.path.exists("assets/bgm.mp3"):
        pygame.mixer.music.load("assets/bgm.mp3")
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)  # loop forever
        background_music_loaded = True
except Exception:
    background_music_loaded = False

# Load optional level up sound
try:
    levelup_sound = pygame.mixer.Sound("assets/levelup.mp3") if os.path.exists("assets/levelup.mp3") else None
except:
    levelup_sound = None

def play_beep():
    # fallback beep for when winsound isn't available
    try:
        import winsound
        winsound.Beep(440, 100)
    except:
        pass

# ---------------- High Score System ----------------
def load_highscore():
    if not os.path.exists("highscore.txt"):
        with open("highscore.txt", "w") as f:
            f.write("0,1")
        return 0, 1
    with open("highscore.txt", "r") as f:
        data = f.read().strip().split(",")
        if len(data) == 2:
            try:
                return int(data[0]), int(data[1])
            except:
                return 0, 1
        return 0, 1

def save_highscore(score, level):
    try:
        with open("highscore.txt", "w") as f:
            f.write(f"{score},{level}")
    except Exception:
        pass

high_score, high_level = load_highscore()

# ---------------- Helper Functions ----------------
def draw_text_centered(text, size, color, y_offset=0):
    f = pygame.font.SysFont("consolas", size)
    surf = f.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(surf, rect)

def draw_rect(color, pos):
    x, y = pos
    pygame.draw.rect(screen, color, pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

# ---------------- Level Design ----------------
def generate_walls(level):
    walls = []
    if level == 1:
        return walls
    elif level == 2:
        for x in range(12, 18):
            walls.append((x, 15))
        for y in range(12, 18):
            walls.append((15, y))
    elif level == 3:
        for x in range(5, 25):
            walls.append((x, 10))
            walls.append((x, 20))
    elif level == 4:
        for x in range(CELL_NUMBER):
            if x not in (0, CELL_NUMBER - 1):
                walls.append((x, 5))
                walls.append((x, CELL_NUMBER - 6))
        for y in range(CELL_NUMBER):
            if y not in (0, CELL_NUMBER - 1):
                walls.append((5, y))
                walls.append((CELL_NUMBER - 6, y))
    else:
        for _ in range(30):
            walls.append((random.randint(2, CELL_NUMBER - 3), random.randint(2, CELL_NUMBER - 3)))
    return walls

# ---------------- Game Reset ----------------
def new_game():
    mid = CELL_NUMBER // 2
    snake = [(mid, mid), (mid - 1, mid), (mid - 2, mid)]
    direction = (1, 0)
    level = 1
    walls = generate_walls(level)
    food = random_food_position(snake, walls)
    score = 0
    speed = FPS
    return snake, direction, food, score, speed, level, walls

def random_food_position(snake_positions, walls):
    while True:
        pos = (random.randint(0, CELL_NUMBER - 1), random.randint(0, CELL_NUMBER - 1))
        if pos not in snake_positions and pos not in walls:
            return pos

# ---------------- Visual Effects ----------------
def show_levelup(level):
    # short flashing level-up, non-blocking events handled
    start = time.time()
    duration = 1.2
    flash = True
    while time.time() - start < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        screen.fill(BLACK)
        draw_text_centered(f"LEVEL {level}!", 64, ORANGE if flash else WHITE)
        pygame.display.flip()
        flash = not flash
        pygame.time.wait(180)

# Draw animated objects (food glow, snake pulse, wall shimmer)
def draw_animated_objects(snake, food, walls, t):
    # Food glow
    glow = int(80 * (1 + math.sin(t * 3)) / 2)
    food_color = (255, 80 + glow, 80)
    draw_rect(food_color, food)

    # Snake pulse: head brighter, tail darker; use sinusoidal pulse per segment
    for i, pos in enumerate(snake):
        phase = (t * 6 + i * 0.5)
        pulse = int(40 * (1 + math.sin(phase)) / 2)
        if i == 0:
            color = (YELLOW[0], min(255, YELLOW[1] + pulse), 60)
        else:
            g = max(20, 200 - int(i * 4) - pulse)
            color = (0, g, 0)
        draw_rect(color, pos)

    # Walls shimmer
    for i, pos in enumerate(walls):
        shimmer = int(30 * (1 + math.sin(t * 2 + i)))  # 0-60
        color = (0, 120 + shimmer, 200)
        draw_rect(color, pos)

# ---------------- Pause Overlay ----------------
def draw_pause_overlay():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    draw_text_centered("PAUSED", 64, WHITE)
    draw_text_centered("Press P to resume", 24, GRAY, 70)

# ---------------- Game Over Animation ----------------
def game_over_fade_animation(snake, walls, food, fps_local=30):
    # Fade out the snake by drawing it on a surface and reducing its alpha progressively
    snake_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    # draw snake onto snake_surf
    snake_surf.fill((0,0,0,0))
    for i, pos in enumerate(snake):
        x, y = pos
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        color = (YELLOW[0], YELLOW[1], 50) if i == 0 else (0,200,0)
        pygame.draw.rect(snake_surf, color + (255,), rect)

    # also draw walls and food onto separate surfaces for nicer fade
    walls_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    walls_surf.fill((0,0,0,0))
    for pos in walls:
        x, y = pos
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(walls_surf, (0,150,255,255), rect)

    food_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    food_surf.fill((0,0,0,0))
    fx, fy = food
    rect = pygame.Rect(fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(food_surf, (255,100,100,255), rect)

    # Fade loop: alpha from 255 down to 0
    for alpha in range(255, -1, -10):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        screen.fill(BLACK)
        draw_grid()
        # draw background grid + dim overlay
        # blit food and walls (full color) but fade the snake layer
        screen.blit(walls_surf, (0,0))
        screen.blit(food_surf, (0,0))
        temp = snake_surf.copy()
        temp.set_alpha(alpha)
        screen.blit(temp, (0,0))

        # dimming overlay to emphasize fade
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int((255-alpha)*0.25)))
        screen.blit(overlay, (0,0))

        draw_text_centered("GAME OVER", 56, RED, -40)
        pygame.display.flip()
        pygame.time.wait(int(1000 / fps_local))
    # small pause after animation
    pygame.time.wait(350)

# ---------------- Menu Screen ----------------
def main_menu():
    selected = 0
    options = ["Start Game", "View Controls", "Quit"]

    while True:
        screen.fill(BLACK)
        draw_text_centered("🐍 SNAKE GAME PRO 🐍", 48, ORANGE, -120)
        for i, option in enumerate(options):
            color = YELLOW if i == selected else WHITE
            draw_text_centered(option, 32, color, i * 60 - 20)
        draw_text_centered("Use ↑ ↓ to move, Enter to select", 20, GRAY, 200)
        # show small hint about pause and music
        hint = "P: Pause/Resume   |   M: Toggle Music   |   R: Restart on Game Over"
        surf = font.render(hint, True, GRAY)
        rect = surf.get_rect(center=(WIDTH//2, HEIGHT - 30))
        screen.blit(surf, rect)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        return "start"
                    elif selected == 1:
                        show_controls()
                    elif selected == 2:
                        pygame.quit(); sys.exit()
        clock.tick(12)

def show_controls():
    while True:
        screen.fill(BLACK)
        draw_text_centered("🕹 CONTROLS 🕹", 44, ORANGE, -160)
        controls = [
            "Arrow Keys / W A S D  → Move Snake",
            "P → Pause / Resume",
            "M → Toggle Background Music On/Off",
            "R → Restart (when Game Over)",
            "Q → Return to Menu (when Game Over)",
            "",
            "Eat food to grow and score points.",
            "Every 5 points = Level Up (new walls + speed).",
        ]
        for i, line in enumerate(controls):
            surf = font.render(line, True, WHITE)
            rect = surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 40 + i*30))
            screen.blit(surf, rect)
        draw_text_centered("Press ESC to return", 20, GRAY, 200)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        clock.tick(12)

# ---------------- Main Game Loop ----------------
def game_loop():
    global high_score, high_level, background_music_loaded
    snake, direction, food, score, speed, level, walls = new_game()
    running = True
    game_over = False
    allow_dir = True
    paused = False
    music_on = background_music_loaded

    # If background music is present and not playing, start it
    try:
        if background_music_loaded and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
            music_on = True
    except:
        music_on = background_music_loaded

    while running:
        # if paused, we sleep slower loop but still handle events
        if paused:
            clock.tick(6)
        else:
            clock.tick(speed)

        t = pygame.time.get_ticks() / 500.0  # animation time variable

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                # Toggle pause
                if event.key == pygame.K_p:
                    paused = not paused
                # Toggle music on/off
                if event.key == pygame.K_m:
                    if music_on:
                        try:
                            pygame.mixer.music.pause()
                        except:
                            pass
                        music_on = False
                    else:
                        try:
                            pygame.mixer.music.unpause()
                        except:
                            pass
                        music_on = True

                # If game is not over and not paused, process movement keys
                if not game_over and not paused:
                    if allow_dir:
                        if event.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                            direction = (0, -1); allow_dir = False
                        elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                            direction = (0, 1); allow_dir = False
                        elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                            direction = (-1, 0); allow_dir = False
                        elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                            direction = (1, 0); allow_dir = False
                # If game over, allow restart or return to menu
                elif game_over:
                    if event.key == pygame.K_r:
                        return "restart"
                    elif event.key == pygame.K_q:
                        return "menu"

        if not game_over and not paused:
            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)
            allow_dir = True

            # Collisions
            x, y = new_head
            if x < 0 or x >= CELL_NUMBER or y < 0 or y >= CELL_NUMBER or new_head in snake or new_head in walls:
                game_over = True
                # update high score if beaten
                if score > high_score:
                    high_score = score
                    high_level = level
                    save_highscore(high_score, high_level)
                    # small positive feedback
                # play a sound or small pause
                try:
                    pygame.mixer.Sound.play(pygame.mixer.Sound("gameover.wav")) if os.path.exists("gameover.wav") else None
                except:
                    pass

                # run custom game over fade animation
                game_over_fade_animation(snake, walls, food, fps_local=30)

            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 1
                    # Level up every 5 points
                    if score % 5 == 0:
                        level += 1
                        speed += 1
                        walls = generate_walls(level)
                        # play level up sound if available
                        if levelup_sound:
                            try:
                                levelup_sound.play()
                            except:
                                pass
                        else:
                            play_beep()
                        show_levelup(level)
                    food = random_food_position(snake, walls)
                else:
                    snake.pop()

        # Drawing
        screen.fill(BLACK)
        draw_grid()
        draw_animated_objects(snake, food, walls, t)

        # HUD
        score_text = font.render(f"Score: {score}  Level: {level}", True, WHITE)
        high_text = font.render(f"High Score: {high_score} (Level {high_level})", True, ORANGE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_text, (10, 40))

        if paused:
            draw_pause_overlay()

        if game_over:
            # show overlay and options (after fade animation)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            draw_text_centered("GAME OVER", 56, RED, -40)
            draw_text_centered(f"Score: {score}   Level: {level}", 26, WHITE, 10)
            draw_text_centered("Press R to Restart or Q for Menu", 22, WHITE, 60)

        pygame.display.flip()

# ---------------- Run the Game ----------------
if __name__ == "__main__":
    while True:
        choice = main_menu()
        if choice == "start":
            result = game_loop()
            if result == "restart":
                continue
            elif result == "menu":
                continue

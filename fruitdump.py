import pygame
import sys
import os
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Fruitdump')

# Asset folder and fruit image filenames
ASSET_DIR = 'assets'
FRUITS = ['apple', 'mango', 'orange', 'guava']
FRUIT_IMAGES = {}
FRUIT_SIZE = (64, 64)

# Load fruit images and scale to 64x64
for fruit in FRUITS:
    path = os.path.join(ASSET_DIR, f'{fruit}.png')
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        FRUIT_IMAGES[fruit] = pygame.transform.smoothscale(img, FRUIT_SIZE)
    else:
        FRUIT_IMAGES[fruit] = None  # Placeholder if image not found

# Box settings
BOX_WIDTH, BOX_HEIGHT = 120, 80
BOX_Y = HEIGHT - 120
BOX_MARGIN = 40
FONT = pygame.font.SysFont('arial', 28, bold=True)
BIG_FONT = pygame.font.SysFont('arial', 48, bold=True)

# Conveyor settings
CONVEYOR_WIDTH = 80
CONVEYOR_COLOR = (180, 180, 180)

# Fruit settings
FRUIT_START_SPEED = 3
SPEED_INCREASE = 0.02  # 2% per point

# Initialize game state
def reset_round():
    global left_label, right_label, current_fruit, fruit_y
    left_label = random.choice(FRUITS)
    right_label = random.choice([f for f in FRUITS if f != left_label])
    current_fruit = random.choice(FRUITS)
    fruit_y = 60

# Initialize variables so they are always in scope
left_label = FRUITS[0]
right_label = FRUITS[1]
current_fruit = FRUITS[2]
fruit_y = 60

reset_round()
fruit_speed = FRUIT_START_SPEED
score = 0
is_game_over = False

def draw_game():
    screen.fill((255, 255, 255))  # White background

    # Draw conveyor belt
    conveyor_rect = pygame.Rect((WIDTH//2 - CONVEYOR_WIDTH//2, 0, CONVEYOR_WIDTH, HEIGHT))
    pygame.draw.rect(screen, CONVEYOR_COLOR, conveyor_rect)

    # Draw left box
    left_box_rect = pygame.Rect(BOX_MARGIN, BOX_Y, BOX_WIDTH, BOX_HEIGHT)
    pygame.draw.rect(screen, (220, 220, 250), left_box_rect, border_radius=12)
    left_text = FONT.render(left_label.capitalize(), True, (60, 60, 120))
    screen.blit(left_text, (left_box_rect.centerx - left_text.get_width()//2, left_box_rect.centery - left_text.get_height()//2))

    # Draw right box
    right_box_rect = pygame.Rect(WIDTH - BOX_MARGIN - BOX_WIDTH, BOX_Y, BOX_WIDTH, BOX_HEIGHT)
    pygame.draw.rect(screen, (250, 220, 220), right_box_rect, border_radius=12)
    right_text = FONT.render(right_label.capitalize(), True, (120, 60, 60))
    screen.blit(right_text, (right_box_rect.centerx - right_text.get_width()//2, right_box_rect.centery - right_text.get_height()//2))

    # Draw fruit moving down the conveyor
    fruit_img = FRUIT_IMAGES[current_fruit]
    fruit_x = WIDTH // 2
    if fruit_img:
        rect = fruit_img.get_rect(center=(fruit_x, fruit_y))
        screen.blit(fruit_img, rect)
    else:
        pygame.draw.circle(screen, (200, 0, 0), (fruit_x, fruit_y), 32)

    # Draw score
    score_text = FONT.render(f"Score: {score}", True, (40, 40, 40))
    screen.blit(score_text, (20, 20))

    if is_game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 220))
        screen.blit(overlay, (0, 0))
        game_over_text = BIG_FONT.render("Game Over!", True, (200, 0, 0))
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 60))
        final_score_text = FONT.render(f"Final Score: {score}", True, (0, 0, 0))
        screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2))
        restart_text = FONT.render("Press R to Restart", True, (0, 0, 0))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 40))

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if is_game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                score = 0
                fruit_speed = FRUIT_START_SPEED
                is_game_over = False
                reset_round()
        else:
            if event.type == pygame.KEYDOWN:
                # If neither label matches, any swipe is game over
                if current_fruit != left_label and current_fruit != right_label:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        is_game_over = True
                else:
                    if event.key == pygame.K_LEFT:
                        if current_fruit == left_label:
                            score += 1
                            fruit_speed += FRUIT_START_SPEED * SPEED_INCREASE
                            reset_round()
                        else:
                            is_game_over = True
                    elif event.key == pygame.K_RIGHT:
                        if current_fruit == right_label:
                            score += 1
                            fruit_speed += FRUIT_START_SPEED * SPEED_INCREASE
                            reset_round()
                        else:
                            is_game_over = True

    if not is_game_over:
        fruit_y += fruit_speed
        if fruit_y > HEIGHT:
            # If neither label matches, just reset round (let it pass)
            if current_fruit != left_label and current_fruit != right_label:
                reset_round()
            else:
                is_game_over = True

    draw_game()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit() 
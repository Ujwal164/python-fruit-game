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

# Conveyor settings
CONVEYOR_WIDTH = 500
CONVEYOR_COLOR = (180, 180, 180)

# Load animated conveyor frames
CONVEYOR_FRAMES = []
for i in range(1, 4):  # Load convey1.png, convey2.png, convey3.png
    path = os.path.join(ASSET_DIR, f'convey{i}.png')
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        CONVEYOR_FRAMES.append(pygame.transform.smoothscale(img, (CONVEYOR_WIDTH, HEIGHT)))
    else:
        # Fallback to JPG if PNG not found
        path = os.path.join(ASSET_DIR, f'conveyor{i}.jpg')
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            CONVEYOR_FRAMES.append(pygame.transform.smoothscale(img, (CONVEYOR_WIDTH, HEIGHT)))

# Animation settings
CONVEYOR_ANIMATION_SPEED = 0.2  # Seconds per frame
conveyor_frame_index = 0
conveyor_animation_timer = 0

# Box settings
BOX_WIDTH, BOX_HEIGHT = 220, 400
BOX_Y = 327
BOX_MARGIN = -2
FONT_PATH = os.path.join(ASSET_DIR, 'font', 'DePixelHalbfett.ttf')
FONT = pygame.font.Font(FONT_PATH, 14)  # Pixelated font from file
BIG_FONT = pygame.font.Font(FONT_PATH, 48)  # Pixelated font from file

# Load background, conveyor, and box images
BACKGROUND_IMG = pygame.image.load(os.path.join(ASSET_DIR, 'background.jpg')).convert()
BACKGROUND_IMG = pygame.transform.smoothscale(BACKGROUND_IMG, (WIDTH, HEIGHT))

BOX_LEFT_IMG = pygame.image.load(os.path.join(ASSET_DIR, 'box_left.png')).convert_alpha()
BOX_LEFT_IMG = pygame.transform.smoothscale(BOX_LEFT_IMG, (BOX_WIDTH, BOX_HEIGHT))

BOX_RIGHT_IMG = pygame.image.load(os.path.join(ASSET_DIR, 'box_right.png')).convert_alpha()
BOX_RIGHT_IMG = pygame.transform.smoothscale(BOX_RIGHT_IMG, (BOX_WIDTH, BOX_HEIGHT))

# Fruit settings
FRUIT_START_SPEED = 3  # Slower start speed
SPEED_INCREASE = 0.01  # Slower speed increase
FRUIT_START_SIZE = 0.8  # Start at 30% of normal size
FRUIT_END_SIZE = 2    # End at 100% of normal size

# Fruit sliding animation
FRUIT_SLIDE_SPEED = 3  # Pixels per frame for sliding
fruit_target_x = WIDTH // 2  # Target position for smooth sliding
reset_delay = 0  # Delay before resetting round to show sliding animation

# Initialize game state
def reset_round():
    global left_label, right_label, current_fruit, fruit_y, fruit_x, fruit_target_x, reset_delay
    left_label = random.choice(FRUITS)
    right_label = random.choice([f for f in FRUITS if f != left_label])
    current_fruit = random.choice(FRUITS)
    fruit_y = HEIGHT // 2  # Start from center of screen
    fruit_x = WIDTH // 2  # Start from center of screen
    fruit_target_x = WIDTH // 2  # Reset target position
    reset_delay = 0  # Reset delay

# Initialize variables so they are always in scope
left_label = FRUITS[0]
right_label = FRUITS[1]
current_fruit = FRUITS[2]
fruit_y = HEIGHT // 2  # Start from center of screen
fruit_x = WIDTH // 2  # Start from center of screen

reset_round()
fruit_speed = FRUIT_START_SPEED
score = 0
is_game_over = False
is_paused = False  # Add pause state

def get_fruit_scale():
    """Calculate fruit scale based on Y position (zoom out effect with falling illusion)"""
    # Calculate progress from center to bottom (0.0 to 1.0)
    center_y = HEIGHT // 2
    conveyor_end_y = HEIGHT - 150  # End of conveyor belt
    
    # If fruit is past the conveyor end, create falling effect
    if fruit_y > conveyor_end_y:
        # Calculate falling progress (0.0 to 1.0)
        fall_progress = (fruit_y - conveyor_end_y) / (HEIGHT - conveyor_end_y)
        fall_progress = max(0.0, min(1.0, fall_progress))  # Clamp between 0 and 1
        
        # Rapidly shrink the fruit as it falls
        scale = FRUIT_END_SIZE * (1.0 - fall_progress * 0.8)  # Shrink to 20% of original size
        return max(0.1, scale)  # Don't let it get too small
    
    # Normal conveyor scaling
    progress = (fruit_y - center_y) / (conveyor_end_y - center_y)
    progress = max(0.0, min(1.0, progress))  # Clamp between 0 and 1
    
    # Interpolate between start and end size
    scale = FRUIT_START_SIZE + (FRUIT_END_SIZE - FRUIT_START_SIZE) * progress
    return scale

def draw_game():
    global conveyor_animation_timer, conveyor_frame_index
    
    # Update conveyor animation
    conveyor_animation_timer += 1/60  # Assuming 60 FPS
    if conveyor_animation_timer >= CONVEYOR_ANIMATION_SPEED:
        conveyor_animation_timer = 0
        conveyor_frame_index = (conveyor_frame_index + 1) % len(CONVEYOR_FRAMES)
    
    # Draw background
    screen.blit(BACKGROUND_IMG, (0, 0))

    # Draw animated conveyor belt
    conveyor_x = WIDTH // 2 - CONVEYOR_WIDTH // 2
    if CONVEYOR_FRAMES:
        screen.blit(CONVEYOR_FRAMES[conveyor_frame_index], (conveyor_x, 0))
    else:
        # Fallback to solid color if no frames loaded
        pygame.draw.rect(screen, CONVEYOR_COLOR, (conveyor_x, 0, CONVEYOR_WIDTH, HEIGHT))

    # Draw left box
    left_box_rect = pygame.Rect(-45, BOX_Y, BOX_WIDTH, BOX_HEIGHT)
    screen.blit(BOX_LEFT_IMG, (left_box_rect.x, left_box_rect.y))
    left_text = FONT.render(left_label.capitalize(), True, (255, 255, 255))
    screen.blit(left_text, (left_box_rect.centerx - left_text.get_width()//2, left_box_rect.centery - left_text.get_height()//2 +53))

    # Draw right box
    right_box_rect = pygame.Rect(WIDTH - BOX_WIDTH + 55, BOX_Y, BOX_WIDTH, BOX_HEIGHT)
    screen.blit(BOX_RIGHT_IMG, (right_box_rect.x, right_box_rect.y))
    right_text = FONT.render(right_label.capitalize(), True, (255, 255, 255))
    screen.blit(right_text, (right_box_rect.centerx - right_text.get_width()//2, right_box_rect.centery - right_text.get_height()//2 +53 ))

    # Draw fruit moving down the conveyor with zoom effect
    fruit_img = FRUIT_IMAGES[current_fruit]
    
    if fruit_img:
        # Calculate scale for zoom effect
        scale = get_fruit_scale()
        
        # Scale the fruit image
        scaled_width = int(FRUIT_SIZE[0] * scale)
        scaled_height = int(FRUIT_SIZE[1] * scale)
        
        if scaled_width > 0 and scaled_height > 0:
            scaled_fruit = pygame.transform.smoothscale(fruit_img, (scaled_width, scaled_height))
            rect = scaled_fruit.get_rect(center=(fruit_x, fruit_y))
            screen.blit(scaled_fruit, rect)
        else:
            # Fallback for very small scales
            pygame.draw.circle(screen, (200, 0, 0), (fruit_x, fruit_y), max(1, int(32 * scale)))
    else:
        # Fallback circle with zoom effect
        scale = get_fruit_scale()
        radius = max(1, int(32 * scale))
        pygame.draw.circle(screen, (200, 0, 0), (fruit_x, fruit_y), radius)

    # Draw score
    score_text = FONT.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))

    # Draw pause overlay if game is paused
    if is_paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        pause_text = BIG_FONT.render("PAUSED", True, (255, 255, 255))
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 60))
        resume_text = FONT.render("Press P to Resume", True, (255, 255, 255))
        screen.blit(resume_text, (WIDTH//2 - resume_text.get_width()//2, HEIGHT//2))

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
                is_paused = False  # Reset pause state
                reset_round()
        else:
            if event.type == pygame.KEYDOWN:
                # Pause/unpause functionality
                if event.key == pygame.K_p:
                    is_paused = not is_paused
                # Only process game controls if not paused
                elif not is_paused:
                    # Fruit sliding controls - set target positions
                    if event.key == pygame.K_LEFT:
                        # Set target for left box
                        fruit_target_x = 80  # Position near left box
                        # Check scoring for left box
                        if current_fruit != left_label and current_fruit != right_label:
                            is_game_over = True
                        elif current_fruit == left_label:
                            score += 1
                            fruit_speed += FRUIT_START_SPEED * SPEED_INCREASE
                            reset_delay = 40  # Show sliding for 2 seconds (30 FPS * 2)
                        else:
                            is_game_over = True
                    elif event.key == pygame.K_RIGHT:
                        # Set target for right box
                        fruit_target_x = WIDTH - 80  # Position near right box
                        # Check scoring for right box
                        if current_fruit != left_label and current_fruit != right_label:
                            is_game_over = True
                        elif current_fruit == right_label:
                            score += 1
                            fruit_speed += FRUIT_START_SPEED * SPEED_INCREASE
                            reset_delay = 40  # Show sliding for 2 seconds (30 FPS * 2)
                        else:
                            is_game_over = True

    if not is_game_over and not is_paused:
        # Handle reset delay
        if reset_delay > 0:
            reset_delay -= 1
            if reset_delay <= 0:
                reset_round()
        
        # Smoothly slide fruit towards the target
        if fruit_x < fruit_target_x:
            fruit_x += FRUIT_SLIDE_SPEED
            if fruit_x > fruit_target_x:
                fruit_x = fruit_target_x
        elif fruit_x > fruit_target_x:
            fruit_x -= FRUIT_SLIDE_SPEED
            if fruit_x < fruit_target_x:
                fruit_x = fruit_target_x

        fruit_y += fruit_speed
        if fruit_y > HEIGHT:
            # If neither label matches, just reset round (let it pass)
            if current_fruit != left_label and current_fruit != right_label:
                reset_round()
            else:
                is_game_over = True

    draw_game()
    pygame.display.flip()
    clock.tick(30)  # Slower frame rate (30 FPS instead of 60)

pygame.quit()
sys.exit() 
import pygame
import random
import time

WIDTH = 600
HEIGHT = 600
ROWS = 10
COLS = 10
NUM_MINES = 15
CELL_SIZE = WIDTH // COLS
STEPS_PER_SECOND = 0.5

BACKGROUND_COLOR = (220, 220, 220)
GRID_COLOR = (150, 150, 150)
CELL_COLOR_HIDDEN = (100, 100, 100)
CELL_COLOR_REVEALED = (200, 200, 200)
MINE_COLOR = (0, 0, 0)
FLAG_COLOR = (255, 0, 0)
FONT_COLOR = (0, 0, 0)
AI_CLICK_COLOR = (255, 0, 0)
BUTTON_COLOR = (0, 200, 0)
STATUS_BAR_COLOR = (200, 200, 200)
STATUS_BAR_TEXT_COLOR = (0, 0, 0)
FLASH_COLOR = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

font = pygame.font.SysFont(None, 24)

def initialize_grid():
    grid = [[0] * COLS for _ in range(ROWS)]
    mine_positions = random.sample(range(ROWS * COLS), NUM_MINES)
    for pos in mine_positions:
        row = pos // COLS
        col = pos % COLS
        grid[row][col] = '*'
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] == '*':
                continue
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if 0 <= row + dr < ROWS and 0 <= col + dc < COLS and grid[row + dr][col + dc] == '*':
                        grid[row][col] += 1
    return grid

def draw_grid(grid, revealed, ai_moves, detected_mines, mines_left):
    screen.fill(BACKGROUND_COLOR)
    for row in range(ROWS):
        for col in range(COLS):
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            if not revealed[row][col]:
                pygame.draw.rect(screen, CELL_COLOR_HIDDEN, rect)
                pygame.draw.rect(screen, GRID_COLOR, rect, 1)
                if (row, col) in ai_moves:
                    pygame.draw.circle(screen, AI_CLICK_COLOR, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 5)
            else:
                pygame.draw.rect(screen, CELL_COLOR_REVEALED, rect)
                pygame.draw.rect(screen, GRID_COLOR, rect, 1)
                if grid[row][col] == 0:
                    continue
                text = font.render(str(grid[row][col]), True, FONT_COLOR)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
                
            if (row, col) in detected_mines:
                pygame.draw.circle(screen, MINE_COLOR, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 5)

    draw_status_bar(mines_left)

def reveal(grid, revealed, row, col):
    if revealed[row][col]:
        return
    revealed[row][col] = True
    if grid[row][col] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if 0 <= row + dr < ROWS and 0 <= col + dc < COLS:
                    reveal(grid, revealed, row + dr, col + dc)

def ai_play(grid, revealed, detected_mines, mines_left):
    move = make_safe_move(grid, revealed)
    if move:
        return move
    else:
        move = make_random_move(grid, revealed)
        if grid[move[0]][move[1]] == '*':
            detected_mines.append(move)
            mines_left -= 1
        return move

def count_adjacent_flags(grid, revealed, row, col):
    count = 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if 0 <= row + dr < ROWS and 0 <= col + dc < COLS:
                if revealed[row + dr][col + dc] and grid[row + dr][col + dc] == '*':
                    count += 1
    return count

def make_safe_move(grid, revealed):
    for row in range(ROWS):
        for col in range(COLS):
            if revealed[row][col] and grid[row][col] > 0 and grid[row][col] == count_adjacent_flags(grid, revealed, row, col):
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if 0 <= row + dr < ROWS and 0 <= col + dc < COLS:
                            if not revealed[row + dr][col + dc]:
                                return row + dr, col + dc
    return None

def make_random_move(grid, revealed):
    while True:
        row = random.randint(0, ROWS - 1)
        col = random.randint(0, COLS - 1)
        if not revealed[row][col]:
            return row, col

def draw_button(text, rect, color):
    pygame.draw.rect(screen, color, rect)
    text_surface = font.render(text, True, FONT_COLOR)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def draw_status_bar(mines_left):
    status_bar_rect = pygame.Rect(0, HEIGHT - 50, WIDTH, 50)
    pygame.draw.rect(screen, STATUS_BAR_COLOR, status_bar_rect)
    text_surface = font.render(f"Mines Left: {mines_left}", True, STATUS_BAR_TEXT_COLOR)
    text_rect = text_surface.get_rect(midleft=(10, HEIGHT - 25))
    screen.blit(text_surface, text_rect)

def draw_you_won():
    flash_timer = 0
    while flash_timer < 1:
        screen.fill(FLASH_COLOR)
        text_surface = font.render("You Won!", True, FONT_COLOR)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        time.sleep(0.1)
        screen.fill(BACKGROUND_COLOR)
        pygame.display.flip()
        time.sleep(0.1)
        flash_timer += 0.2

def main():
    grid = initialize_grid()
    revealed = [[False] * COLS for _ in range(ROWS)]
    game_over = False
    detected_mines = []
    ai_moves = []
    mines_left = NUM_MINES
    running = True
    while running:
        draw_grid(grid, revealed, ai_moves, detected_mines, mines_left)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if not game_over:
            ai_move = ai_play(grid, revealed, detected_mines, mines_left)
            ai_moves.append(ai_move)
            if grid[ai_move[0]][ai_move[1]] == '*':
                game_over = True
                mines_left -= 1
            else:
                reveal(grid, revealed, ai_move[0], ai_move[1])
                time.sleep(1 / STEPS_PER_SECOND)
        if not game_over and all(all(revealed[row][col] or grid[row][col] == '*' for col in range(COLS)) for row in range(ROWS)):
            game_over = True
            draw_you_won()
        if game_over:
            if not all(all(cell != '*' for cell in row) for row in revealed):
                print("Game Over!")
            else:
                print("Congratulations! You won!")
    pygame.quit()

if __name__ == "__main__":
    main()
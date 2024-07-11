import pygame
import time
import random
from Vector2 import Vector2
from StateMachine import State, StateMachine
from Apple import Apple

pygame.init()

#region Colors
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)
purple = (131, 56, 236)
gray = (141, 153, 174)

grid_line_color: tuple[int, int, int] | None = gray #if none the grid won't be colored
#endregion

#region Grid
block_size = 50
block_count = 16
grid_line_size = 4

#grid_line_offset = grid_line_size // 2 #offset because lines are drawn from the center of a point
grid_line_offset = 0 if grid_line_size == 0 else (grid_line_size - 1) // 2

def local_to_world(pos_loc: Vector2):
    return pos_loc * (block_size + grid_line_size) + Vector2(1, 1) * grid_line_size
#endregion

#region Create display
screen_width = block_size * block_count + grid_line_size * (block_count + 1)
screen_height = screen_width

display = pygame.display.set_mode((screen_width, screen_height))
#endregion

#region Clock
clock = pygame.time.Clock()
#endregion

#region fonts
message_font = pygame.font.SysFont("comicsans", 50)
score_font = pygame.font.SysFont("comicsans", 35)
#endregion

#region snake vars
apples = [
    Apple(50, red, 1),
    Apple(15, yellow, 3),
    Apple(1, purple, 6)
]

snake = []
move_direction = None
apple_position = None
current_apple_type: Apple = None

grow_count = None

fps = 10

moves: list[Vector2] = []
#endregion

#region Drawing
def message(msg, color):
    msg_render = message_font.render(msg, True, color)
    msg_rect = msg_render.get_rect(center=(screen_width/2, screen_height/2))
    display.blit(msg_render, msg_rect)

def draw_grid():
    global display, grid_line_size, grid_line_offset, grid_line_color

    if grid_line_color is not None:
        return

    for x in range(grid_line_offset, screen_width, block_size + grid_line_size):
        pygame.draw.line(display, gray, (x, 0), (x, screen_height), width=grid_line_size)
    
    for y in range(grid_line_offset, screen_height, block_size + grid_line_size):
        pygame.draw.line(display, gray, (0, y), (screen_width, y), width=grid_line_size)

def draw_snake():
    draw_snake_head()

    for part in snake[:-1]:
        pos_world = local_to_world(part)
        pygame.draw.rect(display, white, pygame.Rect(pos_world.x, pos_world.y, block_size, block_size))

def draw_snake_head():
    global move_direction, snake

    s = block_size // 4
    e = (3 * block_size) // 4

    l = s
    r = e
    u = s
    d = e

    if move_direction == Vector2(0, -1): #up
        eye1 = Vector2(l, u)
        eye2 = Vector2(r, u)
    elif move_direction == Vector2(0, 1): #down
        eye1 = Vector2(l, d)
        eye2 = Vector2(r, d)
    if move_direction == Vector2(-1, 0): #left
        eye1 = Vector2(l, u)
        eye2 = Vector2(l, d)
    elif move_direction == Vector2(1, 0): #right
        eye1 = Vector2(r, u)
        eye2 = Vector2(r, d)
    

    eye_radius = block_size // 10

    head_pos = snake[-1]
    head_pos_world = local_to_world(head_pos)
    #head
    pygame.draw.rect(display, white, pygame.Rect(head_pos_world.x, head_pos_world.y, block_size, block_size))

    #eyes
    pygame.draw.circle(display, black, (head_pos_world.x + eye1.x, head_pos_world.y + eye1.y), eye_radius)
    pygame.draw.circle(display, black, (head_pos_world.x + eye2.x, head_pos_world.y + eye2.y), eye_radius)

def draw_apple():
    global apple_position

    pos_world = local_to_world(apple_position)
    pygame.draw.rect(display, current_apple_type.color, (pos_world.x, pos_world.y, block_size, block_size))

def draw_frame():
    display.fill(blue)
    draw_grid()
    draw_snake()
    draw_apple()
#endregion

all_positions = {Vector2(x, y) for x in range(block_count) for y in range(block_count)}
def generate_apple_position():
    global all_positions, apple_position
    
    available_positions = list(all_positions - set(snake))

    apple_position = random.choice(available_positions)
    
    return apple_position

def pick_apple_type():
    global apples, current_apple_type

    picked_apple_idx = weighted_random([apple.weight for apple in apples])
    return apples[picked_apple_idx]

def weighted_random(weights: list[int]):
    total = sum(weights)
    r = random.randint(1, total)
    
    for i, weight in enumerate(weights):
        r -= weight
        if r <= 0:
            return i

def quit_game():
    pygame.quit()
    quit()

#sets variables to what they need to be for a new game
def config_new_game():
    global apple_position, current_apple_type, moves, snake, move_direction, grow_count, block_count

    snake = [Vector2(0, block_count//2), Vector2(1, block_count//2), Vector2(2, block_count//2)]
    move_direction = Vector2(1, 0)

    apple_position = generate_apple_position()
    current_apple_type = pick_apple_type()

    moves = []

    grow_count = 0

#region Start
def start_start():
    config_new_game()
    draw_frame()
    
    message("Press movement key to start", red)
    pygame.display.update()

def start_update():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        if event.type == pygame.KEYDOWN:
            inp = None
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                inp = Vector2(-1, 0)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                inp = Vector2(1, 0)
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                inp = Vector2(0, -1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                inp = Vector2(0, 1)
            
            if inp is not None and can_move_in_direction(inp):
                moves.append(inp)
                sm.change_state(running)
                clock.tick(fps)

start = State(
    start=start_start,
    update=start_update
)
#endregion

#region Running
def running_update():
    global move_direction, apple_position, sm, snake, clock, game_over, grow_count, current_apple_type

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                sm.change_state(paused)
                return
            
            inp = None
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                inp = Vector2(-1, 0)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                inp = Vector2(1, 0)
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                inp = Vector2(0, -1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                inp = Vector2(0, 1)
            
            if inp is not None and can_move_in_direction(inp):
                moves.append(inp)

    if moves:
        move_direction = moves[0]
        moves.pop(0)
    
    snake_head = snake[-1]
    future_pos = snake_head + move_direction

    snake_out_of_bounds = future_pos.x < 0 or future_pos.x >= block_count or future_pos.y < 0 or future_pos.y >= block_count
    snake_hit_itself = future_pos in snake
    if snake_out_of_bounds or snake_hit_itself:
        sm.change_state(game_over)
        return

    snake.append(snake_head + move_direction)

    if snake[-1] == apple_position:
        apple_position = generate_apple_position()
        current_apple_type = pick_apple_type()
        grow_count += current_apple_type.grow_amount
    
    if grow_count != 0:
        grow_count -= 1
    else:
        snake.pop(0)
    
    draw_frame()
    #message(str(move_direction), green)
    
    pygame.display.update()
    clock.tick(fps)

def can_move_in_direction(inp: Vector2):
        if moves:
            return inp + moves[-1] != Vector2(0, 0)
        else:
            return inp + move_direction != Vector2(0, 0)

running = State(
    update=running_update
)
#endregion

#region Paused
def paused_start():
    display.fill(yellow)
    message("Paused! Press r to resume", red)
    pygame.display.update()

def paused_update():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                sm.change_state(running)

paused = State(
    start=paused_start,
    update=paused_update
)
#endregion

#region Game over
def game_over_start():
    display.fill(yellow)
    message("You died! Press any key to restart", red)
    pygame.display.update()

def game_over_update():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        if event.type == pygame.KEYDOWN:
            config_new_game()
            sm.change_state(start)

game_over = State(
    start=game_over_start,
    update=game_over_update
)
#endregion

sm = StateMachine(start)

sm.start()
while True:
    sm.update()
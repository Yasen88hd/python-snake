import pygame
import time
import random
from Vector2 import Vector2
from StateMachine import State, StateMachine

pygame.init()


#region Colors
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)
#endregion

#region Grid
block_size = 40
block_count = 20

def local_to_world(pos_loc: Vector2):
    return pos_loc * block_size
#endregion

#region Create display
screen_width = block_size * block_count
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

# snake vars
snake = []
move_direction = None
food_position = None

fps = 10

moves: list[Vector2] = []

is_new_game = True

#region Drawing
def message(msg, color):
    msg_render = message_font.render(msg, True, color)
    msg_rect = msg_render.get_rect(center=(screen_width/2, screen_height/2))
    display.blit(msg_render, msg_rect)

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

def draw_food():
    global food_position

    pos_world = local_to_world(food_position)
    pygame.draw.rect(display, yellow, pygame.Rect(pos_world.x, pos_world.y, block_size, block_size))

def draw_frame():
    display.fill(blue)
    draw_snake()
    draw_food()
#endregion

all_positions = {Vector2(x, y) for x in range(block_count) for y in range(block_count)}
def generate_food_position():
    global all_positions, food_position
    
    available_positions = list(all_positions - set(snake))

    food_position = random.choice(available_positions)
    
    return food_position

def quit_game():
    pygame.quit()
    quit()

#region Start
def start_start():
    display.fill(yellow)
    message("Press any key to start", red)
    pygame.display.update()

def start_update():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        if event.type == pygame.KEYDOWN:
            sm.change_state(running)

start = State(
    start=start_start,
    update=start_update
)
#endregion

#region Running
def running_start():
    global is_new_game

    if is_new_game:
        global food_position, snake, move_direction

        snake = [Vector2(0, block_count//2), Vector2(1, block_count//2), Vector2(2, block_count//2)]
        move_direction = Vector2(1, 0)

        food_position = generate_food_position()

        moves = []

        is_new_game = False

def running_update():
    global move_direction, food_position, sm, snake, clock, game_over

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                sm.change_state(paused)
                return
            if event.key == pygame.K_LEFT:
                inp = Vector2(-1, 0)
            elif event.key == pygame.K_RIGHT:
                inp = Vector2(1, 0)
            elif event.key == pygame.K_UP:
                inp = Vector2(0, -1)
            elif event.key == pygame.K_DOWN:
                inp = Vector2(0, 1)
            
            if inp and can_move_in_direction(inp):
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

    if snake[-1] == food_position:
        food_position = generate_food_position()
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
    start=running_start,
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
    global is_new_game

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        if event.type == pygame.KEYDOWN:
            is_new_game = True
            sm.change_state(running)

game_over = State(
    start=game_over_start,
    update=game_over_update
)
#endregion

sm = StateMachine(start)

sm.start()
while True:
    sm.update()
import pygame, sys
import pymunk
import pymunk.pygame_util
import math

pygame.init()
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 678
BOTTOM_PANEL = 50

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + BOTTOM_PANEL))
pygame.display.set_caption("Pool")

space = pymunk.Space()
static_body = space.static_body
draw_options = pymunk.pygame_util.DrawOptions(screen)

clock = pygame.time.Clock()
FPS = 120

dia = 36
pocket_dia = 66
force = 0
max_force = 10000
force_direction = 1
lives = 3
cue_ball_potted = False
taking_shot = True
powering_up = False
potted_balls = []

#colours

BG = (50,50,50)
RED = (255, 0, 0)

#images
cue_image = pygame.image.load("pool-assets/cue.png").convert_alpha()
table_image = pygame.image.load("pool-assets/table.png").convert_alpha()

ball_images = []
for i in range(1,17):
    ball_image = pygame.image.load(f"pool-assets/ball_{i}.png").convert_alpha()
    ball_images.append(ball_image)
all_ball_images = ball_images.copy()
pixel_font = pygame.font.Font("pixeled.ttf", 24)
lives_font = pygame.font.Font("pixeled.ttf", 16)

ball_pivots = {}

def create_ball(radius, pos):
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.mass = 5
    shape.elasticity = 0.8

    pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
    pivot.max_bias = 0
    pivot.max_force = 1000

    space.add(body, shape, pivot)
    ball_pivots[shape] = pivot
    return shape

balls = []
rows = 5

for col in range(rows):
    for row in range(col + 1):
        pos = (250 + (rows - 1 - col) * (dia+5) * 0.866, SCREEN_HEIGHT / 2 + (row - col / 2) * (dia+5))
        new_ball = create_ball(dia / 2, pos)
        balls.append(new_ball)

pos = (888, SCREEN_HEIGHT / 2)
cue_ball = create_ball(dia / 2,pos)
balls.append(cue_ball)
cue_ball_start_pos = (888, SCREEN_HEIGHT / 2)
game_over = False
game_won = False

def reset_game():
    global balls, ball_images, potted_balls, lives, cue_ball_potted
    global taking_shot, powering_up, force, force_direction, game_over, game_won

    for ball in balls:
        pivot = ball_pivots.pop(ball, None)
        if pivot is not None:
            space.remove(pivot, ball, ball.body)

    balls = []
    for col in range(rows):
        for row in range(col + 1):
            pos = (250 + (rows - 1 - col) * (dia + 5) * 0.866,
                   SCREEN_HEIGHT / 2 + (row - col / 2) * (dia + 5))
            balls.append(create_ball(dia / 2, pos))
    balls.append(create_ball(dia / 2, cue_ball_start_pos))

    ball_images = all_ball_images.copy()
    potted_balls = []
    lives = 3
    cue_ball_potted = False
    taking_shot = True
    powering_up = False
    force = 0
    force_direction = 1
    game_over = False
    game_won = False

pockets = [
  (55, 63),
  (592, 48),
  (1134, 64),
  (55, 616),
  (592, 629),
  (1134, 616)
]

cushions = [
  [(88, 56), (109, 77), (555, 77), (564, 56)],
  [(621, 56), (630, 77), (1081, 77), (1102, 56)],
  [(89, 621), (110, 600),(556, 600), (564, 621)],
  [(622, 621), (630, 600), (1081, 600), (1102, 621)],
  [(56, 96), (77, 117), (77, 560), (56, 581)],
  [(1143, 96), (1122, 117), (1122, 560), (1143, 581)]
]

def create_cushion(poly_dims):
    body = pymunk.Body(body_type = pymunk.Body.STATIC)
    body.position = ((0,0))
    shape = pymunk.Poly(body, poly_dims)
    shape.elasticity = 0.8

    space.add(body, shape)

for c in cushions:
    create_cushion(c)

class Cue():
    def __init__(self, pos):
        self.orginal_image = cue_image
        self.angle = 0
        self.image = pygame.transform.rotate(self.orginal_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self, angle):
        self.angle = angle

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.orginal_image, self.angle)
        surface.blit(self.image,
        (self.rect.centerx - self.image.get_width() / 2,
        self.rect.centery - self.image.get_height() / 2)
        )


cue = Cue(balls[-1].body.position)

power_bar = pygame.Surface((10, 20))
power_bar.fill(RED)

run = True

while run:

    clock.tick(FPS)
    space.step(1 / FPS)

    screen.fill(BG)

    screen.blit(table_image, (0,0))

    # Check the cue ball separately, then remove object balls backwards so
    # list indices and ball images stay aligned while balls are potted.
    cue_ball = balls[-1]
    if any(math.hypot(cue_ball.body.position[0] - pocket[0],
                      cue_ball.body.position[1] - pocket[1]) <= pocket_dia / 2
           for pocket in pockets):
        lives -= 1
        cue_ball_potted = True
        cue_ball.body.position = (-100, -100)
        cue_ball.body.velocity = (0.0, 0.0)
        if lives <= 0:
            game_over = True

    for i in range(len(balls) - 2, -1, -1):
        ball = balls[i]
        if any(math.hypot(ball.body.position[0] - pocket[0],
                          ball.body.position[1] - pocket[1]) <= pocket_dia / 2
               for pocket in pockets):
            space.remove(ball_pivots.pop(ball), ball, ball.body)
            potted_balls.append(ball_images.pop(i))
            balls.pop(i)
    if not balls[:-1]:
        game_won = True
    for i, ball in enumerate (balls):
             screen.blit(ball_images[i], (ball.body.position[0] - ball.radius,ball.body.position[1] - ball.radius ))

    taking_shot = all(
        ball.body.velocity.length < 1
        for ball in (balls[:-1] if cue_ball_potted else balls)
    )
    
    if taking_shot == True and not game_over and not game_won:
        if cue_ball_potted == True:
            #reposition cue ball
            balls[-1].body.position = cue_ball_start_pos
            balls[-1].body.velocity = (0.0, 0.0)
            cue_ball_potted = False
        mouse_pos = pygame.mouse.get_pos()
        cue.rect.center = balls[-1].body.position
        x_dist = balls[-1].body.position[0] - mouse_pos[0]
        y_dist = -(balls[-1].body.position[1] - mouse_pos[1])
        cue_angle = math.degrees(math.atan2(y_dist, x_dist))
        cue.update(cue_angle)
        cue.draw(screen)

    if powering_up == True and not game_over and not game_won:
        force += 100 * force_direction
        if force >= max_force or force <= 0:
            force_direction *= -1
        for b in range(math.ceil(force/ 2000)):
            screen.blit(power_bar,
                (balls[-1].body.position[0] -30+ (b * 15),
                 balls[-1].body.position[1] + 30))
    elif powering_up == False and taking_shot == True:
        x_impulse = math.cos(math.radians(cue_angle))
        y_impulse = math.sin(math.radians(cue_angle))
        balls[-1].body.apply_impulse_at_local_point((force * -x_impulse, force * y_impulse),(0,0))
        force = 0
        force_direction = 1

    pygame.draw.rect(screen, BG, (0,SCREEN_HEIGHT, SCREEN_WIDTH, BOTTOM_PANEL))

    if game_won:
        status_text = pixel_font.render("YOU WIN - PRESS R TO RESTART", True, (255, 255, 255))
        screen.blit(status_text, status_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT + BOTTOM_PANEL // 2)))
    elif game_over:
        status_text = pixel_font.render("GAME OVER - PRESS R TO RESTART", True, (255, 255, 255))
        screen.blit(status_text, status_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT + BOTTOM_PANEL // 2)))
    else:
        lives_text = lives_font.render(f"LIVES: {lives}", True, (255, 255, 255))
        screen.blit(lives_text, lives_text.get_rect(
            midright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT + BOTTOM_PANEL // 2)))
        for i, ball in enumerate(potted_balls):
            screen.blit(ball, (160 + (i * 50), SCREEN_HEIGHT + 10))


    for event in pygame.event.get((pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP)):
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            run = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and (game_over or game_won):
            reset_game()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and taking_shot and not game_won and not game_over:
            powering_up = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and taking_shot and not game_won and not game_over:
            powering_up = False
        
        
           
    
    pygame.display.update()
    

pygame.quit()
sys.exit()
   


import builtins
import math
import pygame

pygame.init()
WIDTH, HEIGHT = 400, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pinball")
clock = pygame.time.Clock()
font = pygame.font.Font("pixeled.ttf", 20)

WALLS = [
    ((20, 440), (20, 100)), ((20, 100), (100, 20)), ((100, 20), (300, 20)),
    ((300, 20), (380, 100)), ((380, 100), (380, 440)),
    ((20, 440), (130, 520)), ((380, 440), (270, 520)),
]

bumpers = [
    {"pos": pygame.Vector2(140, 190), "size": 24, "lit": 0},
    {"pos": pygame.Vector2(260, 190), "size": 24, "lit": 0},
    {"pos": pygame.Vector2(200, 290), "size": 24, "lit": 0},
]

RADIUS = 9
GRAVITY = 0.15
SUBSTEPS = 8      # Smooths out physics and prevents tunneling/sticking
MAX_SPEED = 12
score, lives = 0, 3

def new_ball():
    return pygame.Vector2(200, 60), pygame.Vector2(2 if lives % 2 else -2, 1)

pos, vel = new_ball()

FLIPPER_LEN = 55
REST, UP = 0.5, -0.5
FLIP_SPEED = 0.2
flippers = [
    {"pivot": pygame.Vector2(130, 520), "side": 1, "key": pygame.K_LEFT, "angle": REST, "swing": 0},
    {"pivot": pygame.Vector2(270, 520), "side": -1, "key": pygame.K_RIGHT, "angle": REST, "swing": 0},
]

def tip(f):
    return f["pivot"] + pygame.Vector2(math.cos(f["angle"]) * f["side"], math.sin(f["angle"])) * FLIPPER_LEN

def touch(a, b, thick):
    a, b = pygame.Vector2(a), pygame.Vector2(b)
    line = b - a
    length_sq = line.length_squared()
    if length_sq == 0:
        return None
    t = builtins.max(0.0, builtins.min(1.0, (pos - a).dot(line) / length_sq))
    away = pos - (a + line * t)
    dist = away.length()
    if dist == 0 or dist >= RADIUS + thick:
        return None
    return away / dist, RADIUS + thick - dist

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and lives == 0:
            score, lives = 0, 3
            pos, vel = new_ball()

    # Flipper Controls
    keys = pygame.key.get_pressed()
    for f in flippers:
        hit = touch(f["pivot"], tip(f), 6)
        if hit:
            normal, depth = hit
            pos += normal * (depth + 0.2)
            push = builtins.max(0, -f["swing"]) * pos.distance_to(f["pivot"])
            speed = vel.dot(normal) - push
            if speed < 0:
                vel -= normal * speed * 1.4
        target = UP if keys[f["key"]] else REST
        f["swing"] = builtins.max(-FLIP_SPEED, builtins.min(FLIP_SPEED, target - f["angle"]))
        f["angle"] += f["swing"]

    # Physics & Collisions
    if lives > 0:
        vel.y += GRAVITY
        if vel.length() > MAX_SPEED:
            vel.scale_to_length(MAX_SPEED)

        # Substep loop to resolve collisions smoothly without sticking
        for _ in builtins.range(SUBSTEPS):
            pos += vel / SUBSTEPS

            # Wall collisions with separation bias
            for a, b in WALLS:
                hit = touch(a, b, 2)
                if hit:
                    normal, depth = hit
                    pos += normal * (depth + 0.1)  # Pushes ball cleanly out of walls
                    dot = vel.dot(normal)
                    if dot < 0:
                        vel -= normal * dot * 1.6

            # Bumper collisions with separation bias
            for bp in bumpers:
                away = pos - bp["pos"]
                dist = away.length()
                min_dist = RADIUS + bp["size"]
                if 0 < dist < min_dist:
                    normal = away.normalize()
                    pos = bp["pos"] + normal * (min_dist + 0.1)  # Pushes ball cleanly out of bumpers
                    vel = normal * 8.5  # Clean bumper kick force
                    bp["lit"] = 10
                    score += 100

        # Ball out of bounds (drain)
        if pos.y > HEIGHT + RADIUS:
            lives -= 1
            if lives > 0:
                pos, vel = new_ball()

    # Rendering
    screen.fill((15, 20, 40))
    
    for a, b in WALLS:
        pygame.draw.line(screen, (120, 140, 200), a, b, 4)
        
    for bp in bumpers:
        colour = (255, 230, 120) if bp["lit"] else (220, 60, 90)
        pygame.draw.circle(screen, colour, bp["pos"], builtins.int(bp["size"]))
        bp["lit"] = builtins.max(0, bp["lit"] - 1)
        
    for f in flippers:
        pygame.draw.line(screen, (90, 200, 255), f["pivot"], tip(f), 12)
        pygame.draw.circle(screen, (90, 200, 255), f["pivot"], 6)
        pygame.draw.circle(screen, (90, 200, 255), tip(f), 6)
    
    if lives > 0:
        pygame.draw.circle(screen, (255, 255, 255), (builtins.int(pos.x), builtins.int(pos.y)), RADIUS)
    
    # UI Text
    score_text = font.render(f"Score: {score}", True, (240, 240, 240))
    balls_text = font.render(f"Lives: {lives}", True, (240, 240, 240))

    margin = 20
    hud_y = HEIGHT - 60
    score_x = margin
    balls_x = WIDTH - balls_text.get_width() - margin

    # Keep both HUD items from overlapping if the text gets too wide.
    if score_x + score_text.get_width() + 12 >= balls_x:
        score_x = margin
        balls_x = margin
        hud_y = HEIGHT - 90
        score_y = hud_y
        balls_y = hud_y + score_text.get_height() + 8
    else:
        score_y = hud_y
        balls_y = hud_y

    screen.blit(score_text, (score_x, score_y))
    screen.blit(balls_text, (balls_x, balls_y))
    
    if lives == 0:
        game_over_font = pygame.font.Font("pixeled.ttf", 20)
        for line_num, line in enumerate(("GAME OVER", "PRESS R TO RESTART")):
            text = game_over_font.render(line, True, (255, 230, 120))
            y = 260 + line_num * (text.get_height() + 8)
            screen.blit(text, ((WIDTH - text.get_width()) // 2, y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

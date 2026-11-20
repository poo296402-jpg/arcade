import os
import sys
import shutil
import subprocess
import pygame

def get_app_dir():
    '''Return the folder containing the .exe (when compiled) or menu.py (when running raw).'''

    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    '''Resolve assets (fonts, music, images, game scripts) sitting next to the .exe / script.'''

    return os.path.join(get_app_dir(), relative_path)

def find_python_executable():
    '''Find a working Python interpreter on the system when running as a compiled .exe.'''

    if not getattr(sys, 'frozen', False):
        return sys.executable
    for candidate in ('python', 'py', 'python3'):
        found = shutil.which(candidate)
        if not found:
            continue
        return found
    return 'python'

def main():
    pygame.init()
    WIDTH, HEIGHT = 900, 520
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Arcade Flashback Classics - Game Select')
    clock = pygame.time.Clock()
    def init_audio():
        try:
            pygame.mixer.init()
            music_file = resource_path('music.wav')
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(loops=-1)
                return
        except Exception:
            pass

    def stop_audio():
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                return
        except Exception:
            pass

    init_audio()
    def load_assets():
        font_path = resource_path('Pixeled.ttf')
        if not os.path.exists(font_path):
            font_path = resource_path('pixeled.ttf')
        try:
            t_font = pygame.font.Font(font_path, 22)
            b_font = pygame.font.Font(font_path, 12)
            d_font = pygame.font.Font(font_path, 8)
            f_font = pygame.font.Font(font_path, 8)
        except (OSError, pygame.error):
            t_font = pygame.font.Font(None, 32)
            b_font = pygame.font.Font(None, 24)
            d_font = pygame.font.Font(None, 16)
            f_font = pygame.font.Font(None, 16)
        def load_img(filename):
            try:
                img_path = resource_path(filename)
                image = pygame.image.load(img_path).convert()
                image_width, image_height = image.get_size()
                scale = min(206 / image_width, 126 / image_height)
                scaled_size = max(1, round(image_width * scale)), max(1, round(image_height * scale))
                image = pygame.transform.smoothscale(image, scaled_size)
                preview = pygame.Surface((210, 130), pygame.SRCALPHA)
                preview.fill((10, 10, 20, 255))
                preview.blit(image, image.get_rect(center=preview.get_rect().center))
                rounded_mask = pygame.Surface((210, 130), pygame.SRCALPHA)
                pygame.draw.rect(rounded_mask, (255, 255, 255, 255), rounded_mask.get_rect(), border_radius=12)
                preview.blit(rounded_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                return preview
            except Exception:
                return

        previews = {'snake': load_img('snake.png'), 'flappy': load_img('flappy.png'), 'space': load_img('space.png'), 'tetris': load_img('tetris.png'), 'breakout': load_img('breakout.png'), 'pong': load_img('pong.png'), 'pool': load_img('pool.png'), 'pinball': load_img('pinball.png')}
        return t_font, b_font, d_font, f_font, previews

    title_font, button_font, desc_font, footer_font, previews = load_assets()
    games = [{'label': 'SNAKE ARCADE', 'desc': 'Guide the snake, eat the red food, and grow longer without hitting walls or your tail!', 'script': 'snake.py', 'rect': pygame.Rect(320, 80, 530, 40), 'preview_key': 'snake'}, {'label': 'FLAPPY BIRD', 'desc': 'Tap spacebar to flap your wings. Navigate cleanly through pipes to score points.', 'script': 'flappy.py', 'rect': pygame.Rect(320, 122, 530, 40), 'preview_key': 'flappy'}, {'label': 'SPACE INVADERS', 'desc': 'Defend Earth! Move with arrow keys and press spacebar to shoot lasers.', 'script': 'space.py', 'rect': pygame.Rect(320, 164, 530, 40), 'preview_key': 'space'}, {'label': 'TETRIS', 'desc': 'Rotate and drop falling blocks to clear complete lines and stack up your high score.', 'script': 'tetris.py', 'rect': pygame.Rect(320, 206, 530, 40), 'preview_key': 'tetris'}, {'label': 'BREAKOUT', 'desc': 'Bounce the ball with your paddle to break every brick without letting it fall.', 'script': 'breakout.py', 'rect': pygame.Rect(320, 248, 530, 40), 'preview_key': 'breakout'}, {'label': 'PONG', 'desc': 'Move your paddle to return the ball and score against your opponent.', 'script': 'pong.py', 'rect': pygame.Rect(320, 290, 530, 40), 'preview_key': 'pong'}, {'label': 'POOL', 'desc': 'Line up your shot and sink the balls into the pockets.', 'script': 'pool.py', 'rect': pygame.Rect(320, 332, 530, 40), 'preview_key': 'pool'}, {'label': 'PINBALL', 'desc': 'Keep the ball in play with the flippers and score points by hitting targets.', 'script': 'pinball.py', 'rect': pygame.Rect(320, 374, 530, 40), 'preview_key': 'pinball'}, {'label': 'QUIT ARCADE', 'desc': 'Shut down the arcade cabinet and exit back to your desktop.', 'script': None, 'rect': pygame.Rect(320, 416, 530, 40), 'preview_key': None}]
    bg_surface = pygame.Surface((WIDTH, HEIGHT))
    bg_surface.fill((15, 10, 35))
    star_coords = [(100, 50), (230, 80), (450, 40), (700, 70), (850, 30), (50, 150), (320, 200), (600, 170), (780, 220), (120, 300), (400, 350), (650, 320), (880, 290), (80, 400), (250, 430), (530, 410), (750, 440), (150, 110), (260, 150), (510, 90), (620, 250), (810, 180), (190, 360), (470, 260), (720, 390), (860, 225), (300, 440), (40, 230), (560, 125), (670, 440), (180, 470), (420, 120), (760, 310), (620, 80), (340, 470), (220, 260), (870, 370)]
    for pos in star_coords:
        pygame.draw.circle(bg_surface, (235, 240, 255), pos, 1)
    title_surf = title_font.render('FLASHBACK ARCADE', True, (240, 240, 255))
    fallback_surf = button_font.render('No Screenshot', True, (150, 150, 170))
    footer_surf = footer_font.render('[UP/DOWN] Select   [ENTER] Play   [ESC] Quit', True, (200, 200, 220))
    selected_index = 0
    def render_wrapped_description(text, font, max_width):
        words = text.split()
        lines = []
        current_line = ''
        for word in words:
            candidate = f'{current_line} {word}'.strip()
            if font.size(candidate)[0] <= max_width:
                current_line = candidate
            else:
                if current_line:
                    lines.append(current_line)
                if font.size(word)[0] <= max_width:
                    current_line = word
                else:
                    chunk = ''
                    for char in word:
                        if font.size(chunk + char)[0] <= max_width:
                            chunk += char
                        else:
                            if chunk:
                                lines.append(chunk)
                            chunk = char
                    current_line = chunk
        if current_line:
            lines.append(current_line)
        return [font.render(line, True, (200, 200, 220)) for line in lines]

    python_cmd = find_python_executable()
    def launch_game(script_name):
        nonlocal screen, title_font, button_font, desc_font, footer_font, previews, title_surf, fallback_surf, footer_surf
        stop_audio()
        pygame.event.clear()
        try:
            game_dir = get_app_dir()
            script_path = os.path.join(game_dir, script_name)
            pygame.display.quit()
            subprocess.run([python_cmd, script_path], cwd=game_dir)
        except Exception as e:
            print(f'Subprocess execution error: {e}')
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Arcade Flashback Classics - Game Select')
        title_font, button_font, desc_font, footer_font, previews = load_assets()
        title_surf = title_font.render('FLASHBACK ARCADE', True, (240, 240, 255))
        fallback_surf = button_font.render('No Screenshot', True, (150, 150, 170))
        footer_surf = footer_font.render('[UP/DOWN] Select   [ENTER] Play   [ESC] Quit', True, (200, 200, 220))
        pygame.event.clear()
        pygame.time.delay(100)
        init_audio()
        pygame.event.clear()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(games)
                    continue
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(games)
                    continue
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game = games[selected_index]
                    if game['script']:
                        launch_game(game['script'])
                        continue
                    pygame.quit()
                    return
            if event.type != pygame.MOUSEBUTTONDOWN:
                continue
            if event.button != 1:
                continue
            for idx, game in enumerate(games):
                if game['rect'].collidepoint(event.pos):
                    selected_index = idx
                    if game['script']:
                        launch_game(game['script'])
                    else:
                        pygame.quit()
                        return
            continue
        mouse_pos = pygame.mouse.get_pos()
        for idx, game in enumerate(games):
            if game['rect'].collidepoint(mouse_pos):
                selected_index = idx
        screen.blit(bg_surface, (0, 0))
        pygame.draw.rect(screen, (25, 20, 60), (0, 0, WIDTH, 65))
        pygame.draw.line(screen, (100, 80, 200), (0, 65), (WIDTH, 65), 3)
        screen.blit(title_surf, (30, 18))
        cabinet_rect = pygame.Rect(40, 75, 240, 395)
        pygame.draw.rect(screen, (20, 20, 35), cabinet_rect, border_radius=8)
        pygame.draw.rect(screen, (70, 90, 160), cabinet_rect, 2, border_radius=8)
        mini_screen = pygame.Rect(55, 95, 210, 130)
        pygame.draw.rect(screen, (10, 10, 20), mini_screen, border_radius=12)
        current_preview = previews.get(games[selected_index]['preview_key'])
        if current_preview:
            screen.blit(current_preview, mini_screen.topleft)
        else:
            screen.blit(fallback_surf, fallback_surf.get_rect(center=mini_screen.center))
        pygame.draw.rect(screen, (50, 60, 90), mini_screen, 1, border_radius=12)
        desc_surfs = render_wrapped_description(games[selected_index]['desc'], desc_font, 210)
        start_y = 245
        for desc_surf in desc_surfs:
            screen.blit(desc_surf, (55, start_y))
            start_y += 14
        for idx, game in enumerate(games):
            is_selected = idx == selected_index
            bg_color = (40, 60, 130) if is_selected else (25, 30, 60)
            border_color = (0, 220, 255) if is_selected else (60, 70, 110)
            pygame.draw.rect(screen, bg_color, game['rect'], border_radius=6)
            pygame.draw.rect(screen, border_color, game['rect'], 2, border_radius=6)
            label_color = (255, 255, 255) if is_selected else (190, 200, 220)
            label_surf = button_font.render(game['label'], True, label_color)
            label_rect = label_surf.get_rect(midleft=(game['rect'].x + 20, game['rect'].centery))
            screen.blit(label_surf, label_rect)
        footer_rect = pygame.Rect(0, HEIGHT - 40, WIDTH, 40)
        pygame.draw.rect(screen, (15, 10, 30), footer_rect)
        pygame.draw.line(screen, (70, 60, 120), (0, HEIGHT - 40), (WIDTH, HEIGHT - 40), 2)
        screen.blit(footer_surf, (30, HEIGHT - 26))
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
# WARNING: Decompyle incomplete

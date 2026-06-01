import pygame
import random

# Colors
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
CYAN       = (0,   255, 255)
YELLOW     = (255, 255, 0)
MAGENTA    = (255, 0,   255)
RED        = (255, 0,   0)
GREEN      = (0,   255, 0)
BLUE       = (0,   0,   255)
ORANGE     = (255, 165, 0)
GRAY       = (180, 180, 180)
DARK_GRAY  = (40,  40,  40)
PANEL_BG   = (25,  25,  40)

SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
}

COLORS = {
    'I': CYAN, 'O': YELLOW, 'T': MAGENTA,
    'S': GREEN, 'Z': RED,   'J': BLUE, 'L': ORANGE,
}

BLOCK      = 30
COLS       = 10
ROWS       = 20
PANEL_W    = 180
SW         = COLS * BLOCK + PANEL_W
SH         = ROWS * BLOCK
MAX_LIVES  = 3
FPS        = 60


class Piece:
    def __init__(self):
        self.kind  = random.choice(list(SHAPES))
        self.shape = [row[:] for row in SHAPES[self.kind]]
        self.color = COLORS[self.kind]
        self.x     = COLS // 2 - len(self.shape[0]) // 2
        self.y     = 0


class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SW, SH))
        pygame.display.set_caption("Tetris — Player Lives")
        self.clock  = pygame.time.Clock()
        self.font_l = pygame.font.SysFont("consolas", 32, bold=True)
        self.font_m = pygame.font.SysFont("consolas", 20)
        self.font_s = pygame.font.SysFont("consolas", 16)
        self.new_game()

    # ------------------------------------------------------------------ setup
    def new_game(self):
        self.lives       = MAX_LIVES
        self.total_score = 0
        self._reset_board()

    def _reset_board(self):
        self.grid        = [[None] * COLS for _ in range(ROWS)]
        self.current     = Piece()
        self.next        = Piece()
        self.score       = 0
        self.level       = 1
        self.lines       = 0
        self.fall_ms     = 500
        self.last_fall   = pygame.time.get_ticks()
        self.game_over   = False

    # --------------------------------------------------------------- movement
    def _collides(self, piece, dx=0, dy=0, shape=None):
        shape = shape or piece.shape
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    nx, ny = piece.x + c + dx, piece.y + r + dy
                    if nx < 0 or nx >= COLS or ny >= ROWS:
                        return True
                    if ny >= 0 and self.grid[ny][nx]:
                        return True
        return False

    def _rotate(self):
        rotated = [list(row) for row in zip(*self.current.shape[::-1])]
        for kick in (0, 1, -1, 2, -2):
            if not self._collides(self.current, dx=kick, shape=rotated):
                self.current.shape = rotated
                self.current.x += kick
                return

    def _hard_drop(self):
        while not self._collides(self.current, dy=1):
            self.current.y += 1
        self._lock()

    def _ghost_y(self):
        dy = 0
        while not self._collides(self.current, dy=dy + 1):
            dy += 1
        return self.current.y + dy

    # ---------------------------------------------------------------- locking
    def _lock(self):
        for r, row in enumerate(self.current.shape):
            for c, val in enumerate(row):
                if val:
                    x, y = self.current.x + c, self.current.y + r
                    if y < 0:
                        self._lose_life()
                        return
                    self.grid[y][x] = self.current.color
        self._clear_lines()
        self.current = self.next
        self.next    = Piece()
        if self._collides(self.current):
            self._lose_life()

    def _clear_lines(self):
        full  = [r for r in range(ROWS) if all(self.grid[r])]
        for r in full:
            del self.grid[r]
            self.grid.insert(0, [None] * COLS)
        pts = [0, 100, 300, 500, 800]
        n   = len(full)
        self.score += (pts[n] if n < len(pts) else 800) * self.level
        self.lines += n
        self.level  = self.lines // 10 + 1
        self.fall_ms = max(80, 500 - (self.level - 1) * 42)

    def _lose_life(self):
        self.total_score += self.score
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
        else:
            self._reset_board()

    # ---------------------------------------------------------------- drawing
    def _draw_block(self, col, row, color, alpha=255):
        x, y = col * BLOCK, row * BLOCK
        surf = pygame.Surface((BLOCK - 1, BLOCK - 1))
        surf.fill(color)
        # simple highlight
        pygame.draw.line(surf, tuple(min(255, v + 70) for v in color),
                         (0, 0), (BLOCK - 2, 0), 2)
        pygame.draw.line(surf, tuple(min(255, v + 70) for v in color),
                         (0, 0), (0, BLOCK - 2), 2)
        pygame.draw.line(surf, tuple(max(0, v - 60) for v in color),
                         (BLOCK - 2, 0), (BLOCK - 2, BLOCK - 2), 1)
        pygame.draw.line(surf, tuple(max(0, v - 60) for v in color),
                         (0, BLOCK - 2), (BLOCK - 2, BLOCK - 2), 1)
        if alpha < 255:
            surf.set_alpha(alpha)
        self.screen.blit(surf, (x, y))

    def _draw_grid(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c]:
                    self._draw_block(c, r, self.grid[r][c])
                else:
                    pygame.draw.rect(self.screen, DARK_GRAY,
                                     (c * BLOCK, r * BLOCK, BLOCK - 1, BLOCK - 1))

    def _draw_piece(self, piece):
        for r, row in enumerate(piece.shape):
            for c, val in enumerate(row):
                if val:
                    self._draw_block(piece.x + c, piece.y + r, piece.color)

    def _draw_ghost(self):
        gy     = self._ghost_y()
        gcol   = tuple(max(0, v - 170) for v in self.current.color)
        for r, row in enumerate(self.current.shape):
            for c, val in enumerate(row):
                if val:
                    x = (self.current.x + c) * BLOCK
                    y = (gy + r) * BLOCK
                    pygame.draw.rect(self.screen, gcol,
                                     (x, y, BLOCK - 1, BLOCK - 1), 2)

    def _draw_heart(self, cx, cy, filled):
        color = RED if filled else (80, 30, 30)
        r = 9
        pygame.draw.circle(self.screen, color, (cx - r // 2, cy), r // 2 + 2)
        pygame.draw.circle(self.screen, color, (cx + r // 2, cy), r // 2 + 2)
        pygame.draw.polygon(self.screen, color,
                             [(cx - r, cy + 2), (cx, cy + r + 4), (cx + r, cy + 2)])

    def _draw_panel(self):
        ox = COLS * BLOCK
        pygame.draw.rect(self.screen, PANEL_BG, (ox, 0, PANEL_W, SH))
        pygame.draw.line(self.screen, GRAY, (ox, 0), (ox, SH), 2)

        def label(text, y, color=GRAY):
            s = self.font_s.render(text, True, color)
            self.screen.blit(s, (ox + 14, y))

        def value(text, y, color=WHITE):
            s = self.font_m.render(text, True, color)
            self.screen.blit(s, (ox + 14, y))

        # Title
        t = self.font_l.render("TETRIS", True, CYAN)
        self.screen.blit(t, (ox + (PANEL_W - t.get_width()) // 2, 12))

        # Lives
        label("LIVES", 58)
        for i in range(MAX_LIVES):
            self._draw_heart(ox + 22 + i * 38, 84, i < self.lives)

        # Score
        label("SCORE", 115)
        value(str(self.score), 133, YELLOW)

        # Total score (across lives)
        label("TOTAL", 162)
        value(str(self.total_score + self.score), 180, ORANGE)

        # Level
        label("LEVEL", 210)
        value(str(self.level), 228, CYAN)

        # Lines
        label("LINES", 258)
        value(str(self.lines), 276, GREEN)

        # Next piece preview
        label("NEXT", 316)
        for r, row in enumerate(self.next.shape):
            for c, val in enumerate(row):
                if val:
                    px = ox + 20 + c * (BLOCK - 4)
                    py = 340 + r * (BLOCK - 4)
                    rect = pygame.Rect(px, py, BLOCK - 5, BLOCK - 5)
                    pygame.draw.rect(self.screen, self.next.color, rect)

        # Controls hint
        hints = ["←→  Move", "↑   Rotate", "↓   Soft drop", "SPC Hard drop"]
        for i, h in enumerate(hints):
            s = self.font_s.render(h, True, (100, 100, 120))
            self.screen.blit(s, (ox + 10, SH - 90 + i * 18))

    def _draw_game_over(self):
        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        def center(surf, y):
            self.screen.blit(surf, ((SW - surf.get_width()) // 2, y))

        center(self.font_l.render("GAME  OVER", True, RED),        200)
        center(self.font_m.render(
            f"Final Score: {self.total_score}", True, WHITE),       252)
        center(self.font_m.render("R  — Restart", True, YELLOW),   290)
        center(self.font_m.render("Q  — Quit",    True, YELLOW),   316)

    def _draw_life_lost(self):
        # brief flash — handled by board reset; nothing extra needed
        pass

    # ------------------------------------------------------------------- loop
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.new_game()
                        elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                            pygame.quit()
                            return
                    else:
                        if event.key == pygame.K_LEFT:
                            if not self._collides(self.current, dx=-1):
                                self.current.x -= 1
                        elif event.key == pygame.K_RIGHT:
                            if not self._collides(self.current, dx=1):
                                self.current.x += 1
                        elif event.key == pygame.K_DOWN:
                            if not self._collides(self.current, dy=1):
                                self.current.y += 1
                        elif event.key == pygame.K_UP:
                            self._rotate()
                        elif event.key == pygame.K_SPACE:
                            self._hard_drop()
                        elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                            pygame.quit()
                            return

            if not self.game_over:
                now = pygame.time.get_ticks()
                if now - self.last_fall > self.fall_ms:
                    if not self._collides(self.current, dy=1):
                        self.current.y += 1
                    else:
                        self._lock()
                    self.last_fall = now

            self.screen.fill(BLACK)
            self._draw_grid()
            if not self.game_over:
                self._draw_ghost()
                self._draw_piece(self.current)
            self._draw_panel()
            if self.game_over:
                self._draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Tetris().run()

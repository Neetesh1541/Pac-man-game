import pygame
import random
import sys

# --------------- Constants ---------------
WIDTH, HEIGHT = 560, 620
FPS = 60

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (50, 50, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

PLAYER_SPEED = 2
GHOST_SPEED = 1

GHOST_COUNT = 10
PELLET_COUNT = 30

BORDER_RECT = pygame.Rect(20, 20, WIDTH - 40, HEIGHT - 40)

# Horizontal/vertical play-area bounds (player and ghost centres must stay inside)
_PLAY_LEFT = BORDER_RECT.left + 20
_PLAY_RIGHT = BORDER_RECT.right - 20
_PLAY_TOP = BORDER_RECT.top + 20
_PLAY_BOTTOM = BORDER_RECT.bottom - 20


# --------------- Helper ------------------
def generate_pellets(count: int) -> list:
    """Return a list of *count* random [x, y] pellet positions inside the border."""
    return [
        [random.randint(60, 500), random.randint(60, 560)]
        for _ in range(count)
    ]


# --------------- Classes -----------------
class Player:
    """The Pac-Man player character controlled by the keyboard."""

    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 17
        self.dx = 0
        self.dy = 0

    def move(self):
        """Move the player, clamped within the play area."""
        new_x = self.x + self.dx
        new_y = self.y + self.dy

        if _PLAY_LEFT < new_x < _PLAY_RIGHT:
            self.x = new_x
        if _PLAY_TOP < new_y < _PLAY_BOTTOM:
            self.y = new_y

    def draw(self, surface: pygame.Surface):
        """Draw the player circle on *surface*."""
        pygame.draw.circle(surface, YELLOW, (self.x, self.y), self.radius)


class Ghost:
    """An enemy ghost that bounces around the play area."""

    COLORS = [
        (255, 0, 0), (0, 255, 255), (255, 182, 193),
        (0, 255, 0), (255, 165, 0), (160, 32, 240),
    ]

    def __init__(self):
        self.x = random.randint(80, 480)
        self.y = random.randint(80, 480)
        self.color = random.choice(Ghost.COLORS)
        self.size = 20
        self.delay = random.randint(3, 6)
        self.frame = 0
        self.dx = random.choice([-1, 1])
        self.dy = random.choice([-1, 1])

    def move(self):
        """Advance the ghost by one step (respects its individual delay)."""
        self.frame += 1
        if self.frame % self.delay != 0:
            return

        new_x = self.x + self.dx * GHOST_SPEED
        new_y = self.y + self.dy * GHOST_SPEED

        if not (_PLAY_LEFT < new_x < _PLAY_RIGHT):
            self.dx *= -1
        else:
            self.x = new_x

        if not (_PLAY_TOP < new_y < _PLAY_BOTTOM):
            self.dy *= -1
        else:
            self.y = new_y

    def draw(self, surface: pygame.Surface):
        """Draw the ghost rectangle on *surface*."""
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))


# --------------- Functions ---------------
def check_collision(player: Player, ghost: Ghost) -> bool:
    """Return True when *player* overlaps *ghost* (circle-vs-rect approximation)."""
    ghost_cx = ghost.x + ghost.size // 2
    ghost_cy = ghost.y + ghost.size // 2
    dist = ((player.x - ghost_cx) ** 2 + (player.y - ghost_cy) ** 2) ** 0.5
    return dist < player.radius + ghost.size // 2


def reset_game():
    """Create and return a fresh (player, ghosts, pellets, score) tuple."""
    player = Player()
    ghosts = [Ghost() for _ in range(GHOST_COUNT)]
    pellets = generate_pellets(PELLET_COUNT)
    score = 0
    return player, ghosts, pellets, score


# --------------- Main --------------------
def main():
    """Initialise pygame and run the main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Man")
    clock = pygame.time.Clock()

    # Create fonts once, outside the game loop
    font_score = pygame.font.SysFont("Arial", 28)
    font_big = pygame.font.SysFont("Arial", 40)
    font_mid = pygame.font.SysFont("Arial", 30)

    player, ghosts, pellets, score = reset_game()
    game_over = False
    you_win = False

    running = True
    while running:
        screen.fill(BLACK)
        pygame.draw.rect(screen, BLUE, BORDER_RECT, 5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Arrow keys
                if event.key == pygame.K_LEFT:
                    player.dx, player.dy = -PLAYER_SPEED, 0
                elif event.key == pygame.K_RIGHT:
                    player.dx, player.dy = PLAYER_SPEED, 0
                elif event.key == pygame.K_UP:
                    player.dx, player.dy = 0, -PLAYER_SPEED
                elif event.key == pygame.K_DOWN:
                    player.dx, player.dy = 0, PLAYER_SPEED
                # WASD keys
                elif event.key == pygame.K_a:
                    player.dx, player.dy = -PLAYER_SPEED, 0
                elif event.key == pygame.K_d:
                    player.dx, player.dy = PLAYER_SPEED, 0
                elif event.key == pygame.K_w:
                    player.dx, player.dy = 0, -PLAYER_SPEED
                elif event.key == pygame.K_s:
                    player.dx, player.dy = 0, PLAYER_SPEED

        if not game_over and not you_win:
            # Draw pellets
            for p in pellets:
                pygame.draw.circle(screen, WHITE, (p[0], p[1]), 4)

            # Eat pellets
            for p in pellets[:]:
                if ((player.x - p[0]) ** 2 + (player.y - p[1]) ** 2) ** 0.5 < 20:
                    pellets.remove(p)
                    score += 1

            player.move()
            player.draw(screen)

            for g in ghosts:
                g.move()
                g.draw(screen)

                if check_collision(player, g):
                    game_over = True

            # Check win condition
            if not pellets:
                you_win = True

            # Score display
            text = font_score.render(f"Score: {score}", True, WHITE)
            screen.blit(text, (20, 580))

        elif you_win:
            text = font_big.render("YOU WIN! Press R", True, GREEN)
            screen.blit(text, (130, 280))
            score_text = font_mid.render(f"Final Score: {score}", True, WHITE)
            screen.blit(score_text, (200, 330))

        else:  # game_over
            text = font_big.render("GAME OVER! Press R", True, RED)
            screen.blit(text, (120, 280))
            score_text = font_mid.render(f"Final Score: {score}", True, WHITE)
            screen.blit(score_text, (200, 330))

        # Shared restart handler for both end-game states
        if game_over or you_win:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                player, ghosts, pellets, score = reset_game()
                game_over = False
                you_win = False

        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()

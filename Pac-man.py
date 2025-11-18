import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 560, 620
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (50, 50, 255)
WHITE = (255, 255, 255)

PLAYER_SPEED = 2
GHOST_SPEED = 1

BORDER_RECT = pygame.Rect(20, 20, WIDTH - 40, HEIGHT - 40)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 17
        self.dx = 0
        self.dy = 0

    def move(self):
        new_x = self.x + self.dx
        new_y = self.y + self.dy

        if BORDER_RECT.left + 20 < new_x < BORDER_RECT.right - 20:
            self.x = new_x
        if BORDER_RECT.top + 20 < new_y < BORDER_RECT.bottom - 20:
            self.y = new_y

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius)


class Ghost:
    def __init__(self):
        self.x = random.randint(80, 480)
        self.y = random.randint(80, 480)
        self.color = random.choice([
            (255, 0, 0), (0, 255, 255), (255, 182, 193),
            (0, 255, 0), (255, 165, 0), (160, 32, 240)
        ])
        self.size = 20

        self.delay = random.randint(3, 6)
        self.frame = 0

        self.dx = random.choice([-1, 1])
        self.dy = random.choice([-1, 1])

    def move(self):
        self.frame += 1
        if self.frame % self.delay != 0:
            return

        new_x = self.x + self.dx * GHOST_SPEED
        new_y = self.y + self.dy * GHOST_SPEED

        if not (BORDER_RECT.left + 20 < new_x < BORDER_RECT.right - 20):
            self.dx *= -1
        else:
            self.x = new_x

        if not (BORDER_RECT.top + 20 < new_y < BORDER_RECT.bottom - 20):
            self.dy *= -1
        else:
            self.y = new_y

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))


def collision(p, g):
    dist = ((p.x - g.x)**2 + (p.y - g.y)**2)**0.5
    return dist < 25


# -------- Pellets (Score Dots) ----------
pellets = []
for i in range(30):
    x = random.randint(60, 500)
    y = random.randint(60, 560)
    pellets.append([x, y])


player = Player()
ghosts = [Ghost() for _ in range(10)]  # 🔥 MORE GHOSTS
score = 0

running = True
game_over = False

while running:
    screen.fill(BLACK)
    pygame.draw.rect(screen, BLUE, BORDER_RECT, 5)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.dx, player.dy = -PLAYER_SPEED, 0
            if event.key == pygame.K_RIGHT:
                player.dx, player.dy = PLAYER_SPEED, 0
            if event.key == pygame.K_UP:
                player.dx, player.dy = 0, -PLAYER_SPEED
            if event.key == pygame.K_DOWN:
                player.dx, player.dy = 0, PLAYER_SPEED

    if not game_over:
        # Draw pellets
        for p in pellets:
            pygame.draw.circle(screen, WHITE, (p[0], p[1]), 4)

        # Eat pellets
        for p in pellets[:]:
            if ((player.x - p[0])**2 + (player.y - p[1])**2)**0.5 < 20:
                pellets.remove(p)
                score += 1

        player.move()
        player.draw()

        for g in ghosts:
            g.move()
            g.draw()

            if collision(player, g):
                game_over = True

        # Score Display
        font = pygame.font.SysFont("Arial", 28)
        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (20, 580))

    else:
        font = pygame.font.SysFont("Arial", 40)
        text = font.render("GAME OVER! Press R", True, (255, 0, 0))
        screen.blit(text, (120, 280))

        font2 = pygame.font.SysFont("Arial", 30)
        score_text = font2.render(f"Final Score: {score}", True, WHITE)
        screen.blit(score_text, (200, 330))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            player = Player()
            ghosts = [Ghost() for _ in range(10)]
            pellets = []
            for i in range(30):
                pellets.append([random.randint(60, 500), random.randint(60, 560)])
            score = 0
            game_over = False

    pygame.display.update()
    clock.tick(60)

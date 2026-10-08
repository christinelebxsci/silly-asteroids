import pygame
import math
import random
import asyncio

async def main():
    pygame.init()
    WIDTH = 800
    HEIGHT = 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Enemy class
    class Enemy:
        def __init__ (self):
            self.position = pygame.Vector2(WIDTH / 4, HEIGHT / 2)
            self.angle = 0
            self.velocity = pygame.math.Vector2(HEIGHT / 2, 0)

    # Player class
    class Player:
        def __init__(self):
            self.position = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
            self.angle = 90
            self.velocity = pygame.Vector2(0, 0)
            self.forward = pygame.Vector2(0, 0)
            self.acceleration = pygame.Vector2(0, 0)

    # Missile class
    class Missile:
        def __init__(self, position, r, color, direct, evil):
            self.position = position
            self.r = r
            self.color = color
            self.direct = direct
            self.evil = evil

        def draw(self):
            pygame.draw.circle(screen, self.color, self.position, self.r)

    # Enemy's missiles class
    class evil(Missile):
        def __init__(self, position, r, color, direct, evil):
            super().__init__(position, r, color, direct, evil)
            self.position = position
            self.r = r
            self.color = color
            self.direct = direct
            self.evil = evil

    # Asteroid class
    class Asteroid:
        def __init__(self, pos, r, color, vector):
            self.pos = pos
            self.r = r
            self.color = color
            self.vector = vector

        def draw(self):
            pygame.draw.circle(screen, self.color, self.pos, self.r)

        def move(self):
            self.pos += pygame.math.Vector2(self.vector)

        def collide(self, other):
            if math.sqrt((other.pos.x - self.pos.x)**2 + (other.pos.y - self.pos.y)**2) <= self.r + other.r:
                normal = (self.pos - other.pos).normalize()

                self.vector *= normal + (1, 1)
                other.vector *= normal + (1, 1)
                return True
            return False

    # Create player, enemy, list of missiles, & list of asteroids
    player = Player()
    enemy = Enemy()
    missiles = []
    asteroids = []

    # Speed constants
    MISSILE_SPEED = 8
    ROTATION_SPEED = 0
    MAX_SPEED = 50

    # Gravity constants
    THRUST = .25
    DRAG = 0.99

    # Enemy variables
    DETECTION_RANGE = 250
    FOV_THRESHOLD = 0.97
    detected = False

    font = pygame.font.SysFont("arial", 30)

    # Game variables
    timer = 0
    score = 0
    final = 0
    lives = 10

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Register key inputs
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                ROTATION_SPEED += 1
            
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                ROTATION_SPEED -= 1

            # Thrust
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player.acceleration = player.forward * THRUST
                player.is_thrusting = True
            else:
                player.is_thrusting = False
        
            # Fire a missile
            if keys[pygame.K_SPACE]:
                direction = player.forward
                missile = Missile(pygame.Vector2(player.position.x, player.position.y), 10, "green", direction, False)
                missiles.append(missile)

        # Create asteroids
        if len(asteroids) < 7:
            add = True
            r = random.randint(15, 50)
            pos = pygame.math.Vector2(random.randint(0 + r, WIDTH - r), random.randint(0 + r, HEIGHT - r))
            color = "gray"
            vector = pygame.math.Vector2(random.randint(-5, 5), random.randint(-5, 5))
        
            asteroid = Asteroid(pos, r, color, vector)

            for a in asteroids:
                    if asteroid.collide(a):
                        add = False
        
            if add:
                asteroids.append(asteroid)

        # Move missiles
        for m in missiles:    
            missile_velocity = m.direct * MISSILE_SPEED
            m.position += missile_velocity

            if m.position.x > WIDTH or m.position.y > HEIGHT:
                missiles.remove(m)

        # Move asteroids   
        for a in asteroids:
            a.move()

            if not (-100 < a.pos.x < WIDTH + 100) or not (-100 < a.pos.y < HEIGHT + 100):
                asteroids.remove(a)
            if a.vector == pygame.Vector2(0, 0):
                asteroids.remove(a)

        # Asteroid-asteroid collision
        for i in range(len(asteroids)):
            for j in range(len(asteroids)):
                if j != i:
                    asteroids[i].collide(asteroids[j])

        # Missile-asteroid & missile-player collision
        for m in missiles:
            for a in asteroids:
                distance = m.position.distance_to(a.pos)
            
                if distance < m.r + a.r and m.evil == False and lives > 0:
                    missiles.remove(m)
                    asteroids.remove(a)
                    score += 1
                    break
            
            distance = m.position.distance_to(player.position)
            if distance < m.r and m.evil == True:
                missiles.remove(m)
                lives -= 1

        # Asteroid-player collision
            for a in asteroids:
                distance = a.pos.distance_to(player.position)
            
                if distance < a.r:
                    asteroids.remove(a)
                    lives -= 1

        # Move enemy
        enemy.position += enemy.velocity

        if enemy.position.x > WIDTH:
            enemy.position.x = 0

        if enemy.position.x < 0:
            enemy.position.x = WIDTH

        if enemy.position.y > HEIGHT:
            enemy.position.y = 0

        if enemy.position.y < 0:
            enemy.position.y = HEIGHT

        if enemy.velocity.length() > MAX_SPEED:
            enemy.velocity.scale_to_length(MAX_SPEED)
        
        # Move player
        player.velocity += player.acceleration
        player.velocity *= DRAG
        player.position += player.velocity

        if player.position.x > WIDTH:
            player.position.x = 0

        if player.position.x < 0:
            player.position.x = WIDTH

        if player.position.y > HEIGHT:
            player.position.y = 0

        if player.position.y < 0:
            player.position.y = HEIGHT

        # Rotate player
        player.angle += ROTATION_SPEED

        # Forward direction of player & enemy
        radians = math.radians(player.angle)
        player.forward = pygame.Vector2(math.cos(radians), -math.sin(radians))

        radians = math.radians(enemy.angle)
        enemy_forward = pygame.Vector2(math.cos(radians), -math.sin(radians))

        # Enemy-player detection
        to_player = (player.position - enemy.position)
        if to_player.length() > 0:
            to_player = to_player.normalize()  

        distance = enemy.position.distance_to(player.position)
        dot = enemy_forward.dot(to_player)
    
        if (distance < DETECTION_RANGE and dot > FOV_THRESHOLD):
            detected = True

            direction = enemy_forward
            enemy.velocity = player.velocity * .7

            # Fire a missile at player
            if timer%50 == 0:
                timer = 0
                missile = evil(pygame.Vector2(enemy.position.x, enemy.position.y), 20, "orange", direction, True)
                missiles.append(missile)
            timer += 1
        else:
            detected = False
            enemy.angle += 1
        
        # Set final score
        if lives > 0:
            final = score
    
        # Positions for drawing player
        front = player.position + player.forward * 20
        left = player.forward.rotate(140)
        right = player.forward.rotate(-140)

        p1 = player.position + player.forward * 22
        p2 = player.position + left * 16
        p3 = player.position + right * 16

        # Visual display
        screen.fill((20, 24, 40))

        # Draw player
        if player.is_thrusting:
            back = player.position - player.forward * 18
            pygame.draw.circle(screen, "yellow", back, 5)

        pygame.draw.polygon(screen, "white", [p1, p2, p3], 2)

        # Reset acceleration
        player.acceleration = pygame.Vector2(0, 0)

        # Draw enemy
        if detected:
            pygame.draw.circle(screen, "red", enemy.position, 20)
        else:
            pygame.draw.circle(screen, "white", enemy.position, 20)
    
    # Draw enemy detection range
        pygame.draw.circle(screen, "gray", enemy.position, DETECTION_RANGE, 1)
        pygame.draw.line(screen, "red", enemy.position, enemy.position + enemy_forward * 100, 3)

        # Draw asteroids
        for a in asteroids:
            a.draw()

        # Draw missiles
        for m in missiles:
            m.draw()
        
        # Display score & lives
        scoretext = font.render("Score: " + str(score), True, "white")
        screen.blit(scoretext, (20, 20))
        
        scoretext = font.render("Lives: " + str(lives), True, "white")
        screen.blit(scoretext, (20, 80))

        if lives <= 0:
            screen.fill("black")
            text = font.render("GAME OVER !", True, "red")
            screen.blit(text, (WIDTH / 2, HEIGHT / 2 - 50))
            scoretext = font.render("Final Score: " + str(final), True, "white")
            screen.blit(scoretext, (WIDTH / 2, HEIGHT / 2))

        pygame.display.flip()
        clock.tick(60)

        await asyncio.sleep(0)
pygame.quit()
asyncio.run(main())
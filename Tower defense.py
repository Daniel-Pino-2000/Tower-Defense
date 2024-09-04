import pygame
import math
import random

# Initialize Pygame
pygame.init()

info = pygame.display.Info()
screen = pygame.display.set_mode((800, 600))

# Define some constants for the game
CITY_SIZE = 20
SILO_SIZE = 20
MISSILE_RADIUS = 4
PLAYER_MISSILE_SPEED = 2
ENEMY_MISSILE_SPEED = 1
ENEMY_MISSILE_SPAWN_RATE = 1000  # Lower value means more frequent spawns
EXPLOSION_RADIUS = 40
COLLISION_EXPLOSION_RADIUS = 80
GAME_OVER = False
LEVEL = 1

# Initialize cities
cities = [
    {"x": 100, "y": 550, "size": CITY_SIZE, "color": (0, 255, 0), "destroyed": False},
    {"x": 300, "y": 550, "size": CITY_SIZE, "color": (0, 255, 0), "destroyed": False},
    {"x": 500, "y": 550, "size": CITY_SIZE, "color": (0, 255, 0), "destroyed": False},
    {"x": 700, "y": 550, "size": CITY_SIZE, "color": (0, 255, 0), "destroyed": False},
]

# Initialize silos
silos = [
    {"x": 200, "y": 500, "size": SILO_SIZE, "color": (0, 0, 255), "ready": True, "destroyed": False, "core_destroyed": False},
    {"x": 400, "y": 500, "size": SILO_SIZE, "color": (0, 0, 255), "ready": True, "destroyed": False, "core_destroyed": False},
    {"x": 600, "y": 500, "size": SILO_SIZE, "color": (0, 0, 255), "ready": True, "destroyed": False, "core_destroyed": False},
]

# Initialize player missiles
player_missiles = []

# Initialize enemy missiles
enemy_missiles = []

# Initialize explosions
explosions = []

# Spawn initial enemy missiles
for _ in range(3):
    target = random.choice([city for city in cities if not city["destroyed"]] + [silo for silo in silos if not silo["core_destroyed"]])
    enemy_missiles.append({"x": random.randint(0, 800), "y": 0, "target": target, "target_type": "city" if target in cities else "silo", "trail": []})

# Main game loop
running = True
time = 0
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Find the closest ready silo to the click position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            closest_silo = None
            closest_distance = float("inf")
            for silo in silos:
                if silo["ready"] and not silo["core_destroyed"]:
                    distance = math.hypot(silo["x"] - mouse_x, silo["y"] - mouse_y)
                    if distance < closest_distance:
                        closest_silo = silo
                        closest_distance = distance
            if closest_silo is not None:
                # Fire a missile from the closest silo towards the click position
                player_missiles.append({"x": closest_silo["x"], "y": closest_silo["y"], "target_x": mouse_x, "target_y": mouse_y, "trail": []})
                # Allow the silo to fire again after a short delay
                closest_silo["ready"] = False
                pygame.time.set_timer(pygame.USEREVENT, 500, True)
        elif event.type == pygame.USEREVENT:
            for silo in silos:
                if not silo["ready"]:
                    silo["ready"] = True

    # Move player missiles
    for player_missile in player_missiles[:]:
        # Calculate the direction towards the target
        direction_x = player_missile["target_x"] - player_missile["x"]
        direction_y = player_missile["target_y"] - player_missile["y"]
        distance = math.hypot(direction_x, direction_y)
        if distance > PLAYER_MISSILE_SPEED:
            player_missile["x"] += direction_x / distance * PLAYER_MISSILE_SPEED
            player_missile["y"] += direction_y / distance * PLAYER_MISSILE_SPEED
            player_missile["trail"].append((player_missile["x"], player_missile["y"]))
        else:
            # Missile has reached its target, remove it and create an explosion
            if player_missile in player_missiles:
                player_missiles.remove(player_missile)
            explosions.append({"x": player_missile["target_x"], "y": player_missile["target_y"], "radius": 0})
        
    # Move enemy missiles
    for enemy_missile in enemy_missiles:
        # Calculate the direction towards the target
        direction_x = enemy_missile["target"]["x"] - enemy_missile["x"]
        direction_y = enemy_missile["target"]["y"] - enemy_missile["y"]
        distance = math.hypot(direction_x, direction_y)
        if distance > ENEMY_MISSILE_SPEED:
            enemy_missile["x"] += direction_x / distance * ENEMY_MISSILE_SPEED
            enemy_missile["y"] += direction_y / distance * ENEMY_MISSILE_SPEED
            enemy_missile["trail"].append((enemy_missile["x"], enemy_missile["y"]))
        else:
            # Missile has reached its target, remove it and damage the target
            if enemy_missile["target_type"] == "city":
                if enemy_missile["target"] in cities:
                    cities.remove(enemy_missile["target"])
            elif enemy_missile["target_type"] == "silo":
                if enemy_missile["target"] in silos:
                    if not enemy_missile["target"]["destroyed"]:
                        enemy_missile["target"]["destroyed"] = True
                    else:
                        enemy_missile["target"]["core_destroyed"] = True
            enemy_missiles.remove(enemy_missile)

    # Update explosions
    for explosion in explosions:
        explosion["radius"] += 1
        for enemy_missile in enemy_missiles[:]:
            distance = math.hypot(enemy_missile["x"] - explosion["x"], enemy_missile["y"] - explosion["y"])
            if distance < explosion["radius"]:
                enemy_missiles.remove(enemy_missile)
        if explosion["radius"] > EXPLOSION_RADIUS:
            explosions.remove(explosion)

    # Check for collisions between player missiles and enemy missiles
    for player_missile in player_missiles[:]:
        for enemy_missile in enemy_missiles[:]:
            distance = math.hypot(player_missile["x"] - enemy_missile["x"], player_missile["y"] - enemy_missile["y"])
            if distance < MISSILE_RADIUS * 2:
                # Missiles have collided, remove them and create a collision explosion
                if player_missile in player_missiles:
                    player_missiles.remove(player_missile)
                enemy_missiles.remove(enemy_missile)
                explosions.append({"x": player_missile["x"], "y": player_missile["y"], "radius": 0, "collision": True})


    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw cities
    for city in cities:
        pygame.draw.rect(screen, city["color"], (city["x"] - city["size"] / 2, city["y"] - city["size"] / 2, city["size"], city["size"]))

    # Draw silos
    for silo in silos:
        if not silo["destroyed"]:
            pygame.draw.rect(screen, silo["color"], (silo["x"] - silo["size"] / 2, silo["y"] - silo["size"] / 2, silo["size"], silo["size"]))
        if not silo["core_destroyed"]:
            pygame.draw.circle(screen, (255, 255, 255), (silo["x"], silo["y"]), silo["size"] / 4)

    # Draw player missiles
    for player_missile in player_missiles[:]:
        pygame.draw.circle(screen, (255, 255, 255), (int(player_missile["x"]), int(player_missile["y"])), MISSILE_RADIUS)
        for i in range(len(player_missile["trail"]) - 1):
            pygame.draw.line(screen, (255, 255, 255), player_missile["trail"][i], player_missile["trail"][i + 1], 2)

    # Draw enemy missiles
    for enemy_missile in enemy_missiles:
        pygame.draw.circle(screen, (255, 0, 0), (int(enemy_missile["x"]), int(enemy_missile["y"])), MISSILE_RADIUS)
        for i in range(len(enemy_missile["trail"]) - 1):
            pygame.draw.line(screen, (255, 0, 0), enemy_missile["trail"][i], enemy_missile["trail"][i + 1], 2)

    # Draw explosions
    for explosion in explosions:
        if "collision" in explosion:
            pygame.draw.circle(screen, (255, 255, 255), (explosion["x"], explosion["y"]), min(explosion["radius"], COLLISION_EXPLOSION_RADIUS))
        else:
            pygame.draw.circle(screen, (255, 255, 255), (explosion["x"], explosion["y"]), min(explosion["radius"], EXPLOSION_RADIUS))

    # Draw level
    font = pygame.font.Font(None, 32)
    text = font.render("Level: " + str(LEVEL), True, (255, 255, 255))
    screen.blit(text, (10, 10))

    # Update the game window
    pygame.display.flip()

    # Check for game over
    if all(city["destroyed"] for city in cities) and all(silo["core_destroyed"] for silo in silos):
        GAME_OVER = True

    if GAME_OVER:
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 64)
        text = font.render("Game Over", True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 - 100))
        screen.blit(text, text_rect)
    
        font = pygame.font.Font(None, 32)
        text = font.render("Level reached: " + str(LEVEL), True, (255, 215, 0))
        text_rect = text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 - 50))
        screen.blit(text, text_rect)
    
        restart_button = pygame.Rect(screen.get_width() / 2 - 100, screen.get_height() / 2, 200, 50)
        pygame.draw.rect(screen, (0, 255, 0), restart_button)
        font = pygame.font.Font(None, 32)
        text = font.render("Restart", True, (255, 255, 255))
        text_rect = text.get_rect(center=restart_button.center)
        screen.blit(text, text_rect)
    
        quit_button = pygame.Rect(screen.get_width() / 2 - 100, screen.get_height() / 2 + 60, 200, 50)
        pygame.draw.rect(screen, (255, 0, 0), quit_button)
        font = pygame.font.Font(None, 32)
        text = font.render("Quit", True, (255, 255, 255))
        text_rect = text.get_rect(center=quit_button.center)
        screen.blit(text, text_rect)
    
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.collidepoint(event.pos):
                        GAME_OVER = False
                        LEVEL = 1
                        cities = [
                            {"x": 100, "y": 550, "size": CITY_SIZE, "color": (0, 255, 0), "destroyed": False},
                            {"x": 300, "y": 550, "size": CITY_SIZE, "color": (0, 255, 0), "destroyed": False},
                            {"x": 500, "y": 550, "size": CITY_SIZE, "color": (0, 255, 0), "destroyed": False},
                            {"x": 700, "y": 550, "size": CITY_SIZE, "color": (0, 255, 0), "destroyed": False},
                        ]
                        silos = [
                            {"x": 200, "y": 500, "size": SILO_SIZE, "color": (0, 0, 255), "ready": True, "destroyed": False, "core_destroyed": False},
                            {"x": 400, "y": 500, "size": SILO_SIZE, "color": (0, 0, 255), "ready": True, "destroyed": False, "core_destroyed": False},
                            {"x": 600, "y": 500, "size": SILO_SIZE, "color": (0, 0, 255), "ready": True, "destroyed": False, "core_destroyed": False},
                        ]
                        player_missiles = []
                        enemy_missiles = []
                        explosions = []
                        time = 0
                        enemy_missiles = []
                        for _ in range(3):
                            target = random.choice([city for city in cities if not city["destroyed"]] + [silo for silo in silos if not silo["core_destroyed"]])
                            enemy_missiles.append({"x": random.randint(0, 800), "y": 0, "target": target, "target_type": "city" if target in cities else "silo", "trail": []})
                        break
                    elif quit_button.collidepoint(event.pos):
                        running = False
                        break
            if not running:
                break

    # Increase level
    if len(enemy_missiles) == 0:
        LEVEL += 1
        for _ in range(LEVEL * 3):
            target = random.choice([city for city in cities if not city["destroyed"]] + [silo for silo in silos if not silo["core_destroyed"]])
            enemy_missiles.append({"x": random.randint(0, 800), "y": 0, "target": target, "target_type": "city" if target in cities else "silo", "trail": []})

    # Cap the frame rate
    pygame.time.Clock().tick(60)

    # Increase the time
    time += 1

# Quit Pygame
pygame.quit()
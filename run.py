#!/usr/bin/env python3
"""Run Squares and Ships.

Squares and Ships is a simple, fun arcade game that has the player face ever
faster enemies that spawn endlessly. All sounds for the game are stored in the
/audio/ folder, and all images in the /sprites/ folder.
"""
import os
from random import randint

import pygame


def ship_control():
    """Update the position and state of the player."""
    game_display.blit(player_image, ship_rect)


def bullet_control(speed):
    """Update the position and state of each bullet."""
    for bullet in bullet_list:
        # Move the bullet upwards.
        bullet.y -= speed

        # Remove the bullet if it is offscreen.
        if bullet.y < 0 - bullet_height or bullet.y > display_height:
            bullet_list.remove(bullet)

        # Draw the bullet.
        game_display.blit(bullet_image, bullet)


def enemy_control(speed):
    """Update the position and state of each enemy."""
    for enemy in enemy_list:
        enemy_rect = enemy[0]
        image_index = enemy[1]

        # Move the enemy downwards.
        enemy_rect.y += speed

        # Create random side-to-side movement.
        enemy_rect.x += randint(-1, 1) * speed

        # Remove the enemy if it is offscreen.
        if enemy_rect.y > display_height:
            enemy_list.remove(enemy)

        # Draw the enemy.
        game_display.blit(enemy_images[image_index], enemy_rect)


def enemy_explosion_control():
    """Update the position and state of each enemy explosion."""
    for enemy_explosion in enemy_explosion_list:
        enemy_explosion_rect = enemy_explosion[0]
        current_frame = enemy_explosion[1]

        # Draw the explosion.
        game_display.blit(enemy_explosion_frames[int(current_frame)], enemy_explosion_rect)

        # Update the graphic.
        if int(current_frame) < len(enemy_explosion_frames) - 1:
            enemy_explosion[1] += .25
        else:
            enemy_explosion_list.remove(enemy_explosion)


def player_explosion_control():
    """Create and update the explosion that appears upon the player's death."""
    for frame in player_explosion_frames:
        game_display.fill(black)
        game_display.blit(frame, (ship_rect.x - 15, ship_rect.y - 14))

        # Update the game screen for each frame of explosion, since it runs outside of the main loop.
        pygame.display.update()
        pygame.time.wait(100)

    game_display.fill(black)
    pygame.display.update()


def load_images(image_name, n, extension='.bmp'):
    """Create a list of n images from filenames of the format [image_name][#][extension]."""
    images = []

    for i in range(n):
        filename = image_name + str(i) + extension
        images.append(pygame.image.load(os.path.join(image_folder, filename)).convert_alpha())

    return images


def game_loop():	
    """Create an instance of the game. Upon dying, call this function again until SystemExit."""
    ship_rect.x = 0.5 * display_width - 0.5 * ship_rect.w
    ship_rect.y = 0.8 * display_height

    frame_rate = 60

    score = 0

    player_speed = 5
    bullet_speed = 5

    # Set the variables related to enemy spawn.
    spawn_counter = 0
    initial_wait = 2 * frame_rate    # measured in frames
    spawn_frequency = 10
    number_per_spawn = 1

    game_over = False

    # Clear the events left over from the previous game.
    for event in pygame.event.get():
        pygame.event.clear()

    # Run this loop once per frame.
    while not game_over:
        for event in pygame.event.get():
            # End game if the program is exited.
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            # Spawn bullets if space is pressed.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Represent the bullet with a collision object.
                    bullet_list.append(pygame.Rect(ship_rect.x + 0.5 * ship_rect.w - 3, ship_rect.y - bullet_height, bullet_width, bullet_height))
                    bullet_sound.play()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            if ship_rect.x + ship_rect.w + player_speed < display_width:
                ship_rect.x += player_speed
            else:
                ship_rect.x = display_width - ship_rect.w

        if keys[pygame.K_LEFT]:
            if ship_rect.x - player_speed > 0:
                ship_rect.x -= player_speed
            else:
                ship_rect.x = 0

        # Check for collisions.
        for enemy in enemy_list:
            enemy_rect = enemy[0]

            if enemy_rect.colliderect(ship_rect):
                game_over = True

            for bullet in bullet_list:
                if enemy_rect.colliderect(bullet):
                    score += 1

                    bullet_list.remove(bullet)

                    # Represent an enemy explosion with a list containing a collision object and its current frame.
                    enemy_explosion_list.append([pygame.Rect(enemy[0].x - 18, enemy[0].y - 18, enemy_explosion_width, enemy_explosion_height), 0])

                    enemy_death_sound.play()
                    enemy_list.remove(enemy)

        # Spawn enemies.
        enemy_speed = 1 + int((score % 100) / 10)
        number_per_spawn = 1 + int(score / 100)

        if spawn_counter >= initial_wait and (spawn_counter - initial_wait) % spawn_frequency == 0:
            for i in range(number_per_spawn):
                # Represent an enemy explosion with a list containing a collision object and its image.
                random_image = randint(0, len(enemy_images) - 1)
                enemy_list.append((pygame.Rect(randint(0, display_width - enemy_width), 0 - enemy_height, enemy_width, enemy_height), random_image))

        spawn_counter += 1

        # Draw the screen.
        game_display.fill(black)

        ship_control()
        bullet_control(bullet_speed)
        enemy_control(enemy_speed)
        enemy_explosion_control()

        # Render the text.
        score_text = game_font.render("Score: %s" % (score), True, white)
        level_text = game_font.render("Level: %s-%s" % (number_per_spawn, enemy_speed), True, white)

        game_display.blit(score_text, (10, 5))
        game_display.blit(level_text, (10, 29))

        # print(event)
        # print(ship_rect)
        # print(bullet_list)
        # print(enemy_list)
        # print(enemy_explosion_list)

        pygame.display.update()
        clock.tick(frame_rate)

    del enemy_list[:]
    del bullet_list[:]
    del enemy_explosion_list[:]

    # Run through the death animation.
    player_death_sound.play()
    player_explosion_control()
 
    pygame.time.wait(1000)


data_folder = os.path.dirname(os.path.abspath(__file__))
audio_folder = os.path.join(data_folder, 'audio')
image_folder = os.path.join(data_folder, 'sprites')

# Initialize pygame.
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()

# Create a display and a title.
display_width = 600
display_height = 800

game_display = pygame.display.set_mode((display_width, display_height))

pygame.display.set_caption("Squares and Ships")

# Set up the in-game font.
game_font = pygame.font.SysFont('roboto', 24)

# Set some color constants.
black = (0, 0, 0)
white = (255, 255, 255)

# Create a clock object that tracks time within game in frames.
clock = pygame.time.Clock()

# Initialize the sound effects (ripped straight from Space Invaders).
bullet_sound = pygame.mixer.Sound(os.path.join(audio_folder, 'bullet.wav'))
enemy_death_sound = pygame.mixer.Sound(os.path.join(audio_folder, 'enemy_death.wav'))
player_death_sound = pygame.mixer.Sound(os.path.join(audio_folder, 'player_death.wav'))

# Initialize the sprites (ripped straight from Galaga).
player_width = 32
player_height = 32
player_image = pygame.image.load(os.path.join(image_folder, 'ship.bmp')).convert_alpha()

pygame.display.set_icon(player_image)   # Set the icon to appear at the top-left corner.

bullet_width = 6
bullet_height = 16
bullet_image = pygame.image.load(os.path.join(image_folder, 'bullet.bmp')).convert_alpha()

enemy_width = 26
enemy_height = 20
enemy_images = load_images('enemy', 5)

enemy_explosion_width = 64
enemy_explosion_height = 64
enemy_explosion_frames = load_images('enemy_explosion', 5)

player_explosion_frames = load_images('player_explosion', 4)

# Keep track of the collision objects onscreen.
ship_rect = pygame.Rect(0.5 * display_width - 0.5 * player_width, 0.8 * display_height, player_width, player_height)
bullet_list = []
enemy_list = []
enemy_explosion_list = []

while True:
    game_loop()


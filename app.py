import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
import random
import socket
from datetime import datetime
import json
import os
import pygame
import time

# Initialize pygame mixer for sound effects
pygame.mixer.init()

# Load sound effects
choice_sound = pygame.mixer.Sound('choice.wav')
apple_sound = pygame.mixer.Sound('apple.wav')
gameover_sound = pygame.mixer.Sound('gameover.wav')

# Function to get the IP address
def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

# Function to log score and player data
def log_score(score, ip_address, player_data):
    with open("scores.txt", "a") as file:
        file.write(f"{datetime.now()} | Score: {score} | User: {ip_address}\n")
    
    with open(f"{ip_address}_data.json", "a") as file:
        json.dump(player_data, file)
        file.write("\n")

# Function to calculate new game speed based on player's previous performance
def calculate_game_speed(ip_address, base_speed=150):
    try:
        with open(f"{ip_address}_data.json", "r") as file:
            data = [json.loads(line) for line in file]
            if not data:
                return base_speed
            average_score = sum([d['score'] for d in data]) / len(data)
            average_duration = sum([d['duration'] for d in data]) / len(data)
            speed_adjustment = int(average_score / 10)
            new_speed = base_speed - speed_adjustment
            return max(new_speed, 50)  # Ensure the speed doesn't get too fast
    except FileNotFoundError:
        return base_speed

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    sh, sw = stdscr.getmaxyx()
    menu_win = curses.newwin(10, 30, (sh // 2) - 5, (sw // 2) - 15)
    
    # Display menu
    menu_win.addstr(2, 5, "1. Start the game")
    menu_win.addstr(3, 5, "2. Quit")
    menu_win.refresh()

    while True:
        key = menu_win.getch()
        if key == ord('1'):
            choice_sound.play()  # Play sound for choice selection
            menu_win.clear()  # Clear menu
            break
        elif key == ord('2'):
            choice_sound.play()  # Play sound for choice selection
            return
        elif key == ord('0'):
            # Secret admin page
            choice_sound.play()  # Play sound for choice selection
            menu_win.clear()
            menu_win.addstr(2, 5, "Welcome to Admin Page!")
            menu_win.addstr(4, 5, "Press any key to continue...")
            menu_win.refresh()
            menu_win.getch()
            menu_win.clear()
            menu_win.addstr(2, 5, "1. Start the game")
            menu_win.addstr(3, 5, "2. Quit")
            menu_win.refresh()

    # Setup game window
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Snake color
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Apple color
    win = curses.newwin(20, 60, (sh // 2) - 10, (sw // 2) - 30)
    win.keypad(1)

    # Initial snake and food settings
    snake = [(4, 10), (4, 9), (4, 8)]
    food = (10, 20)
    win.addch(food[0], food[1], '●', curses.color_pair(2))
    score = 0

    ESC = 27
    key = KEY_RIGHT

    # Get user's IP address
    ip_address = get_ip_address()

    # Calculate game speed
    game_speed = calculate_game_speed(ip_address)

    # Player data
    player_data = {
        'moves': {KEY_UP: 0, KEY_DOWN: 0, KEY_LEFT: 0, KEY_RIGHT: 0},
        'score': 0,
        'duration': 0,
    }

    # Main game loop
    start_time = datetime.now()
    while key != ESC:
        win.border(0)
        win.addstr(0, 2, 'Score : ' + str(score) + ' ')
        win.timeout(game_speed - (len(snake)) // 5 + len(snake) // 10 % 120)

        prev_key = key
        event = win.getch()
        key = key if event == -1 else event

        if key not in [KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, ESC]:
            key = prev_key

        # Track player moves
        if key in player_data['moves']:
            player_data['moves'][key] += 1

        # Calculate new coordinates of the head of the snake
        y = snake[0][0]
        x = snake[0][1]
        if key == KEY_DOWN:
            y += 1
        if key == KEY_UP:
            y -= 1
        if key == KEY_LEFT:
            x -= 1
        if key == KEY_RIGHT:
            x += 1

        # Insert new head and remove tail
        snake.insert(0, (y, x))

        # Check if snake hits the border
        if y == 0 or y == 19 or x == 0 or x == 59:
            gameover_sound.play()  # Play game over sound
            time.sleep(2)  # Wait for 2 seconds to let the sound play
            break
        if snake[0] in snake[1:]:
            gameover_sound.play()  # Play game over sound
            time.sleep(2)  # Wait for 2 seconds to let the sound play
            break

        if snake[0] == food:
            score += 1
            apple_sound.play()  # Play apple eat sound
            player_data['score'] = score
            food = ()
            while food == ():
                food = (random.randint(1, 18), random.randint(1, 58))
                if food in snake:
                    food = ()
            win.addch(food[0], food[1], '●', curses.color_pair(2))
        else:
            last = snake.pop()
            win.addch(last[0], last[1], ' ')

        win.addch(snake[0][0], snake[0][1], '■', curses.color_pair(1))

    curses.endwin()

    # Log game duration
    end_time = datetime.now()
    player_data['duration'] = (end_time - start_time).total_seconds()

    # Log the score and player data
    log_score(score, ip_address, player_data)

    print(f"Final score = {score}")

if __name__ == "__main__":
    curses.wrapper(main)

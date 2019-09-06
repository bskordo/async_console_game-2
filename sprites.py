import curses
import asyncio
from tools import get_terminal_size, draw_frame,get_frame_size,read_controls
from physics import update_speed
from obstacles import Obstacle, show_obstacles
from explosion import explode
from glob_vars import obstacles, coroutines, obstacles_in_last_collisions, year
from pictures import get_game_over_text

async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    global obstacles
    global obstacles_in_last_collisions
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                obstacles_in_last_collisions.append(obstacle)
                return
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def correct_row(max_available_row, current_row, frame_rows_number ):
    corrected_row = current_row
    if current_row >= max_available_row - frame_rows_number :
        corrected_row = max_available_row - frame_rows_number  - 1
    elif current_row <= 0:
        corrected_row = 1
    return corrected_row


def correct_column(max_available_column, current_column, frame_columns_number):
    corrected_column = current_column
    if current_column > max_available_column - frame_columns_number:
        corrected_column = max_available_column - (frame_columns_number + 1)
    elif current_column <= 1:
        corrected_column = 1
    return corrected_column


async def animate_spaceship(sprites):
    global spaceship_frame
    while True:
        for sprite in sprites:
            spaceship_frame = sprite
            await asyncio.sleep(0)


async def show_gameover(canvas):
    max_available_row, max_available_column = get_terminal_size()
    gameover_frame = get_game_over_texts()
    rows, columns = get_frame_size(gameover_frame)
    center_row = (max_available_row / 2) - (rows / 2)
    center_column = (max_available_column / 2) - (columns / 2)
    while True:
        draw_frame(canvas,  center_row, center_column, gameover_frame)
        await asyncio.sleep(0)


async def run_spaceship(canvas):
    global year
    global spaceship_frame
    global coroutines
    global obstacles
    global spaceship_frame
    max_available_row, max_available_column = get_terminal_size()
    row, column = max_available_row - 10, max_available_column / 2
    row_speed = column_speed = 0

    while True:
        current_year = year.get('current_year')
        frame_rows_number, frame_columns_number = get_frame_size(spaceship_frame)

        prev_sprite_row, prev_sprite_column = row, column
        prev_spaceship_frame = spaceship_frame
        canvas.nodelay(True)
        row_pos, column_pos, space = read_controls(canvas)

        row_speed, column_speed = update_speed(row_speed, column_speed, row_pos, column_pos)
        row += row_pos + row_speed
        column += column_pos + column_speed
        if space and current_year >= 2020:
            # for gun position in the center of the spaceship
            column_for_fire = column+2
            fire_animation = fire(canvas, row, column_for_fire, rows_speed=FIRE_SPEED)
            coroutines.append(fire_animation)
        row = correct_row(max_available_row, row, frame_rows_number)
        column = correct_column(max_available_column, column, frame_columns_number)
        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                draw_frame(canvas, prev_sprite_row, prev_sprite_column, prev_spaceship_frame, negative=True)
                coroutines.append(show_gameover(canvas))
                return
        await asyncio.sleep(0)
        draw_frame(canvas, prev_sprite_row, prev_sprite_column, prev_spaceship_frame, negative=True)
        draw_frame(canvas, row, column, spaceship_frame, negative=False)


async def fly_garbage(canvas, column, garbage_frame, speed=0.8):
    global obstacles
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)
    row = 0
    rows, columns = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, rows, columns)
    obstacles.append(obstacle)
    canvas.addstr('')
    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        obstacle.row = row

        await asyncio.sleep(0)

        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        obstacle.row += speed
        if obstacle in obstacles_in_last_collisions:
            explode_row = row + (rows/2)
            explode_column = column + (columns/2)
            await explode(canvas, explode_row, explode_column)
            obstacles.remove(obstacle)
            return
    obstacles.remove(obstacle)



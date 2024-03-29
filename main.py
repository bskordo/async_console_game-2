import sys
import time
import random
import curses
import asyncio
from game_scenario import get_garbage_delay_tics, PHRASES
from sprites import fly_garbage, animate_spaceship, run_spaceship, fire
from glob_vars import coroutines, year, obstacles
from tools import get_terminal_size, draw_frame
from pictures import get_frames, get_garbages


SPACESHIP_SPEED = 2
STARS_COUNT = 80
FIRE_SPEED = -3
TIC_TIMEOUT = 0.1
YEAR_DURATION = 20
BORDER_MARGIN = 1


async def sleep(tics=0):
    for step in range(tics):
        await asyncio.sleep(0)


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(200)

        canvas.addstr(row, column, symbol)
        await sleep(50)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(100)

        canvas.addstr(row, column, symbol)
        await sleep(5)


def get_message(year):
    phrase = PHRASES.get(year)
    message = year
    if phrase:
        message = f'{year}: {phrase}'
    return message


def get_stars(canvas, stars_count=80):
    stars = []
    max_y, max_x = get_terminal_size()
    for _ in range(0, stars_count):
        symbol = random.choice('+*.:')
        y_coord = random.randint(1, max_y - BORDER_MARGIN)
        x_coord = random.randint(1, max_x - BORDER_MARGIN)
        star = blink(canvas, y_coord, x_coord, symbol)
        stars.append(star)
    return stars


def get_fire(canvas):
    max_y, max_x = get_terminal_size()
    return fire(canvas, max_y - BORDER_MARGIN, round(max_x / 2) + 2, rows_speed=FIRE_SPEED)


def get_trash(canvas):
    garbages = get_garbages()
    garbage = random.choice(garbages)
    _, max_x = get_terminal_size()
    columns = max_x - BORDER_MARGIN
    column_for_trash = random.randint(1, columns)
    return fly_garbage(canvas, column_for_trash, garbage)


async def fill_orbit_with_garbage(canvas):
    global coroutines
    global obstacles
    global year
    while True:
        current_year = year.get('current_year')
        await_time = get_garbage_delay_tics(current_year)
        await sleep(await_time)
        garbage = get_trash(canvas)
        coroutines.append(garbage)


async def run_scenario(canvas):
    global year
    max_y, max_x = get_terminal_size()

    while True:
        current_year = year.get('current_year')
        previous_message = get_message(current_year-1)
        draw_frame(canvas, round(max_y - BORDER_MARGIN), round(2), str(previous_message), negative=True)
        message = get_message(current_year)
        draw_frame(canvas, round(max_y - BORDER_MARGIN), round(2), str(message))
        if current_year == 1961:
            orbit_with_garbage = fill_orbit_with_garbage(canvas)
            coroutines.append(orbit_with_garbage)
        if current_year == 2020:
            fire_animation = get_fire(canvas)
            coroutines.append(fire_animation)
        await sleep(YEAR_DURATION)
        year['current_year'] += 1


def main(canvas, frames):
    global coroutines
    global year

    curses.curs_set(False)
    canvas.nodelay(True)
    year_change = run_scenario(canvas)
    coroutines.append(year_change)
    spaceship_frame = animate_spaceship(frames)
    coroutines.append(spaceship_frame)
    spaceship = run_spaceship(canvas)
    coroutines.append(spaceship)

    stars = get_stars(canvas, STARS_COUNT)
    coroutines += stars

    while True:
        for coro in coroutines:
            try:
                coro.send(None)
            except StopIteration:
                coroutines.remove(coro)
        canvas.refresh()

        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    frames = get_frames()
    garbages = get_garbages()
    curses.update_lines_cols()
    curses.wrapper(main, frames)
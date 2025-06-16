import curses
import random

# Define directions
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)

KEY_DIRECTION = {
    curses.KEY_UP: UP,
    curses.KEY_DOWN: DOWN,
    curses.KEY_LEFT: LEFT,
    curses.KEY_RIGHT: RIGHT,
}


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    sh, sw = stdscr.getmaxyx()
    box = [[3, 3], [sh - 3, sw - 3]]
    for y in range(box[0][0], box[1][0]):
        stdscr.addstr(y, box[0][1], '|' + ' ' * (box[1][1] - box[0][1] - 1) + '|')
    stdscr.addstr(box[0][0] - 1, box[0][1], '+' + '-' * (box[1][1] - box[0][1] - 1) + '+')
    stdscr.addstr(box[1][0], box[0][1], '+' + '-' * (box[1][1] - box[0][1] - 1) + '+')

    snake = [[sh // 2, sw // 2 + i] for i in range(3)][::-1]
    direction = LEFT
    food = None
    score = 0

    def place_food():
        while True:
            nf = [random.randint(box[0][0] + 1, box[1][0] - 1),
                  random.randint(box[0][1] + 1, box[1][1] - 1)]
            if nf not in snake:
                return nf

    food = place_food()

    while True:
        stdscr.addstr(box[0][0] - 2, box[0][1], f"Score: {score}")
        stdscr.addstr(food[0], food[1], '*')
        for y, x in snake:
            stdscr.addstr(y, x, '#')
        stdscr.refresh()

        key = stdscr.getch()
        if key in KEY_DIRECTION:
            new_direction = KEY_DIRECTION[key]
            # Prevent reversing
            if (new_direction[0] != -direction[0] or new_direction[1] != -direction[1]):
                direction = new_direction

        head = [snake[0][0] + direction[0], snake[0][1] + direction[1]]
        if (head[0] in (box[0][0], box[1][0]) or
                head[1] in (box[0][1], box[1][1]) or
                head in snake):
            msg = "Game Over! Press any key to exit"
            stdscr.nodelay(False)
            stdscr.addstr(sh // 2, sw // 2 - len(msg) // 2, msg)
            stdscr.getch()
            break

        snake.insert(0, head)
        if head == food:
            score += 1
            food = place_food()
        else:
            tail = snake.pop()
            stdscr.addstr(tail[0], tail[1], ' ')
        stdscr.addstr(head[0], head[1], '#')
        stdscr.addstr(food[0], food[1], '*')


if __name__ == '__main__':
    curses.wrapper(main)

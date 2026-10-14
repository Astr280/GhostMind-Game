"""Central tuning values and the GhostMind Neon Nocturne palette."""
WIDTH, HEIGHT, FPS = 1280, 800, 60
COIN_SCORE, POWER_SCORE, GHOST_SCORE, LEVEL_SCORE = 10, 50, 200, 500
PLAYER_SPEED = 8.0
DIFFICULTIES = {
    # Enemy speed stays meaningfully below the player on every setting.
    'EASY': {'ghost': 2.35, 'power': 10.0, 'replan': .95},
    'MEDIUM': {'ghost': 3.00, 'power': 7.5, 'replan': .65},
    'HARD': {'ghost': 3.65, 'power': 5.5, 'replan': .42},
}
NAVY=(5, 8, 24); SURFACE=(12, 19, 43); SURFACE_2=(19, 29, 61)
CYAN=(34, 230, 255); CYAN_DIM=(24, 94, 157); BLUE=(53, 119, 255)
GOLD=(255, 190, 58); YELLOW=(255, 224, 73); WHITE=(232, 244, 255); MUTED=(137, 158, 202)
RED=(245, 65, 82); PINK=(255, 92, 201); ORANGE=(255, 159, 58); FRIGHT=(94, 128, 255)
MAZE_ACCENTS=(CYAN, (94, 128, 255), (193, 91, 255))

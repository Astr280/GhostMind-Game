import unittest
from maze import Maze
from entities import Player
from game import Game

class GameplayTests(unittest.TestCase):
    def test_every_level_target_is_connected(self):
        from algorithms import bfs
        for level in (1, 2, 3):
            maze = Maze.build(level)
            for target in maze.coins | maze.powers | set(maze.ghost_spawns):
                self.assertTrue(bfs(maze.player_spawn, target, maze.walkable).found)

    def test_sectors_have_visibly_distinct_layouts(self):
        layouts = {tuple(Maze.build(level).rows) for level in (1, 2, 3)}
        self.assertEqual(len(layouts), 3)

    def test_player_moves_smoothly_and_never_enters_wall(self):
        maze = Maze.build(1); player = Player(maze.player_spawn, speed=4)
        player.queued = 'RIGHT'; player.update(maze, .1)
        self.assertIsNotNone(player.next_tile)
        player.update(maze, .1)
        self.assertGreater(player.position[0], float(maze.player_spawn[0]))
        self.assertLess(player.position[0], float(maze.player_spawn[0] + 1))
        for _ in range(10): player.update(maze, .1)
        self.assertTrue(maze.walkable(player.tile))

    def test_coin_and_power_core_score_once(self):
        game = Game(); pos = game.player.tile
        game.maze.coins.add(pos); game.update(0)
        self.assertEqual(game.score, 10)
        game.update(0)
        self.assertEqual(game.score, 10)
        game.maze.powers.add(pos); game.update(0)
        self.assertEqual(game.score, 60)
        self.assertGreater(game.power, 0)

    def test_one_up_token_awards_a_life_once(self):
        game = Game(); token = game.maze.life_token
        game.player.tile = token; game.player.position[:] = token; game.player.next_tile = None
        before = game.lives; game.update(0)
        self.assertEqual(game.lives, before + 1)
        self.assertIsNone(game.maze.life_token)

    def test_continuous_ghost_collision_starts_a_respawn_freeze(self):
        game = Game(); ghost = game.ghosts[0]
        ghost.tile = game.player.tile; ghost.position[:] = game.player.position; ghost.speed = 0
        game.invulnerable = 0; game.opening_timer = 0; before = game.lives; game.update(0)
        self.assertEqual(game.lives, before - 1)
        self.assertGreater(game.respawn_timer, 0)

if __name__ == '__main__': unittest.main()

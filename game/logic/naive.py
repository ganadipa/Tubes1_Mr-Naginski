import random
from typing import Optional, List, Tuple

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction


class NaiveLogic(BaseLogic):
    def __init__(self):
        self.teleport_gate: List[Position]
        self.possible_directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        return
        # self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        # self.current_direction = 0

    def set_goal(self, goal: GameObject, force: bool):
        pos_x = self.current_position.x
        pos_y = self.current_position.y
        teleports = self.teleport_gate
        props = goal.properties

        min_distance = float('inf')
        if (self.goal_position and not force):
            min_distance = abs(pos_x - self.goal_position.x) + \
                abs(pos_y - self.goal_position.y)

        # Masuk tanpa teleport
        distance = abs(goal.position.x - pos_x) + \
            abs(goal.position.y - pos_y)
        if (min_distance > distance):
            self.goal_position = Position(
                goal.position.y, goal.position.x)
            min_distance = distance
        elif (goal.type == "DiamondGameObject"):
            if (min_distance == distance and props.points == 2):
                self.goal_position = Position(
                    goal.position.y, goal.position.x)
                min_distance = distance

        # Masuk lewat teleport pertama
        distance_x = abs(teleports[0].x - pos_x) + \
            abs(teleports[1].x - goal.position.x)
        distance_y = abs(teleports[0].y - pos_y) + \
            abs(teleports[1].y - goal.position.y)
        distance = distance_x + distance_y
        if (min_distance > distance):
            self.goal_position = Position(
                teleports[0].y, teleports[0].x)
            min_distance = distance
        elif (goal.type == "DiamondGameObject"):
            if (min_distance == distance and props.points == 2):
                self.goal_position = Position(
                    teleports[0].y, teleports[0].x)

        # Masuk lewat teleport Kedua
        distance_x = abs(teleports[1].x - pos_x) + \
            abs(teleports[0].x - goal.position.x)
        distance_y = abs(teleports[1].y - pos_y) + \
            abs(teleports[0].y - goal.position.y)
        distance = distance_x + distance_y
        if (min_distance > distance):
            self.goal_position = Position(
                teleports[1].y, teleports[1].x)
            min_distance = distance
        elif (goal.type == "DiamondGameObject"):
            if (min_distance == distance and props.points == 2):
                self.goal_position = Position(
                    teleports[1].y, teleports[1].x)

        if (self.goal_position.x == pos_x and self.goal_position.y == pos_y):
            pos = self.possible_directions[random.randint(
                0, len(self.possible_directions) - 1)]
            self.goal_position.x += pos[0]
            self.goal_position.y += pos[1]

    def next_move(self, board_bot: GameObject, board: Board):
        self.current_position = board_bot.position
        self.goal_position: Optional[Position] = None
        self.possible_directions = list(filter(lambda t: board.is_valid_move(
            self.current_position, t[0], t[1]), self.possible_directions))
        print(self.possible_directions)
        # attributes = vars(board_bot)
        # for attribute, value in attributes.items():
        #     print(attribute, "=", value)

        self.teleport_gate = list()
        board_attributes = vars(board)
        props = board_bot.properties
        obj: GameObject
        for obj in board_attributes['game_objects']:
            var = vars(obj)
            print(var['type'])
            print(obj.position.x, obj.position.y)
            if (var['type'] == "TeleportGameObject"):
                self.teleport_gate.append(obj.position)

        '''
            Secara naif ambil diamond terdekat, baik lewat teleport ataupun engga
            jika ada yang jaraknya sama, ambil yang pointnya lebih besar. Kalo udah ngambil 5 diamond
            bakal pulang dulu.
        '''

        diamonds = board.diamonds
        for diamond in diamonds:
            # Ga bisa ngambil kalo 4 + 2
            if (diamond.properties.points == 2 and props.diamonds == 4):
                continue

            self.set_goal(diamond, False)

        if props.diamonds == 5:
            # Move to base
            base = board_bot.properties.base
            print(board_bot.position)

            self.goal_position = base

        delta_x, delta_y = get_direction(
            self.current_position.x,
            self.current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )

        print(self.goal_position.x, self.goal_position.y)

        return delta_x, delta_y


class Naive2Logic(BaseLogic):
    def __init__(self):
        self.teleport_gate: List[Position]
        self.possible_directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        return
        # self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        # self.current_direction = 0

    def set_goal(self, goal: GameObject, force: bool):
        pos_x = self.current_position.x
        pos_y = self.current_position.y
        teleports = self.teleport_gate
        props = goal.properties

        min_distance = float('inf')
        if (self.goal_position and not force):
            min_distance = abs(pos_x - self.goal_position.x) + \
                abs(pos_y - self.goal_position.y)

        # Masuk tanpa teleport
        distance = abs(goal.position.x - pos_x) + \
            abs(goal.position.y - pos_y)
        if (min_distance > distance):
            self.goal_position = Position(
                goal.position.y, goal.position.x)
            min_distance = distance
        elif (goal.type == "DiamondGameObject"):
            if (min_distance == distance and props.points == 2):
                self.goal_position = Position(
                    goal.position.y, goal.position.x)
                min_distance = distance

        # Masuk lewat teleport pertama
        distance_x = abs(teleports[0].x - pos_x) + \
            abs(teleports[1].x - goal.position.x)
        distance_y = abs(teleports[0].y - pos_y) + \
            abs(teleports[1].y - goal.position.y)
        distance = distance_x + distance_y
        if (min_distance > distance):
            self.goal_position = Position(
                teleports[0].y, teleports[0].x)
            min_distance = distance
        elif (goal.type == "DiamondGameObject"):
            if (min_distance == distance and props.points == 2):
                self.goal_position = Position(
                    teleports[0].y, teleports[0].x)

        # Masuk lewat teleport Kedua
        distance_x = abs(teleports[1].x - pos_x) + \
            abs(teleports[0].x - goal.position.x)
        distance_y = abs(teleports[1].y - pos_y) + \
            abs(teleports[0].y - goal.position.y)
        distance = distance_x + distance_y
        if (min_distance > distance):
            self.goal_position = Position(
                teleports[1].y, teleports[1].x)
            min_distance = distance
        elif (goal.type == "DiamondGameObject"):
            if (min_distance == distance and props.points == 2):
                self.goal_position = Position(
                    teleports[1].y, teleports[1].x)

    def next_move(self, board_bot: GameObject, board: Board):
        self.current_position = board_bot.position
        self.goal_position: Optional[Position] = None
        self.possible_directions = list(filter(lambda t: board.is_valid_move(
            self.current_position, t[0], t[1]), self.possible_directions))
        # attributes = vars(board_bot)
        # for attribute, value in attributes.items():
        #     print(attribute, "=", value)

        self.teleport_gate = list()
        board_attributes = vars(board)
        props = board_bot.properties
        obj: GameObject
        for obj in board_attributes['game_objects']:
            var = vars(obj)
            if (var['type'] == "TeleportGameObject"):
                self.teleport_gate.append(obj.position)

        '''
            Secara naif ambil diamond terdekat, baik lewat teleport ataupun engga
            jika ada yang jaraknya sama, ambil yang pointnya lebih besar. Kalo udah ngambil 5 diamond
            bakal pulang dulu.
        '''

        other_bots = list(
            filter(lambda bot: board_bot.id != bot.id, board.bots))

        diamonds = board.diamonds
        for diamond in diamonds:
            # Ga bisa ngambil kalo 4 + 2
            if (diamond.properties.points == 2 and props.diamonds == 4):
                continue

            self.set_goal(diamond, False)

        if props.diamonds == 5:
            # Move to base
            base = board_bot.properties.base

            self.goal_position = base

        delta_x, delta_y = get_direction(
            self.current_position.x,
            self.current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )

        # Kill other bot!
        for bot in other_bots:
            if (abs(self.current_position.x - bot.position.x) + abs(self.current_position.y - bot.position.y) <= 1):
                print("Can Kill!!!")
                self.goal_position = bot.position

        # distance_to_base = abs(self.current_position.x -
        #                        base.x) + abs(self.current_position.y - base.y)
        # print(props)
        # print(distance_to_base)
        # if (props.milliseconds_left/1000 - 2 <= distance_to_base):
        #     self.goal_position = base

        delta_x, delta_y = get_direction(
            self.current_position.x,
            self.current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )

        if (delta_x + delta_y == 0):
            delta_x, delta_y = random.choice(self.possible_directions)

        next_position: Position = Position(
            self.current_position.x + delta_x, self.current_position.y + delta_y)

        # is it safe to go there?
        for bot in other_bots:
            # check if it is safe, otherwise ###TODO: diem aja ????
            if (abs(next_position.x - bot.position.x) + abs(next_position.y - bot.position.y) == 1):
                self.goal_position = self.current_position
                break

        return delta_x, delta_y


class Naive3Logic(BaseLogic):
    def __init__(self):
        self.teleport_gate: List[Position]
        self.possible_directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        return
        # self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        # self.current_direction = 0

    def set_goal(self, goal: GameObject, force: bool):
        pos_x = self.current_position.x
        pos_y = self.current_position.y
        teleports = self.teleport_gate
        props = goal.properties

        min_distance = float('inf')
        if (self.goal_position and not force):
            min_distance = abs(pos_x - self.goal_position.x) + \
                abs(pos_y - self.goal_position.y)

        # Masuk tanpa teleport
        distance = abs(goal.position.x - pos_x) + \
            abs(goal.position.y - pos_y)
        if (min_distance > distance):
            self.goal_position = Position(
                goal.position.y, goal.position.x)
            min_distance = distance
        elif (goal.type == "DiamondGameObject"):
            if (min_distance == distance and props.points == 2):
                self.goal_position = Position(
                    goal.position.y, goal.position.x)
                min_distance = distance

        # Masuk lewat teleport pertama
        distance_x = abs(teleports[0].x - pos_x) + \
            abs(teleports[1].x - goal.position.x)
        distance_y = abs(teleports[0].y - pos_y) + \
            abs(teleports[1].y - goal.position.y)
        distance = distance_x + distance_y
        if (min_distance > distance):
            self.goal_position = Position(
                teleports[0].y, teleports[0].x)
            min_distance = distance
        elif (goal.type == "DiamondGameObject"):
            if (min_distance == distance and props.points == 2):
                self.goal_position = Position(
                    teleports[0].y, teleports[0].x)

        # Masuk lewat teleport Kedua
        distance_x = abs(teleports[1].x - pos_x) + \
            abs(teleports[0].x - goal.position.x)
        distance_y = abs(teleports[1].y - pos_y) + \
            abs(teleports[0].y - goal.position.y)
        distance = distance_x + distance_y
        if (min_distance > distance):
            self.goal_position = Position(
                teleports[1].y, teleports[1].x)
            min_distance = distance
        elif (goal.type == "DiamondGameObject"):
            if (min_distance == distance and props.points == 2):
                self.goal_position = Position(
                    teleports[1].y, teleports[1].x)

    def get_nearest(self, goal: GameObject) -> float:
        pos_x = self.current_position.x
        pos_y = self.current_position.y
        teleports = self.teleport_gate

        min_distance = float('inf')

        # Masuk tanpa teleport
        distance = abs(goal.position.x - pos_x) + \
            abs(goal.position.y - pos_y)
        if (min_distance > distance):
            min_distance = distance

        # Masuk lewat teleport pertama
        distance_x = abs(teleports[0].x - pos_x) + \
            abs(teleports[1].x - goal.position.x)
        distance_y = abs(teleports[0].y - pos_y) + \
            abs(teleports[1].y - goal.position.y)
        distance = distance_x + distance_y
        if (min_distance > distance):
            min_distance = distance

        # Masuk lewat teleport Kedua
        distance_x = abs(teleports[1].x - pos_x) + \
            abs(teleports[0].x - goal.position.x)
        distance_y = abs(teleports[1].y - pos_y) + \
            abs(teleports[0].y - goal.position.y)
        distance = distance_x + distance_y
        if (min_distance > distance):
            min_distance = distance

        return min_distance

    def next_move(self, board_bot: GameObject, board: Board):
        self.current_position = board_bot.position
        self.goal_position: Optional[Position] = None
        self.possible_directions = list(filter(lambda t: board.is_valid_move(
            self.current_position, t[0], t[1]), self.possible_directions))
        # attributes = vars(board_bot)
        # for attribute, value in attributes.items():
        #     print(attribute, "=", value)

        self.teleport_gate = list()
        board_attributes = vars(board)
        props = board_bot.properties
        obj: GameObject
        for obj in board_attributes['game_objects']:
            var = vars(obj)
            if (var['type'] == "TeleportGameObject"):
                self.teleport_gate.append(obj.position)

        other_bots = list(
            filter(lambda bot: board_bot.id != bot.id, board.bots))

        diamonds = board.diamonds
        for diamond in diamonds:
            # Ga bisa ngambil kalo 4 + 2
            if (diamond.properties.points == 2 and props.diamonds == props.inventory_size - 1):
                continue

            self.set_goal(diamond, False)

        base = board_bot.properties.base
        if props.diamonds == board_bot.properties.inventory_size:
            # Move to base
            self.set_goal(GameObject(9999, Position(
                base.y, base.x), "Base", None), True)

        delta_x, delta_y = get_direction(
            self.current_position.x,
            self.current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )

        # Kill other bot!
        for bot in other_bots:
            if (abs(self.current_position.x - bot.position.x) + abs(self.current_position.y - bot.position.y) <= 1):
                if (board_bot.properties.milliseconds_left > bot.properties.milliseconds_left):
                    continue
                self.goal_position = bot.position

        # Kalo waktunya tinggal dikit, pulang aja
        min_distance_to_base = self.get_nearest(GameObject(
            9999, Position(base.y, base.x), "Base", None))
        if (props.milliseconds_left - 2500 <= min_distance_to_base*1000):
            print("GO TO BASE NOW!!!")
            self.set_goal(GameObject(
                9999, Position(base.y, base.x), "Base", None), True)

        delta_x, delta_y = get_direction(
            self.current_position.x,
            self.current_position.y,
            self.goal_position.x,
            self.goal_position.y,
        )

        if (delta_x + delta_y == 0):
            delta_x, delta_y = random.choice(self.possible_directions)

        next_position: Position = Position(
            self.current_position.x + delta_x, self.current_position.y + delta_y)

        # is it safe to go there?
        for bot in other_bots:
            # check if it is safe, otherwise menjauh
            if (abs(next_position.x - bot.position.x) + abs(next_position.y - bot.position.y) <= 1):
                go_away = list(
                    filter(lambda t: (abs(self.current_position.x + t[0] - bot.position.x) + abs(self.current_position.y - bot.position.y) >= 2), self.possible_directions))
                delta_x, delta_y = random.choice(go_away)
                print("GO AWAY!!!")
                break

        return delta_x, delta_y

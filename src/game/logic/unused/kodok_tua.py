import random
from typing import Optional, List, Tuple

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from math import sqrt

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def get_direction(current_x, current_y, dest_x, dest_y):
    delta_x = clamp(dest_x - current_x, -1, 1)
    delta_y = clamp(dest_y - current_y, -1, 1)
    if delta_x != 0:
        delta_y = 0
    return (delta_x, delta_y)

def get_direction(curr: Position, dest: Position) -> Tuple[int, int]:
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    mn = float('inf')

    using = 0
    for i in range(len(directions)):
        new_x = curr.x + directions[i][0]
        new_y = curr.y + directions[i][1]

        euclidean = sqrt((new_x - dest.x)**2 + (new_y - dest.y)**2)
        if (mn > euclidean):
            using = i
            mn = euclidean

    return directions[using]


def distance(obj1: Position, obj2: Position, teleports: List[Position]):
    pos_x = obj1.x
    pos_y = obj1.y

    min_distance = float('inf')

    # Masuk tanpa teleport
    distance = abs(obj2.x - pos_x) + \
        abs(obj2.y - pos_y)
    if (min_distance > distance):
        min_distance = distance

    # Masuk lewat teleport pertama
    distance_x = abs(teleports[0].x - pos_x) + \
        abs(teleports[1].x - obj2.x)
    distance_y = abs(teleports[0].y - pos_y) + \
        abs(teleports[1].y - obj2.y)
    distance = distance_x + distance_y
    if (min_distance > distance):
        min_distance = distance

    # Masuk lewat teleport Kedua
    distance_x = abs(teleports[1].x - pos_x) + \
        abs(teleports[0].x - obj2.x)
    distance_y = abs(teleports[1].y - pos_y) + \
        abs(teleports[0].y - obj2.y)
    distance = distance_x + distance_y
    if (min_distance > distance):
        min_distance = distance

    return min_distance


def get_teleports(board: Board):
    teleport_gate = list()
    obj: GameObject
    for obj in board.game_objects:
        if (obj.type == "TeleportGameObject"):
            teleport_gate.append(obj.position)

    return teleport_gate


class KodokTua(BaseLogic):
    bot: GameObject
    board: Board

    '''
    We will be using 3 parameters to evaluate a our goal's cell.
    1. Diamond in backpack
    2. Distance to goal from current position
    3. Distance base from goal
    '''

    def __init__(self) -> None:
        self.goal: Position | None = None
        pass

    def set_goal(self, goal: GameObject, force: bool):
        pos_x = self.bot.position.x
        pos_y = self.bot.position.y
        teleports = self.teleports
        props = goal.properties

        min_distance = float('inf')
        if (self.goal and not force):
            min_distance = abs(pos_x - self.goal.x) + \
                abs(pos_y - self.goal.y)

        # Masuk tanpa teleport
        distance = abs(goal.position.x - pos_x) + \
            abs(goal.position.y - pos_y)
        if (min_distance > distance):
            self.goal = Position(
                goal.position.y, goal.position.x)
            min_distance = distance
        elif (goal.type == "DiamondGameObject"):
            if (min_distance == distance and props.points == 2):
                self.goal = Position(
                    goal.position.y, goal.position.x)
                min_distance = distance

        # Masuk lewat teleport pertama
        distance_x = abs(teleports[0].x - pos_x) + \
            abs(teleports[1].x - goal.position.x)
        distance_y = abs(teleports[0].y - pos_y) + \
            abs(teleports[1].y - goal.position.y)
        distance = distance_x + distance_y
        if (min_distance > distance):
            self.goal = Position(
                teleports[0].y, teleports[0].x)
            min_distance = distance
        elif (goal.type == "DiamondGameObject"):
            if (min_distance == distance and props.points == 2):
                self.goal = Position(
                    teleports[0].y, teleports[0].x)

        # Masuk lewat teleport Kedua
        distance_x = abs(teleports[1].x - pos_x) + \
            abs(teleports[0].x - goal.position.x)
        distance_y = abs(teleports[1].y - pos_y) + \
            abs(teleports[0].y - goal.position.y)
        distance = distance_x + distance_y
        if (min_distance > distance):
            self.goal = Position(
                teleports[1].y, teleports[1].x)
            min_distance = distance
        elif (goal.type == "DiamondGameObject"):
            if (min_distance == distance and props.points == 2):
                self.goal = Position(
                    teleports[1].y, teleports[1].x)

    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int]:
        self.bot = board_bot
        self.board = board
        self.teleports = get_teleports(self.board)
        self.goal = None
        self.allowed = list(filter(lambda t: board.is_valid_move(
            self.bot.position, t[0], t[1]), [(0, 1), (1, 0), (0, -1), (-1, 0)]))

        props = self.bot.properties
        other_bot: List[GameObject] = list(filter(lambda bot: bot.id !=
                                                  self.bot.id, board.bots))
        diamonds = board.diamonds

        best_evaluation = float('-inf')
        max_depth = 0
        DEBUGG = []
        DEPTH2 = float('-inf')
        # Trying depth = 2
        points = 0
        total_distance = 0
        for d1 in diamonds:
            current = [d1]
            dist = distance(self.bot.position, d1.position, self.teleports)

            # Don't check if our backpack is not capable
            if (d1.properties.points + self.bot.properties.diamonds > props.inventory_size):
                continue

            # If it is close to other bot, decrease points
            can = True
            for other in other_bot:
                if (distance(other.position, d1.position, self.teleports) < dist):
                    can = False

            if (not can):
                points -= 0.5

            points += d1.properties.points
            total_distance += dist
            max_depth = 1

            for d2 in diamonds:
                # If it is the same diamond then we don't care
                if (d1.id == d2.id):
                    continue

                diamonds_distance = distance(
                    d1.position, d2.position, self.teleports)

                # Don't check if our backpack is not capable
                if (d1.properties.points + d2.properties.points + props.diamonds > self.bot.properties.inventory_size):
                    continue

                # If it is close to other bot, decrease points
                can = True
                for other in other_bot:
                    if (distance(other.position, d2.position, self.teleports) < dist + diamonds_distance):
                        can = False

                if (not can):
                    points -= 0.5

                current.append(d2)

                points += d2.properties.points
                total_distance += diamonds_distance

                if (points/float(total_distance) > best_evaluation):
                    best_evaluation = points/float(total_distance)
                    self.set_goal(d1, False)
                    DEBUGG = current.copy()

                if (DEPTH2 < points/float(total_distance)):
                    DEPTH2 = points/float(total_distance)

                points -= d2.properties.points
                total_distance -= diamonds_distance
                max_depth = 2

                current.pop()

            if (max_depth == 1 and points/float(total_distance) > best_evaluation):
                best_evaluation = points/float(total_distance)
                self.set_goal(d1, False)
                DEBUGG = current.copy()

            points -= d1.properties.points
            total_distance -= dist

        if (self.goal == None or (best_evaluation <= 0.1 and len(other_bot) > 0)):
            self.set_goal(GameObject(9999, Position(
                props.base.y, props.base.x), "Base", None), True)

        if (self.bot.position.x == self.goal.x and self.bot.position.y == self.goal.y):
            return random.choice(self.allowed)

        print(self.bot.position)
        print(self.goal)
        print(best_evaluation)
        print(get_direction(self.bot.position, self.goal))
        print("\n\nroute:")
        for obj in DEBUGG:
            print(obj.position)

        print("depth2 best:", DEPTH2)
        print("max_depth: ", max_depth)

        return get_direction(self.bot.position, self.goal)

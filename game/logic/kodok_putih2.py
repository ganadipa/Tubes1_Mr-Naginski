import random
from typing import Optional, List, Tuple

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from math import sqrt
from ..util import get_direction


def get_direction(curr: Position, dest: Position, teleports: List[Position], allowed_directions) -> Tuple[int, int]:

    directions = allowed_directions
    mn = float('inf')
    dest_tele = False

    # Destination is teleport
    for t in teleports:
        if (dest.x == t.x and dest.y == t.y):
            dest_tele = True

    if (dest_tele == False):
        print("Dont go to teleport!!!")
        _new = list()
        for i in range(len(directions)):
            get = True
            for t in teleports:
                if ((curr.x + directions[i][0]) == t.x and (curr.y + directions[i][1]) == t.y):
                    get = False
                    break

            if (get):
                _new.append(directions[i])

        directions = _new
    else:
        print("Go to teleport!!!")

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


def get_teleports(board: Board) -> list[Position]:
    teleport_gate = list()
    obj: GameObject
    for obj in board.game_objects:
        if (obj.type == "TeleportGameObject"):
            teleport_gate.append(obj.position)

    return teleport_gate


def get_reset(board: Board) -> List[GameObject]:
    reset = list()
    obj: GameObject
    for obj in board.game_objects:
        if (obj.type == "DiamondButtonGameObject"):
            reset.append(obj)

    return reset


class KodokPutih(BaseLogic):
    bot: GameObject
    board: Board
    route: List[Position]
    goal_evaluation: float

    '''
    We will be using 3 parameters to evaluate a our goal's cell.
    1. Diamond in backpack
    2. Distance to goal from current position
    3. Distance base from goal
    
    Jadi instead of finding nearest diamond, kita cari diamond terbanyak dalam jangkauan 15 dari jarak kita sekarang, apabila diamond tersebut lebih dekat ke lawan, maka poin diamond tersebut effectively 0.7 dari worthnya.
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

    def search_optimal(self, max_diamond: int, position: Position, total_points, total_distance) -> None:
        if (max_diamond == 0 or (0 < total_distance < 15) or len(self.route) == len(self.diamonds)):

            last_goal_to_base = distance(
                self.route[len(self.route) - 1], self.bot.properties.base, self.teleports)

            evaluation = (
                total_points/(total_distance + ((0.3)*self.bot.properties.diamonds)*last_goal_to_base))
            if (self.goal_evaluation < evaluation):
                self.best_route = self.route.copy()
                self.goal_evaluation = evaluation
                obj = GameObject(99999, self.route[0], "diamond", None)

                self.set_goal(obj, False)
            return

        diamonds = self.diamonds

        for d in diamonds:
            search = True

            # Don't go more deep using the same diamond
            for pos in self.route:
                if (d.position.x == pos.x and d.position.y == pos.y):
                    search = False

            if (not search):
                continue

            # Don't check if our backpack is not capable
            if (d.properties.points > max_diamond):
                continue

            self.route.append(d.position)
            dist = distance(position, d.position, self.teleports)

            # If it is close to other bot, decrease points
            count = 0
            for other in self.other_bot:
                if (distance(other.position, d.position, self.teleports) < dist):
                    count += 1

            # Go more deep
            if (total_distance + dist <= 15):
                self.search_optimal(max_diamond - d.properties.points,
                                    d.position, total_points + d.properties.points*(1 - (count*count)*0.06), total_distance + dist)

            self.route.pop()

    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int]:
        self.bot = board_bot
        self.board = board
        self.teleports = get_teleports(self.board)
        self.reset = get_reset(self.board)
        self.goal = None
        self.allowed = list(filter(lambda t: board.is_valid_move(
            self.bot.position, t[0], t[1]), [(0, 1), (1, 0), (0, -1), (-1, 0)]))
        self.route: List[Position] = list()
        self.goal_evaluation = float('-inf')
        self.best_route: List[Position] = list()

        # Early return
        if (self.bot.properties.diamonds == self.bot.properties.inventory_size):
            return get_direction(self.bot.position, self.bot.properties.base, self.teleports, self.allowed)

        props = self.bot.properties

        # Time is up! lets go home
        if (self.bot.properties.milliseconds_left/1000 - 2.5 < distance(self.bot.position, props.base, self.teleports)):
            print("TIME TO GO TO BASE!!!")
            self.set_goal(GameObject(9999, Position(
                props.base.y, props.base.x), "Base", None), True)
            return get_direction(self.bot.position,
                                 self.bot.properties.base, self.teleports, self.allowed)

        self.other_bot: List[GameObject] = list(filter(lambda bot: bot.id !=
                                                       self.bot.id, board.bots))

        # Kill other bot!
        for other in self.other_bot:
            if (abs(self.bot.position.x - other.position.x) + abs(self.bot.position.y - other.position.y) <= 1):
                if (props.milliseconds_left > other.properties.milliseconds_left):
                    continue
                return get_direction(self.bot.position, other.position, self.teleports, self.allowed)

        self.diamonds = board.diamonds

        self.search_optimal(props.inventory_size -
                            props.diamonds, self.bot.position, 0, 0)

        # Go to reset button conditionally.
        if (self.goal_evaluation > 0):
            for rstBtn in self.reset:
                d = distance(self.bot.position,
                             rstBtn.position, self.teleports)
                if (0.25/d > self.goal_evaluation):
                    self.goal_evaluation = 0.25/d
                    self.set_goal(rstBtn, True)

        print("bot position:", self.bot.position)
        print(self.goal_evaluation)
        print("goal: ", self.goal)
        print("with route: ")
        for pos in self.best_route:
            print(pos)
        print(self.teleports)
        print("=====")

        # if goal is too bad just go home
        if (self.goal == None or (self.goal_evaluation <= 0.06 and len(self.other_bot) > 0)):
            self.set_goal(GameObject(9999, Position(
                props.base.y, props.base.x), "Base", None), True)

        if (self.bot.position.x == self.goal.x and self.bot.position.y == self.goal.y):
            return random.choice(self.allowed)

        # TODO: (OPTIONAL) Self defence and enemy awareness
        delta_x, delta_y = get_direction(
            self.bot.position, self.goal, self.teleports, self.allowed)
        next_position = Position(
            self.bot.position.x + delta_x, self.bot.position.y + delta_y)

        print("Bot position is:", self.bot.position)
        print("It's goal is:", self.goal)
        print("With goal evaluation:", self.goal_evaluation)
        print("\n\nWith route:")
        for pos in self.best_route:
            print(pos)

        print("max_depth: ", len(self.best_route))
        print("with route: ")

        return get_direction(self.bot.position, self.goal, self.teleports, self.allowed)

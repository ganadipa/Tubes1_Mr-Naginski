import random
from typing import Optional, List, Tuple

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def get_direction(current_x, current_y, dest_x, dest_y):
    delta_x = clamp(dest_x - current_x, -1, 1)
    delta_y = clamp(dest_y - current_y, -1, 1)
    if delta_x != 0:
        delta_y = 0
    return (delta_x, delta_y)

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


class WeightedArea(BaseLogic):
    def __init__(self):
        self.teleport_gate: List[Position]
        return

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
        self.possible_directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.possible_directions = list(filter(lambda t: board.is_valid_move(
            self.current_position, t[0], t[1]), self.possible_directions))
        print("initially, :", self.possible_directions)

        self.teleport_gate = list()
        self.board = board

        board_attributes = vars(board)
        props = board_bot.properties
        obj: GameObject
        for obj in board_attributes['game_objects']:
            var = vars(obj)
            if (var['type'] == "TeleportGameObject"):
                self.teleport_gate.append(obj.position)
        base = board_bot.properties.base

        other_bots = list(
            filter(lambda bot: board_bot.id != bot.id, board.bots))

        diamonds = board.diamonds

        highest_area = float('-inf')
        min_distance = float('inf')
        for diamond in diamonds:

            # Jangan ambil diamond yang lebih deket ke lawan
            cannot = False
            our_distance = distance(
                diamond.position, self.current_position, self.teleport_gate)
            for bot in other_bots:
                other_distance = distance(
                    diamond.position, bot.position, self.teleport_gate)
                if (our_distance < other_distance):
                    cannot = True
                    break

            if (cannot):
                continue

            # Check surrounding
            count = float(diamond.properties.points)
            for surrounding in diamonds:
                if (diamond.id == surrounding.id):
                    continue

                # Gausah ngitungin yang ada di deket lawan
                cannot = False
                for bot in other_bots:
                    other_distance = distance(
                        diamond.position, bot.position, self.teleport_gate)
                    if (our_distance < other_distance):
                        cannot = True
                        break

                if (cannot):
                    continue

                dist = distance(surrounding.position,
                                diamond.position, self.teleport_gate)

                points = surrounding.properties.points
                if (dist <= 1):
                    count += 0.5*points
                elif (dist <= 2):
                    count += 0.3*points
                elif (dist <= 3):
                    count += 0.1*points
                elif (dist <= 4):
                    count += 0.05*points

            if (diamond.properties.points + props.diamonds > props.inventory_size):
                self.set_goal(GameObject(9999, Position(
                    base.y, base.x), "Base", None), True)
                break

            print(count)
            print(diamond.position)

            count -= our_distance
            if (count > highest_area):
                highest_area = count
                self.set_goal(diamond, False)
            elif (count == highest_area):
                if (distance(diamond.position, self.current_position, self.teleport_gate) < min_distance):
                    self.set_goal(diamond, False)

        if (self.goal_position == None):
            self.set_goal(GameObject(9999, Position(
                base.y, base.x), "Base", None), True)

        # if props.diamonds == board_bot.properties.inventory_size:
        #     # Move to base
        #     self.set_goal(GameObject(9999, Position(
        #         base.y, base.x), "Base", None), True)

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

        # Evaluate every possible direction
        current_distance = distance(
            self.current_position, self.goal_position, self.teleport_gate)

        print("possible directions: ", self.possible_directions)
        better_directions = list(filter(
            lambda d: d[0]*(self.goal_position.x - self.current_position.x) >= 0, self.possible_directions))
        print(self.current_position)
        print(self.goal_position)
        print("better direction first filter: ", better_directions)
        better_directions = list(filter(
            lambda d: d[1]*(self.goal_position.y - self.current_position.y) >= 0, better_directions))

        print("better direction second filter: ", better_directions)
        print("NOW GO TO LOOP!!!!")
        print(better_directions)
        for direction in better_directions:
            print("directino is")
            print(direction)
            # Only if not using teleport
            next_position: Position = Position(
                self.current_position.y + direction[1], self.current_position.x + direction[0])

            if not (current_distance == (abs(next_position.x - self.goal_position.x) + abs(next_position.y - self.goal_position.y))):
                continue

            for tele in self.teleport_gate:
                if (tele[0] == next_position.x and tele[0] == self.goal_position.x and (next_position.y <= tele[1] < self.goal_position.y)):
                    print(tele)
                    print(next_position)
                    print(self.goal_position)
                    better_directions = list(filter(
                        lambda d: direction != d, better_directions))
                    break
                elif (tele[1] == next_position.y and tele[1] == self.goal_position.y and next_position.x <= tele[0] < self.goal_position.x):
                    print(tele)
                    print(next_position)
                    print(self.goal_position)
                    better_directions = list(filter(
                        lambda d: direction != d, better_directions))
                    break

        delta_x, delta_y = 0, 0
        min_distance = float('inf')
        for (direction) in better_directions:
            print(direction)
            next_position: Position = Position(
                self.current_position.y + direction[1], self.current_position.x + direction[0])
            current = distance(self.goal_position,
                               next_position, self.teleport_gate)
            print(current)
            if (min_distance > current):
                min_distance = current
                delta_x, delta_y = direction

        if (delta_x + delta_y == 0):
            delta_x, delta_y = random.choice(self.possible_directions)

        next_position: Position = Position(
            self.current_position.y + delta_y, self.current_position.x + delta_x)

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

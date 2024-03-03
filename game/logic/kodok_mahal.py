import random
from typing import Optional, Tuple

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position

class KodokMahal(BaseLogic):
    """
    Like KodokGanteng, but also like KodokSehat.
    It will try to make the bot to go to base if have diamond before the time is up.
    If there's a base nearby (radius <= 1) but the base is not in the path to the diamond we're trying to reach, and the diamond in inventory is more than 0, always go to base. Because getting stepped on is brutal
    """
    def __init__(self):
        pass

    def is_diamond_almost_full(self, bot: GameObject) -> bool:
        return bot.properties.diamonds >= bot.properties.inventory_size-1
    def is_diamond_full(self, bot: GameObject) -> bool:
        return bot.properties.diamonds == bot.properties.inventory_size
    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        # try:
            # case diamond almost full
            if self.is_diamond_almost_full(board_bot):
                return self.move_towards_base(board_bot, board)
            
            # case time is almost up and have diamond
            if board_bot.properties.diamonds > 0 and board_bot.properties.milliseconds_left < self.miliseconds_to_base(board_bot, board):
                return self.move_towards_base(board_bot, board)
            
            # case base in radius 1 and have diamond
            if board_bot.properties.diamonds > 0 and self.is_base_near(board_bot, board):
                return self.move_towards(board_bot, board_bot.properties.base)
            
            # Move to nearest diamond
            target_pos = self.find_best_next_move(board_bot, board)
            return self.move_towards_through_base(board_bot, target_pos)
        # except Exception as e:
        #     print(e)
        #     return (0, 0)

    # return both teleporter if exist
    def get_both_teleporter(self, board: Board) -> Tuple[GameObject, GameObject]:
        teleporters = [d for d in board.game_objects if d.type == "TeleportGameObject"]
        if len(teleporters) != 2:
            return None, None
        return teleporters[0], teleporters[1]

    # Move towards base, also handle teleport
    # also handle if there's diamond in the way, go to the diamond first
    def move_towards_base(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        teleporter1, teleporter2 = self.get_both_teleporter(board)
        current_position = board_bot.position
        base_position = board_bot.properties.base
        base_distance = self.distance(current_position, base_position)
        distance_to_base_by_teleport = base_distance+1
        if teleporter1 and teleporter2:
            distance_to_teleport1 = self.distance(current_position, teleporter1.position)
            distance_to_teleport2 = self.distance(current_position, teleporter2.position)
            distance_from_teleport1_to_base = self.distance(teleporter1.position, base_position)
            distance_from_teleport2_to_base = self.distance(teleporter2.position, base_position)

            distance_to_base_by_teleport = min(
                distance_to_teleport1 + distance_from_teleport2_to_base,
                distance_to_teleport2 + distance_from_teleport1_to_base
            )
        if distance_to_base_by_teleport < base_distance:
            if distance_to_teleport1 < distance_to_teleport2:
                return self.move_towards(board_bot, teleporter1.position)
            else:
                return self.move_towards(board_bot, teleporter2.position)
        else:

            return self.move_towards(board_bot, base_position)
    # The solution itself
    def find_best_next_move(self, my_bot: GameObject, board: Board) -> Position:
        enemy_bot_list = board.bots
        enemy_bot_list.remove(my_bot)
        diamond_list = board.diamonds

        # put all nearest diamonds to each bot to a set
        nearest_diamond_list = list()
        for bot in enemy_bot_list:
            nearest_diamond_list.append(self.find_nearest_diamond_regard_to_teleport(bot, diamond_list, board))

        # pop all those diamonds from the list
        for diamond in nearest_diamond_list:
            if diamond in diamond_list:
                diamond_list.remove(diamond)

        # move to the nearest diamond from the remaining list
        best_diamond = self.find_nearest_diamond_regard_to_teleport(my_bot, diamond_list, board)
        if best_diamond:
            return best_diamond.position

        # if no suitable diamond left, return to base
        return my_bot.properties.base
    
    # Will return the nearest diamond without considering teleport
    def find_nearest_diamond(self, bot: GameObject, diamonds: list[GameObject], board: Board) -> GameObject:
        min_distance = board.width + board.height
        target_diamond: GameObject = None

        for diamond in diamonds:
            distance = self.distance(diamond.position, bot.position)
            if distance < min_distance:
                min_distance = distance
                target_diamond = diamond
            # case distance is the same but point is bigger
            elif distance==min_distance and target_diamond and diamond.properties.points > target_diamond.properties.points:
                target_diamond = diamond

        return target_diamond
    

    # Will return the teleporter if the diamond is closer after teleporting
    def find_nearest_diamond_regard_to_teleport(self, bot: GameObject, diamonds: list[GameObject], board: Board) -> GameObject:
        min_distance = board.width + board.height
        target_diamond: GameObject = None
        current_diamond_points = 0
        
        teleporter1, teleporter2 = self.get_both_teleporter(board)
        if teleporter1 and teleporter2:
            for diamond in diamonds:
                distance_to_diamond = self.distance(diamond.position, bot.position)
                distance_to_teleport1 = self.distance(bot.position, teleporter1.position)
                distance_to_teleport2 = self.distance(bot.position, teleporter2.position)
                distance_from_teleport1_to_diamond = self.distance(teleporter1.position, diamond.position)
                distance_from_teleport2_to_diamond = self.distance(teleporter2.position, diamond.position)
                
                distance_by_teleporting = min(
                    distance_to_teleport1 + distance_from_teleport2_to_diamond,
                    distance_to_teleport2 + distance_from_teleport1_to_diamond
                )

                # case diamond is nearer
                if distance_to_diamond < distance_by_teleporting:
                    if distance_to_diamond < min_distance:
                        min_distance = distance_to_diamond
                        target_diamond = diamond
                        current_diamond_points = diamond.properties.points
                    # case distance is the same but point is bigger
                    elif distance_to_diamond==min_distance and diamond.properties.points > current_diamond_points:
                        target_diamond = diamond
                        current_diamond_points = diamond.properties.points
                # case teleporting is nearer
                else:
                    if distance_by_teleporting < min_distance:
                        min_distance = distance_by_teleporting
                        current_diamond_points = diamond.properties.points
                        if distance_to_teleport1 < distance_to_teleport2:
                            target_diamond = teleporter1
                        else:
                            target_diamond = teleporter2
                    # case distance_by_teleporting is the same but point is bigger
                    elif distance_by_teleporting==min_distance and diamond.properties.points > current_diamond_points:
                        current_diamond_points = diamond.properties.points
                        if distance_to_teleport1 < distance_to_teleport2:
                            target_diamond = teleporter1
                        else:
                            target_diamond = teleporter2
        # case no teleporter
        else:
            for diamond in diamonds:
                distance_to_diamond = self.distance(diamond.position, bot.position)
                if distance_to_diamond < min_distance:
                    min_distance = distance_to_diamond
                    target_diamond = diamond
                    current_diamond_points = diamond.properties.points
                # case distance is the same but point is bigger
                elif distance_to_diamond==min_distance and diamond.properties.points > current_diamond_points:
                    target_diamond = diamond
                    current_diamond_points = diamond.properties.points

        return target_diamond
    

    def distance(self, a: Position, b: Position) -> int:
        x = abs(a.x - b.x)
        y = abs(a.y - b.y)
        return x + y
    
    # Move towards a destination. If its possible to go to base, go to base
    def move_towards(self, board_bot: GameObject, dest: Position) -> Tuple[int, int]:
        delta_x = dest.x - board_bot.position.x
        delta_y = dest.y - board_bot.position.y
        
        direction = (0, 0)

        if abs(delta_x) > abs(delta_y):
            direction = (1 if delta_x > 0 else -1, 0)
        else:
            direction = (0, 1 if delta_y > 0 else -1)            
        
        return direction
    
    def move_towards_through_base(self, board_bot: GameObject, dest: Position) -> Tuple[int, int]:
        base_position = board_bot.properties.base
        delta_x = 0
        delta_y = 0

        # check all 4 quadrant
        # quadrant 1
        if board_bot.position.x < base_position.x < dest.x and board_bot.position.y < base_position.y < dest.y:
            delta_x = base_position.x - board_bot.position.x
            delta_y = base_position.y - board_bot.position.y
        # quadrant 2
        elif dest.x < base_position.x < board_bot.position.x and board_bot.position.y < base_position.y < dest.y:
            delta_x = base_position.x - board_bot.position.x
            delta_y = base_position.y - board_bot.position.y
        # quadrant 3
        elif dest.x < base_position.x < board_bot.position.x and dest.y < base_position.y < board_bot.position.y:
            delta_x = base_position.x - board_bot.position.x
            delta_y = base_position.y - board_bot.position.y
        # quadrant 4
        elif board_bot.position.x < base_position.x < dest.x and dest.y < base_position.y < board_bot.position.y:
            delta_x = base_position.x - board_bot.position.x
            delta_y = base_position.y - board_bot.position.y
        else:
            delta_x = dest.x - board_bot.position.x
            delta_y = dest.y - board_bot.position.y
        
        direction = (0, 0)

        if abs(delta_x) > abs(delta_y):
            direction = (1 if delta_x > 0 else -1, 0)
        else:
            direction = (0, 1 if delta_y > 0 else -1)            
        
        return direction
    
    def move_towards_through_nearest_diamond(self, board_bot: GameObject, board: Board, dest: Position) -> Tuple[int, int]:
        nearest_diamond = self.find_nearest_diamond(board_bot, board.diamonds, board)
        diamond_position: Position
        if nearest_diamond:
            diamond_position = nearest_diamond.position
        else:
            return self.move_towards(board_bot, dest)
        delta_x = 0
        delta_y = 0

        # check all 4 quadrant
        # quadrant 1
        if board_bot.position.x < diamond_position.x < dest.x and board_bot.position.y < diamond_position.y < dest.y:
            delta_x = diamond_position.x - board_bot.position.x
            delta_y = diamond_position.y - board_bot.position.y
        # quadrant 2
        elif dest.x < diamond_position.x < board_bot.position.x and board_bot.position.y < diamond_position.y < dest.y:
            delta_x = diamond_position.x - board_bot.position.x
            delta_y = diamond_position.y - board_bot.position.y
        # quadrant 3
        elif dest.x < diamond_position.x < board_bot.position.x and dest.y < diamond_position.y < board_bot.position.y:
            delta_x = diamond_position.x - board_bot.position.x
            delta_y = diamond_position.y - board_bot.position.y
        # quadrant 4
        elif board_bot.position.x < diamond_position.x < dest.x and dest.y < diamond_position.y < board_bot.position.y:
            delta_x = diamond_position.x - board_bot.position.x
            delta_y = diamond_position.y - board_bot.position.y
        else:
            return self.move_towards(board_bot, dest)
        
        direction = (0, 0)

        if abs(delta_x) > abs(delta_y):
            direction = (1 if delta_x > 0 else -1, 0)
        else:
            direction = (0, 1 if delta_y > 0 else -1)            
        
        return direction

    
    # find the time needed to go to base, also handle teleport
    # time_needed = (distance*time_each_step + bias) * 1000
    def miliseconds_to_base(self, board_bot: GameObject, board: Board) -> int:
        bias = 3
        time_each_step = 1
        base_position = board_bot.properties.base
        distance = self.distance(board_bot.position, base_position)
        teleporter1, teleporter2 = self.get_both_teleporter(board)
        if teleporter1 and teleporter2:
            distance_to_teleport1 = self.distance(board_bot.position, teleporter1.position)
            distance_to_teleport2 = self.distance(board_bot.position, teleporter2.position)
            distance_from_teleport1_to_base = self.distance(teleporter1.position, base_position)
            distance_from_teleport2_to_base = self.distance(teleporter2.position, base_position)

            distance_by_teleporting = min(
                distance_to_teleport1 + distance_from_teleport2_to_base,
                distance_to_teleport2 + distance_from_teleport1_to_base
            )
            if distance_by_teleporting < distance:
                distance = distance_by_teleporting

        return (distance*time_each_step + bias) * 1000
    
    def is_base_near(self, bot: GameObject, board: Board) -> bool:
        base_position = bot.properties.base
        distance = self.distance(bot.position, base_position)
        return distance == 1 or distance == 2
    
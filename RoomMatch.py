
from enum import Enum

from GameCoreSSC import gameCoreSSC
from Timer2 import LifecycleObject

class stateBase:
    '''base class of room states'''
    def on_enter(self,room_match):
        pass

    def send_msg_to_game(self,room_match,msg_dict):
        return room_match.game.interact(msg_dict)

    def on_exit(self,room_match):
        pass

class stateEmpty(stateBase):
    def on_enter(self,room_match):
        pass
    
    def on_exit(self,room_match):
        pass

class stateWaiting(stateBase):
    def on_enter(self,room_match):
        pass
    
    def on_exit(self,room_match):
        pass

class stateFull(stateBase):
    def on_enter(self,room_match):
        ''' when room is full, send player information to game
        '''
        player_id_list = list(room_match.player_state.keys())
        print(player_id_list)
        msg_dict_1 = {
            'event_type': 'to_game',
            'event_act': 'add_player',
            'event_obj': player_id_list[0]
        }
        msg_dict_2 = {
            'event_type': 'to_game',
            'event_act': 'add_player',
            'event_obj': player_id_list[1]
        }
        rsps_dict_1 = room_match.game.interact(msg_dict_1)
        if rsps_dict_1['event_act'] != 'confirm_player_added,wait_more':
            RuntimeError('player added not good')
        rsps_dict_2 = room_match.game.interact(msg_dict_2)
        if rsps_dict_2['event_act'] != 'confirm_player_added,enough':
            RuntimeError('player added not good')
    
    def on_exit(self,room_match):
        pass

class stateGaming(stateBase):
    def on_enter(self,room_match):
        pass
    
    def on_exit(self,room_match):
        pass

        

class roomState(Enum):
    EMPTY = 'EMPTY'
    WAITING = 'WAITING'
    FULL = 'FULL'
    GAMING = 'GAMING'


class roomMatch(LifecycleObject):

    def __init__(self, key, registry, room_code:str, player_num_max:int, timeout=30):
        super().__init__(key,registry,timeout)
        self.room_code = room_code
        self.player_num_max = player_num_max
        self.player_num = 0
        self.player_state = {}
        self.states = {
            roomState.EMPTY : stateEmpty(),
            roomState.WAITING: stateWaiting(),
            roomState.FULL : stateFull(),
            roomState.GAMING: stateGaming(),
        }
        self.state_name = roomState.EMPTY
        self.state = self.states[roomState.EMPTY]
        self._change_state(roomState.WAITING)
        #### init game ####
        self.game = gameCoreSSC(self.player_num_max)
        #### test #####
        # print(f'room {self.room_code} set')
    
    def _change_state(self,to_state):
        self.state.on_exit(self)
        self.state_name = to_state
        self.state = self.states[to_state]
        self.state.on_enter(self)

    def get_state(self):
        return self.state_name

    def get_room_code(self):
        return self.room_code
    
    def get_player_num(self):
        return self.player_num

    def add_player(self,player_id):
        ''' add a player
        return:
            True: success
            False: failed
        '''
        if self.get_state() == roomState.WAITING:
            self.player_state[player_id] = None
            self.player_num += 1
        else: # not in waiting state
            return False
        if self.player_num == self.player_num_max:
            self._change_state(roomState.FULL)
        return True
    
    def check_is_room_full(self):
        '''return:
            True -> full
            False -> not full
        '''
        if self.player_num == self.player_num_max:
            return True
        else:
            return False
    
    def send_msg_to_game(self,msg_dict):
        return self.state.send_msg_to_game(self,msg_dict)

# room = roomMatch('1',2)

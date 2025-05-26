from GameCoreSSC import gameCoreSSC
from RoomMatch import roomMatch, roomState
import threading
from GameMsg import gameMsg
from Timer2 import LifecycleObject, ObjectRegistry



class gameMatch():

    def __init__(self):
        self.lock = threading.Lock()
        self.rooms = ObjectRegistry() # key: room number, value: gameRoom instance
    
    def join_room(self,room_code,user_id):
        ''' a user (user_id) join a room (room_code)
        return:
            0 -> join failed
            1 -> join success, room is not full, waiting for more players
            2 -> join success, room is now full
        '''
        with self.lock:
            if (room_code not in self.rooms) or (self.rooms[room_code] == None): # room not exist or room is none
                # set the room and put user in the room
                self.rooms[room_code] = roomMatch(room_code,self.rooms,room_code,2)
            print(f'join_room, room_code {room_code}, user id {user_id}')
            flag_sccs = self.rooms[room_code].add_player(user_id)
            if flag_sccs == False:
                return 0
            # check if the room is full
            if self.rooms[room_code].check_is_room_full():
                return 2
            else:
                return 1
    
    def check_is_a_room_full(self,room_code):
        ''' check if the room is full
        return:
            None -> fail to check
            True -> full
            False -> not full
        '''
        with self.lock:
            if room_code in self.rooms:
                return self.rooms[room_code].check_is_room_full()
            else:
                return None

    def send_msg_to_game(self,room_code,msg_dict):
        '''return:
            None -> failed
            rspc_dict -> success
        '''
        with self.lock:
            if room_code in self.rooms:
                return self.rooms[room_code].send_msg_to_game(msg_dict)
            else:
                return None

game_match = gameMatch()
game_msg = gameMsg()
# if __name__ == '__main__':
#     game_match = gameMatch()
#     game_match.join_room('r1','player1')
#     game_match.join_room('r1','palyer2')
#     print(game_match.check_is_a_room_full('r1'))


            


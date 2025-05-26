import streamlit as st
import uuid
from GameMatch import gameMatch,game_match, gameMsg, game_msg
import time


st.set_page_config(page_title="石头剪刀布", layout="centered")

# game_match is imported from GameMatch

# 生成唯一用户 ID
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# 初始化界面状态
if "room_code" not in st.session_state:
    st.session_state.room_code = None
    # a string as room_code

if "room_state" not in st.session_state:
    st.session_state.room_state = None
    # None -> for initalize
    # 0 -> waiting for players
    # 1 -> room is full, game started

if "page" not in st.session_state:
    st.session_state.page = 'match'
    # page: 'match'/'game'/'result'/'waiting_result'/'admin'. when page is generated, default to 'match'

st.text(f'user_id: {st.session_state.user_id}')

# check page
if st.session_state.page == 'match':
    if st.session_state.room_state == None:
        st.title("石头剪刀布 - 匹配房间")
        room_code = st.text_input("房间名")
        if st.button("加入游戏") and room_code:
            if room_code == 'admin':
                st.session_state.page = 'admin'
                st.rerun()
            else:
                join_return = game_match.join_room(room_code, st.session_state.user_id)
                # join return:
                # 0 -> join failed
                # 1 -> join success, room is not full, waiting for more players
                # 2 -> join success, room is now full
                if join_return == 1:
                    st.session_state.room_code = room_code
                    st.session_state.room_state = 0
                    st.rerun()
                elif join_return == 2:
                    st.session_state.room_code = room_code
                    st.session_state.room_state = 1
                    st.session_state.page = 'game'
                    st.rerun()
                elif join_return == 0:
                    st.error("加入失败")
    elif st.session_state.room_state == 0: # waiting for more player
        flag_full_room = game_match.check_is_a_room_full(st.session_state.room_code)
        # print(game_match.rooms)
        # print(flag_full_room)
        if flag_full_room:
            st.session_state.room_state = 1
            st.session_state.page = 'game'
            st.rerun()
        else:
            st.title("石头剪刀布 - 匹配房间")
            st.text(f'正在等待其他玩家加入房间{st.session_state.room_code}')
            time.sleep(2)
            st.rerun()
elif st.session_state.page == 'game':
    st.title(f"匹配码: {st.session_state.room_code}")
    if "choice" not in st.session_state:
        st.subheader("请选择你出什么：")
        choice = st.radio("出拳", ["石头", "剪刀", "布"])
        if st.button("提交"):
            st.session_state.choice = choice
            # send a choise message to a room
            rspc_dict = game_match.send_msg_to_game(st.session_state.room_code,game_msg.submit_player_choise(st.session_state.user_id,choice))
            print(rspc_dict)
            if rspc_dict['event_act'] == 'confirm_winner':
                # game over, display winner
                st.session_state.result_dict = rspc_dict
                st.session_state.page = 'result'
                st.rerun()
            elif rspc_dict['event_act'] == 'confirm_player_choose,wait_more':
                # waiting for other player to submit choise
                st.session_state.page = 'waiting_result'
                st.rerun()
elif st.session_state.page == 'waiting_result':
    rspc_dict = game_match.send_msg_to_game(st.session_state.room_code,game_msg.enquiry_result())
    if rspc_dict['event_act'] == 'waiting_for_other_player':
        st.title(f"匹配码: {st.session_state.room_code}")
        st.text(f'你出了{st.session_state.choice}')
        st.text('等待对手提交')
        time.sleep(2)
        st.rerun()
    elif rspc_dict['event_act'] == 'confirm_winner':
        # game over, display winner
        st.session_state.result_dict = rspc_dict
        st.session_state.page = 'result'
        st.rerun()
elif st.session_state.page == 'result':
    if st.session_state.result_dict['event_obj'] == 'draw':
        st.title('平局')
    elif st.session_state.result_dict['event_obj'] == st.session_state.user_id:
        st.title('你赢了')
    else:
        st.title('你输了')
elif st.session_state.page == 'admin':
    st.title('admin')
    st.text(str(game_match.rooms.keys()))
    for room_code in game_match.rooms:
        st.text(f'room_code = {room_code}: ')
        st.text(f'room {room_code} id -> {id(game_match.rooms[room_code])}')
        st.text(f'player_stat id -> {id(game_match.rooms[room_code].player_state)}')
        st.text(str(game_match.rooms[room_code].player_state))
    if st.button('rerun'):
        st.rerun()



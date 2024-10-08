from aiogram.fsm.state import StatesGroup, State


class Tnmts(StatesGroup):
    start_menu = State()
    find_menu = State()
    tournament_info = State()
    vote_for_set = State()
    enter_game_account = State()

class MyGames(StatesGroup):
    my_games_menu = State()
    registered_tournament_info = State()
    choice_set = State()
    ongoing_tournament = State()
    enter_match_result = State()
    update_game_account = State()

class Stats(StatesGroup):
    stats_menu = State()
    manage_accounts = State()
    account_stats = State()


class Admin_panel(StatesGroup):
    ap_menu = State()
    manage_accounts = State()
    account_stats = State()


class Add_tnmt(StatesGroup):
    tnmt_date = State()
    tnmt_set = State()
    tnmt_name = State()



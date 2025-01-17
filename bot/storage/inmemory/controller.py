import typing

from bot.dto.room import Room
from bot.dto.user import User
from bot.dto.game import Game
from bot.dto.game_state import GameState
from bot.dto.question_set import QuestionSet
from bot.dto.question import Question

from bot.storage.exceptions import RoomNotFoundError

from bot.storage.storage_controller_base import StorageControllerBase

from bot.storage.inmemory.storage import Storage


class InmemoryStorageController(StorageControllerBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = Storage()

    def create_room(self, room_id: Room.ID_TYPE) -> None:
        self.storage.rooms[room_id] = Room(room_id)

    def remove_room(self, room_id: Room.ID_TYPE) -> None:
        self.storage.rooms.pop(room_id, None)

    def add_user_to_room(self, room_id: Room.ID_TYPE, user: User) -> None:
        self.storage.rooms[room_id].participants[user.id] = user

    def remove_user_from_room(self, room_id: Room.ID_TYPE, user: User) -> None:
        room = self.storage.rooms[room_id]
        if user.id in room.participants:
            room.participants.pop(user.id)

    def is_user_in_room(self, room_id: Room.ID_TYPE, user_id: int) -> bool:
        return user_id in self.storage.rooms[room_id].participants

    def get_users_in_room(self, room_id: Room.ID_TYPE) -> typing.Dict[int, User]:
        return self.storage.rooms[room_id].participants

    def start_game(self, room_id: Room.ID_TYPE, questions: typing.Iterable[typing.Tuple[str, str]]) -> None:
        self.storage.rooms[room_id].game = Game(QuestionSet(
            [Question(word, description) for word, description in questions]
        ))
        self.storage.rooms[room_id].game_state = GameState(0)

    def next_round(self, room_id: Room.ID_TYPE) -> None:
        old_question_idx = self.storage.rooms[room_id].game_state.question_idx
        if old_question_idx == len(self.storage.rooms[room_id].game.question_set.questions) - 1:
            raise IndexError
        self.storage.rooms[room_id].game_state = GameState(old_question_idx+1)

    def get_current_word(self, room_id: Room.ID_TYPE) -> str:
        room = self.storage.rooms[room_id]
        return room.game.question_set.questions[room.game_state.question_idx].word

    def get_current_description(self, room_id: Room.ID_TYPE) -> str:
        room = self.storage.rooms[room_id]
        return room.game.question_set.questions[room.game_state.question_idx].description

    def get_current_user_descriptions(self, room_id: Room.ID_TYPE) -> typing.Dict[int, str]:
        room = self.storage.rooms[room_id]
        return room.game_state.user_descriptions

    def add_user_question_message_id(self, room_id: Room.ID_TYPE, user_id: int, message_id: int) -> None:
        room = self.storage.rooms[room_id]
        room.game_state.user_question_message_id[user_id] = message_id

    def get_room_id_by_private_message_id(self, user_id: int, message_id: int) -> Room.ID_TYPE:
        user_rooms = list(filter(lambda room: user_id in room.participants, self.storage.rooms.values()))
        for room in user_rooms:
            if room.game_state.user_question_message_id[user_id] == message_id:
                return room.id
        raise RoomNotFoundError

    def add_user_description(self, room_id: Room.ID_TYPE, user_id: int, description: str) -> None:
        self.storage.rooms[room_id].game_state.user_descriptions[user_id] = description

    def set_poll_description_order(self, room_id: Room.ID_TYPE,
                                   description_order: typing.List[typing.Tuple[str, typing.Optional[int]]]) -> None:
        self.storage.rooms[room_id].game_state.poll_description_order = description_order

    def get_description_order(self, room_id: Room.ID_TYPE) -> typing.List[typing.Tuple[str, typing.Optional[int]]]:
        return self.storage.rooms[room_id].game_state.poll_description_order

    def add_poll(self, room_id: Room.ID_TYPE, poll_id: str, message_id: int) -> None:
        self.storage.rooms[room_id].game_state.poll_id = poll_id
        self.storage.rooms[room_id].game_state.poll_message_id = message_id

    def get_room_id_by_poll_id(self, poll_id: str) -> typing.Optional[Room.ID_TYPE]:
        for room in self.storage.rooms.values():
            if room.game_state.poll_id == poll_id:
                return room.id

    def get_poll_message_id(self, room_id) -> int:
        return self.storage.rooms[room_id].game_state.poll_message_id

    def add_user_vote(self, room_id: Room.ID_TYPE, user_id: int, vote: int) -> None:
        self.storage.rooms[room_id].game_state.user_votes[user_id] = vote

    def get_user_votes(self, room_id: Room.ID_TYPE) -> typing.Dict[int, int]:
        return self.storage.rooms[room_id].game_state.user_votes

    def add_scores(self, room_id: Room.ID_TYPE, scores: typing.Dict[User, int]) -> None:
        room = self.storage.rooms[room_id]
        for user, score in scores.items():
            room.game.scoreboard.scores[user] += score

    def get_scores(self, room_id: Room.ID_TYPE) -> typing.Dict[User, int]:
        room = self.storage.rooms[room_id]
        return room.game.scoreboard.scores

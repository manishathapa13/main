# app.py
import streamlit as st
import numpy as np

# Game logic from your code
class TicTacToe:
    def __init__(self):
        self.board = [' '] * 9
        self.current_winner = None

    def get_state(self):
        return tuple(self.board)

    def available_actions(self):
        return [i for i, x in enumerate(self.board) if x == ' ']

    def make_move(self, action, player):
        if self.board[action] == ' ':
            self.board[action] = player
            if self.check_winner(player):
                self.current_winner = player
            return True
        return False

    def check_winner(self, player):
        win_patterns = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        return any(all(self.board[i] == player for i in pattern) for pattern in win_patterns)

    def is_full(self):
        return ' ' not in self.board

# Initialize game
if 'game' not in st.session_state:
    st.session_state.game = TicTacToe()

game = st.session_state.game

st.title("Tic-Tac-Toe (Streamlit Edition)")

# Board display and interaction
cols = st.columns(3)
for i in range(9):
    if game.board[i] == ' ':
        if cols[i % 3].button(f" ", key=i):
            game.make_move(i, 'X')
            if not game.current_winner and not game.is_full():
                ai_move = np.random.choice(game.available_actions())
                game.make_move(ai_move, 'O')
    else:
        cols[i % 3].write(f"**{game.board[i]}**")

# Status
if game.current_winner:
    st.success(f"Player {game.current_winner} wins!")
elif game.is_full():
    st.warning("It's a draw!")

if st.button("Restart"):
    st.session_state.game = TicTacToe()
    st.experimental_rerun()

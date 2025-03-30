
import streamlit as st
import numpy as np
import random
import pickle
import os

# --------------------- Tic-Tac-Toe Game ---------------------
class TicTacToe:
    def __init__(self):
        self.board = [' '] * 9
        self.current_winner = None

    def reset(self):
        self.board = [' '] * 9
        self.current_winner = None
        return self.get_state()

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
        win_patterns = [(0,1,2), (3,4,5), (6,7,8),
                        (0,3,6), (1,4,7), (2,5,8),
                        (0,4,8), (2,4,6)]
        return any(all(self.board[i] == player for i in pattern) for pattern in win_patterns)

    def is_full(self):
        return ' ' not in self.board

# --------------------- Q-Learning Agent ---------------------
class QLearningAgent:
    def __init__(self, player='O', alpha=0.1, gamma=0.9, epsilon=0.1):
        self.q_table = {}
        self.player = player
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.load_q_table()

    def load_q_table(self):
        if os.path.exists("q_table.pkl"):
            with open("q_table.pkl", "rb") as f:
                self.q_table = pickle.load(f)

    def save_q_table(self):
        with open("q_table.pkl", "wb") as f:
            pickle.dump(self.q_table, f)

    def get_qs(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0] * 9
        return self.q_table[state]

    def choose_action(self, state, available_actions, train=False):
        win_move = check_threat(state, 'O')
        if win_move is not None:
            return win_move
        block_move = check_threat(state, 'X')
        if block_move is not None:
            return block_move
        if 4 in available_actions:
            return 4
        if train and random.random() < self.epsilon:
            return random.choice(available_actions)
        qs = self.get_qs(state)
        best = max([qs[a] if a in available_actions else -float('inf') for a in range(9)])
        best_actions = [a for a in available_actions if qs[a] == best]
        return random.choice(best_actions)

    def update(self, state, action, reward, next_state, done):
        qs = self.get_qs(state)
        next_qs = self.get_qs(next_state)
        target = reward if done else reward + self.gamma * max(next_qs)
        qs[action] += self.alpha * (target - qs[action])

def check_threat(state, player):
    board = list(state)
    for i in range(9):
        if board[i] == ' ':
            board[i] = player
            temp_game = TicTacToe()
            temp_game.board = board.copy()
            if temp_game.check_winner(player):
                return i
            board[i] = ' '
    return None

# --------------------- Streamlit App ---------------------
st.title("🤖 Tic-Tac-Toe with Q-Learning + Strategy")
st.markdown("You are **❌ (X)** | AI is **⭕ (O)**")

if 'game' not in st.session_state:
    st.session_state.game = TicTacToe()
    st.session_state.board = [' '] * 9
    st.session_state.agent = QLearningAgent()
    st.session_state.train_mode = False

game = st.session_state.game
agent = st.session_state.agent
game.board = st.session_state.board

# Sidebar controls
st.sidebar.title("⚙️ Settings")
st.session_state.train_mode = st.sidebar.checkbox("Training Mode", value=False)
if st.sidebar.button("💾 Save Q-Table"):
    agent.save_q_table()
    st.sidebar.success("Q-Table saved.")
if st.sidebar.button("🧽 Reset Q-Table"):
    agent.q_table = {}
    st.sidebar.warning("Q-Table reset.")

# Board layout
def display_cell(idx):
    mark = game.board[idx]
    if mark == ' ' and game.current_winner is None:
        if st.button(" ", key=idx):
            game.make_move(idx, 'X')
            state = game.get_state()
            if not game.current_winner and not game.is_full():
                action = agent.choose_action(state, game.available_actions(), train=st.session_state.train_mode)
                game.make_move(action, 'O')
                agent.update(state, action, 1 if game.current_winner == 'O' else 0, game.get_state(), game.is_full())
            st.session_state.board = game.board.copy()
            st.rerun()
    else:
        st.markdown(f"<div style='text-align:center; font-size:30px'><b>{mark}</b></div>", unsafe_allow_html=True)

# Draw board with dividers
for row in range(3):
    cols = st.columns([1, 0.1, 1, 0.1, 1])
    display_cell(row * 3)
    with cols[1]: st.markdown("<div style='text-align:center;'>#</div>", unsafe_allow_html=True)
    display_cell(row * 3 + 1)
    with cols[3]: st.markdown("<div style='text-align:center;'>#</div>", unsafe_allow_html=True)
    display_cell(row * 3 + 2)
    if row < 2:
        st.markdown("<div style='text-align:center; font-weight:bold;'># # #</div>", unsafe_allow_html=True)

# Status
if game.current_winner:
    st.success(f"🎉 Player **{game.current_winner}** wins!")
elif game.is_full():
    st.warning("🤝 It's a draw!")

if st.button("🔄 Restart Game"):
    st.session_state.game = TicTacToe()
    st.session_state.board = [' '] * 9
    st.rerun()

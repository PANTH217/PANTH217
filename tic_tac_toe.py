import os
import json
import sys
import random

STATE_FILE = "tic-tac-toe/state.json"
README_FILE = "README.md"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "board": [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]],
        "status": "playing",
        "last_move": "None"
    }

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def check_winner(board):
    # Rows
    for r in range(3):
        if board[r][0] == board[r][1] == board[r][2] != " ":
            return board[r][0]
    # Cols
    for c in range(3):
        if board[0][c] == board[1][c] == board[2][c] != " ":
            return board[0][c]
    # Diagonals
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]
    
    # Check draw
    for r in range(3):
        for c in range(3):
            if board[r][c] == " ":
                return None
    return "draw"

def minimax(board, depth, is_maximizing):
    winner = check_winner(board)
    if winner == "X":
        return 10 - depth
    elif winner == "O":
        return depth - 10
    elif winner == "draw":
        return 0

    if is_maximizing:
        best_score = -float("inf")
        for r in range(3):
            for c in range(3):
                if board[r][c] == " ":
                    board[r][c] = "X"
                    score = minimax(board, depth + 1, False)
                    board[r][c] = " "
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float("inf")
        for r in range(3):
            for c in range(3):
                if board[r][c] == " ":
                    board[r][c] = "O"
                    score = minimax(board, depth + 1, True)
                    board[r][c] = " "
                    best_score = min(score, best_score)
        return best_score

def get_best_move(board):
    # 20% chance to make a random move to make it beatable and fun
    if random.random() < 0.20:
        empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == " "]
        if empty_cells:
            return random.choice(empty_cells)

    best_score = -float("inf")
    best_move = None
    for r in range(3):
        for c in range(3):
            if board[r][c] == " ":
                board[r][c] = "X"
                score = minimax(board, 0, False)
                board[r][c] = " "
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
    return best_move

def render_board(state):
    board = state["board"]
    status = state["status"]
    last_move = state["last_move"]

    lines = []
    lines.append("### 🎮 Play Tic-Tac-Toe")
    
    if status == "playing":
        lines.append("Click on any empty square `⬜` to make your move as **⭕**. The bot will respond as **❌**.")
    elif status == "won_O":
        lines.append("🎉 **Congratulations! You won the game!** 🏆")
    elif status == "won_X":
        lines.append("🤖 **The Bot won! Better luck next time.**")
    else:
        lines.append("🤝 **It's a draw! Well played.**")
        
    lines.append("")
    lines.append("| | | |")
    lines.append("| :---: | :---: | :---: |")
    
    for r in range(3):
        row_strs = []
        for c in range(3):
            cell = board[r][c]
            if cell == "O":
                row_strs.append("⭕")
            elif cell == "X":
                row_strs.append("❌")
            else:
                if status == "playing":
                    # Make it link to a new issue
                    row_strs.append(f"[⬜](https://github.com/PANTH217/PANTH217/issues/new?title=ttt%3A+{r}+{c})")
                else:
                    row_strs.append("⬜")
        lines.append(f"| {row_strs[0]} | {row_strs[1]} | {row_strs[2]} |")
        
    lines.append("")
    lines.append(f"**Last Move:** {last_move}")
    
    if status != "playing":
        lines.append("🎮 [🔄 Click Here to Restart Game](https://github.com/PANTH217/PANTH217/issues/new?title=ttt%3A+restart)")
    else:
        lines.append("[🔄 Restart Game](https://github.com/PANTH217/PANTH217/issues/new?title=ttt%3A+restart)")
        
    return "\n".join(lines)

def update_readme(board_markdown):
    with open(README_FILE, "r") as f:
        content = f.read()

    start_tag = "<!--START_SECTION:tic-tac-toe-->"
    end_tag = "<!--END_SECTION:tic-tac-toe-->"
    
    if start_tag in content and end_tag in content:
        start_idx = content.find(start_tag) + len(start_tag)
        end_idx = content.find(end_tag)
        new_content = content[:start_idx] + "\n" + board_markdown + "\n" + content[end_idx:]
        with open(README_FILE, "w") as f:
            f.write(new_content)
    else:
        print("Error: Tic-Tac-Toe tags not found in README.md")

def main():
    if len(sys.argv) < 2:
        return
        
    cmd = sys.argv[1].strip().lower()
    state = load_state()
    
    if cmd == "ttt: restart":
        state = {
            "board": [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]],
            "status": "playing",
            "last_move": "Game restarted. Your turn!"
        }
    elif cmd.startswith("ttt:"):
        if state["status"] != "playing":
            # Just render the finished board
            update_readme(render_board(state))
            return
            
        parts = cmd.split()
        if len(parts) == 3:
            try:
                r = int(parts[1])
                c = int(parts[2])
                if state["board"][r][c] == " ":
                    # Player Move
                    state["board"][r][c] = "O"
                    state["last_move"] = f"You placed ⭕ at ({r}, {c})"
                    
                    # Check win
                    winner = check_winner(state["board"])
                    if winner == "O":
                        state["status"] = "won_O"
                    elif winner == "draw":
                        state["status"] = "draw"
                    else:
                        # Bot Move
                        bot_move = get_best_move(state["board"])
                        if bot_move:
                            state["board"][bot_move[0]][bot_move[1]] = "X"
                            state["last_move"] += f" | Bot placed ❌ at ({bot_move[0]}, {bot_move[1]})"
                            
                            winner = check_winner(state["board"])
                            if winner == "X":
                                state["status"] = "won_X"
                            elif winner == "draw":
                                state["status"] = "draw"
            except Exception as e:
                print(f"Error processing move: {e}")
                
    save_state(state)
    board_md = render_board(state)
    update_readme(board_md)

if __name__ == "__main__":
    main()

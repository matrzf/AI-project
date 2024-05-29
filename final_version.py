import tkinter as tk
import math
import random
import time

class MainMenu:
    def __init__(self, master):
        self.master = master
        self.master.title("Main Menu")
        self.master.geometry("300x250")

        self.label_dots = tk.Label(master, text="Select the number of dots (15-25):")
        self.label_dots.pack()

        self.entry = tk.Entry(master)
        self.entry.pack()

        self.label_start = tk.Label(master, text="Select who starts the game:")
        self.label_start.pack()

        self.start_var = tk.StringVar()
        self.start_var.set("AI")
        self.radio_ai = tk.Radiobutton(master, text="AI", variable=self.start_var, value="AI")
        self.radio_ai.pack()
        self.radio_player = tk.Radiobutton(master, text="Player", variable=self.start_var, value="Player")
        self.radio_player.pack()

        self.button = tk.Button(master, text="Start Game", command=self.start_game)
        self.button.pack()

    def start_game(self):
        num_dots = int(self.entry.get())
        if 15 <= num_dots <= 25:
            start_player = self.start_var.get()
            self.master.destroy()
            root = tk.Tk()
            root.title("Line Drawing Game")
            ai = GameAI(num_dots)
            app = GameGUI(root, ai, start_player)
            root.mainloop()
        else:
            tk.messagebox.showerror("Error", "Number of dots must be between 15 and 25")

class GameAI():
    def __init__(self, num_dots):
        # This variable get the number of fots the user choose to starts the game
        self.num_points = num_dots
        # The nummber of lines already draw in the game
        self.drawen_lines = {'lines': []}  # Stores tuples of points (e.g., (1, 2) means a line between points 1 and 2)
        # this variable suppose to show the player who is going to start the game and it chages by the user choice
        self.player = "AI"
        self.intersection_counter = 0
        self.intersection_level = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
        self.minmax_depth = 1
        self.counter = 0
        self.total_time_taken = 0
        self.num_moves = 0

    def is_game_over(self):
        # Check if there is any other moves left
        all_possible_lines = self.num_points * (self.num_points - 1) / 2
        return len(self.drawen_lines['lines']) >= all_possible_lines

    def get_legal_moves(self):
        # Put all the possible left moves in a list
        legal_moves = []
        for i in range(self.num_points):
            for j in range(i + 1, self.num_points):
                if (i, j) not in self.drawen_lines['lines'] and (j, i) not in self.drawen_lines['lines']:
                    legal_moves.append((i, j))
        # we shuffle the list to make the AI move more random and its movement be nicer (It has no change in the AI performance)
        random.shuffle(legal_moves)
        return legal_moves

    def apply_move(self, move, player):
        # Update the lines drawn in the game (It makes the code a bit inefficient because this process happens twice each time in the algorithm)
        if move not in self.drawen_lines['lines']:
            self.drawen_lines['lines'].append(move)
            return True
        return False

    def minmax(self, depth, maximizing_player, move):
        # Check if it reaches the depth we mentioned in the algorithm 
        if depth == 0 or self.is_game_over():
            total_intersection = 0
            for i in range(11):
                total_intersection += self.intersection_level[i]
            return total_intersection
            """if self.intersection_level[0] > 0:
                return 1
            elif self.intersection_level[0] < 0:
                return -1
            else:
                return 0"""
        # Maximize the AI score
        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_legal_moves():
                # This move will be clean and now is just for evaluation adn implementation of the algorithm
                self.apply_move(move, "AI")
                self.intersection_level[depth-1] += self.evaluate_game(move, False)
                eval = self.minmax(depth - 1, False, move)
                # Undo the move that we make in the game for evaluation and implement the algorithm
                self.undo_move(move)
                max_eval = max(max_eval, eval)
                self.intersection_level[depth-1] = 0
            return max_eval
        else:

            min_eval = float('inf')
            for move in self.get_legal_moves():
                # This move will be clean and now is just for evaluation adn implementation of the algorithm
                self.apply_move(move, "Human")
                self.intersection_level[depth-1] += self.evaluate_game(move, True)
                eval = self.minmax(depth - 1, True, move)
                # Undo the move that we make in the game for evaluation and implement the algorithm
                self.undo_move(move)
                min_eval = min(min_eval, eval)
                self.intersection_level[depth-1] = 0
            return min_eval


    def alphabeta(self, depth, alpha, beta, maximizing_player, move):
        if depth == 0 or self.is_game_over():
            total_intersection = 0
            for i in range(11):
                total_intersection += self.intersection_level[i]
            return total_intersection
        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_legal_moves():
                self.apply_move(move, self.player)
                eval = self.alphabeta(depth - 1, alpha, beta, False, move)
                self.undo_move(move)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # β cutoff
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_legal_moves():
                self.apply_move(move, self.player)
                eval = self.alphabeta(depth - 1, alpha, beta, True, move)
                self.undo_move(move)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # α cutoff
            return min_eval



    # Undo the move which are not necessary and just we draw for implementation of the algorithm 
    def undo_move(self, move):
        if move in self.drawen_lines['lines']:
            self.drawen_lines['lines'].remove(move)

    # Check if the lines intersect inside the circle (We choose the circle because the game is played in a circle board)
    def check_intersection(self, line1, line2, num_points):
        a, b = sorted(line1)
        c, d = sorted(line2)
        
        # Check if lines share a point; if so, they do not intersect inside the circle
        if len(set([a, b, c, d])) < 4:
            return False
    
        # A function to check if points have intersection
        def is_between(x, y, z, num_points): 
            if x < z:
                return x < y < z
            else:
                return x < y or y < z
        return is_between(a, c, b, num_points) != is_between(a, d, b, num_points) and is_between(c, a, d, num_points) != is_between(c, b, d, num_points)

    # Report the intersection between specific line a line which drawen previously
    def find_num_intersections(self, new_line, lines, num_points):
        Num_intersections = 0
        for i in range(len(lines)):
            if self.check_intersection(new_line, lines[i], num_points):
                Num_intersections += 1
        return Num_intersections

    def evaluate_game(self,new_line,player):
        lines = self.drawen_lines['lines']
        num_points = self.num_points
        num_intersections = self.find_num_intersections(new_line, lines, num_points)
        #print(f"Intersection score for {new_line}: ", num_intersections)
        if player:
            return num_intersections
        else:
            return -num_intersections

    # Count number of the specific line and all other lines drawen tiill that moment
    def find_total_intersections(self, lines, num_points):
        total_intersections = 0
        for i in range(len(lines)):
            for j in range(i+1, len(lines)):
                if self.check_intersection(lines[i], lines[j], num_points):
                    total_intersections += 1
        return total_intersections


    # Find the best move that the AI can make in the game (It is working quite well but it is not perfect yet because it iis not completly efficient) 
    def choose_best_move(self):
        best_score = float(-1000)
        best_move = None
        for move in self.get_legal_moves():
            self.apply_move(move, self.player)
            self.intersection_level[self.minmax_depth] += self.evaluate_game(move, False)
            score = self.minmax(self.minmax_depth, False, move) 
            if self.intersection_level[self.minmax_depth] > 0:
                score += 1
            elif self.intersection_level[self.minmax_depth] < 0:
                score -= 1
            print("The score is: ", score, ", ", best_move)
            self.intersection_level[self.minmax_depth] = 0
            self.undo_move(move)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    # Make the best move for the AI
    def make_move(self):
        start_time = time.time()
        best_move = self.choose_best_move()
        end_time = time.time()
        move_time = end_time - start_time
        self.total_time_taken += move_time
        self.num_moves += 1
        average_time = self.total_time_taken / self.num_moves
        print("AI move took {:.4f} seconds (Average: {:.4f} seconds)".format(self.total_time_taken, average_time))
        if best_move:
            self.apply_move(best_move, self.player)
            converted_best_move = tuple(chr(i+65) for i in best_move)
            #print(f"AI moves: {converted_best_move}")
            #print("--------------------------------------------------------------------------------------------------")
            return best_move
        else:
            # When it shows None it means there is no move left 
            return None
        

class GameGUI:
    def __init__(self, master, ai, start_player):
        self.master = master
        self.ai = ai
        self.start_player = start_player
        self.points = []
        self.lines = []
        self.player_score = 0
        self.ai_score = 0

        self.player_score_label = tk.Label(master, text="Player Score: 0")
        self.player_score_label.pack()
        self.ai_score_label = tk.Label(master, text="AI Score: 0")
        self.ai_score_label.pack()

        self.canvas = tk.Canvas(master, width=400, height=400)
        self.canvas.pack()

        self.draw_game_board()
        self.canvas.bind("<Button-1>", self.human_move)

        if self.start_player == "AI":
            self.ai_move()

        self.restart_button = tk.Button(master, text="Restart", command=self.restart_game)
        self.restart_button.pack()

    def draw_game_board(self):
        center_x, center_y = 200, 200
        radius = 150
        labels = 'abcdefghijklmnopqrstuvwxyz'
        for i in range(self.ai.num_points):
            angle = 2 * math.pi * i / self.ai.num_points
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.points.append((x, y))
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='black')
            self.canvas.create_text(x, y - 20, text=labels[i], fill="black")

    def human_move(self, event):
        closest_point = None
        min_distance = float('inf')
        for i, (x, y) in enumerate(self.points):
            distance = math.sqrt((x - event.x) ** 2 + (y - event.y) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_point = i

        if self.ai.drawen_lines.get('selected_point') is None:
            self.ai.drawen_lines['selected_point'] = closest_point
            self.canvas.create_oval(self.points[closest_point][0] - 7, self.points[closest_point][1] - 7,
                                    self.points[closest_point][0] + 7, self.points[closest_point][1] + 7,
                                    outline='red')
        else:
            start_point = self.ai.drawen_lines['selected_point']
            end_point = closest_point
            if (start_point, end_point) not in self.ai.drawen_lines['lines'] and start_point != end_point:
                crossed_lines = self.count_crossed_lines((start_point, end_point))
                self.player_score += crossed_lines
                self.player_score_label.config(text="Player Score: " + str(self.player_score))
                self.ai.apply_move((start_point, end_point), "Human")
                self.lines.append((start_point, end_point))
                self.canvas.create_line(self.points[start_point][0], self.points[start_point][1],
                                        self.points[end_point][0], self.points[end_point][1],
                                        width=2, fill='blue')
                self.ai.drawen_lines.pop('selected_point', None)
                self.ai_move()

    def ai_move(self):
        ai_move = self.ai.make_move()
        if ai_move:
            crossed_lines = self.count_crossed_lines(ai_move)
            self.ai_score += crossed_lines
            self.ai_score_label.config(text="AI Score: " + str(self.ai_score))
            self.lines.append(ai_move)
            self.canvas.create_line(self.points[ai_move[0]][0], self.points[ai_move[0]][1],
                                    self.points[ai_move[1]][0], self.points[ai_move[1]][1],
                                    width=2, fill='red')

    def count_crossed_lines(self, new_line):
        crossed_lines = 0
        for line in self.lines:
            if self.do_lines_intersect(line, new_line):
                crossed_lines += 1
        return crossed_lines

    def do_lines_intersect(self, line1, line2):
        x1, y1 = self.points[line1[0]]
        x2, y2 = self.points[line1[1]]
        x3, y3 = self.points[line2[0]]
        x4, y4 = self.points[line2[1]]

        def ccw(ax, ay, bx, by, cx, cy):
            return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)

        intersect = ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4) and \
                    ccw(x1, y1, x2, y2, x3, y3) != ccw(x1, y1, x2, y2, x4, y4)

        touch_endpoints = (line1[0] == line2[0] or line1[0] == line2[1] or line1[1] == line2[0] or line1[1] == line2[1])

        return intersect and not touch_endpoints
    
    """
    def does_line_intersect(self, new_line):
        for line in self.lines:
            if self.do_lines_intersect(line, new_line):
                for point in line:
                    if point in new_line:
                        return False
                return True
        return False
    """
    
    def restart_game(self):
        self.master.destroy()
        menu_root = tk.Tk()
        menu = MainMenu(menu_root)
        menu_root.mainloop()

def main():
    menu_root = tk.Tk()
    menu = MainMenu(menu_root)
    menu_root.mainloop()

if __name__ == "__main__":
    main()

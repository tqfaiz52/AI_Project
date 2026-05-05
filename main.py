

import pygame
import sys
import time
import threading
from game_engine import GameEngine, PLAYER, AI, ROWS, COLS, EMPTY
from ai_agent import AIAgent
from heuristic import HEURISTIC_PRESETS

#Layout
CELL_SIZE    = 90
RADIUS       = CELL_SIZE // 2 - 6
BOARD_W      = COLS * CELL_SIZE
BOARD_H      = ROWS * CELL_SIZE
HEADER_H     = CELL_SIZE          
PANEL_W      = 340             # Had to change PANEL_W from 300 to 340 because the text was clipping   
WIN_W        = BOARD_W + PANEL_W
WIN_H        = HEADER_H + BOARD_H + 60   


BG           = (10,  12,  26)
BOARD_BG     = (18,  22,  48)
GRID_COLOR   = (30,  36,  70)
P1_COLOR     = (230, 60,  60)    
P2_COLOR     = (60,  180, 255)  
EMPTY_COLOR  = (25,  30,  60)
WIN_GLOW     = (255, 255, 80)    
PANEL_BG     = (14,  17,  38)
ACCENT       = (80,  130, 255)
TEXT_MAIN    = (220, 225, 255)
TEXT_DIM     = (100, 110, 160)
TEXT_GOOD    = (80,  220, 120)
TEXT_BAD     = (230, 80,  80)
BTN_BG       = (30,  40,  90)
BTN_HOVER    = (50,  70,  140)
BTN_ACTIVE   = (60,  110, 220)
SHADOW       = (5,   7,   18)

pygame.init()
pygame.display.set_caption("Connect 4")


def load_fonts():
    fonts = {}
    fonts["title"]  = pygame.font.SysFont("Courier New", 15, bold=True)
    fonts["body"]   = pygame.font.SysFont("Courier New", 13)
    fonts["small"]  = pygame.font.SysFont("Courier New", 11)
    fonts["status"] = pygame.font.SysFont("Courier New", 16, bold=True)
    fonts["big"]    = pygame.font.SysFont("Courier New", 22, bold=True)
    return fonts


class Button:
    def __init__(self, rect, label, font, active=False):
        self.rect   = pygame.Rect(rect)
        self.label  = label
        self.font   = font
        self.active = active

    def draw(self, surface, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        if self.active:
            color = BTN_ACTIVE
        elif hovered:
            color = BTN_HOVER
        else:
            color = BTN_BG
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, ACCENT, self.rect, 1, border_radius=6)
        txt = self.font.render(self.label, True, TEXT_MAIN)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Connect4App:
    def __init__(self):
        self.screen  = pygame.display.set_mode((WIN_W, WIN_H))
        self.fonts   = load_fonts()
        self.clock   = pygame.time.Clock()

        self.engine  = GameEngine()
        self.ai      = AIAgent(depth=5, use_alpha_beta=True)
        self.ai_pure = AIAgent(depth=5, use_alpha_beta=False)  # For comparison

        self.ai_depth     = 5
        self.use_ab       = True
        self.heuristic    = "Balanced (Default)"
        self.hover_col    = -1
        self.ai_thinking  = False
        self.winner       = 0
        self.win_cells    = []
        self.win_glow_t   = 0

        # Research stats
        self.last_ab_nodes    = 0
        self.last_pure_nodes  = 0
        self.ab_history       = []
        self.pure_history     = []
        self.move_times_ab    = []
        self.move_times_pure  = []
        self.total_moves      = 0

        self.status_msg   = "YOUR TURN  —  Click a column to drop a piece"
        self.status_color = P1_COLOR

        self._build_buttons()

    def _build_buttons(self):
        f = self.fonts["small"]
        px = BOARD_W + 12
        self.btn_newgame = Button((px, 14, PANEL_W - 24, 28), "NEW GAME", f)

        # Depth buttons
        self.depth_btns = []
        for i, d in enumerate([3, 5, 7]):
            b = Button((px + i * 68, 56, 62, 24), f"Depth {d}", f, active=(d == self.ai_depth))
            self.depth_btns.append((d, b))

        # Algorithm toggle
        self.btn_ab   = Button((px,       88, 148, 24), "Alpha-Beta ON",  f, active=True)
        self.btn_pure = Button((px + 155, 88, 148, 24), "Pure Minimax",   f, active=False)

        # Heuristic buttons
        self.heur_btns = []
        for i, name in enumerate(HEURISTIC_PRESETS.keys()):
            short = name.split(" ")[0]
            b = Button((px + (i % 2) * 158, 136 + (i // 2) * 30, 148, 24),
                       short, f, active=(name == self.heuristic))
            self.heur_btns.append((name, b))

    def _apply_settings(self):
        w = HEURISTIC_PRESETS[self.heuristic]
        self.ai      = AIAgent(depth=self.ai_depth, use_alpha_beta=self.use_ab, weights=w)
        self.ai_pure = AIAgent(depth=self.ai_depth, use_alpha_beta=False, weights=w)
        for d, b in self.depth_btns:
            b.active = (d == self.ai_depth)
        self.btn_ab.active   = self.use_ab
        self.btn_pure.active = not self.use_ab
        for name, b in self.heur_btns:
            b.active = (name == self.heuristic)

    def _col_from_x(self, x):
        if x < 0 or x >= BOARD_W:
            return -1
        return x // CELL_SIZE

    def board_to_screen(self, row, col):
        sx = col * CELL_SIZE + CELL_SIZE // 2
        sy = HEADER_H + row * CELL_SIZE + CELL_SIZE // 2
        return sx, sy

    #Draw

    def draw_board(self):
        s = self.screen
        pygame.draw.rect(s, BOARD_BG, (0, HEADER_H, BOARD_W, BOARD_H))

        for row in range(ROWS):
            for col in range(COLS):
                cx, cy = self.board_to_screen(row, col)

              
                pygame.draw.circle(s, SHADOW, (cx + 2, cy + 2), RADIUS + 2)
                
                pygame.draw.circle(s, EMPTY_COLOR, (cx, cy), RADIUS)

                piece = self.engine.board[row][col]
                if piece == PLAYER:
                    color = P1_COLOR
                elif piece == AI:
                    color = P2_COLOR
                else:
                    color = None

                if color:
                
                    glow = pygame.Surface((RADIUS * 2 + 20, RADIUS * 2 + 20), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (*color, 40), (RADIUS + 10, RADIUS + 10), RADIUS + 8)
                    s.blit(glow, (cx - RADIUS - 10, cy - RADIUS - 10))
                    pygame.draw.circle(s, color, (cx, cy), RADIUS)
                    # Shine
                    pygame.draw.circle(s, tuple(min(255, c + 60) for c in color),
                                       (cx - RADIUS // 4, cy - RADIUS // 4), RADIUS // 4)

                # Win highlight
                if self.win_cells and (row, col) in self.win_cells:
                    pulse = abs(int(180 * ((pygame.time.get_ticks() % 800) / 400 - 1)))
                    pygame.draw.circle(s, WIN_GLOW, (cx, cy), RADIUS, 4)
                    glow2 = pygame.Surface((RADIUS * 2 + 30, RADIUS * 2 + 30), pygame.SRCALPHA)
                    pygame.draw.circle(glow2, (255, 255, 80, pulse),
                                       (RADIUS + 15, RADIUS + 15), RADIUS + 10)
                    s.blit(glow2, (cx - RADIUS - 15, cy - RADIUS - 15))

                # Grid line
                pygame.draw.circle(s, GRID_COLOR, (cx, cy), RADIUS, 1)

    def draw_header(self):
        s = self.screen
        pygame.draw.rect(s, BG, (0, 0, BOARD_W, HEADER_H))

        if not self.engine.game_over and self.hover_col >= 0 and self.engine.is_valid_location(self.hover_col):
            cx = self.hover_col * CELL_SIZE + CELL_SIZE // 2
            cy = HEADER_H // 2
            color = P1_COLOR if self.engine.turn == PLAYER else P2_COLOR
            #bounce
            bounce = int(6 * abs((pygame.time.get_ticks() % 600) / 300 - 1))
            pygame.draw.circle(s, color, (cx, cy + bounce), RADIUS - 4)
            #Glow
            glow = pygame.Surface((RADIUS * 2 + 20, RADIUS * 2 + 20), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*color, 60), (RADIUS + 10, RADIUS + 10), RADIUS + 8)
            s.blit(glow, (cx - RADIUS - 10, cy + bounce - RADIUS - 10))

    def draw_status(self):
        s = self.screen
        y = HEADER_H + BOARD_H
        pygame.draw.rect(s, SHADOW, (0, y, BOARD_W, 60))
        pygame.draw.line(s, ACCENT, (0, y), (BOARD_W, y), 1)
        txt = self.fonts["status"].render(self.status_msg, True, self.status_color)
        s.blit(txt, txt.get_rect(center=(BOARD_W // 2, y + 30)))

    def draw_panel(self):
        s = self.screen
        px = BOARD_W
        mouse = pygame.mouse.get_pos()
        pygame.draw.rect(s, PANEL_BG, (px, 0, PANEL_W, WIN_H))
        pygame.draw.line(s, ACCENT, (px, 0), (px, WIN_H), 1)
        f = self.fonts

        def label(text, x, y, color=TEXT_DIM, font="small"):
            t = f[font].render(text, True, color)
            s.blit(t, (x, y))

        #Title
        label("CONNECT 4", px + 12, 0, ACCENT, "title")

        #Buttons
        self.btn_newgame.draw(s, mouse)
        label("SEARCH DEPTH:", px + 12, 44, TEXT_DIM)
        for _, b in self.depth_btns:
            b.draw(s, mouse)
        label("ALGORITHM:", px + 12, 76, TEXT_DIM)
        self.btn_ab.draw(s, mouse)
        self.btn_pure.draw(s, mouse)
        label("HEURISTIC PRESET:", px + 12, 122, TEXT_DIM)
        for _, b in self.heur_btns:
            b.draw(s, mouse)

        #Research Stats
        sy = 200
        pygame.draw.line(s, GRID_COLOR, (px + 8, sy), (px + PANEL_W - 8, sy))
        label("NODE EXPANSION ANALYSIS", px + 12, sy + 6, ACCENT, "title")

        label("Algorithm:", px + 12, sy + 30)
        algo_name = "Alpha-Beta Pruning" if self.use_ab else "Pure Minimax"
        label(algo_name, px + 140, sy + 30, TEXT_MAIN, "body")

        label("Last Move Nodes:", px + 12, sy + 48)
        label(f"{self.last_ab_nodes:,}" if self.use_ab else f"{self.last_pure_nodes:,}",
              px + 140, sy + 48, TEXT_GOOD, "body")

        label("Nodes Saved (pruned):", px + 12, sy + 66)
        saved = max(0, self.last_pure_nodes - self.last_ab_nodes)
        if self.last_pure_nodes > 0 and self.last_ab_nodes > 0:
            pct = 100 * saved / max(self.last_pure_nodes, 1)
            label(f"{saved:,}  ({pct:.0f}% fewer)", px + 12, sy + 82, TEXT_GOOD, "small")
        else:
            label("Play a move to measure", px + 12, sy + 82, TEXT_DIM, "small")

        label("Total Moves", px + 12, sy + 100)
        label(str(self.total_moves), px + 200, sy + 100, TEXT_MAIN, "body")

        #Bar
        sy2 = sy + 118
        label("Node Count History (last 8 moves):", px + 12, sy2, TEXT_DIM)
        sy2 += 16
        if self.ab_history:
            max_val = max(max(self.ab_history[-8:] or [1]),
                          max(self.pure_history[-8:] or [1]), 1)
            bar_area_w = PANEL_W - 24
            bar_area_h = 60
            pygame.draw.rect(s, BOARD_BG, (px + 12, sy2, bar_area_w, bar_area_h))
            n = min(len(self.ab_history), 8)
            bw = bar_area_w // (n * 2 + 1)

            for i in range(n):
                ab_val  = self.ab_history[-(n - i)]
                pur_val = self.pure_history[-(n - i)] if i < len(self.pure_history) else 0
                bx = px + 12 + bw + i * bw * 2

                # AB bar
                ab_h = int((ab_val / max_val) * (bar_area_h - 4))
                pygame.draw.rect(s, P2_COLOR,
                                 (bx, sy2 + bar_area_h - ab_h, bw - 2, ab_h))

                # Pure bar
                pur_h = int((pur_val / max_val) * (bar_area_h - 4))
                pygame.draw.rect(s, (200, 80, 80),
                                 (bx + bw, sy2 + bar_area_h - pur_h, bw - 2, pur_h))

            sy2 += bar_area_h + 4
            label("Alpha-Beta", px + 12, sy2, P2_COLOR, "small")
            label("Pure Minimax", px + 80, sy2, (200, 80, 80), "small")

        #Heuristic Explanation
        sy3 = sy + 250
        pygame.draw.line(s, GRID_COLOR, (px + 8, sy3), (px + PANEL_W - 8, sy3))
        label("HEURISTIC WEIGHTS", px + 12, sy3 + 6, ACCENT, "title")

        from heuristic import HEURISTIC_PRESETS
        w = HEURISTIC_PRESETS[self.heuristic]
        items = [
            ("4-in-row",   w["four_in_a_row"]),
            ("3-in-row",   w["three_in_a_row"]),
            ("2-in-row",   w["two_in_a_row"]),
            ("Center",     w["center_control"]),
            ("Blk opp 3",  w["opp_three_block"]),
            ("Blk opp 2",  w["opp_two_block"]),
        ]
        wy = sy3 + 24
        for name, val in items:
            bar_w = min(abs(int(val / 2000 * 80)), 80)
            color = TEXT_GOOD if val > 0 else TEXT_BAD
            label(f"{name:<12} {val:>9,}", px + 12, wy, color, "small")
            bx = px + 200
            if val > 0:
                pygame.draw.rect(s, TEXT_GOOD, (bx, wy + 2, bar_w, 8))
            else:
                pygame.draw.rect(s, TEXT_BAD, (bx - bar_w, wy + 2, bar_w, 8))
            wy += 16

        #Research Notes
        sy4 = sy + 400
        pygame.draw.line(s, GRID_COLOR, (px + 8, sy4), (px + PANEL_W - 8, sy4))
        label("RESEARCH NOTES", px + 12, sy4 + 6, ACCENT, "title")
        notes = [
           "The AI looks ahead a few moves",
            "to find the best spot.",
            "",
            "Pruning is currently ENABLED",
            "to make the AI faster.",
            "",
            "Press 'N' if the game gets",
            "stuck or you want to restart."
] 
        ny = sy4 + 24
        for line in notes:
            label(line, px + 12, ny, TEXT_DIM)
            ny += 14



    def run_ai_move(self):
        print(f"--- AI is calculating move at depth {self.ai_depth} ---") 
        self.ai_thinking = True
        self.status_msg   = "AI IS THINKING..."
        self.status_color = P2_COLOR

    
        t0 = time.time()
        col_ab, nodes_ab = AIAgent(
            depth=self.ai_depth, use_alpha_beta=True,
            weights=HEURISTIC_PRESETS[self.heuristic]
        ).get_move(self.engine)
        t_ab = time.time() - t0

        t0 = time.time()
        col_pure, nodes_pure = AIAgent(
            depth=self.ai_depth, use_alpha_beta=False,
            weights=HEURISTIC_PRESETS[self.heuristic]
        ).get_move(self.engine)
        t_pure = time.time() - t0

        # Record for research panel
        self.last_ab_nodes   = nodes_ab
        self.last_pure_nodes = nodes_pure
        self.ab_history.append(nodes_ab)
        self.pure_history.append(nodes_pure)
        self.move_times_ab.append(t_ab)
        self.move_times_pure.append(t_pure)

    
        col = col_ab if self.use_ab else col_pure

    
        row = self.engine.drop_piece(col, AI)
        self.total_moves += 1

        if self.engine.check_win(AI):
            self.win_cells = self.engine.get_winning_cells(AI)
            self.engine.game_over = True
            self.winner = AI
            self.status_msg   = "AI WINS! (Press N for new game)"
            self.status_color = P2_COLOR
        elif self.engine.is_draw():
            self.engine.game_over = True
            self.winner = -1
            self.status_msg   = "DRAW! (Press N for new game)"
            self.status_color = TEXT_DIM
        else:
            self.engine.turn  = PLAYER
            self.status_msg   = "YOUR TURN  —  Click a column to drop"
            self.status_color = P1_COLOR

        self.ai_thinking = False

    # This loop keeps the window open and handles clicks. Don't touch the clock.tick(60) or it lags.

    def run(self):
        while True:
            self.clock.tick(60)
            mouse = pygame.mouse.get_pos()
            self.hover_col = self._col_from_x(mouse[0]) if mouse[0] < BOARD_W else -1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        self._new_game()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)

            # Draw everything
            self.screen.fill(BG)
            self.draw_header()
            self.draw_board()
            self.draw_status()
            self.draw_panel()
            pygame.display.flip()

    def _handle_click(self, pos):
        mx, my = pos
        mouse = pos

        # Board click — player move
        if (mx < BOARD_W and my > HEADER_H
                and not self.engine.game_over
                and not self.ai_thinking
                and self.engine.turn == PLAYER):
            col = self._col_from_x(mx)
            if col >= 0 and self.engine.is_valid_location(col):
                row = self.engine.drop_piece(col, PLAYER)
                self.total_moves += 1

                if self.engine.check_win(PLAYER):
                    self.win_cells = self.engine.get_winning_cells(PLAYER)
                    self.engine.game_over = True
                    self.winner = PLAYER
                    self.status_msg   = "YOU WIN! (Press N for new game)"
                    self.status_color = P1_COLOR
                elif self.engine.is_draw():
                    self.engine.game_over = True
                    self.winner = -1
                    self.status_msg   = "DRAW! (Press N for new game)"
                    self.status_color = TEXT_DIM
                else:
                    self.engine.turn = AI
                    t = threading.Thread(target=self.run_ai_move, daemon=True)
                    t.start()

        # Panel button clicks
        if self.btn_newgame.is_clicked(pos):
            self._new_game()
            return

        for d, b in self.depth_btns:
            if b.is_clicked(pos):
                self.ai_depth = d
                self._apply_settings()

        if self.btn_ab.is_clicked(pos):
            self.use_ab = True
            self._apply_settings()
        if self.btn_pure.is_clicked(pos):
            self.use_ab = False
            self._apply_settings()

        for name, b in self.heur_btns:
            if b.is_clicked(pos):
                self.heuristic = name
                self._apply_settings()

    def _new_game(self):
        if self.ai_thinking:
            return
        self.engine.reset()
        self.winner    = 0
        self.win_cells = []
        self.total_moves = 0
        self.last_ab_nodes = 0
        self.last_pure_nodes = 0
        self.status_msg   = "YOUR TURN  —  Click a column to drop a piece"
        self.status_color = P1_COLOR


if __name__ == "__main__":
    app = Connect4App()
    app.run()

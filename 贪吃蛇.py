import pygame
import random
import time
import os

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.width = 20
        self.height = 20
        self.cell_size = 20
        self.screen_width = self.width * self.cell_size + 40
        self.screen_height = self.height * self.cell_size + 80
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Snake Game")
        
        self.colors = {
            "background": (0, 0, 0),
            "snake": (0, 255, 0),
            "head": (0, 200, 0),
            "food": (255, 0, 0),
            "wall": (100, 100, 100),
            "text": (255, 255, 255),
            "score": (200, 200, 200)
        }
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 20)
        self.big_font = pygame.font.SysFont('Arial', 30)
        
        self.highscore_file = "highscore.txt"
        self.highscore = 0
        self.load_highscore()
        
        self.reset_game()
    
    def load_highscore(self):
        if os.path.exists(self.highscore_file):
            with open(self.highscore_file, 'r') as f:
                try:
                    self.highscore = int(f.read())
                except:
                    self.highscore = 0
    
    def save_highscore(self):
        with open(self.highscore_file, 'w') as f:
            f.write(str(self.highscore))
    
    def reset_game(self):
        self.snake = [(self.width // 2, self.height // 2)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.speed = 200  # ms per move
        self.last_move_time = pygame.time.get_ticks()
    
    def generate_food(self):
        while True:
            food = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if food not in self.snake:
                return food
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                if self.game_over:
                    if event.key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                        self.reset_game()
                    continue
                
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    continue
                
                if self.paused:
                    continue
                
                if event.key == pygame.K_UP and self.direction != (0, 1):
                    self.next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                    self.next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                    self.next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                    self.next_direction = (1, 0)
        
        return True
    
    def update(self):
        if self.paused or self.game_over:
            return
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < self.speed:
            return
        
        self.last_move_time = current_time
        self.direction = self.next_direction
        
        head_x, head_y = self.snake[0]
        new_x = head_x + self.direction[0]
        new_y = head_y + self.direction[1]
        
        # Check collisions
        if (new_x < 0 or new_x >= self.width or 
            new_y < 0 or new_y >= self.height or 
            (new_x, new_y) in self.snake):
            self.game_over = True
            if self.score > self.highscore:
                self.highscore = self.score
                self.save_highscore()
            return
        
        # Move snake
        self.snake.insert(0, (new_x, new_y))
        
        # Check food
        if (new_x, new_y) == self.food:
            self.score += 1
            self.food = self.generate_food()
        else:
            self.snake.pop()
    
    def draw(self):
        self.screen.fill(self.colors["background"])
        
        # Draw walls
        pygame.draw.rect(self.screen, self.colors["wall"], 
                         (10, 30, self.width * self.cell_size + 20, self.height * self.cell_size + 20), 2)
        
        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            color = self.colors["head"] if i == 0 else self.colors["snake"]
            pygame.draw.rect(self.screen, color, 
                             (20 + x * self.cell_size, 40 + y * self.cell_size, 
                              self.cell_size - 2, self.cell_size - 2))
        
        # Draw food
        pygame.draw.rect(self.screen, self.colors["food"], 
                         (20 + self.food[0] * self.cell_size, 40 + self.food[1] * self.cell_size, 
                          self.cell_size - 2, self.cell_size - 2))
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}  High Score: {self.highscore}", True, self.colors["score"])
        self.screen.blit(score_text, (20, 10))
        
        # Draw game state messages
        if self.game_over:
            game_over_text = self.big_font.render("GAME OVER! Press R to restart", True, self.colors["text"])
            text_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(game_over_text, text_rect)
        
        if self.paused and not self.game_over:
            paused_text = self.big_font.render("PAUSED - Press SPACE to continue", True, self.colors["text"])
            text_rect = paused_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(paused_text, text_rect)
        
        pygame.display.flip()
    
    def show_start_screen(self):
        self.screen.fill(self.colors["background"])
        
        title_text = self.big_font.render("SNAKE GAME", True, self.colors["text"])
        title_rect = title_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 60))
        self.screen.blit(title_text, title_rect)
        
        controls = [
            "Controls:",
            "Arrow Keys - Move",
            "SPACE - Pause",
            "ESC - Quit",
            "R - Restart after game over",
            "",
            "Press any key to start"
        ]
        
        for i, line in enumerate(controls):
            text = self.font.render(line, True, self.colors["text"])
            self.screen.blit(text, (self.screen_width//2 - 100, self.screen_height//2 - 20 + i * 25))
        
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                if event.type == pygame.KEYDOWN:
                    waiting = False
        
        return True
    
    def run(self):
        if not self.show_start_screen():
            return
        
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
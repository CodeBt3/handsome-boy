import pygame
import random
import sys
from enum import Enum
from collections import namedtuple

# Initialize Pygame
pygame.init()

# Constants
BLOCK_SIZE = 20
SPEED = 10

# Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# Font
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class FoodType(Enum):
    REGULAR = 1    # Red - score +1
    BONUS = 2      # Yellow - score +3
    SPEED = 3      # Purple - temporary speed boost

Point = namedtuple('Point', 'x, y')
Food = namedtuple('Food', 'x, y, type')

class SnakeGame:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Greedy Snake Game - Three Food Types & Lives!')
        self.clock = pygame.time.Clock()
        
        # Initialize game state
        self.direction = Direction.RIGHT
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        self.score = 0
        self.lives = 3  # Start with 3 lives
        self.foods = []  # List to hold multiple food items
        self.speed_boost_timer = 0
        self.current_speed = SPEED
        self.game_over = False
        self.paused = False
        self.wall_hit = False  # Flag to indicate wall collision
        
        # Place initial foods
        self._place_foods()
        
    def _place_foods(self):
        """Place three different types of food on the board"""
        self.foods.clear()
        
        # Place regular food (red)
        self.foods.append(self._get_random_food_position(FoodType.REGULAR))
        
        # Place bonus food (yellow)
        self.foods.append(self._get_random_food_position(FoodType.BONUS))
        
        # Place speed food (purple)
        self.foods.append(self._get_random_food_position(FoodType.SPEED))
    
    def _get_random_food_position(self, food_type):
        """Get a random position for food that doesn't overlap with snake or other foods"""
        while True:
            x = random.randint(0, (self.w-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
            y = random.randint(0, (self.h-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
            new_food = Food(x, y, food_type)
            
            # Check if position overlaps with snake
            if new_food in self.snake:
                continue
                
            # Check if position overlaps with other foods
            overlap = False
            for existing_food in self.foods:
                if new_food.x == existing_food.x and new_food.y == existing_food.y:
                    overlap = True
                    break
            
            if not overlap:
                return new_food
    
    def _reset_snake_position(self):
        """Reset snake to center after losing a life"""
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        self.direction = Direction.RIGHT
        self.wall_hit = False
        
    def play_step(self):
        # 1. Collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                if event.key == pygame.K_r and self.game_over:
                    self.__init__(self.w, self.h)
                if not self.paused and not self.game_over and not self.wall_hit:
                    if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                        self.direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                        self.direction = Direction.RIGHT
                    elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                        self.direction = Direction.UP
                    elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                        self.direction = Direction.DOWN
        
        if self.paused or self.game_over:
            return
            
        # Handle wall hit recovery
        if self.wall_hit:
            # Wait a moment before allowing movement
            pygame.time.wait(1000)  # Wait 1 second
            self._reset_snake_position()
            return
            
        # 2. Move
        self._move(self.direction)
        self.snake.insert(0, self.head)
        
        # 3. Check collisions
        collision_type = self._check_collision()
        
        if collision_type == "wall":
            self.lives -= 1
            self.wall_hit = True
            if self.lives <= 0:
                self.game_over = True
            return
        elif collision_type == "self":
            self.game_over = True
            return
            
        # 4. Check food collision and place new food
        food_eaten = False
        for i, food in enumerate(self.foods):
            if self.head.x == food.x and self.head.y == food.y:
                self._eat_food(food)
                self.foods.pop(i)
                food_eaten = True
                break
        
        if food_eaten:
            # Place new food of the same type
            self._place_foods()
        else:
            self.snake.pop()
        
        # 5. Update speed boost timer
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer == 0:
                self.current_speed = SPEED
        
        # 6. Update UI and clock
        self._update_ui()
        self.clock.tick(self.current_speed)
        
    def _check_collision(self):
        """Check for collisions and return collision type"""
        # Check wall collision
        if (self.head.x >= self.w or self.head.x < 0 or 
            self.head.y >= self.h or self.head.y < 0):
            return "wall"
        
        # Check self collision
        if self.head in self.snake[1:]:
            return "self"
        
        return None
        
    def _eat_food(self, food):
        """Handle eating different types of food"""
        if food.type == FoodType.REGULAR:
            self.score += 1
        elif food.type == FoodType.BONUS:
            self.score += 3
        elif food.type == FoodType.SPEED:
            self.score += 1
            self.current_speed = SPEED + 5  # Increase speed
            self.speed_boost_timer = 50      # Speed boost lasts for 50 frames
        
    def _update_ui(self):
        self.display.fill(BLACK)
        
        # Draw snake
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
        
        # Draw foods with different colors
        for food in self.foods:
            if food.type == FoodType.REGULAR:
                color = RED
            elif food.type == FoodType.BONUS:
                color = YELLOW
            elif food.type == FoodType.SPEED:
                color = PURPLE
            
            pygame.draw.rect(self.display, color, pygame.Rect(food.x, food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        # Draw score and lives
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.display.blit(score_text, [10, 10])
        
        # Draw lives as hearts
        lives_text = font.render(f'Lives: ', True, WHITE)
        self.display.blit(lives_text, [10, 70])
        
        for i in range(self.lives):
            # Draw heart symbol (simple red square for now)
            heart_x = 80 + i * 25
            pygame.draw.rect(self.display, RED, pygame.Rect(heart_x, 70, 20, 20))
        
        # Draw speed boost indicator
        if self.speed_boost_timer > 0:
            speed_text = font.render(f'Speed Boost: {self.speed_boost_timer//10 + 1}s', True, GREEN)
            self.display.blit(speed_text, [10, 40])
        
        # Draw wall hit warning
        if self.wall_hit:
            warning_text = big_font.render(f'LIFE LOST! ({self.lives} remaining)', True, ORANGE)
            self.display.blit(warning_text, 
                            [self.w//2 - warning_text.get_width()//2, self.h//2 - 30])
        
        # Draw food legend
        legend_y = self.h - 120
        legend_items = [
            ('Red Food', RED, '+1 Score'),
            ('Yellow Food', YELLOW, '+3 Score'),
            ('Purple Food', PURPLE, '+1 Score + Speed Boost')
        ]
        
        for i, (name, color, effect) in enumerate(legend_items):
            # Draw colored square
            pygame.draw.rect(self.display, color, pygame.Rect(10, legend_y + i * 25, 15, 15))
            # Draw text
            legend_text = font.render(f'{name}: {effect}', True, WHITE)
            self.display.blit(legend_text, [30, legend_y + i * 25])
        
        # Draw instructions
        if not self.game_over:
            instructions = [
                'Use Arrow Keys to move',
                'Space to pause',
                'ESC to quit'
            ]
            for i, instruction in enumerate(instructions):
                text = font.render(instruction, True, GRAY)
                self.display.blit(text, [self.w - 200, self.h - 80 + i * 25])
        
        # Draw game over screen
        if self.game_over:
            game_over_text = big_font.render('GAME OVER!', True, RED)
            restart_text = font.render('Press R to restart', True, WHITE)
            final_score = font.render(f'Final Score: {self.score}', True, WHITE)
            
            self.display.blit(game_over_text, 
                            [self.w//2 - game_over_text.get_width()//2, self.h//2 - 60])
            self.display.blit(restart_text, 
                            [self.w//2 - restart_text.get_width()//2, self.h//2])
            self.display.blit(final_score, 
                            [self.w//2 - final_score.get_width()//2, self.h//2 + 40])
        
        # Draw pause screen
        if self.paused and not self.game_over:
            pause_text = big_font.render('PAUSED', True, WHITE)
            self.display.blit(pause_text, 
                            [self.w//2 - pause_text.get_width()//2, self.h//2 - 30])
        
        pygame.display.flip()
        
    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        self.head = Point(x, y)

def main():
    game = SnakeGame()
    
    # Game loop
    while True:
        game.play_step()
        
        if game.game_over:
            # Wait for restart or quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game = SnakeGame()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

if __name__ == '__main__':
    main()

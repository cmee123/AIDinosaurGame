import pygame
import os
import random
import math
import sys
import neat
import matplotlib.pyplot as plt
from IPython import display

# initialize pygame window and graph window
pygame.init()
plt.ion()

# -------- Global Constants --------

# set record for highest score for each generation
record = 0

# set lists to hold scores and mean scores
# 0s are to keep data points in correct generation on graph
scores = [0]
mean_scores = [0]

# set screen size
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100

# make screen
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# make list of pictures of dinosaur running
RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
# make list of pictures of dinosaur jumping
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
# make list of pictures of dinosaur ducking
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

# make list of pictures of the small cacti
SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
# make list of pictures of the large cacti
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]
# make list of pictures of the bird
BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

# load image for background clouds
CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))

# load image for background "track"
BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

# set the font
FONT = pygame.font.Font('freesansbold.ttf', 20)

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))

# create class for the dinosaur
class Dinosaur:
    # set the position of the dino on screen
    X_POS = 80
    Y_POS = 310
    # set the position of the dino on screen when it ducks
    Y_POS_DUCK = 340
    # set the jump velocity for when the dino jumps
    JUMP_VEL = 8.5

    def __init__(self, img=RUNNING[0]):
        # specify the image of the dino
        self.image = img
        # set the default score for each dino
        self.score = 0
        # set the default dino to running
        self.dino_run = True
        # specify that the dino is not jumping
        self.dino_jump = False
        # specify that the dino is not ducking
        self.dino_duck = False
        # set the dino's jump velocity
        self.jump_vel = self.JUMP_VEL
        # create the rectangle for the dino
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, img.get_width(), img.get_height())
        # randomly generate 3 rgb values for the colored box around the dino
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        # set the original step index (aka how long it is running for)
        self.step_index = 0

    # method to update the state of the dino and current picture
    def update(self):
        # if run is selected, make the dino run
        if self.dino_run:
            self.run()
        # if jump is selected, make the dino jump
        if self.dino_jump:
            self.jump()
        # if duck is selected, make the dino duck
        if self.dino_duck:
            self.duck()
        # reset the step index to show correct animation
        if self.step_index >= 10:
            self.step_index = 0

    # method to make the dino jump
    def jump(self):
        # specify that the current image is the jumping dino
        self.image = JUMPING
        if self.dino_jump:
            # change the dino's y value so it moves upwards
            self.rect.y -= self.jump_vel * 4
            # change the jump velocity so the dino will eventually stop moving
            self.jump_vel -= 0.8
        # if the dino has reached the ground again
        if self.jump_vel <= -self.JUMP_VEL:
            # specify that the dino is running again, and not jumping
            self.dino_jump = False
            self.dino_run = True
            # reset the jump velocity
            self.jump_vel = self.JUMP_VEL

    # method to make the dino run
    def run(self):
        # set the image to the correct image from potential running images
        # because the dino is animated, images must change
        # basically after x amount of time, step index // 5 will change and a different image will show up
        self.image = RUNNING[self.step_index // 5]
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS
        self.step_index += 1

    def duck(self):
        self.image = DUCKING[self.step_index // 5]
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS_DUCK
        self.step_index += 1

    # method to draw the dino
    def draw(self, SCREEN):
        # put the dino image on screen at specified location
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))
        # draw a colored rectangle around the dino
        pygame.draw.rect(SCREEN, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)
        # for every obstacle on screen
        for obstacle in obstacles:
            # draw a line between the dino and that obstacle to show it's sight path
            # offsets in line position are to make line start from eye of dino
            pygame.draw.line(SCREEN, self.color, (self.rect.x + 54, self.rect.y + 12), obstacle.rect.center, 2)


# umbrella class for every obstacle
class Obstacle:
    def __init__(self, image, number_of_cacti):
        # set the image for the obstacle
        self.image = image
        self.type = number_of_cacti
        # get the rectangle around the obstacle
        self.rect = self.image[self.type].get_rect()
        # set the starting x position of the obstacle just off the right side of the screen
        self.rect.x = SCREEN_WIDTH

    # method to update the position of the obstacle
    def update(self):
        # move the obstacle left according to the game speed
        self.rect.x -= game_speed
        # if the obstacle is off the left side of the screen
        if self.rect.x < -self.rect.width:
            # remove that obstacle from the list of obstacles (aka delete it)
            obstacles.pop()

    # method to draw the obstacle onto the screen
    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)

# class for the small cacti
class SmallCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        # set the rectangle size
        self.rect.y = 325


# class for the small cacti
class LargeCactus(Obstacle):
    def __init__(self, image, number_of_cacti):
        super().__init__(image, number_of_cacti)
        # set the rectangle size
        self.rect.y = 300


class Bird:

    def __init__(self):
        # get the rectangle around the obstacle
        self.rect = BIRD[0].get_rect()
        # set the starting x position of the obstacle just off the right side of the screen
        self.rect.x = SCREEN_WIDTH
        # set the rectangle position
        self.rect.y = 250
        # set index for animation
        self.index = 0

    # method to update the position of the obstacle
    def update(self):
        # move the obstacle left according to the game speed
        self.rect.x -= game_speed
        # if the obstacle is off the left side of the screen
        if self.rect.x < -self.rect.width:
            # remove that obstacle from the list of obstacles (aka delete it)
            obstacles.pop()

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(BIRD[self.index // 5], self.rect)
        self.index += 1


# function to remove a dinosaur from existence if that dino dies
def remove(index):
    # remove it from the list of dinos
    dinosaurs.pop(index)
    # remove its genomes
    ge.pop(index)
    # remove its neural network
    nets.pop(index)


# function to get the distance between the dinosaur and the obstacle
def distance(pos_a, pos_b):
    dx = pos_a[0]-pos_b[0]
    dy = pos_a[1]-pos_b[1]
    return math.sqrt(dx**2+dy**2)


# main loop for game
def eval_genomes(genomes, config):
    global game_speed, x_pos_bg, y_pos_bg, obstacles, dinosaurs, ge, nets, points, scores, mean_scores
    # set the clock and starting score
    clock = pygame.time.Clock()
    points = 0

    # create instance of cloud class
    cloud = Cloud()

    # set the list of obstacles and dinosaurs
    obstacles = []
    dinosaurs = []

    # lists to hold the genome and neural network for each dinosaur
    ge = []
    nets = []

    # set the position for the background
    x_pos_bg = 0
    y_pos_bg = 380

    # set the starting game speed
    game_speed = 40

    # for each item in dictionary of genomes
    for genome_id, genome in genomes:
        # create a dinosaur object
        dinosaurs.append(Dinosaur())
        # append the genome to list of genomes
        ge.append(genome)
        # create a neural network for that dinosaur
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        # append that neural network to list of neural networks
        nets.append(net)
        # set the fitness of that genome
        genome.fitness = 0

    # function to get the current score
    def score():
        global points, game_speed, record
        # first add one to score
        points += 1
        for dino in dinosaurs:
            dino.score += 1
        # if we get to 100 points
        if points % 100 == 0:
            # increase game speed
            game_speed += 1
        # show the font on screen
        text = FONT.render(f'Points:  {str(points)}', True, (0, 0, 0))
        SCREEN.blit(text, (950, 50))
        # if this is a new record, update the record
        if points > record:
            record = points

    # method to show general stats on the screen
    def statistics():
        global dinosaurs, game_speed, ge, record
        # create text for dinos alive, generation, game speed, and current record
        text_1 = FONT.render(f'Dinosaurs Alive:  {str(len(dinosaurs))}', True, (0, 0, 0))
        text_2 = FONT.render(f'Generation:  {pop.generation+1}', True, (0, 0, 0))
        text_3 = FONT.render(f'Game Speed:  {str(game_speed)}', True, (0, 0, 0))
        text_4 = FONT.render(f'Record:  {str(record)}', True, (0, 0, 0))

        # put that text on the screen at the correct position
        SCREEN.blit(text_1, (50, 450))
        SCREEN.blit(text_2, (50, 480))
        SCREEN.blit(text_3, (50, 510))
        SCREEN.blit(text_4, (50, 540))

    # function to create the background
    def background():
        global x_pos_bg, y_pos_bg
        # get the width of the background image
        image_width = BG.get_width()
        # put the image on the screen
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        # put the image on again except just off the right side of screen
        # basically make an image that is twice the original image
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        # if the image has fully gone across the screen, put the image behind the other image
        # now we have a never ending loop
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        # move the image left according to the game speed
        x_pos_bg -= game_speed

    # function to plot the data on a graph to track AI performance overt time
    def plot(scores, mean_scores):
        # clear the screen
        display.clear_output(wait=True)
        display.display(plt.gcf())
        plt.clf()
        # set the title and axis labels
        plt.title('Training...')
        plt.xlabel('Generation')
        plt.ylabel('Max Score')
        # plot the scores and mean scores for each generation
        plt.plot(scores)
        plt.plot(mean_scores)
        # set the y limit of the graph
        plt.ylim(ymin=0)
        # create labels at the end of the line
        plt.text(len(scores) - 1, scores[-1], str(scores[-1]))
        plt.text(len(mean_scores) - 1, mean_scores[-1], str(mean_scores[-1]))
        # show the graph
        plt.show(block=False)
        plt.pause(.1)

    run = True
    # main loop for the game
    while run:
        # for every event that happens
        for event in pygame.event.get():
            # if it is the user hitting the "x" button
            if event.type == pygame.QUIT:
                # quit the game and stop the function
                pygame.quit()
                sys.exit()

        # fill the entire screen white
        SCREEN.fill((255, 255, 255))

        # for every dinosaur that exists update it's current state and draw them on screen
        for dinosaur in dinosaurs:
            dinosaur.update()
            dinosaur.draw(SCREEN)

        # if no dinosaurs are left in this generation, stop the loop to begin a new generation
        if len(dinosaurs) == 0:
            break

        # if no obstacles currently exist
        if len(obstacles) == 0:
            # randomly select a small or large cactus
            rand_int = random.randint(0, 2)
            if rand_int == 0:
                # append a small cactus object to the list of obstacles
                obstacles.append(SmallCactus(SMALL_CACTUS, random.randint(0, 2)))
            elif rand_int == 1:
                # append a large cactus object to the list of obstacles
                obstacles.append(LargeCactus(LARGE_CACTUS, random.randint(0, 2)))
            elif rand_int == 2:
                # append a large cactus object to the list of obstacles
                obstacles.append(Bird())


        # for each obstacle
        for obstacle in obstacles:
            # draw each obstacle
            obstacle.draw(SCREEN)
            # move the obstacle
            obstacle.update()
            for i, dinosaur in enumerate(dinosaurs):
                # if a dinosaur collides with an obstacle
                if dinosaur.rect.colliderect(obstacle.rect):
                    # decrease that dinosaur's fitness
                    ge[i].fitness -= 1
                    # if it is the last dino
                    if len(dinosaurs) == 1:
                        # append its score to list of top scores in each generation
                        scores.append(dinosaur.score)
                        # calculate a new mean score after the last generation
                        mean_scores.append(sum(scores) / (len(scores)))
                        # remove that dinosaur
                        remove(i)
                        # plot the graph to show new data
                        plot(scores, mean_scores)
                    # this wasn't the last dinosaur, nothing special needs to happen
                    else:
                        # remove that dino
                        remove(i)

        for i, dinosaur in enumerate(dinosaurs):
            # generate an output (aka movement for the dino)
            outputs = nets[i].activate((dinosaur.rect.y,
                                       distance((dinosaur.rect.x, dinosaur.rect.y),obstacle.rect.midtop),
                                        obstacle.rect.y))

            if outputs[0] > outputs[1]:
                if outputs[0] > 0.5 and dinosaur.rect.y == dinosaur.Y_POS:
                    # make the dino jump
                    dinosaur.dino_jump = True
                    dinosaur.dino_run = False
                    dinosaur.dino_duck = False
            elif outputs[1] > 0.5 and dinosaur.rect.y == dinosaur.Y_POS:
                # make the dino duck
                dinosaur.dino_jump = False
                dinosaur.dino_run = False
                dinosaur.dino_duck = True

        # call functions to get and show stats, get the score, and move the background
        statistics()
        score()
        cloud.draw(SCREEN)
        cloud.update()
        background()
        # update the clock
        clock.tick(30)
        # update the display
        pygame.display.update()


# Setup the NEAT Neural Network
def run(config_path):
    global pop
    # configure NEAT with default settings
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # create a population object
    pop = neat.Population(config)
    # run the fitness function to evaluate genomes based on the population,
    # fitness function is "eval genomes", specify that we want 100 generations max
    pop.run(eval_genomes, 100)


if __name__ == '__main__':
    # access the config.txt file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    # run the "run" function with the config.txt file
    run(config_path)



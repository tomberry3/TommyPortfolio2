# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)
# This code has again been hoisted by the CGS Digital Innovation Department
# giving credit to the above authors for the benfit of our education in ML

import math
import random
import sys
import os

import neat
import pygame

# Constants
# WIDTH = 1600
# HEIGHT = 880

WIDTH = 1920
HEIGHT = 1080

CAR_SIZE_X = 60
CAR_SIZE_Y = 60

BORDER_COLOR = (255, 255, 255, 255)  # Color To Crash on Hit

current_generation = 0  # Generation counter
"""
The Car Class 

Throughout this section, you will need to explore each function
and provide extenive comments in the spaces denoted by the 
triple quotes(block quotes) """ """.
Your comments should describe each function and what it is doing, 
why it is necessary and where it is being used in the rest of the program.

"""


class Car:
    """1. This Function:
    The sprite image is Loaded and resized, while also setting its initial properties; speed, position, and angle (sets speed and angle to 0).
    The center point of the car is determined according to its size and position, which will be used as a center point for the radars/sensors.
    A list of sensors/radars are initialised; 'radars', 'drawing_radars', which will be used later for collision detection.
    A boolean defines the car to be "alive", so the car is considered to be in a functioning condition.

    
    1 line summary: This code sets the cars basic properties and behaviors within the simulation
    """

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load("car.png").convert()  # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite

        # self.position = [690, 740] # Starting Position
        self.position = [830, 920]  # Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False  # Flag For Default Speed Later on

        self.center = [
            self.position[0] + CAR_SIZE_X / 2,
            self.position[1] + CAR_SIZE_Y / 2,
        ]  # Calculate Center

        self.radars = []  # List For Sensors / Radars
        self.drawing_radars = []  # Radars To Be Drawn

        self.alive = True  # Boolean To Check If Car is Crashed

        self.distance = 0  # Distance Driven
        self.time = 0  # Time Passed

    """ 2. This Function:
    The code defines a 'draw' method, to render the sprites on the screen.
    This is done by using the 'blit' method to place the car at the intended place on the screen.
    The method 'draw_radar' makes the radar lines visible on the screen, without it there would be no visible radar lines.


    1 line summary: The sprites are rendered and placed on the specified part of the screen
    """

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)  # Draw Sprite
        self.draw_radar(screen)  # OPTIONAL FOR SENSORS

    """ 3. This Function:
    Leading on from the optional line in function 2 'self.draw_radar(screen)', this code iterates through the the list of sensors called 'self.radars' 
    and draws green radar lines from the center position of the car to the sensors position, placing a green circle at the end of the radar as 
    a visual aid. The sensors help to give understanding on how the car interacts with and percieves its environment in the simulation.


    1 line summary: This code visualises the radars from the cars
    """

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    """ 4. This Function:
    The 'check_collision' function assesses whether the car has had a collision with a boundary on the game map.
    The cars 'alive' status is initially set to 'true', checking if any of the cars corners (as the car is represented as a box) 
    have had a collision with a boundary which is represented as 'BORDER_COLOR'.
    If a collision is detected then its 'alive' status is set to 'false', indicating a collision.


    1 line summary: This code checks for any car collisions with the boundary
    """

    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    """ 5. This Function:
    The code defines the "check_radar" method, which initiates the function of the radars for the car, this is
    done by taking the 3 parameters 'self', 'degree', and 'game_map'.
    The code iterates through a loop to extend the radar until it hits a border, without exceeding a length of 300.
    Finally after exiting the loop, the distance between the border and the center point of the car is calculated, and appended to the radars list. 
    This step is critical to the functionality of the sensors, by measuring distances within the simulated environment to boundaries.
    

    1 line summary: The code is essential for conveying the functionality of the sensors, while immitating how they detect obstacles within the simulation.
    """

    def check_radar(self, degree, game_map):
        length = 0
        x = int(
            self.center[0]
            + math.cos(math.radians(360 - (self.angle + degree))) * length
        )
        y = int(
            self.center[1]
            + math.sin(math.radians(360 - (self.angle + degree))) * length
        )

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length = length + 1
            x = int(
                self.center[0]
                + math.cos(math.radians(360 - (self.angle + degree))) * length
            )
            y = int(
                self.center[1]
                + math.sin(math.radians(360 - (self.angle + degree))) * length
            )

        # Calculate Distance To Border And Append To Radars List
        dist = int(
            math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2))
        )
        self.radars.append([(x, y), dist])

    """ 6. This Function:
    This code defines an 'update' method which updates the position and state of the sprite, including;
    -The cars speed is set to 20 if it has not already been set
    -The cars orientation is updated, by rotating the car based on its current angle
    -The code tracks distance and time driven
    -The cars center point and the location of the corners are calculated based on its position and angle, this step is essential to setting the location of the radars
    -collision with obstacles is checked, and the radar data is cleared


    1 line summary: The sprites position and state are updated in coordination with the current data gathered
    """

    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1

        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate New Center
        self.center = [
            int(self.position[0]) + CAR_SIZE_X / 2,
            int(self.position[1]) + CAR_SIZE_Y / 2,
        ]

        # Calculate Four Corners
        # Length Is Half The Side
        length = 0.5 * CAR_SIZE_X
        left_top = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length,
        ]
        right_top = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length,
        ]
        left_bottom = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length,
        ]
        right_bottom = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length,
        ]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    """ 7. This Function:
    This code defines a 'get_data' method, which is used only to get the data from the radars.
    First the data is collected from the 'self.radars' list, and assigns the list 'return_values' with 5 values, which are all set to 0,
    then the code loops through the radar data, scaling them down by a factor of 30 and allocates the value to the corresponding position 
    in the 'return_values' list
    The radar data is scaled down by a factor of 30 to make the values suitable to be used in the cars decision making system.
    

    1 line summary: This code gathers important data about the radars which is used for decision making within the self driving car simulation
    """

    def get_data(self):
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    """ 8. This Function:
    The code defines a method called 'is_alive' which holds responsibility for evaluating the cars status, and then returns the value of the 'self.alive' attribute.
    The 'self.alive' attribute tracks whether the car has had a collision.
    The 'self.avlive' attrivute was set to be 'true' earlier in the code, and there is a previous function that sets the value to 'false' if any collision has been detected

    
    1 line summary: This code provides a easily accessible way to determine if the car is still functional and 'alive'
    """

    def is_alive(self):
        # Basic Alive Function
        return self.alive

    """ 9. This Function:
    This code calculates a reward relative to the distance the car has traveled.
    The line '(CAR_SIZE_X / 2)' divides the value by 2 to ensure that a desired balance is achieved in the reward calculation by considering both distance traveled and car size.
    

    1 line summary: This code provides feedback on the cars performance, which can be used in reinforcement learning to encourage behaviors that maximise the reward given.
    """

    def get_reward(self):
        # Calculate Reward (Maybe Change?)
        # return self.distance / 50.0
        return self.distance / (CAR_SIZE_X / 2)

    """ 10. This Function:
    The 'rotate_center' method rotates the sprite image to match its current angle in the simulation by taking 3 parameters 'self', 'image' and 'angle,
    using the 'image' parameter which is the image to be rotated, and the 'angle' paramater which is the angle that the image should be rotated.
    The function first creates a rectangle to represent the images dimensions, then uses 'pygame.transform.rotate' to rotate the image to the desired angle.
    Then a new rectangle is created to extract the rotated image, this step is necessary to maintain visual consistency as the car is constantly moving and rotating, 
    and to create a more realistic simulation so the car is moving in the direction that the sprite is facing.
    

    1 line summary: This code is critical in the visual representation of the cars orientation as it moves within the simulation
    """

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image


""" This Function:
The 'run_simulation' function is completely responsible for running the simulation, assembling all of the following elements together;
-Initialises the necessary components of the simulaiton, eg; pygame, game map
-A Neural Network (using NEAT algorithms) is created for each genome passed, and the neural networks are assigned to the cars
-An 'exit on quit' loop is entered, which processes the actions of each car depending on the outputs from the neural networks
-The loop checks if the cars are still alive, and breaks the loop if they are not
-Finally the function updates the display to show the map, cars that are still alive, and other information


1 line summary: This function arranges the entire simulation, and is a key part in the simulations implementation and running
"""


def run_simulation(genomes, config):
    # Empty Collections For Nets and Cars
    nets = []
    cars = []

    # Initialize PyGame And The Display
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(Car())

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    game_map = pygame.image.load("map4.png").convert()  # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    while True:
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                car.angle += 10  # Left
            elif choice == 1:
                car.angle -= 10  # Right
            elif choice == 2:
                if car.speed - 2 >= 12:
                    car.speed -= 2  # Slow Down
            else:
                car.speed += 2  # Speed Up

        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40:  # Stop After About 20 Seconds
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # Display Info
        text = generation_font.render(
            "Generation: " + str(current_generation), True, (0, 0, 0)
        )
        text_rect = text.get_rect()
        text_rect.center = (900, 450)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900, 490)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)  # 60 FPS


""" 1. This Section: #main section that configs everything
The if statement serves as an entry point for running the NEAT algorithm, in order to evolve the neural networks.
The 'config.txt' file is loaded, which states the specific settings for the genetic algorithm (such as activation function, which I am using for my experiment).
Reporters are added to monitor the progress of the algorithm.
The simulation which is represented by the 'run_simulation' function, is executed for a maximum of 1000 generations.

1 line summary: This code initialises and runs a NEAT algorithm to evolve the neural networks, and executes the simulation
""" 
if __name__ == "__main__":
    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 1000)

import pygame
from pygame.locals import *
from dataclasses import dataclass
import math

config = {
    "fps": 60,
    "gravity_acceleration": 0.2, # acceleration in pixels / second^2
    "height": 1000,
    "width": 1600,
    "debug": False,
}


@dataclass
class Player:
    x: float
    y: float
    vy: float
    vx: float
    r: float
    omega: float
    phi: float   # the angle of rotation in radians
    collisionDirectionX: float  # collision direction provides direction of the collision force vector
    collisionDirectionY: float
    pixelMinDistance: float
    color: tuple = (70,70,70)
    accent_color: tuple = (0,128,255)
    friction: float = 1
    

@dataclass
class World:
    image: pygame.surface.Surface
    x: float = 0
    y: float = 0


def scalarProduct(ax, ay, bx, by):
    return ax*bx + ay*by;

def vectorProjection(ax, ay, bx, by):
    coef = scalarProduct(ax, ay, bx, by) / scalarProduct(bx, by, bx, by);
    return [coef * bx, coef * by];


def execute_tick():
    worldEdgeCheck()
    drawWorld()
    if (touch()):
        collide();
        rotate(player);
    move();
    drawPlayer(player);



"""checks the location of the player and moves the view
of the wold accordingly"""

def worldEdgeCheck():
    x_pad = 20
    y_pad = 100
    center_x = config['width']/2
    center_y = config['height']/2
    ##x-axis - follows constantly
    if(player.x > (center_x + x_pad)):
        world.x -= player.x - (center_x + x_pad);
        player.x = (center_x + x_pad);
    
    elif(player.x < (center_x - x_pad)):
        world.x -= player.x - (center_x - x_pad);
        player.x = (center_x - x_pad);
    
    ##--y-axis - moves at treshhold
    if(player.y > (center_y + y_pad)):
        world.y -= player.y - (center_y + y_pad);
        player.y = (center_y + y_pad);
    
    elif(player.y < (center_y-y_pad)):
        world.y -= player.y - (center_y-y_pad);
        player.y = (center_y-y_pad);
    
def drawWorld():
    # Drawing
    screen.fill((0, 0, 0))  # Fill the screen with black
    screen.blit(world.image, (world.x, world.y))


def touch():
    # Loop through the pixels around the player
    r = math.floor(player.r)
    x = math.floor(player.x)
    y = math.floor(player.y)
    pixelSumX = 0
    pixelSumY =  0
    pixelsHit = 0
    player.pixelMinDistance = player.r
    player.collisionDirectionX = 0
    player.collisionDirectionY = 0 
    for dx in range(-r, r+1):
        for dy in range(-r, r+1):
            pixel_x = x + dx
            pixel_y = y + dy
            pixelDistance = math.sqrt(dx**2 + dy**2) # pythagoras
            # color = world.image.get_at((pixel_x, pixel_y))

            # check pixel values from the screen itself
            screen_surface = pygame.display.get_surface()
            color = screen_surface.get_at((pixel_x, pixel_y))
            if (
                (color[0] < 15) and
                (color[1] < 15) and
                (color[2] < 15) and
                (pixelDistance <= player.r)
            ):
                pixelsHit += 1
                pixelSumX += dx
                pixelSumY += dy
                # we store the closes distance to a pixel as a metric
                # of how hard we have collided (how far into the terrain the player is)
                if pixelDistance < player.pixelMinDistance:
                    player.pixelMinDistance = pixelDistance

    
    if(pixelsHit != 0):
        # this is the kind of average "center" location of all the pixels we hit. 
        weightMedX = pixelSumX / pixelsHit;
        weightMedY = pixelSumY / pixelsHit;

        # The deeper into the player hitbox the hit pixel center is, the harder the collision
        weightMedDist = math.sqrt(weightMedX*weightMedX + weightMedY*weightMedY);
        # a unit vector to define the direction of the collision
        player.collisionDirectionX = weightMedX / weightMedDist;
        player.collisionDirectionY = weightMedY / weightMedDist;
        return True;
    else:
        return False;
    



def collide():
    #pop player onto surface
    player.x -= player.collisionDirectionX * (player.r - player.pixelMinDistance);
    player.y -= player.collisionDirectionY * (player.r - player.pixelMinDistance);

    # change velocity direction
    velocity_change = vectorProjection(player.vx, player.vy, player.collisionDirectionX, player.collisionDirectionY);
    player.vx -= (1.6 * velocity_change[0]);
    player.vy -= (1.6 * velocity_change[1]);


def rotate(player):
    
    # Get the state of all keys
    keys = pygame.key.get_pressed()

    friction = player.friction;
    if(keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
        speedMean = 0;
        scalar = player.vx*player.collisionDirectionY - player.vy*player.collisionDirectionX;
        scalar2 = player.vx*player.collisionDirectionX + player.vy*player.collisionDirectionY;

        player.vx = scalar2 * player.collisionDirectionX;
        player.vy = scalar2 * player.collisionDirectionY;

        speedMean = (scalar + player.r*player.omega)/2;
        player.vy += friction*speedMean * (-player.collisionDirectionX);
        player.vx += friction*speedMean * (player.collisionDirectionY);
        player.omega = friction*speedMean/player.r;
    
    else:
        scalar = player.vx*player.collisionDirectionY - player.vy*player.collisionDirectionX;
        player.omega = friction*scalar/player.r;
    pass


def move():
    # Get the state of all keys
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player.omega += (-1 - player.omega) * 0.1
    if keys[pygame.K_RIGHT]:
        player.omega += (1-player.omega) * 0.1

    # friction
    player.vy *= 0.99;
    player.vx *= 0.99;
    player.omega *= 0.95;

    # Gravity
    player.vy += config['gravity_acceleration']

    # Rotate and move
    player.phi += player.omega;
    player.x += player.vx;
    player.y += player.vy;


def drawPlayer(player: Player):
    # main body of the player
    pygame.draw.circle(screen, player.color, (player.x,player.y), player.r)

    # Accent dot to make the rotation of the player visible
    # we divide by 4 so the dot is 
    accent_xy = (
        player.x + math.cos(player.phi)*player.r*0.7,
        player.y + math.sin(player.phi)*player.r*0.7
    )
    pygame.draw.circle(screen, player.accent_color, accent_xy, player.r/5)

    if config['debug']:
        # draw the center of the player position
        pygame.draw.circle(screen, player.accent_color, (player.x, player.y), 2)

    if config['debug']:
        collsion_center_xy = (
            player.x + player.collisionDirectionX * player.pixelMinDistance,
            player.y + player.collisionDirectionY * player.pixelMinDistance
        )
        pygame.draw.circle(screen, (255,128,0), collsion_center_xy, 2)




if __name__ == "__main__":


    # Initialize Pygame
    pygame.init()

    # Set up the game window
    screen = pygame.display.set_mode((config['width'], config['height']))
    pygame.display.set_caption('2D Side Roller')

    # Set up the game clock
    clock = pygame.time.Clock()


    world = World(
        x=400, 
        y=-100,
        image = pygame.image.load('map3.png').convert()
    )

 
    player = Player(
        x = config['width']/2, 
        y = config['height']/2, 
        vy = 0,
        vx = 0,
        r = 20,
        omega =0,
        phi =0,
        friction = 1,
        collisionDirectionX = 1,
        collisionDirectionY = 1,
        pixelMinDistance = 20 # whould be <= player.r
    );

    # Game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False


        # player.x += 1   
        print(player)


        # (draw your game objects here)
        execute_tick()

        pygame.display.flip()  # Update the display

        # Cap the frame rate
        clock.tick(config['fps'])

    # Clean up
    pygame.quit()
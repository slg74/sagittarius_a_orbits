import math
import pygame

WIDTH, HEIGHT = 800, 800
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(
    "Stars orbiting the Galactic Central Black Hole, Sagittarius A*"
)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

class StellarObject:

    # Constants
    AU = 149597870700  # 1 Astronomical Unit = 149,597,870,700 meters
    G = 6.67408e-11  # Gravitational constant, hopefully the same most everywhere.
    SCALE = 2 / AU  # 1 AU = 100 pixels
    #TIMESTEP = 3600 * 24 * 365 * 10  # Timestep is number of seconds in 10 years.
    TIMESTEP = 3600 * 6
    #TIMESTEP = 3600

    def __init__(self, x, y, radius, color, mass):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass

        # sgrA* central black hole is at (0, 0)
        self.orbit = []
        self.sagittarius_a = False
        self.distance_to_sagittarius_a = 0

        self.x_velocity = 0
        self.y_velocity = 0

    def draw(self, window):
        print(self.SCALE)
        print(WIDTH)

        x = self.x * self.SCALE + WIDTH // 2
        y = self.y * self.SCALE + HEIGHT // 2

        pygame.draw.circle(window, self.color, (x, y), self.radius)

    def attraction(self, other_stellar_object):
        distance_x = other_stellar_object.x - self.x
        distance_y = other_stellar_object.y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)

        if other_stellar_object.sagittarius_a:
            self.distance_to_sagittarius_a = distance

        gravitational_force = (
            self.G * self.mass * other_stellar_object.mass / (distance**2)
        )
        theta = math.atan2(distance_y, distance_x)
        x_force = gravitational_force * math.cos(theta)
        y_force = gravitational_force * math.sin(theta)

        return x_force, y_force

    def update_position(self, stellar_objects):
        total_x_force = total_y_force = 0

        for stellar_object in stellar_objects:
            if stellar_object != self:
                x_force, y_force = self.attraction(stellar_object)
                total_x_force += x_force
                total_y_force += y_force

        # F = ma; a = F/m
        self.x_velocity += total_x_force / self.mass * self.TIMESTEP
        self.y_velocity += total_y_force / self.mass * self.TIMESTEP

        self.x += self.x_velocity * self.TIMESTEP
        self.y += self.y_velocity * self.TIMESTEP

        self.orbit.append((self.x, self.y))
        print(self.orbit)


def main():

    AU = 149597870700  # 1 Astronomical Unit = 149,597,870,700 meters
    SOLAR_MASS = 1.989 * 10 ** 30  # Solar mass in kg
    SAGITTARIUS_A_MASS = (
        4 * 10**6 * 5 * SOLAR_MASS
    )  # Sagittarius A* mass is 4 million solar masses.

    sagittarius_a = StellarObject(0, 0, 1, GREEN, SAGITTARIUS_A_MASS)
    sagittarius_a.sagittarius_a = True

    # stars orbiting Sagittarius A*
    S2 = StellarObject(-100 * AU, 10, 5, WHITE, 12.5 * SOLAR_MASS)
    S8 = StellarObject(125 * AU, 10,5, WHITE, 15 * SOLAR_MASS)
    S12 = StellarObject(-130 * AU, 10, 5, WHITE, 15 * SOLAR_MASS)
    S13 = StellarObject(150 * AU, 10, 5, WHITE, 15 * SOLAR_MASS)

    S2.y_velocity = 7005.3 * 1000
    S8.y_velocity = -8000 * 1000
    S12.y_velocity = 6000 * 1000
    S13.y_velocity = -5000.13 * 1000

    stars = [sagittarius_a, S2, S8, S12, S13]

    run = True
    clock = pygame.time.Clock()

    while run:

        clock.tick(60)
        WINDOW.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for star in stars:
            star.update_position(stars)
            star.draw(WINDOW)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()

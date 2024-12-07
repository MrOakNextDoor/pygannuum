# Libraries
from abc import ABC, abstractmethod
from random import randint
from typing import List, Tuple

from pygame import math as pmath, Rect, Surface, sprite, transform # To distinguish it from ye olde math

# TODO:
# Particle:
# - Support multiple textures.
# StackRenderer:
# - Implement spritestacking.
# ParticleSystem:
# - Support multiple particles.
# Miscellaneous stuff:
# - Move to an actual logger.

# Code
class GameObject(sprite.Sprite):
    """GameObjects for Pygannuum.

    Args:
        texture (pygame.Surface): Texture of the GameObject. Defaults to 
        DEFAULT_TEXTURE.
        position (pygame.math.Vector2 | Tuple[float, float]): Position of the 
        GameObject. Defaults to (0, 0).
        scale (pygame.math.Vector2 | Tuple[float, float]): Scale of the 
        GameObject in pixels. Defaults to (10, 10).
        rotation (float): Rotation of the GameObject. Defaults to 0.0.
        renderer (GORenderer | None): How the GameObject is drawn. Defaults to 
        BasicRenderer.
        updater (GOUpdater | None): How the GameObject is updated. Defaults to 
        None.
    """

    def __init__(self, texture: Surface, 
        position: pmath.Vector2 | Tuple[float, float]=(0.0, 0.0), 
        scale:pmath.Vector2 | Tuple[float, float]=(10, 10), rotation: float=0.0, 
        renderer: "GORenderer"=None, updater: "GOUpdater"=None):
        sprite.Sprite.__init__(self)

        self.image = texture
        self.position = position
        self.scale = scale
        self.rotation = rotation

        self.renderer = renderer
        self.updater = updater
        # By default, hitboxes are rects. Good for performance, bad for pixel accuracy.
        self.rect = self.renderer.hitbox(self)

    @property
    def position(self) -> pmath.Vector2:
        return self._position
    
    @property
    def scale(self) -> pmath.Vector2:
        return self._scale

    @property
    def rotation(self) -> float:
        return self._rotation

    @property
    def renderer(self) -> "GORenderer":
        return self._renderer

    @position.setter
    def position(self, p: pmath.Vector2 | Tuple[float, float]):
        self._position = pmath.Vector2(p)   # Just make sure everything is converted.

    @scale.setter
    def scale(self, s: pmath.Vector2 | Tuple[float, float]):
        self._scale = pmath.Vector2(s)

    @rotation.setter
    def rotation(self, r: float):
        self._rotation = r % 360

    @renderer.setter
    def renderer(self, r: "GORenderer"):
        # Ensure that the GameObject always has a renderer present.
        self._renderer = DEFAULT_RENDERER if r is None else r

    def update(self, dt: float):
        """Updates the state of the GameObject. 

        Args:
            dt (float): Delta-time. Allows for framerate independence.
        """
        try:
            self.updater(dt)
        except TypeError:
            pass

    def draw(self, surface: Surface, area=None, special_flags=0):
        """Draws the texture onto a surface."""

        self.renderer(self, surface, area=None, special_flags=0)

class GORenderer(ABC):
    """Base class for GameObject renderers. GameObjects are drawn with their
    centres on their position."""

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __call__(self, gameobject: GameObject, surface: Surface, area=None, 
        special_flags=0):
        pass

    @abstractmethod
    def hitbox(self, gameobject: GameObject):
        """Returns the hitbox of the GameObject based on its texture."""
        pass

class BasicRenderer(GORenderer):
    """Basic renderer for GameObjects."""
    
    def __init__(self):
        pass

    def __call__(self, gameobject: GameObject, surface: Surface, area=None, 
        special_flags=0):
        """Draw the GameObject.

        Args:
            gameobject (GameObject): The GameObject to draw.
            surface (pygame.Surface): Surface the GameObject is drawn on.
            area: Same as pygame.Surface.blit(). Defaults to None.
            special_flags: Same as pygame.Surface.blit(). Defaults to 0.
        """
        
        # Scale the GameObject texture and rotate it around its position.
        texture = transform.rotate(transform.scale(gameobject.image, 
            (round(gameobject.scale.x), round(gameobject.scale.y))), 
            gameobject.rotation)
        
        # Check if the GameObject is within the display. If not, don't draw. 
        if not surface.get_rect().colliderect(texture.get_rect(
            center=tuple(gameobject.position))):
            return

        # Blit the GameObject around its centre.
        surface.blit(
            texture,
            (
                round(gameobject.position.x) - texture.get_width()//2,
                round(gameobject.position.y) - texture.get_height()//2
            ),
            area=area,
            special_flags=special_flags)

    def hitbox(self, gameobject: GameObject) -> Rect:
        return transform.rotate(transform.scale(gameobject.image, 
            (round(gameobject.scale.x), round(gameobject.scale.y))), 
            gameobject.rotation).get_rect(center=tuple(gameobject.position))

class StackRenderer(GORenderer):
    """Spritestack renderer for GameObjects. Stacks multiple Surfaces to create 
    the illusion of a 3D GameObject."""
    def __init__(self, spread: int=1):
        
        self.spread = spread    # Determines how far apart the Surface are rendered.

    def __call__(self, gameobject: GameObject, surface: Surface, area=None, special_flags=0):
        """Draw the GameObject.

        Args:
            gameobject (GameObject): The GameObject to draw.
            surface (pygame.Surface): Surface the GameObject is drawn on.
            area=None: Same as pygame.Surface.blit().
            special_flags=0: Same as pygame.Surface.blit().
        """

        raise NotImplementedError('Spritestacking not yet implemented. Come back later.')

    def hitbox(self, gameobject: GameObject):
        raise NotImplementedError('Spritestacking not yet implemented. Come back later.')

class GOUpdater(ABC):
    """Base class for GameObject updaters. Useful especially when GameObjects 
    need to move on their own (e.g. Particles)."""
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __call__(self, dt: float):
        """Updates the state of the GameObject.

        Args:
            dt (float): Delta-time. Allows for framerate independence.
        """
        pass

class BasicParticleUpdater(GOUpdater):
    """Basic particle motion.

    Args:
        particle (Particle | None): Particle to be updated.
        velocity (pygame.math.Vector2 | Tuple[float, float]): Velocity of the 
        particle. Defaults to (0.0, 0.0).
        accel (pygame.math.Vector2 | Tuple[float, float]): Acceleration of the 
        particle. Defaults to (0.0, 0.0).
    """
    def __init__(self, particle: "Particle"=None, 
        velocity: pmath.Vector2 | Tuple[float, float]=(0.0, 0.0),
        accel: pmath.Vector2 | Tuple[float, float]=(0.0, 0.0)):
        
        self.particle = particle
        self.velocity = velocity
        self.accel = accel

    @property
    def velocity(self) -> pmath.Vector2 :
        return self._velocity

    @property
    def accel(self) -> pmath.Vector2 :
        return self._accel

    @velocity.setter
    def velocity(self, p: pmath.Vector2 | Tuple[float, float]):
        self._velocity = pmath.Vector2(p)   # Just make sure everything is converted.

    @accel.setter
    def accel(self, p: pmath.Vector2 | Tuple[float, float]):
        self._accel = pmath.Vector2(p)   # Just make sure everything is converted.

    def __call__(self, dt: float):

        self.particle.position += self.velocity * dt
        self.velocity += self.accel * dt

class Particle(GameObject):
    """Basic particles for Pygannuum.

    Args:
        texture (pygame.Surface): Texture of the particle. Defaults to 
        DEFAULT_TEXTURE.
        position (pygame.math.Vector2): Position of the particle. Defaults to 
        (0, 0).
        scale (pygame.math.Vector2): Scale of the particle in pixels. Defaults 
        to (10, 10).
        rotation (float): Rotation of the particle. Defaults to 0.0.
        renderer (GORenderer | None): How the particle is drawn. Defaults to 
        BasicRenderer.
        updater (GOUpdater | None): How the particle is updated. Defaults to 
        BasicParticleMotion.
        lifespan (float): Lifespan of the particle in seconds. If set to a 
        negative value, the particle will be immortal. Defaults to 10.0.
    """

    def __init__(self, texture: Surface, 
        position: pmath.Vector2 | Tuple[float, float]=(0.0, 0.0), 
        scale:pmath.Vector2 | Tuple[float, float]=(10, 10), rotation: float=0.0, 
        renderer: GORenderer=None, updater=None, lifespan: float=10.0):
        super().__init__(texture, position, scale, rotation, renderer, updater)

        self.updater = updater
        self.lifespan = lifespan
    
    @property
    def updater(self) -> GOUpdater:
        return self._updater
    
    @updater.setter
    def updater(self, u: GOUpdater):
        # Ensures that the Particle always has an updater present.
        # Particles need updaters because without them, why tf would you have a particle??
        self._updater = DEFAULT_PARTICLE_MOTION if u is None else u
        self._updater.particle = self

    def update(self, dt: float, base_fps: int=60):
        """Update the particle's state.

        Args:
            dt (float): Delta-time. Allows for framerate independence.
            base_fps (int, optional): Base framerate of the game. Defaults to 60.
        """
        # Values, let l be lifespan: l>0: alive; l==0: dead; l<0: immortal.
        if self.lifespan > 0: # If the particle is alive...
            super().update(dt) # update it...
            self.lifespan -= dt/base_fps # then update its lifespan...
            if self.lifespan <= 0: # If the lifespan falls below zero after the update (since delta-time isn't a constant 1 or smth).
                self.kill() # remove particle from (all) ParticleSystems...
                self.lifespan = 0.0 # then ensure that the particle stays dead.
        elif self.lifespan == 0:
            return
        else: # If the particle is immortal, just keep updating it.
            super().update(dt)

    def draw(self, surface: Surface, area=None, special_flags=0):
        if self.lifespan == 0: # Do not draw if particle is dead.
            return
        super().draw(surface, area, special_flags)

class ParticleSystem(sprite.Group):
    def __init__(self, particle: Particle=None):
        super().__init__()

        self.particle = particle

    @property
    def particle(self) -> Particle:
        return self._particle
    
    @particle.setter
    def particle(self, p: Particle):
        self._particle = DEFAULT_PARTICLE if p is None else p

    def spawn_particle(self, rate: int=10):
        pass

    def update(self, dt: float, base_fps: int=60):
        for particle in self:
            particle.update(dt, base_fps)

    def draw(self, surface: Surface, area=None, special_flags=0):
        for particle in self:
            particle.draw(surface, area, special_flags)

# More defaults...
DEFAULT_PARTICLE = 0 # Add textures immediately !
DEFAULT_PARTICLE_MOTION = BasicParticleUpdater()
DEFAULT_RENDERER = BasicRenderer()

# Testing stuff
if __name__ == '__main__':
    pass

else:
    print(f'Imported {__name__}.')

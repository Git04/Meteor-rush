#Meteor Rush

import sys, pygame, random
from itertools  import repeat


#TODO: forbid asteroids to spawn on top  of the player
#TODO: use sreen size parameter instead of the plain numbers
SCREEN_SIZE = (800,600)


class Asteroid:
	#Initialize common values for asteroid object
	#surface - to be able to rotate objects 
	#rect - for collision
	#pygame vector class instance for movement
	def __init__(self, rect_center = None):
		self.surface = pygame.Surface((26,26))
		self.surface.set_colorkey(0,0)
		self.asteroid = pygame.draw.polygon(self.surface, (255,255,255), 
			((13,0), (random.randint(1,12),random.randint(1,12)),
			(0,13),(random.randint(1,12),random.randint(12,24)),
			(13,25),(random.randint(12,24),random.randint(12,24)),
			(25,13), (random.randint(12,24),random.randint(1,12))),
			 1)
		self.org_surface = self.surface.copy()
		self.angle = 0
		self.velocity = pygame.Vector2(random.uniform(-0.4,0.4),random.uniform(-0.4,0.4))
		if rect_center == None: self.rect = self.surface.get_rect(center = (random.randint(50,750),random.randint(50,550)))
		else: self.rect = self.surface.get_rect(center = rect_center)
		self.pos = pygame.Vector2(self.rect.center)

	#Update: rotate and make sure to keep asteroids inside the window
	def update(self):
		self.pos += self.velocity
		self.rect.center = self.pos
		
		if self.rect.left > 800: self.pos.x = 0
		elif self.rect.right < 0: self.pos.x = 800
		elif self.rect.top > 600: self.pos.y = 0
		elif self.rect.bottom < 0: self.pos.y = 600

		self.angle += random.randint(0,1)
		self.surface = pygame.transform.rotate(self.org_surface, self.angle)
		self.rect = self.surface.get_rect(center=self.rect.center)


class Debries:
	#Same as the asteroid class but init metho of this class also takes two arguments as it follows shot asteroids
	#TODO Inheritance is better choice?
	def __init__(self, debry_pos, direction):
		self.surface = pygame.Surface((6,6))
		self.rect = self.surface.get_rect(center = debry_pos)
		self.debry = pygame.draw.circle(self.surface, (255,255,255), (3,3), 4, 1)
		self.debry_pos = self.rect.center
		self.direction = pygame.Vector2(direction)

	def update(self):
		self.debry_pos += self.direction * 5
		self.rect.center = self.debry_pos

#Player class, similar to every other class, but keeps track of player specific values: ammo, health, acceleration(misspeled in code, sorry)
#Direction used to pass it to projectile instance
class Player:
	def __init__(self):
		self.surface = pygame.Surface((21,21))
		self.surface.set_colorkey(0,0)
		self.player = pygame.draw.polygon(self.surface, (255,255,255), ((10,0),(20,20),(0,20)), 1)
		self.org_surface = self.surface.copy()
		self.angle = 0
		self.accelaration = pygame.math.Vector2(0,-0.1)
		self.velocity = pygame.math.Vector2(0,-0.2)
		self.direction = pygame.Vector2(0,-1)
		self.rect = self.surface.get_rect(center = (400,300))
		self.pos = pygame.Vector2(self.rect.center)
		self.ammo = 15
		self.health = 10
		self.score = 0

	#Keep player inside the window
	def update(self):
		if self.rect.left > 800: self.pos.x = 0
		elif self.rect.right < 0: self.pos.x = 800
		elif self.rect.top > 600: self.pos.y = 0
		elif self.rect.bottom < 0: self.pos.y = 600

#Same, uses direction of the player instance
class Projectile:
	def __init__(self, pos, direction):
		self.surface = pygame.Surface((8,8))
		#self.surface.set_colorkey(0,0)
		self.projectile = pygame.draw.circle(self.surface, (255,255,255), (4,4), 4, 1)
		self.rect = self.surface.get_rect(center = pos)
		self.direction = direction
		self.pos = pygame.Vector2(self.rect.center)
	#Moves it
	def update(self):
		self.pos += self.direction * 6
		self.rect.center = self.pos


class Pickups:
	def __init__(self):
		self.surface = pygame.Surface((24,24),pygame.SRCALPHA)
		self.image = pygame.image.load('ammo.png')
		self.image.set_colorkey(1,1)
		self.pickup = pygame.draw.rect(self.surface, (255,255,255), (0,0,17,17))
		self.rect = self.image.get_rect(center = (random.randint(100,700),random.randint(100,500)))
		self.type = 'ammo'
		#self.cooldown = 200

#Main game class
#Making a copy of a screen to blit it under the main one for shake effect
#Otherwise, initializing general stuff, making lists of game objects (should'v used groups: TODO)
class Game:
	def __init__(self):
		pygame.init()
		self.org_screen = pygame.display.set_mode(SCREEN_SIZE)
		self.screen = self.org_screen.copy()
		self.screen_rect = self.screen.get_rect()
		self.offset = repeat((0,0))
		#self.screen.fill((0,0,0))
		self.clock = pygame.time.Clock()
		#Initialize game objects
		self.player = Player()
		self.asteroids = []
		self.projectiles = []
		self.pickups = []
		self.debries = []
		for i in range(20):
			self.asteroids.append(Asteroid())
		#Initialize font and text
		self.font = pygame.font.Font('freesansbold.ttf', 16)

		self.spawn_locations = ['top','bottom','left','right']

#Shakes the screen, thanks to KidsCanCode for the example
#Method is the same, using generators to blit copy of the screen by the offset value
	def screen_shake(self):
		s = -1
		#Number of shakes
		for number in range(0, 3):
			#Intensity
			for x in range(0, 20, 5):
				yield (x*s, 0)
			for x in range(20, 0, 5):
				yield (x*s, 0)
			s *= -1
		while True: yield (0, 0)

	def event_handling(self):
		#A and D for turning
		#W for adding accelaration in rect direction
		pressed = pygame.key.get_pressed()
		if pressed[pygame.K_a]: self.player.angle += 4
		if pressed[pygame.K_d]: self.player.angle -= 4
		if pressed[pygame.K_w]: 
			self.player.velocity += self.player.accelaration
		#Keeping player under top speed
		if self.player.velocity.length() > 3.5: self.player.velocity.scale_to_length(3.5)
		#updating direction for projectile, heading for accelaration, probably more logical to put it in player update method?
		self.player.direction = pygame.Vector2(0, -1).rotate(-self.player.angle)
		self.player.accelaration = pygame.Vector2(0,-0.1).rotate(-self.player.angle)
		self.player.pos += self.player.velocity
		self.player.rect.center = self.player.pos

		self.player.surface = pygame.transform.rotate(self.player.org_surface, self.player.angle)
		self.player.rect = self.player.surface.get_rect(center=self.player.rect.center)
			#SPACEBAR to shoot a projectile
		for event in pygame.event.get():
			if event.type == pygame.QUIT: pygame.quit(), sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					if self.player.ammo > 0:
						self.projectiles.append(Projectile(pos = self.player.rect.center, direction = self.player.direction.normalize()))
						self.player.ammo -= 1
	#Mostly collisions and different update methods of other classes 
	def update(self):
		self.player.update()
		for projectile in self.projectiles:
			projectile.update()
			if not pygame.display.get_surface().get_rect().contains(projectile.rect): self.projectiles.remove(projectile)
		for asteroid in self.asteroids:
			asteroid.update()
			if self.player.rect.colliderect(asteroid.rect):
				self.asteroids.remove(asteroid)
				self.player.health -= 1
				self.offset = self.screen_shake()
		for pickup in self.pickups:
			if pickup.rect.colliderect(self.player.rect):
				self.player.ammo += 5
				self.pickups.remove(pickup)
		for debry in self.debries:
			debry.update()
			if not pygame.display.get_surface().get_rect().contains(debry.rect): self.debries.remove(debry)
	#Spawn new asteroids on the edges
	#TODO assign few of them vector pointing to the center
		if len(self.asteroids) < 20:
			spawn = random.choice(self.spawn_locations)
			if spawn == 'top': self.asteroids.append(Asteroid(rect_center = (random.randint(0,800),0)))
			elif spawn == 'bottom': self.asteroids.append(Asteroid(rect_center = (random.randint(0,800),600)))
			elif spawn == 'left': self.asteroids.append(Asteroid(rect_center = (0, random.randint(0,600))))
			else: self.asteroids.append(Asteroid(rect_center = (800, random.randint(0,600))))

		if len(self.pickups) < 1: self.pickups.append(Pickups())
	#Exception for the rare crash when projectile hits asteroid past the window edge, deleting it twice
		for p in self.projectiles:
			for a in self.asteroids:
				if p.rect.colliderect(a):
					try: self.projectiles.remove(p)
					except: print('avoided crash')
					for i in range(random.randint(4,6)): self.debries.append(Debries(debry_pos = a.rect.center, 
						direction = (random.uniform(-5,5),random.uniform(-5,5))))
					self.asteroids.remove(a)
					self.player.score += 10
	#TODO: write t in c -style
		self.text = self.font.render(('Health: ' + str(self.player.health) + ' Ammo: ' +  str(self.player.ammo) + ' Score: ' + str(self.player.score)), True, (255,255,255))
		self.text_rect = self.text.get_rect()

	def render(self):
		self.screen.fill((0,0,0))
		self.org_screen.fill((255,255,255))
		#blit sprites
		for pickup in self.pickups:
			self.screen.blit(pickup.image, pickup.rect)
		for p in self.projectiles:
			self.screen.blit(p.surface, p.rect)
		for asteroid in self.asteroids:
			self.screen.blit(asteroid.surface, asteroid.rect)
		for d in self.debries:
			self.screen.blit(d.surface, d.rect)
		self.screen.blit(self.player.surface, self.player.rect)
		#blit text
		self.screen.blit(self.text, self.text_rect)

		self.org_screen.blit(self.screen, next(self.offset))
		pygame.display.flip()

	def run(self):
		while True:
			if self.player.health > 0:
				self.update()
				self.render()
				self.event_handling()

				self.clock.tick(60)
			else:
				sys.exit()

game = Game()
game.run()

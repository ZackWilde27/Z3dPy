import z3dpy as zp
import pygame

# Variables
speed = 11
zp.screenSize = (1280, 720)
zp.gravity = [0, 4, 0]
zp.worldColour = (0.3, 0.3, 0.3)
delta = 0

# Initialize PyGame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()


# Setting FOV
# FindHowVars(fov, *aspectRatio)
#zp.FindHowVars(75)
zp.SetHowVars(0.7330638661047614, 1.3032245935576736)

print("")
print("Controls:")
print("WASD to move character")
print("Space to jump")
print("Up and Down arrow to move platform")

# Cam(vPos)
myCamera = zp.Cam([0, 0, -2])

# LoadMesh(filename, *vPos, *vScale)
smallCube = zp.LoadMesh("z3dpy/mesh/cube.obj", [0, 0, 0], [2.0, 0.5, 2.0])
cubeMesh = zp.LoadMesh("z3dpy/mesh/cube.obj", [0, 0, 0], [0.5, 0.5, 0.5])
planeMesh = zp.LoadMesh("z3dpy/mesh/plane.obj", VScale=[5, 5, 5])

planeMesh.SetColour([0, 100, 0])
smallCube.SetColour([255, 0, 0])

cubeMesh.material = smallCube.material = planeMesh.material = zp.MATERIAL_DYNAMIC

# Thing(meshList, vPos)
char = zp.Thing([cubeMesh], [0, 1, 3])

# Giving the character a hitbox and physics body
# Hitbox(type, id, radius, height)
char.hitbox = zp.Hitbox(zp.HITBOX_BOX, 0, 0.5, 0.5)
# Type determines the shape of the hitbox: 0 is sphere, 2 is cube
# Only things with the same id will collide
# Radius and height determine the size of hitbox
char.physics = zp.PhysicsBody()

bar = zp.Thing([smallCube], [0.5, 0, 3])
bar.hitbox = zp.Hitbox(zp.HITBOX_BOX, 0, 2, 0.5)
bar.visible = False


plane = zp.Thing([planeMesh], [0, 2, 0])

zp.AddThings([plane, char, bar])


# Light(type, vAngle, FStrength, unused, *vColour)
myLight = zp.Light(zp.LIGHT_SUN, (-45, 10, 0), 1, 0)
zp.lights.append(myLight)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    clock.tick(60)
    delta = zp.GetDelta()

    # Input
    keys = pygame.key.get_pressed()

    trueSpeed = speed * delta

    if keys[pygame.K_w]:
        char.position[2] += trueSpeed
    if keys[pygame.K_s]:
        char.position[2] -= trueSpeed
    if keys[pygame.K_a]:
        char.position[0] -= trueSpeed
    if keys[pygame.K_d]:
        char.position[0] += trueSpeed

    if keys[pygame.K_UP]:
        bar.position[1] += -8 * delta
    if keys[pygame.K_DOWN]:
        bar.position[1] += 8 * delta
        
    if keys[pygame.K_SPACE] and char.physics.velocity[1] >= -0.3:
        char.physics.velocity = [0, -13, 0]

    zp.HandlePhysicsFloor([char], 2)

    zp.PhysicsCollisions([char, bar])

    camLoc = zp.VectorSub(char.position, [0, 2, 5])
    
    # Camera will ease towards the desired location
    myCamera.Chase(camLoc, 5)
    
    myCamera.target = char.position
    zp.SetInternalCam(myCamera) 

    screen.fill("black")

    for tri in zp.Render():
        pygame.draw.polygon(screen, zp.TriGetColour(tri), zp.FormatTri(tri, False))

    for tri in zp.DebugRender():
        pygame.draw.lines(screen, zp.TriGetColour(tri), True, zp.FormatTri(tri, False))
        
    pygame.display.flip()

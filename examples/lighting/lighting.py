import z3dpy as zp
import pygame

print("")
print("Controls:")
print("Arrow Keys to move mesh around")
print("WASD to move camera")

# PyGame stuff
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Create the Camera
myCamera = zp.Cam(0, 0, 0, 1280, 720)

# Changing FOV
#zp.FindHowVars(75)
zp.SetHowVars(0.7330638371434377, 1.3032244450784043)

# Susanne Mesh
sus = zp.Thing([zp.NewSusanne()], 0, 0, 4)

# Adding Thing
zp.AddThing(sus)

# Create a PointLight and append it to the z3dpy.lights list
myLight = zp.Light_Point(0, 0, 2, 1, 25)

zp.lights.append(myLight)

# Raster Loop
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    # Input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        zp.CamAddPos(myCamera, zp.VectorMulF(zp.CamGetTargetDir(myCamera), 0.1))
    if keys[pygame.K_s]:
        zp.CamSubPos(myCamera, zp.VectorMulF(zp.CamGetTargetDir(myCamera), 0.1))
    if keys[pygame.K_a]:
       zp.CamAddPos(myCamera, zp.VectorMulF(zp.CamGetRightVector(myCamera), 0.1))
    if keys[pygame.K_d]:
        zp.CamSubPos(myCamera, zp.VectorMulF(zp.CamGetRightVector(myCamera), 0.1))
        

    if keys[pygame.K_UP]:
        zp.ThingAddPosZ(sus, 0.1)
    if keys[pygame.K_DOWN]:
        zp.ThingAddPosZ(sus, -0.1)
    if keys[pygame.K_LEFT]:
        zp.ThingAddPosX(sus, -0.1)
    if keys[pygame.K_RIGHT]:
        zp.ThingAddPosX(sus, 0.1)
        
    # The camera always looks forward
    zp.CamSetTargetDir(myCamera, [0, 0, 1])

    zp.SetInternalCam(myCamera)

    # Clear the screen
    screen.fill("black")

    # Using DebugRaster() to draw the light as well
    for tri in zp.DebugRaster():
        # Debug things will have an ID of -1, draw them with a red outline
        if zp.TriGetId(tri) == -1:
            zp.PgDrawTriOutl(tri, [1, 0, 0], screen, pygame)
        else:
            # Use DrawTriFL for flat lighting.
            zp.PgDrawTriFL(tri, screen, pygame)
            
    pygame.display.flip()

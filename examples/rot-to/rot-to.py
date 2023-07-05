import pygame
import z3dpy as zp

print("")
print("Controls:")
print("WASD to move")
print("Mouse to aim")

# Pygame stuff
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

# Our camera to view from
FPCamera = zp.Cam(0, -1, -3)

zp.CamSetTargetDir(FPCamera, [0, 0, 1])

# Setting Internal Camera
zp.SetInternalCam(FPCamera)

# Changing FOV
#zp.FindHowVars(75)
zp.SetHowVars(0.733063872892536, 1.303224560042964)

car_body = zp.LoadMesh("mesh/cars/car1_body.obj")
zp.MeshSetColour(car_body, [209, 224, 255])

car_window = zp.LoadMesh("mesh/cars/car1_window.obj")
zp.MeshSetColour(car_window, [78, 168, 255])

car_headlights = zp.LoadMesh("mesh/cars/car1_headlights.obj")

car_rearlights = zp.LoadMesh("mesh/cars/car1_rearlights.obj")
zp.MeshSetColour(car_rearlights, [255, 0, 0])

car = zp.Thing([car_body, car_window, car_headlights, car_rearlights], 0, 0, 5)

zp.AddThing(car)


zp.lights.append(zp.Light_Point(0, -8, 0, 0.2, 15))

zp.BakeLighting([car])


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            
    clock.tick(30)

    # Clearing with a sky colour
    screen.fill("#317FC4")

    # RotTo(objectRot, targetDir)
    carDir = zp.RotTo(zp.ThingGetRot(car), [0, 0, 1])

    # -Y is up
    carUp = zp.RotTo(zp.ThingGetRot(car), [0, -1, 0])

    carRt = zp.RotTo(zp.ThingGetRot(car), [1, 0, 0])

    tRay = zp.Ray(zp.ThingGetPos(car), zp.VectorAdd(zp.ThingGetPos(car), zp.VectorMulF(carDir, 5)))

    uRay = zp.Ray(zp.ThingGetPos(car), zp.VectorAdd(zp.ThingGetPos(car), zp.VectorMulF(carUp, 5)))

    rRay = zp.Ray(zp.ThingGetPos(car), zp.VectorAdd(zp.ThingGetPos(car), zp.VectorMulF(carRt, 5)))

    zp.rays = [tRay, uRay, rRay]

    for tri in zp.DebugRaster():
        if zp.TriGetId(tri) == -1:
            zp.PgDrawTriOutl(tri, [1, 0, 0], screen, pygame)
        else:
            zp.PgDrawTriFL(tri, screen, pygame)
        
    pygame.display.flip()

    zp.ThingAddRot(car, [1, 2, 3])

import math
import random as rand

def ComplexX(x, fov):
    f = 1 / math.tan(fov / 2)
    return (16/9) * f * x

def ComplexY(x, fov):
    f = 1 / math.tan(fov / 2)
    return f * x

def ComplexZ(z, fc, nc):
    q = fc / (fc - nc)
    return (q * z) - (q * nc)

def SimpleFormula(x, y):
    return x * y

def CamX(y, fov):
    score = 0
    for x in range(1920):
        rY = ComplexX(x, fov)
        aY = SimpleFormula(x, y)
        score += abs(rY - aY)
    return score

def CamY(y, fov):
    score = 0
    for x in range(1920):
        rY = ComplexY(x, fov)
        aY = SimpleFormula(x, y)
        score += abs(rY - aY)
    return score

calc = True

def CalculateCam(foV):
    print("Calculating Camera..")
    finished = [0, 0, 0]
    fov = foV * 0.0174533
    for z in range(0, 2):
        currentScore = 9999999
        currentBest = 1
        noImp = 0
        srchRad = 12
        aiY = 1
        calc = True
        while calc:
            match z:
                case 0:
                    Score = CamX(aiY, fov)
                case 1:
                    Score = CamY(aiY, fov)
            if Score < currentScore:
                currentBest = aiY
                currentScore = Score
            else:
                noImp += 1
            if noImp > 50:
                srchRad /= 2
                noImp = 0
            if srchRad < 0.00000000000000001:
                match z:
                    case 0:
                        finished[0] = currentBest
                        print("Found X...")
                    case 1:
                        finished[1] = currentBest
                        print("Found Y...")
                        print("Done!")
                        print("X: " + str(finished[0]) + ", Y: " + str(finished[1]))
                        print("Use SetHowVars() to skip the calculations")
                        return finished
                        
                calc = False
            
            aiY = currentBest + ((rand.random() - 0.5) * (srchRad * 2))
        
    

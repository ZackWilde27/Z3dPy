def CreateAOBJ(filename):
    count = 1
    verts = 0
    while True:
        try:
            file = open(filename[:-4] + str(count) + filename[-4:], 'r')
            file.close()
            count += 1
        except:
            break

    def Compare(v, string):
        return v[0] == string[0] and v[1] == string[1] and v[2] == string[2]

    output = ""
    vertis = []
    start = True

    for f in range(1, count):
        file = open(filename[:-4] + str(f) + filename[-4:], 'r')
        verts = 0
        buffer = ""
        while (line := file.readline()):
            if line:
                if start:
                    buffer += line
                if line[:2] == "v ":
                    strip = line[2:].strip()
                    split = strip.split(' ')
                    if start:
                        vertis.append(split)
                    else:
                        verts += 1
                        if verts > len(vertis):
                            break
                        if not Compare(vertis[verts - 1], split):
                            buffer += str(verts - 1) + ' ' + strip + "\n"
                            vertis[verts - 1] = split

        if verts and verts != len(vertis):
            buffer = ""
            f -= 1
            start = True
            vertis = []
            output += "new\n"
            continue

        output += buffer + ("a\n" if start else "next\n")
        start = False
        file.close()

    file = open(filename[:-4] + ".aobj", 'w')
    file.write(output)
    file.close()
    print("Your mesh has been converted to a .aobj")


print("Directory to OBJ sequence to convert:")
print("If your list of files is anim1.obj, anim2.obj, etc. put in 'anim.obj'")
CreateAOBJ(input(">"))

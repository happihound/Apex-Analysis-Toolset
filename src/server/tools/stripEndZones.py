
x_array = []
y_array = []
radius_array = []
fileName = "internal/temp/valid_end_zones_we"

with open(fileName+".txt") as f:
    for line in f:
        line = line.strip()
        if "origin" in line:
            splitLine = line.split(" ")
            splitLine[1] = splitLine[1].strip('"')
            print("X: " + splitLine[1])
            x_array.append(float(splitLine[1]))
            splitLine[2] = splitLine[2].strip('"')
            print("Y: " + splitLine[2])
            y_array.append(float(splitLine[2]))
        elif "script_radius" in line:
            splitLine = line.split(" ")
            splitLine[1] = splitLine[1].strip('"')
            print("Radius: " + splitLine[1])
            radius_array.append(float(splitLine[1]))


for i in range(len(x_array)):
    with open(fileName+"_stripped.txt", "a") as f:
        f.write("[" + str(x_array[i]) + ", " + str(y_array[i]) + ", " + str(radius_array[i]) + "]")
        # dont do a new line on the last one
        if i != len(x_array)-1:
            f.write("\n")


print("Done")

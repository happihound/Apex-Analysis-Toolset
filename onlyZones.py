import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob
from matplotlib.widgets import RadioButtons
from matplotlib.widgets import Button
from gameMapImage import gameMapImage
from userMapImage import userMapImage


class onlyZones:

    __slots__ = ['mapName', 'invalid_zones', 'valid_zones', 'map_image',
                 'fig', 'ax1', 'ax2', 'ratio', 'user_map_image1', 'user_map_image2']

    def __init__(self, mapName, ratio="4by3"):
        self.mapName = mapName
        self.map_image = None
        self.invalid_zones = []
        self.valid_zones = []
        self.map_image = None
        self.load_map()
        self.load_invalid_zones()
        self.user_map_image1 = None
        self.user_map_image2 = None
        self.load_valid_zones()
        self.fig = None
        self.ax1 = None
        self.ratio = "4by3"
        self.ax2 = None
        #plt.gcf().canvas.mpl_connect('button_press_event', self.__showCurrentPoiAssociations)
        self.fig, (self.ax2) = plt.subplots(1, 1)
        plt.ion()
        win = self.fig.canvas.window()
        win.setFixedSize(800, 600)
        self.ax2.imshow(self.map_image)
        self.ax2.set_title('Map')
        # self.plot_valid_zones()
        # self.plot_invalid_zones()
        self.fig.canvas.draw()
        self.load_user_map()
        self.ax2.imshow(self.map_image)
        # self.show_with_cv2()
        self.extract_zone()
        self.fig.canvas.draw()

    def load_map(self):
        try:
            self.map_image = cv2.imread(f'internal/maps/16by9/map{self.mapName}16by9.jpg', cv2.IMREAD_UNCHANGED)
            self.map_image = cv2.cvtColor(self.map_image, cv2.COLOR_BGR2RGB)
        except:
            print('map not found')

    def load_invalid_zones(self):
        file = glob.glob(f'internal/zones/invalid_zones/{self.mapName}.txt')
        self.invalid_zones = self.text_loader(file)

    def load_valid_zones(self):
        file = glob.glob(f'internal/zones/valid_zones/{self.mapName}.txt')
        self.valid_zones = self.text_loader(file)

    def text_loader(self, file):
        returnArray = []
        x_array = []
        y_array = []
        radius_array = []
        print(file)
        with open(file[0]) as f:
            for line in f:
                line = line.strip().strip(" ").strip("\n").strip("[").strip("]")
                split = line.split(",")
                #print("x: " + str(split[0]) + " y: " + str(split[1]) + " radius: " + str(split[2]))

                max_x = 42560
                max_y = 42560
                min_x = -42560
                min_y = -42560

                map_x = 4096
                map_y = 4096

                scale_x = map_x / (max_x - min_x)
                scale_y = map_y / (max_y - min_y)

                scale_factor = 0.945

                x_coord = int((float(split[0])*scale_factor - min_x) * scale_x)
                y_coord = int((-float(split[1])*scale_factor - min_y) * scale_y)
                x_array.append(x_coord)
                y_array.append(y_coord)
                radius_array.append(int(float(split[2])*scale_factor/19))

        for i in range(len(x_array)):
            returnArray.append([x_array[i], y_array[i], radius_array[i]])
        return returnArray

    def plot_invalid_zones(self) -> None:
        self.load_invalid_zones()
        # Show the image
        # self.ax2.cla()
        self.ax2.imshow(self.map_image)
        # Plot all the POIs
        for zone in self.invalid_zones:
            x = zone[0]
            y = zone[1]
            radius = zone[2]
            #print("x: " + str(x) + " y: " + str(y) + " radius: " + str(radius))
            #self.ax2.scatter(x, y, s=radius, color='red')
            self.map_image = cv2.circle(self.map_image, (int(x), int(y)), int(radius), (255, 0, 0), 5)

    def plot_valid_zones(self) -> None:
        self.load_valid_zones()
        # Show the image
        # self.ax2.cla()
        self.ax2.imshow(self.map_image)
        # Plot all the POIs
        for zone in self.valid_zones:
            x = zone[0]
            y = zone[1]
            radius = zone[2]
            #print("x: " + str(x) + " y: " + str(y) + " radius: " + str(radius))
            #self.ax2.scatter(x, y, s=radius, color='green')
            self.map_image = cv2.circle(self.map_image, (int(x), int(y)), int(radius), (0, 255, 0), 5)

    def load_user_map(self):
        image_path = glob.glob(f'input/mapScreenShot/*.png')
        print(image_path)
        image2 = cv2.imread(image_path[0], cv2.IMREAD_UNCHANGED)
        image1 = cv2.imread(image_path[1], cv2.IMREAD_UNCHANGED)
        userMapImage1 = userMapImage(image2, self.ratio)
        userMapImage2 = userMapImage(image1, self.ratio)
        print(userMapImage1.getOriginalImage().ratio())
        print(userMapImage2.getOriginalImage().ratio())
        self.user_map_image1 = userMapImage1
        self.user_map_image2 = userMapImage2
        #cv2.imshow("User Map", self.user_map_image1.getCroppedImage())

    def extract_zone(self):
        circles = self.user_map_image1.extractZone()
        self.ax2.imshow(self.user_map_image1.getCroppedImage().image())
        for circle in circles:
            self.map_image = cv2.circle(self.user_map_image1.getCroppedImage().image(), (int(
                circle[0]), int(circle[1])), int(circle[2]), (0, 0, 255), 5)
        self.ax2.imshow(self.map_image)
        self.fig.canvas.draw()



    def show_with_cv2(self):
        cv2.namedWindow("User Map", cv2.WINDOW_NORMAL)
        image = cv2.cvtColor(self.user_map_image1.getCroppedImage().image(), cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (2048, 2048), interpolation=cv2.INTER_AREA)
        #cv2.imshow("User Map", image)
        cv2.waitKey(0)

    def main(self):
        plt.show(block=True)


if __name__ == '__main__':
    onlyZones = onlyZones('WE', "16by9")
    onlyZones.main()

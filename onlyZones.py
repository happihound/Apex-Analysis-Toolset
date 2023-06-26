import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob
from matplotlib.widgets import RadioButtons
from matplotlib.widgets import Button
from gameMapImage import gameMapImage
from userMapImage import userMapImage


class onlyZones:

    __slots__ = ['mapName', 'invalid_zones', 'valid_zones', 'map_image', 'fig', 'ax1', 'ax2', 'ratio']

    def __init__(self, mapName, ratio):
        self.mapName = mapName
        self.map_image = None
        self.invalid_zones = []
        self.valid_zones = []
        self.map_image = None
        self.load_map()
        self.load_invalid_zones()
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
        self.plot_valid_zones()
        self.plot_invalid_zones()
        self.fig.canvas.draw()
        self.load_user_map()
        self.ax2.imshow(self.map_image)
        self.show_with_cv2()

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
                print("x: " + str(split[0]) + " y: " + str(split[1]) + " radius: " + str(split[2]))

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

    def extract_zone(self):
        pass

    def load_user_map(self):
        image_path = glob.glob(f'input/mapScreenShot/*.png')
        image = cv2.imread(image_path[0], cv2.IMREAD_UNCHANGED)
        #userMapImage1 = userMapImage(image, "4:3")
        cv2.namedWindow("User Map", cv2.WINDOW_NORMAL)
        #cv2.resizeWindow("User Map", 800, 600)
        #cv2.imshow("User Map", userMapImage1.getThresheldImage().image())

    def show_with_cv2(self):
        cv2.namedWindow("User Map", cv2.WINDOW_NORMAL)
        self.map_image = cv2.cvtColor(self.map_image, cv2.COLOR_BGR2RGB)
        self.map_image = cv2.resize(self.map_image, (2048, 2048), interpolation=cv2.INTER_AREA)
        cv2.imshow("User Map", self.map_image)
        cv2.waitKey(0)

    def main(self):
        plt.show(block=True)


if __name__ == '__main__':
    onlyZones = onlyZones('WE', "16by9")
    onlyZones.main()

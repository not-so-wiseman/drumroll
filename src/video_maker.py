import os
import re
import subprocess
from zipfile import ZipFile
from time import time


class Slide:
    def __init__(self, origin, line):
        duration_times = re.findall('=\"(\d+\.\d+)\"', line)
        self.start = float(duration_times[0])
        self.end = float(duration_times[1])
        self.duration = round(self.end - self.start, 1)

        href = re.findall('xlink:href="\.\.\/meetingFiles\/(.+\.png)', line)[0]
        self.path = origin.replace("\\", "\\\\") + href.replace("/", "\\\\")


class Video:
    def __init__(self, input_folder):
        self.folder = input_folder.replace('.zip','')

        directory = input_folder.split('\\')
        folder_name = directory.pop()
        self.root = "\\".join(directory)

        # unzip folder
        zf = ZipFile(input_folder, 'r')
        zf.extractall(self.root)
        zf.close()

        # Re-join path w/o .zip and with sub directory added
        directory.extend([folder_name.replace('.zip', ''), "meetingFiles"])  
        self.path = "\\".join(directory) + "\\"

    def get_name(self):
        # Get name of lecture from events metadata
        events = open(self.path + 'events.xml', 'r')
        meeting_info = events.readlines()[2]
        name = re.search('name=\"((\w|\s|-|&)+)\"', meeting_info).group(1)
        name = name.replace(" ","")

        # Check if name already exists at root
        for file in os.listdir():
            if (file == name + '.mp4'):
                name += str(round(time()))
                break

        return name

    def _index_slides(self):
        # Read slide information from ../shapes.svg
        shapes = open('{}\\shapes.svg'.format(self.path), 'r')
        contents = shapes.readlines()[3:-1]
        shapes.close()
        slides = [Slide(self.path, line) for line in contents if re.search('<image', line)]

        # Write slide info to in.ffconcat for use by FFMEG
        listing = open(self.path + "input.txt", "w")
        for slide in slides:
            listing.write("file {}\nduration {}\n".format(slide.path, slide.duration))
        listing.write("file {}".format(slides[-1].path))
        listing.close()

    def is_screenshare(self):
        files = " ".join(os.listdir(self.path))
        screenshare = re.match('_screenshare.mp4', files)
        return True if screenshare else False

    def run_ffmeg(self, arguments):
        print("ffmpeg ", arguments)
        try:
            subprocess.run("ffmpeg {}".format(arguments),shell=True, check=True)
        except Exception as e:
            print(e)


    def create_video(self, output_filename="output.avi"):
        files = " ".join(os.listdir(self.path))
        output = '{}\\{}.mp4'.format(self.root, self.get_name()) 

        # Convert audio voice over from video to audio only
        print("Generating audio...")
        audio = self.path + re.findall("__\d{7}_.{32}\.mp4", files).pop()
        self.run_ffmeg("-i {} {}".format(audio, audio.replace(".mp4", ".mp3")))
        
        video = None
        if self.is_screenshare():
            #Screnario 1 - No audio folder and 2 MP4s. 1 MP4 contains audio and the other is 
            # a screenshare
            video = self.path + re.findall("__\d{7}_.{32}_screenshare\.mp4", files).pop()
        else:
            # Screnario 2 - There is slides and an audio folder containing the
            # voice over for the lecture
            
            # Create a transcript of the slide's location and duration for conversion to video
            self._index_slides()
            # Create video from slides
            print("Generating video...")
            self.run_ffmeg("-f concat -safe 0 -i {} -i {} -c:v libx264 -r 30 -pix_fmt yuv420p {}".format(
                self.path + "input.txt", audio.replace(".mp4", ".mp3"), output))
    
        # Combine audio and video
        #if video != None:
        #    self.run_ffmeg("-safe 0 -i {} -i {} -c copy -map 0:v:0 -map 1:a:0 {}".format(
        #    video, audio, output))
        
        # Cleanup
        try:
            os.remove(self.folder)
        except:
            print("Could not complete cleanup")
        print('Done')
        
      

        


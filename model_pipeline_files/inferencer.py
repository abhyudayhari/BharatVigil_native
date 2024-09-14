from model_packet_data import Model
import argparse
import yaml
import torch
from mnist import MNIST
import numpy as np
import glob
import os
from PIL import Image
def load_config(filename):

    try:
        with open(filename, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None
config = load_config('config.yaml')
parser = argparse.ArgumentParser(description='Pass an argument for model inference')
parser.add_argument('input_file',type=str,help="path of the input_file")

class inferencer:
    def __init__(self):
        self.gpu_code=config["model"]["cuda_code"]
        self.model_path=config["model"]["model_dir_packet_data"]
        if self.gpu_code==None:
             self.device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
        elif self.gpu_code=="cpu":
            self.device=torch.device('cpu')
        elif self.gpu_code=="cuda":
            self.device=torch.device('cuda')
        else:
            print("Invalid choice")
        self.num_classes=config["model"]["num_classes"]
        self.dimension= config["model"]["model_dim"]
        self.model=Model(self.dimension,self.num_classes)
        self.model.load_state_dict(torch.load(self.model_path))
        self.model.to(device=self.device)
        self.model.eval()

    
    def load_images(self,input_dir):
        png_file_l=glob.glob(os.path.join(input_dir,"*.png"))
        images=[]
        for image in png_file_l:
            img=Image.open(image)
            img_array=np.array(img,dtype=np.uint8)
            hex_image_array = np.vectorize(lambda x: int(hex(x), 16))(img_array)
            images.append(hex_image_array)
        image_batch=np.stack(images,axis=0)
        images_tensor = torch.tensor(image_batch, dtype=torch.float32)
    
        return images_tensor
    
    # def load_ubyte(self,file_path):
    #     with open(file_path, 'rb') as f:
    #         # Read magic number (first 4 bytes), but you can ignore it
    #         magic = int.from_bytes(f.read(4), byteorder='big')
            
    #         # Read the number of images (next 4 bytes)
    #         num_images = int.from_bytes(f.read(4), byteorder='big')
            
    #         # Read the number of rows and columns (next 8 bytes)
    #         num_rows = int.from_bytes(f.read(4), byteorder='big')
    #         num_cols = int.from_bytes(f.read(4), byteorder='big')
            
    #         # Read the rest of the file as raw pixel data
    #         data = np.frombuffer(f.read(), dtype=np.uint8)
            
    #         # Reshape the data into the appropriate shape (num_images, height, width)
    #         data = data.reshape((num_images, num_rows, num_cols))
            
    #         return data

    def inference_input(self,input_dir):
        
        data_load=self.load_images(input_dir)
        # data_load=self.load_ubyte(input_file)
        # mn_data=MNIST(input_file)
        # data_load=mn_data.load_training()
        output=self.model.forward(data_load.to(self.device),inference=True)
        print(output)   
        #self.model.forward()

if __name__=="__main__":
    args=parser.parse_args()
    inference=inferencer()
    inference.inference_input(args.input_file)

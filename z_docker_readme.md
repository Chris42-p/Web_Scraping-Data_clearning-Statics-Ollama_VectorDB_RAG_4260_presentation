This is for a linux system 

### building and starting the image 
     sudo docker compose up --build

### Build the images. 
     sudo docker compose build

### start the containers. 
     sudo docker compose up

### bring down the containers. 
     sudo docker compose down

### clean unused docker resoruces
     sudo docker system prune

### deleting conflicting images. 
     sudo docker remove <name of image>



#### change ownership of file. 
Docker can change the permission on a file preventing it from rerunnig, to fix need to change ownership to user 

sudo chown -R $USER:$USER Modules/user_GUI/front_end
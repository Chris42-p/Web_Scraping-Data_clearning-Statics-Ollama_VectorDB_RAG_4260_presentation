#select the OS you want the image to run on. 
FROM nginx:1.10.1-alpine
# copy files from the local computer into the image. 
COPY ./src/html/index.html /usr/share/nginx/html
# ENV FOO=BAR  #use this if youre importing another img that needs params , else pass param into img 

#expose ports.  -- can set /udp also #this is mainly documentation. 
EXPOSE 80/tcp

#can pass commands into the image to run on boot #cmd to run at start of execution
CMD [ "nginx","-g","daemon off;" ]

#to build it 
#check if docker is installed 

#comainer becomes an image after we run the image. 

#build a container/image
#1: check docker is installed.   cmd: docker info 
#2: build the docker container:  cmd: docker build -t tag-of-img . 
#3: check img:                   cmd: docker images 
#4: run the img:                 cmd: docker run -d -p 80:80 <img id>
#5: see the running image:       cmd: docker ps.
#5.1: see all imgs           cmd: docker ps -a 
#6: stopping the container       cmd: docker stop <comainer id/Name>
#7: delete the container         cmd: docker rm <container_name>
#8: delete the image             cmd: docker rmi <img ID>


# Docker ignore file 
#run to ignore the 

#exec allows to execute in a container while its running
#step into the machine: docker exec -it <img ID> /bin/sh #gives interactive mode. 
#then i get a CLI into the containe . 


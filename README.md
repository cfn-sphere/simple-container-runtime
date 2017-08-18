# SCR - Simple-Container-Runtime

This project aims to be a really simple solution to run Docker containers on AWS EC2 instances.

### Why

There are solutions out there like AWS ECS, Kubernetes and so on. They all do a good job on their own. But what if I simply want to run some containers without the complexity of maintaining all the things around. Even if AWS ECS brings a lot out of the box and Kubernetes can be run by simply executing a script there is a lot to do to really have a production ready system.

Don't get me wrong, SCR is not specifically intended to run all containers on a single box. It is designed to be simple and leave topics other than running containers on one instance to other infrastructure components. It perfectly fits into a world where infrastructure is maintained by AWS CloudFormation and instances run in AWS AutoScaling groups for scalability.

### How

SCR is build around docker-compose. Users can simply use a docker-compose.yaml file stored in S3, on filesystem or any reachable webserver run their app. One can extend the config for specific use cases like health checks, instance preparation, status signaling and so on but in the end it is up to your usecase. Stick with a simple plain docker-compose config or use all the modules available.

## Build it

This project uses pybuilder as build tool.

    pip install pybuilder
    pyb install_dependencies
    pyb
 
## Run it

    scr my-config-file
    
### Examples
    
#### load configuration filesystem
    scr /etc/my-app-config.yaml
    
#### load configuration from S3
    scr s3://my-bucket/my-app-config.json

#### Get configuration from any http(s) server
    scr http://my-infrastructure.service/my-app-config.yaml
    
#### Run on an EC2 instance and get configuration from instance user-data
    scr http://169.254.169.254/latest/user-data
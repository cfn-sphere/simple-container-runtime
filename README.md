# SCR - Simple-Container-Runtime

[![Build Status](https://travis-ci.org/cfn-sphere/simple-container-runtime.svg?branch=master)](https://travis-ci.org/cfn-sphere/simple-container-runtime)

[![Code Health](https://landscape.io/github/cfn-sphere/simple-container-runtime/master/landscape.svg?style=flat)](https://landscape.io/github/cfn-sphere/simple-container-runtime/master)

This project aims to be a really simple solution to run Docker containers on AWS EC2 instances.

### Why

There are solutions out there like AWS ECS, Kubernetes and so on. They all do a good job on their own. But what if I simply want to run some containers without the complexity of maintaining all the things around. Even if AWS ECS brings a lot out of the box and Kubernetes can be run by simply executing a script there is a lot to do to really have a production ready system.

Don't get me wrong, SCR is not specifically intended to run all containers on a single box. It is designed to be simple and leave topics other than running containers on one instance to other infrastructure components. It perfectly fits into a world where infrastructure is maintained by AWS CloudFormation and instances run in AWS AutoScaling groups for scalability.

### How

SCR is build around docker-compose. Users can simply use a docker-compose.yaml file stored in S3, on filesystem or any reachable webserver run their app. One can extend the config for specific use cases like health checks, instance preparation, status signaling and so on but in the end it is up to your usecase. Stick with a simple plain docker-compose config or use all the modules available.

## Give it a try

All theory is gray. Give it a try without a lot of hazzle. Let SCR start a container with wordpress and another one with mysql for you:

    pip install scr
    scr run quickstart/wordpress-with-mysql.yaml
    
After some time waiting for the images to load scr finally executes a local heathcheck to make sure that wordpress is up and running. 
You can connect on [http://localhost:8000](http://localhost:8000). Simply press CTRL+C to gracefully stop everything.

## Build it

This project uses pybuilder as build tool.

    pip install pybuilder
    pyb install_dependencies
    pyb

## Requirements

Python 3 is required

## Install it

A Package is available at the Python Package Index: https://pypi.python.org/pypi?name=simple-container-runtime&:action=display

    pip install simple-container-runtime
 
## Run it

    scr run [options] my-config-file
    
### Examples
    
#### load configuration from filesystem
    scr run /etc/my-app-config.yaml
    
#### load configuration from S3
    scr run s3://my-bucket/my-app-config.json

#### Get configuration from any http(s) server
    scr run http://my-infrastructure.service/my-app-config.yaml
    
#### Run on an EC2 instance and get configuration from instance user-data

This is the prefered way to configure scr on EC2 instances. You can use cfn-sphere to simply create AWS CloudFormation templates properly configuring user-data.

    scr run http://169.254.169.254/latest/user-data
    
## Example Config Yaml

    # things to be done before composition starts
    pre_start:
      - AwsEcrLogin:
          region: eu-west-1
          account_id: 123456789123
    
    #health checks to be made executed the composition started to verify its health
    healthchecks:
      - http:
          port: 8000
      - AwsElb:
          loadbalancer_name: my-alb
    
    # signals to be send to inform the outside world about the status of this composition
    signals:
      - AwsCfn:
          region: eu-west-1
          stack_name: my-stack
          logical_resource_id: my-asg
    
    #plain docker-compose yaml
    docker-compose:
        version: '2'
        services:
           db:
             image: mysql:5.7
             volumes:
               - db_data:/var/lib/mysql
             restart: always
             environment:
               MYSQL_ROOT_PASSWORD: wordpress
               MYSQL_DATABASE: wordpress
               MYSQL_USER: wordpress
               MYSQL_PASSWORD: wordpress
    
           wordpress:
             depends_on:
               - db
             image: wordpress:latest
             ports:
               - "8000:80"
             restart: always
             environment:
               WORDPRESS_DB_HOST: db:3306
               WORDPRESS_DB_PASSWORD: wordpress
        volumes:
            db_data:

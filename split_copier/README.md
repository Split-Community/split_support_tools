# split_copier

## Overview

This is a simple tool to copy the Split definitions from one environment to another.

# Getting Started
Please update your nodeJS to at least version v14.21 

## Project setup
```
npm install
```

### Compiles and hot-reloads for development

```
npm run serve
```
This will start a web app at localhost:8080

  App running at:
  - Local:   http://localhost:8080/ 
  - Network: http://10.20.3.249:8080/

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

### To use the app:

Requirements: 
 - Admin API key.
    - Navigate to your Split admin console, go to the API key section 
    ![image](https://user-images.githubusercontent.com/49971676/213550551-04a54aa9-d858-4b21-967a-45a7f1b69e8e.png)

    - Click on create API Key button on the top right corner
    
    - Give it a name, and choose Admin in the option
    ![image](https://user-images.githubusercontent.com/49971676/213553660-8a5cecdb-51f3-483e-998e-5422eef6191d.png)

    - Now you have an Admin API key, copy it for the next step
    ![image](https://user-images.githubusercontent.com/49971676/213553690-06b731a2-3f53-4a2e-a20c-076c49a7c07c.png)


- Navigate to the web app at localhost:8080
![image](https://user-images.githubusercontent.com/49971676/213553712-7422c85a-eea9-4d82-9254-b4fc8465b123.png)

- Input the API key we copied from earlier and choose connect
![image](https://user-images.githubusercontent.com/49971676/213553746-d81ae430-4aa8-4ae6-8700-d8de65bd300f.png)

- Once connected, you should see your workspace menu

- Choose the workspace from the list
![image](https://user-images.githubusercontent.com/49971676/213553914-c068f1fb-f058-45b7-b0e3-2072091e5fa7.png)

- You will now see the menu to select your Split, the From, and to environment

![image](https://user-images.githubusercontent.com/49971676/213553978-9f46ee32-d44c-40a1-b148-ec5aacc9b515.png)

- Once you have selected the environments, click Preview to see the changes

- Finally click save to save the changes.
![image](https://user-images.githubusercontent.com/49971676/213554044-24792007-c894-4a29-8521-2dfeec1f73ce.png)

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

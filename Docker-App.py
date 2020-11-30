# Importing python3 default modules
import tkinter as tk
from ast import literal_eval
from tkinter import messagebox

# Creating main tkinter GUI window
main = tk.Tk()
main.title('Docker-App')
main.geometry('600x600')

# Importing docker sdk module for python
# If module not installed exiting app
try:
    import docker
except ModuleNotFoundError as exception:
    messagebox.showerror('Module Import Error', f'{exception}\nUse pip install docker to install module')
    main.destroy()
    exit()

# Adding app directivies for the contaniers and images
app_propeties = ['Image Name', 'Container Name', 'Port', 'Enviroment', 'Repository']
length = len(app_propeties)

# Connecng to local docker instance using docker sdk
# If docker not found or running exiting app
try:
    client = docker.from_env()
except docker.errors.DockerException:
    messagebox.showerror('Docker Error', 'Docker not installed or not running')
    main.destroy()
    exit()

# Getting all docker containers or a specified container by its name
def get_container():
    # Cleaning the previous frame in the gui window
    [data.grid_remove() for data in main.grid_slaves(row=length+4)]
    # Create frame inside the main gui window for displaying contianers info
    frame = tk.LabelFrame(main, border=0)
    frame.grid(row=length+4, column=0, columnspan=2)

    # Checking if a container name was used for lookup:
    # If not getting all containers
    # If there is a container name getting only the specified container if it exist
    if text_boxes[1].get() == '':
        containers = client.containers.list(all)
    else:
        try:
            containers = client.containers.get(text_boxes[1].get())
        except:
            messagebox.showerror('Get Container', f'Container {text_boxes[1].get()} not found or exist')
            return None
    
    # Creating the containers list objects to show
    container_list = [['Container ID', 'Image', 'Name', 'Status', 'Ports']]
    if isinstance(containers, list):
        for container in containers:
            ports = ",".join([f"{key}:{value[0]['HostPort']}" for key,value in container.ports.items() if container.ports[key] != None])
            container_list.append([container.short_id, "".join(container.image.tags), container.name, container.status, ports])
    else:
        ports = ",".join([f"{key}:{value[0]['HostPort']}" for key,value in containers.ports.items() if containers.ports[key] != None])
        container_list.append([containers.short_id, "".join(containers.image.tags), containers.name, containers.status, ports])
    
    # Printing the containers info in the gui
    for row in range(len(container_list)):
        for col in range(len(container_list[0])):
            tk.Label(frame, text=container_list[row][col]).grid(row=row, column=col)

# Run a new container with provieded paramters from text boxes if used
def run_container():
    # Check if an image name was given or not
    if text_boxes[0].get() == '':
        messagebox.showerror('Run Container', f"Can't run a container without an image")
    else:
        # Getting an image name and/or tag if given
        image = text_boxes[0].get().split(':')
        if len(image) == 1:
            image = f'{image[0]}:latest'
        elif len(image) == 2:
            image = f'{image[0]}:{image[1]}'
        else:
            messagebox.showerror('Run Container', f'Image {image} is in an incorrect syntax')
            return None
        
        # Getting container name from user
        name = ports = environment = ''
        if text_boxes[1].get() != '':
            name = text_boxes[1].get()

        # Getting container ports to be used with new container
        if text_boxes[2].get() != '':
            try:
                port = literal_eval('{' + text_boxes[2].get() + '}')
            except ValueError:
                messagebox.showerror('Run Container', f'{text_boxes[2].get()} is not a valid input for ports parameter')
                return None

        # Getting environment variables if used
        if text_boxes[3].get() != '':
            environment = text_boxes[3].get().split(',')

        # Trying to create a new container by given parametrs if not throwing an exception by relavane of the parameter or the container itself
        try:
            client.containers.run(image=image, name=name, ports=port, environment=environment, detach=True)
        except docker.errors.ImageNotFound:
            messagebox.showerror('Run Container', f'Image {image} not found or exist')
        except docker.errors.APIError as exeception:
            if exeception.status_code == 400:
                messagebox.showerror('Run Container', f'Invalid container name: {name}')
            elif exeception.status_code == 409:
                messagebox.showerror('Run Container', f'The container name {name} is already in use')
            elif exeception.status_code == 500:
                messagebox.showerror('Run Container', f'Ports {ports} are not available or already in use by another container')
        except docker.errors.NotFound:
            tag = image.split(':')[1]
            messagebox.showerror('Run Container', f'Tag {tag} for image {image} is not found or unknown')

# Starting an exsiting container that is not running
def start_container():
    # Check if a container name was given or not
    if text_boxes[1].get() == '':
        messagebox.showerror('Start Container', "Can't start a container without a container name")
    else:
        name = text_boxes[1].get()
        # Trying to start the container
        try:
            client.containers.get(name).start()
        except docker.errors.APIError:
            messagebox.showerror('Pause Container', f'Container {name} is paused and be cannot started, try unpause instead')
        except:
            messagebox.showerror('Start Container', f'Container {name} not found or exist')

# Stopping a running container
def stop_container():
    # Check if a container name was given or not
    if text_boxes[1].get() == '':
        messagebox.showerror('Stop Container', "Can't stop a container without a container name")
    else:
        name = text_boxes[1].get()
        # Trying to stop the container
        try:
            client.containers.get(name).stop()
        except:
            messagebox.showerror('Stop Container', f'Container {name} not found or exist')

# Pausing a running container
def pause_container():
    # Check if a container name was given or not
    if text_boxes[1].get() == '':
        messagebox.showerror('Pause Container', "Can't pause a container without a container name")
    else:
        name = text_boxes[1].get()
        # Trying to pause the container
        try:
            client.containers.get(name).pause()
        except docker.errors.APIError:
            messagebox.showerror('Pause Container', f'Container {name} is already paused or not running')
        except:
            messagebox.showerror('Pause Container', f'Container {name} not found or exist')

# Unpausing a paused container
def unpause_container():
    # Check if a container name was given or not
    if text_boxes[1].get() == '':
        messagebox.showerror('UnPause Container', "Can't unpause a container without a container name")
    else:
        name = text_boxes[1].get()
        # Trying to unpause the container
        try:
            client.containers.get(name).unpause()
        except docker.errors.APIError:
            messagebox.showerror('UnPause Container', f'Container {name} is not paused')
        except:
            messagebox.showerror('UnPause Container', f'Container {name} not found or exist')

# Removing an existing container
def remove_container():
    # Check if a container name was given or not
    if text_boxes[1].get() == '':
        messagebox.showerror('Remove Container', "Can't remove a container without a container name")
    else:
        name = text_boxes[1].get()
        # Trying to remove a container
        try:
            client.containers.get(name).remove()
        except docker.errors.NotFound:
            messagebox.showerror('Remove Container', f'Container {name} not found or exist')
        except docker.errors.APIError:
            # If the container is running prompting the user to remove it forcefully or not
            response = messagebox.askquestion('Remove Container', f'Container {name} is running or paused.\nDo you want to force remove it?')
            if response == 'yes':
                client.containers.get(name).remove(force=True)
        except:
            messagebox.showerror('Remove Container', f'Container {name} not found or exist')

# Getting all docker images or a specified image by its name
def get_image():
    # Cleaning the previous frame in the gui window
    [data.grid_remove() for data in main.grid_slaves(row=length+4)]
    # Create frame inside the main gui window for displaying image info
    frame = tk.LabelFrame(main, border=0)
    frame.grid(row=length+4, column=0, columnspan=2)

    # Checking if a image name was used for lookup:
    # If not getting all images
    # If there is a image name getting only the specified image if it exist
    if text_boxes[0].get() == '':
        images = client.images.list()
    else:
        try:
            images = client.images.get(text_boxes[0].get())
        except docker.errors.ImageNotFound:
            messagebox.showerror('Get Image', f'Image {text_boxes[0].get()} not found or exist')
            return None

    # Creating the images list objects to show
    image_list = [['Image ID', 'Image Name']]
    if isinstance(images, list):
        for image in images:
            if len(image.tags) == 1:
                image_list.append([image.short_id.replace('sha256:',''), image.tags[0]])
            else:
                for image_tag in image.tags:
                    image_list.append([image.short_id.replace('sha256:',''), image_tag])
    else:
        image_name = [image for image in images.tags if image.startswith(text_boxes[0].get())]
        image_list.append([images.short_id.replace('sha256:',''), image_name])
    
    # Printing the images info in the gui
    for row in range(len(image_list)):
        for col in range(len(image_list[0])):
            tk.Label(frame, text=image_list[row][col]).grid(row=row, column=col)

# Pulling image from the docker hub registry
def pull_image():
    # Check if an image name was given or not
    if text_boxes[0].get() == '':
        messagebox.showerror('Pull Image', f"Can't pull an image without an image name")
    else:
        # Getting an image name and/or tag if given
        image = text_boxes[0].get().split(':')
        if len(image) == 1:
            image = image[0]
            tag = 'latest'
        elif len(image) == 2:
            tag = image[1]
            image = image[0]
        else:
            messagebox.showerror('Pull Image', f'Image {image} is in an incorrect syntax')
            return None
        
        # After getting an imge name trying to pull it from the docker hub registry
        try:
            client.images.pull(image, tag=tag)
        except docker.errors.ImageNotFound:
            messagebox.showerror('Pull Image', f'Image/Repository {image} not found or exist')
        except docker.errors.APIError:
            messagebox.showerror('Pull Image', f'No such image: {image}: invalid reference format')
        except docker.errors.NotFound:
            messagebox.showerror('Pull Image', f'Tag {tag} for image {image} is not found or unknown')

# Commiting a container to an image and saving it for future use as an image
def commit_container_to_image():
    # Check if a container name was given or not
    if text_boxes[1].get() == '':
        messagebox.showerror('Commit Container to Image', "Can't commit a container without a container name")
    else:
        # Getting the container name and/or tag if given
        container_name = text_boxes[1].get().split(':')
        if len(container_name) == 1:
            container_name = container_name[0]
            tag = 'latest'
        elif len(container_name) == 2:
            tag = container_name[1]
            container_name = container_name[0]
        else:
            messagebox.showerror('Commit Container to Image', f'Container {container_name} is in an incorrect syntax for commit')
            return None

        # Getting the container object by its name
        try:
            container = client.containers.get(container_name)
        except:
            messagebox.showerror('Commit Container to Image', f'Container {container_name} not found or exist')
            return None
        
        # Checking if an image of the container already exist if not commiting and creating a new image
        try:
            client.images.get(f'{container_name}:{tag}')
            messagebox.showerror('Commit Container to Image', f'Image {container_name}:{tag} already exist')
        except docker.errors.ImageNotFound:
                container.commit(container_name, tag=tag)

# Taggin an imaging with repository account and pushing it to the docker hub registry
def tag_and_push_image():
    # Check if an image name was given or not and a repository account name
    if text_boxes[0].get() == '' or text_boxes[4] == '':
        messagebox.showerror('Push Image', "Can't push image to docker hub registry without image name and repository account")
    else:
        # Getting an image name and/or tag if given
        image = text_boxes[0].get().split(':')
        if len(image) == 1:
            image_name = image[0]
            tag = 'latest'
        elif len(image) == 2:
            tag = image[1]
            image_name = image[0]
        else:
            messagebox.showerror('Push Image', f'Image {image} is in an incorrect syntax')
            return None
        
        # Getting an image objet by name and tag
        try:
            image = client.images.get(f'{image_name}:{tag}')
        except docker.errors.ImageNotFound:
            messagebox.showerror('Push Image', f'Image {image_name}:{tag} not found or exist')
            return None

        # Trying to Tag the image with repository account name
        tagged_image_name = f'{text_boxes[4].get()}/{image_name}'
        try:
            image_tagged = image.tag(tagged_image_name, tag=tag)
        except docker.errors.APIError:
            messagebox.showerror('Push Image', f'Repository {text_boxes[4]} is in an incorrect format/syntax for tagging image')
            return None

        # Pushing the tagged image to docker hub registry
        if image_tagged:
            pushed_image = [line for line in client.images.push(tagged_image_name, tag=tag, stream=True, decode=True)]
            # Checking if push falied by error in output
            if 'error' in pushed_image[-1]:
                messagebox.showerror('Push Image', f'Failed to push image {tagged_image_name}:{tag} to docker hub\n{pushed_image[-1]["error"]}')
        else:
            messagebox.showerror('Push Image', f'Failed to tag image {image_name} as {tagged_image_name}')

# Removing an image from local docker
def remove_image():
    # Check if an image name was given or not and a repository account name
    if text_boxes[0].get() == '':
        messagebox.showerror('Remove Image', "Can't remove an image without an image name")
    else:
        image = text_boxes[0].get()
        # Trying to remove image
        try:
            client.images.remove(image)
        except docker.errors.ImageNotFound:
            messagebox.showerror('Remove Image', f'Image {image} not found or exist')
        except docker.errors.APIError:
            # If the image is referenced by existing container prompting the user to remove it forcefully or not
            response = messagebox.askquestion('Remove Image', f"Image {image} is referenced by an exisiting container and therefore can't be normally deleted.\nDo you want to force remove it?")
            if response == 'yes':
                client.images.remove(image,force=True)

# Function called by button in gui main window to call all other function
# The function checks the chosen radio button in the gui and using its name as a key to call the relavant function inside the dictionary value for the key
def submit(value):
    functions_dict = {'Get': get_container, 
                      'Run': run_container, 
                      'Start': start_container, 
                      'Stop': stop_container, 
                      'Pause': pause_container, 
                      'UnPause': unpause_container,
                      'Remove': remove_container, 
                      'Get ': get_image, 
                      'Pull': pull_image, 
                      'Commit': commit_container_to_image, 
                      'Push': tag_and_push_image,
                      'Remove ': remove_image}
    
    functions_dict[value]()

# Label with app name
tk.Label(main, text="Docker-App").grid(row=0, column=0, columnspan=3, pady=(5,5))

# Text boxses to enter the gui parametrs for docker sdk
text_boxes = [tk.Entry(main, width=75) for num in range(length)]
[text_boxes[num].grid(row=num+1, column=1, sticky='w', columnspan=2) for num in range(length)]

# Labels for instruting the user for text boxes
label_names = app_propeties
labels = [tk.Label(main, text=f"{label_names[num]}:") for num in range(length)]
[labels[num].grid(row=num+1, column=0, sticky='w') for num in range(length)]

# Frame for the container functions radio buttons
container_frame = tk.LabelFrame(main, text="Container Commands", padx=20, pady=15)
container_frame.grid(row=length+1, column=0, columnspan=2)

# Frame for the image functions radio buttons
image_frame = tk.LabelFrame(main, text="Image Commands", padx=20, pady=15)
image_frame.grid(row=length+2, column=0, columnspan=2)

# Container and image radio buttons to call their functions
container_command_list = ['Get', 'Run', 'Start', 'Stop', 'Pause', 'UnPause', 'Remove']
image_command_list = ['Get ', 'Pull', 'Commit', 'Push', 'Remove ']
option = tk.StringVar()
option.set(container_command_list[0])
[tk.Radiobutton(container_frame, text=command, variable=option, value=command).pack(side='left') for command in container_command_list]
[tk.Radiobutton(image_frame, text=command, variable=option, value=command).pack(side='left') for command in image_command_list]

# Submit button to call the functions connected the relavant radio buttons
submit_button = tk.Button(main, text="Submit", command=lambda: submit(option.get()))
submit_button.grid(row=length+3, column=0, columnspan=2, pady=(10,5), padx=10, ipadx=100, ipady=5)

# Starting the main gui window
main.mainloop()
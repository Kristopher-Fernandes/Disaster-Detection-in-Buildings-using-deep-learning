from tkinter import *
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog
import ttkbootstrap as tb
import subprocess
import time
import os
import socket
from PIL import Image, ImageTk
from twilio.rest import Client
import keys

processes = [] # Initialize the list to keep track of subprocesses
refresh_interval = 5000 #auto refresh GUI in 5 secs interval

current_file_path = os.path.abspath(__file__)  #Get the absolute path of the current file
integration2_index = current_file_path.find("Integration2") # Find the index of the "Integration2" part in the path
default_path = current_file_path[:integration2_index] + "Integration2\\" # Extract up to the end of "Integration2\\" 

f = open(f"{default_path}assets\\SafestPath\\fire_room.txt", "r")
fire_room = f.read()


root = tb.Window(themename='litera')
# root = tb.Window()
# root['bg']='#005C83'
bg = PhotoImage(file = f"{default_path}codes\\test.png")
label1 = Label( root, image = bg) 
label1.place(x = 0, y = 0) 

root.title("TTK BOOTSTRAP")
root.geometry('1500x600')

#start yolo model to scan
def start_script():
    if not is_process_running("PrimaryModel.py"):
        process = subprocess.Popen(["python", "PrimaryModel.py"])
        processes.append(process)

#generate safest paths also with the streamlit interface
def gen_path():
    if not is_process_running("SafestPath.py"):
        process = subprocess.Popen(["python", "SafestPath.py"])
        processes.append(process)

    if not is_process_running("app.py"):        
        time.sleep(2)
        process = subprocess.Popen(['streamlit', 'run', "app.py", "--server.port", "8501"])
        processes.append(process)

     # Wait for the server to start and print initial logs
    time.sleep(5)  # Adjust this depending on how quickly your app starts
    
    #port to send twillio sms
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()

    port = 8501  # Default Streamlit port or the one you usually set
    ip_address = IP
    
    url=f"Streamlit is accessible at: http://{ip_address}:{port}"
    print(f"fire caught at {fire_room} Safest path {url}")
    
    # twilio to send sms
    # client=Client(keys.account_sid,keys.auth_token)

    # message = client.messages.create(
    #     body=f"fire caught at {fire_room} Safest path {url}",
    #     from_=keys.twilio_number,
    #     to=keys.target_number
    # )

    client=Client('','') #put your sid,token

    message = client.messages.create(
        body=f"fire caught at {fire_room} Safest path {url}",
        from_='+', #put your twilio phno
        to='+' #put your number to send
    )

    print(message.body)

    message = client.messages.create(
        body=f"fire caught at {fire_room} Safest path {url}",
        from_='+',
        to='+'
    )

    print(message.body)

    #time.sleep(2)

def instance_segmentation():
    if not is_process_running("test.py"):
        process = subprocess.Popen(["python", f"{default_path}assets\\InstanceSegmentation\\test.py"])
        processes.append(process)

#stop the entire system
def stop_all_scripts():
    for process in processes:
        if process.poll() is None:  # Check if process is still running
            process.terminate()  # Send termination request
            try:
                process.wait(timeout=5)  # Wait for the process to terminate
            except subprocess.TimeoutExpired:
                process.kill()  # Force kill if not terminated within timeout
    processes.clear()  # Reset the process list

def is_process_running(script_name):
    return any(script_name in p.args[0] for p in processes if p.poll() is None)



#output images to be displayed ROI
def load_and_display_images(folder_path, frame):
    # Remove previous images/widgets from the frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Assuming a maximum of 5 images per row for example
    max_images_per_row = 5
    row = 0
    column = 0

    # Load and display images from the specified folder
    for file in os.listdir(folder_path):
        if file.lower().endswith(".jpg"):
            img = Image.open(os.path.join(folder_path, file))
            img = img.resize((200, 200), Image.Resampling.LANCZOS)  # Resize to desired size
            img = ImageTk.PhotoImage(img)
            label = tb.Label(frame, image=img)
            label.image = img  # Keep a reference to prevent garbage-collection
            label.grid(row=row, column=column, padx=20, pady=20)  # Place it in the grid

            # Caption Label (under the image)
            caption_label = tb.Label(frame, text=file)  # Use file name as caption
            caption_label.grid(row=row*2 + 1, column=column, padx=20, pady=10)

            column += 1
            if column == max_images_per_row:
                column = 0
                row += 1

    frame.after(refresh_interval, lambda: load_and_display_images(folder_path, frame))

# Function to read and display file content in tab2 for the rooms and thier ip camera details
def read_and_display_file(file_path, tab):
    # Clear existing content first
    for widget in tab.winfo_children():
        widget.destroy()

    text_area = tb.Text(tab, wrap='word')
    text_area.pack(expand=True, fill='both')

    try:
        with open(file_path, 'r') as file:
            # Insert the headings
            text_area.insert('1.0', "ip address\t\troom\n")
            
            # Process each line in the file
            for line in file:
                line = line.strip()  # Remove leading/trailing whitespaces
                if line:
                    text_area.insert(tb.END, line.replace(',', '\t\t') + '\n')
                    
    except FileNotFoundError:
        text_area.insert('1.0', f"Error: The file {file_path} was not found.")
    
    # Set back to read-only after updating
    text_area.config(state='disabled')

    # Schedule the function to be called again after the specified interval
    tab.after(refresh_interval, lambda: read_and_display_file(file_path, tab))


def Summary(file_path, tab):
    # Remove previous summary if it exists
    for widget in tab.winfo_children():
        widget.destroy()
    
    text_area = tb.Text(tab, wrap='word')
    text_area.pack(expand=True, fill='both')

    # Re-enable the widget to update content
    text_area.config(state='normal')
    text_area.delete('1.0', tb.END)  # Clear existing content

    try:
        with open(file_path, 'r') as file:
            # Insert the headings
            text_area.insert('1.0',"Summary Details")
            text_area.insert('3.0',"\n")
            
            # Process each line in the file
            for line in file:
                if line:
                    text_area.insert(tb.END, line)

        # Now read from the additional file
        text_area.insert('4.0',"\n")
        text_area.insert(tb.END, "\nMinimun Damage Cost Estimation:\n")
        with open(f'{default_path}assets\\InstanceSegmentation\\costsummary.txt', 'r') as file:
            # Process each line in the file
            for line in file:
                if line:
                    text_area.insert(tb.END, line)
                    
    except FileNotFoundError as e:
        text_area.insert('1.0', f"Error: {e}")
    
    # Set back to read-only after updating
    text_area.config(state='disabled')

    # Schedule the function to be called again after the specified interval
    tab.after(refresh_interval, lambda: Summary(file_path, tab))



    

# Function to load camera URLs (from the first code block) in tab 3
data_file = f"{default_path}codes\\camera_urls_and_nodes.txt"
def load_camera_urls():
    if not os.path.exists(data_file):
        return []
    with open(data_file, 'r') as file:
        lines = file.readlines()
    return [line.split(',')[0].strip() for line in lines]

def update_combobox():
    camera_urls = load_camera_urls()
    url_combobox['values'] = camera_urls
    if camera_urls:
        url_combobox.current(0)
    else:
        url_combobox.set('')

def add_camera():
    camera_url = simpledialog.askstring("Input", "Enter the camera URL:")
    node_mapping = simpledialog.askstring("Input", "Enter the node mapping:")
    if camera_url and node_mapping:
        with open(data_file, 'a') as file:
            file.write(f'{camera_url},{node_mapping}\n')
        messagebox.showinfo("Success", "Camera URL and node mapping added successfully.")
        update_combobox()
    else:
        messagebox.showerror("Error", "Camera URL and node mapping cannot be empty.")

def remove_camera():
    camera_url = url_combobox.get()
    if camera_url:
        with open(data_file, 'r') as file:
            lines = file.readlines()
        with open(data_file, 'w') as file:
            for line in lines:
                if not line.startswith(camera_url + ','):
                    file.write(line)
        messagebox.showinfo("Success", "Camera URL removed successfully.")
        update_combobox()
    else:
        messagebox.showerror("Error", "Please select a camera URL to remove.")
            
# GUI Elements
start_button = tb.Button(root, text="Start Script", bootstyle="success", command=start_script)
start_button.pack(pady=10)

gen_path_button = tb.Button(root, text="Generate Paths", bootstyle="warning", command=gen_path)
gen_path_button.pack(pady=10)


stop_button = tb.Button(root, text="Stop Script", bootstyle="danger", command=stop_all_scripts)
stop_button.pack(pady=10)



my_notebook = tb.Notebook(root,bootstyle='primary')
my_notebook.pack(pady=20)


s = tb.Style()
s.configure('My.TFrame',background='#00C0F0')
# Tabs
tab1 = tb.Frame(my_notebook,style='My.TFrame')
tab2 = tb.Frame(my_notebook,style='My.TFrame')
tab3 = tb.Frame(my_notebook,style='My.TFrame')
tab4 = tb.Frame(my_notebook,style='My.TFrame')
tab5 = tb.Frame(my_notebook,style='My.TFrame')


my_notebook.add(tab1, text="Output Fire")

my_notebook.add(tab2, text="Camera Urls")
my_notebook.add(tab3, text="Add Remove Rooms")
my_notebook.add(tab4, text="Summary Details")
my_notebook.add(tab5, text="Instance Segmentation")

url_label = Label(tab3, text="Select Camera URL:")
url_label.pack(pady=(10, 0))
url_combobox = tb.Combobox(tab3, width=50)
url_combobox.pack(pady=5)
update_combobox() 

add_button = tb.Button(tab3, text="Add Camera URL and Node Mapping", bootstyle="danger", command=add_camera)
add_button.pack(pady=(10, 5))

remove_button = tb.Button(tab3, text="Remove Selected Camera URL",bootstyle="danger" ,command=remove_camera)
remove_button.pack(pady=5)

instance_segmentation_button = tb.Button(tab5, text="Calculate min damage cost",bootstyle="danger" ,command=instance_segmentation)
instance_segmentation_button.pack(pady=(10, 20))


# Example usage: Load images from a folder into tab1
load_and_display_images(f"{default_path}images", tab1)

# Display the file content in tab2
read_and_display_file(f'{default_path}codes\\camera_urls_and_nodes.txt', tab2)



Summary(f'{default_path}codes\\summary.txt',tab4)



root.mainloop()





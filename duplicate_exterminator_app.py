import os
import sys
from tkinter import *
import tkinter as tk
from tkinter import font
from tkinter import filedialog 
from tkinter import messagebox
from ctypes import windll
import pygame
import threading
import subprocess
import time
from PIL import Image,ImageTk

# Dynamically getting the path, so to able to move the file around
if getattr(sys,'frozen',False):  # Check if the script is running as an executable
    script_dir=os.path.dirname(sys.executable)  # Get the executable's directory
else:
    script_dir=os.path.dirname(os.path.abspath(__file__))  # Get the script's directory in normal Python mode

def duplicate_exterminator():
    # Gets all items from the txt documents to put them in the arrays
    with open(script_dir+'\\Filters\\search_list.txt','r') as f:
        all_search_items=f.readlines()

    # To go from / to \\
    corrected_all_search_items=[]
    temp_string=''
    for i in range(len(all_search_items)):
        for letter in all_search_items[i]:
            if letter=='/':
                temp_string+='\\'
            else:
                temp_string+=letter
        corrected_all_search_items.append(temp_string.rstrip('\n'))
        temp_string=''

    with open(script_dir+'\\Filters\\exclude_list.txt','r') as f:
        all_exclude_items=f.readlines()
    
    # To go from / to \\
    corrected_all_exclude_items=[]
    for i in range(len(all_exclude_items)):
        for letter in all_exclude_items[i]:
            if letter=='/':
                temp_string+='\\'
            else:
                temp_string+=letter
        corrected_all_exclude_items.append(temp_string.rstrip('\n'))
        temp_string=''
    
    # To remove the '\n' at the end of each item
    with open(script_dir+'\\Filters\\file_types.txt','r') as f:
        all_file_type_items=f.readlines()

    corrected_all_file_type_items=[]
    for i in range(len(all_file_type_items)): 
        corrected_all_file_type_items.append('.'+all_file_type_items[i].rstrip('\n'))

    search_dirs=corrected_all_search_items
    exclude_dirs=corrected_all_exclude_items
    file_extensions=corrected_all_file_type_items
    png_file_dirs={} # Holds all png file directories


    for directory in search_dirs: # For every item in the search_dirs array
        for root,dir,files in os.walk(directory): # It searches inside the search_dirs item
            for filename in files:
                if any(filename.endswith(ext) for ext in file_extensions): # For every item in the file_extensions array
                    if any(excluded_dir in os.path.join(root,filename) for excluded_dir in exclude_dirs): # If it's inside an excluded directory, it goes to the next one
                        break

                    # It adds every new png,jpg... directory to the dictionary and if that png name already exists, it adds only the path
                    if os.path.join(filename) not in png_file_dirs:
                        png_file_dirs[os.path.join(filename)]={'paths':[os.path.join(root,filename)],'size':os.path.getsize(os.path.join(root,filename))}
                    else:
                        png_file_dirs[os.path.join(filename)]['paths'].append(os.path.join(root,filename))
                        png_file_dirs[os.path.join(filename)]['size']=os.path.getsize(os.path.join(root,filename))
    # Sorts based on size in descending order
    png_file_dirs=sorted(png_file_dirs.items(),key=lambda x:x[1]['size'],reverse=True)


    # Function to convert bytes to the appropriate size unit (KB, MB, GB, etc.)
    def convert_size(size_bytes):
        for unit in ['B','KB','MB','GB']:
            if size_bytes<1024.0:
                return str(round(size_bytes,2))+unit
            size_bytes/=1024.0
        return str(size_bytes)

    # Searches the png,jpg... files till it finds a duplicate name and holds the name,size and the multiple paths of it for later
    count=0
    duplicates=[]
    for file_info in png_file_dirs:
        file_name,info=file_info
        if len(info['paths']) >= 2:
            duplicates.append('Duplicate File Name: '+file_name+' | Size:'+convert_size(info['size']))
            duplicates.append('\nPaths:')
            for path in info['paths']:
                duplicates.append(path)
            duplicates.append('\n')

            count+=1

    duplicates.append('Duplicate count: '+str(count))
    duplicates.append('')
    duplicates.append('Press F5 To Try Again!')
    return duplicates


# Setup
windll.shcore.SetProcessDpiAwareness(1)
root=tk.Tk()
root.title('Main Menu')
root.geometry('1920x1080')
root.state('zoomed') 
root.configure(bg='#28282B')
pygame.mixer.init()

# Changing the logo next to the title in the window
icon=Image.open(script_dir+'\\Icon\\favicon1.ico')
icon=ImageTk.PhotoImage(icon)
root.iconphoto(True,icon)


# Duplicate Exterminator Label
custom_font=font.Font(family='Impact',size=75)
title_label=tk.Label(root,text='Duplicate Exterminator',font=custom_font,bg='#28282B',fg='#FF0000')
title_label.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2,y=(root.winfo_screenheight()-title_label.winfo_reqheight())/2-400)


# Search List - Exclude List - File Types
# What to do when pressing the buttons
def open_dir_dialog(which_txt,item_list):
    dir_path=filedialog.askdirectory(initialdir='Desktop')  # Opens the directory's dialog, starting from This PC, to select a file
    
    # Gets all the items of the txt document
    with open(script_dir+'\\Filters\\'+which_txt+'.txt','r') as f:
        all_items=f.readlines()

    # Displays the selected file's path in the listbox, If the user has selected a path and it's not already inputed in the listbox
    if dir_path:
        if which_txt=='search_list':
            # To not put items that are in the excluded list, in the search list (it causes a minor bug)
            # Gets excluded items and removes the '\n' at the end
            corrected_all_excluded_items=[]
            with open(script_dir+'\\Filters\\exclude_list.txt','r') as f:
                all_excluded_items=f.readlines()
                for i in range(len(all_excluded_items)):
                    corrected_all_excluded_items.append(all_excluded_items[i].rstrip('\n'))
            
            # Checks if this path is in the excluded list
            if dir_path in corrected_all_excluded_items:
                messagebox.showwarning('Error','This path is on the excluded list!')
                return
            
        if dir_path not in all_items: 
            item_list.insert(tk.END,' '+dir_path)
        else:
            messagebox.showwarning('Error','This item has already been inputted!')
            return
    
    # Writes the path to the according document that saves it
    with open(script_dir+'\\Filters\\'+which_txt+'.txt', 'a+') as f:
        f.seek(0)
        search_filters_length=len(f.readlines())
        
        if search_filters_length==0:
            f.write(dir_path)
        else:
            f.write('\n'+dir_path)


# Create item_list_1
item_list_1=tk.Listbox(root,selectmode=tk.SINGLE,width=40)
item_list_1.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2-17,y=360)

# Create a vertical scrollbar for item_list_1
y_scrollbar_1=tk.Scrollbar(root,orient=tk.VERTICAL)
y_scrollbar_1.place(in_=item_list_1,relx=1.0,relheight=1.1,bordermode='outside')

# Create a horizontal scrollbar for item_list_1
x_scrollbar_1=tk.Scrollbar(root,orient=tk.HORIZONTAL)
x_scrollbar_1.place(in_=item_list_1,rely=1.0,relwidth=1.0,bordermode='outside')

# Configure the scrollbars for item_list_1
item_list_1.config(yscrollcommand=y_scrollbar_1.set,xscrollcommand=x_scrollbar_1.set)
y_scrollbar_1.config(command=item_list_1.yview)
x_scrollbar_1.config(command=item_list_1.xview)

item_list_2=tk.Listbox(root,selectmode=tk.SINGLE,width=40)
item_list_2.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2+418,y=360)

y_scrollbar_2=tk.Scrollbar(root,orient=tk.VERTICAL)
y_scrollbar_2.place(in_=item_list_2,relx=1.0,relheight=1.1,bordermode='outside')

x_scrollbar_2=tk.Scrollbar(root,orient=tk.HORIZONTAL)
x_scrollbar_2.place(in_=item_list_2,rely=1.0,relwidth=1.0,bordermode='outside')

item_list_2.config(yscrollcommand=y_scrollbar_2.set,xscrollcommand=x_scrollbar_2.set)
y_scrollbar_2.config(command=item_list_2.yview)
x_scrollbar_2.config(command=item_list_2.xview)

item_list_3=tk.Listbox(root,selectmode=tk.SINGLE,width=40)
item_list_3.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2+855,y=360)

y_scrollbar_3=tk.Scrollbar(root,orient=tk.VERTICAL)
y_scrollbar_3.place(in_=item_list_3,relx=1.0,relheight=1.1,bordermode='outside')

x_scrollbar_3=tk.Scrollbar(root,orient=tk.HORIZONTAL)
x_scrollbar_3.place(in_=item_list_3,rely=1.0,relwidth=1.0,bordermode="outside")

item_list_3.config(yscrollcommand=y_scrollbar_3.set,xscrollcommand=x_scrollbar_3.set)
y_scrollbar_3.config(command=item_list_3.yview)
x_scrollbar_3.config(command=item_list_3.xview)


# Button to open the file dialog and select the folders to search on
button_1=tk.Button(root,text='To Search',command=lambda: open_dir_dialog('search_list',item_list_1))
button_1.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2+118,y=320)

# Button to open the file dialog and select the folders to exclude
button_2=tk.Button(root,text='Exclude',command=lambda: open_dir_dialog('exclude_list',item_list_2))
button_2.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2+560,y=320)

# Create an Entry widget for inputting file types
file_types_entry=tk.Entry(root,width=27)
file_types_entry.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2+855,y=330)

# Create a button to confirm inputting file types
def add_file_type():
    file_type=file_types_entry.get()

    if file_type!='':
        item_list_3.insert(tk.END,' '+file_type)
        file_types_entry.delete(0,tk.END)  # Clear the entry field

        with open(script_dir+'\\Filters\\file_types.txt','a+') as f:
            f.seek(0)
            file_types_length=len(f.readlines())
            
            if file_types_length==0:
                f.write(file_type)
            else:
                f.write('\n'+file_type)

# Bind the ENTER key event to add_file_type
file_types_entry.bind('<Return>',lambda event=None:add_file_type())

file_types_button = tk.Button(root,text='Add File Type',command=add_file_type)
file_types_button.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2+1098, y=320)


# Fills the listboxs with the search filters that had been inputed in the past
txt_array=['search_list','exclude_list','file_types']
item_list_array=[item_list_1,item_list_2,item_list_3]
for i in range(3):
    with open(script_dir+'\\Filters\\'+txt_array[i]+'.txt','r') as f:
        lines=f.readlines()

        if len(lines)!=0: # To avoid a blank line if the text document is empty
            for line in lines:
                item_list_array[i].insert(tk.END,' '+line)


# Creates a context menu for removing items
# What to do when right clicking and pressing delete
def remove_item(which_txt,item_list):
    # Removes item from the listbox
    selected_index=item_list.curselection()
    item_list.delete(selected_index)
    
    # Removes it from the text document by writing every line, except the one being removed
    with open(script_dir+'\\Filters\\'+which_txt+'.txt','r') as f:
        lines=f.readlines()

    with open(script_dir+'\\Filters\\'+which_txt+'.txt','w') as f:
        for line in lines:
            # Have to do it in this way instead of f.write(), to avoid some weird bug
            if line!=lines[selected_index[0]]:
                if line==lines[0]:
                    f.write(line.rstrip('\n'))
                else:
                    f.write('\n'+line.rstrip('\n'))

context_menu=tk.Menu(root,tearoff=0)
context_menu.add_command(label='Remove',command=lambda:remove_item(selected_which_txt,selected_listbox))


item_left_clicked=False
# Function to handle left-click on listbox items
def left_click_item(event):
    global item_left_clicked
    item_left_clicked=True

# Bind the left-click event to each listbox
item_list_1.bind('<Button-1>',left_click_item)
item_list_2.bind('<Button-1>',left_click_item)
item_list_3.bind('<Button-1>',left_click_item)

# Function to show the context menu and set the selected_listbox
def show_context_menu(event,which_txt,listbox):
    global selected_which_txt,selected_listbox,item_left_clicked
    if item_left_clicked: # Only if an item is left clicked, the context menu will open
        selected_which_txt=which_txt
        selected_listbox=listbox
        context_menu.post(event.x_root,event.y_root)
    item_left_clicked = False

# Bind the right-click event to show the context menu
item_list_1.bind('<Button-3>',lambda event:show_context_menu(event,'search_list',item_list_1))
item_list_2.bind('<Button-3>',lambda event:show_context_menu(event,'exclude_list',item_list_2))
item_list_3.bind('<Button-3>',lambda event:show_context_menu(event,'file_types',item_list_3))


# All the actions to do after clicking the begin the search button
def on_click():
    def task():
        root.title("Duplicate Exterminator")
        sound=pygame.mixer.Sound(script_dir+'\\Sounds\\blood_splat.mp3') 
        sound.play()


        # Removes old widgets
        begin_search_button.place_forget()
        item_list_1.place_forget()
        item_list_2.place_forget()
        item_list_3.place_forget()
        button_1.place_forget()
        button_2.place_forget()
        file_types_entry.place_forget()
        file_types_button.place_forget()


        # Loading label
        custom_font=font.Font(family='Impact',size=75)
        loading_label=tk.Label(root,text='Loading...',font=custom_font,bg='#28282B',fg='#FF0000')
        loading_label.place(x=(root.winfo_screenwidth()-loading_label.winfo_reqwidth())/2,y=(root.winfo_screenheight()-loading_label.winfo_reqheight())/2+150)

        # Plays a sound when the label is clicked
        def label_clicked(event):
            sound=pygame.mixer.Sound(script_dir+'\\Sounds\\hehe.mp3')
            sound.play()

        # Bind the label to the click event and call label_clicked
        loading_label.bind('<Button-1>',label_clicked)


        # Gets duplicate png,jpg... and removes the loading widget
        duplicates=duplicate_exterminator()
        loading_label.place_forget()


        # Create a vertical scrollbar
        y_scrollbar=tk.Scrollbar(root,orient=tk.VERTICAL)
        y_scrollbar.pack(side=tk.RIGHT,fill=tk.Y)

        # Create a horizontal scrollbar
        x_scrollbar=tk.Scrollbar(root,orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM,fill=tk.X)

        # Create a Listbox widget and it associates it with the scrollbars
        custom_font=font.Font(family='Times New Roman',size=12)
        listbox=tk.Listbox(root,font=custom_font,bg='#404243',fg='#FFFFFF',yscrollcommand=y_scrollbar.set,xscrollcommand=x_scrollbar.set)
        listbox.pack(expand=tk.YES,fill=tk.BOTH)

        # Configure the scrollbars to control the Listbox
        y_scrollbar.config(command=listbox.yview)
        x_scrollbar.config(command=listbox.xview)

        # Actions to do when clicking a listbox box
        def open_selected_folder(event):
            time.sleep(0.75) # So it doesn't open the file 2 times when clicked and then double clicked
            clicked_box=listbox.get(listbox.curselection())[5:]  # Gets the clicked box from the listbox

            corrected_clicked_box=''
            for letter in clicked_box:
                if letter=='\\':
                    corrected_clicked_box+='/'
                else:
                    corrected_clicked_box+=letter
            
            try:
                os.startfile(corrected_clicked_box) # Opens the directory if found
            except FileNotFoundError:
                pass

        # Bind the function to the left mouse click
        listbox.bind('<Double-Button-1>',open_selected_folder)


        # Actions to do when right clicking listbox box
        def open_file_location():
            selected_item=listbox.get(listbox.curselection())[5:]  # Get the selected item from the listbox
    
            try:
                # Use subprocess.Popen to open the grandparent directory in the file explorer
                subprocess.Popen(['explorer','/select,',os.path.abspath(selected_item)])
            except FileNotFoundError:
                pass

        # Create a context menu for the listbox items
        listbox_context_menu=tk.Menu(root,tearoff=0)
        listbox_context_menu.add_command(label='Open File Location',command=open_file_location)

        # Function to show the context menu when right-clicking on listbox items
        def show_listbox_context_menu(event):
            try: # To avoid useless error in the terminal, when right clicking somewhere else
                selected_item=listbox.get(listbox.curselection())[5:]  # Get the selected item from the listbox
            except:
                pass

            if os.path.exists(selected_item):  # Check if it's a directory path
                listbox_context_menu.post(event.x_root,event.y_root)

        # Bind the right-click event to show the context menu
        listbox.bind('<Button-3>',show_listbox_context_menu)


        # Inserts line by line the duplicates in the listbox
        listbox.insert(tk.END,'\n')
        for line in duplicates:
            if 'Duplicate filename:' in line:
                listbox.insert(tk.END,'     '+line)
            else:
                listbox.insert(tk.END,'     '+line)

        def reset_application():
            # Destroys the listbox and any other widgets you want to remove
            listbox.destroy()
            y_scrollbar.destroy()
            x_scrollbar.destroy()

            # Recreates the initial widgets and settings
            begin_search_button.place(x=(root.winfo_screenwidth()-begin_search_button.winfo_reqwidth())/2,y=(root.winfo_screenheight()-begin_search_button.winfo_reqheight())/2+250)
            title_label.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2, y=(root.winfo_screenheight()-title_label.winfo_reqheight())/2-400)
            item_list_1.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2, y=360)
            item_list_2.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2+430, y=360)
            item_list_3.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2+855, y=360)
            button_1.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2+125, y=320)
            button_2.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2+560, y=320)
            file_types_entry.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2+855, y=330)
            file_types_button.place(x=(root.winfo_screenwidth()-title_label.winfo_reqwidth())/2+1098, y=320)

            # Reset the window title
            root.title('Main Menu')
        
        root.bind('<F5>',lambda event:reset_application())

    thread=threading.Thread(target=task)
    thread.start()


# Change the colour of the button, when the curson is entering or leaving
def on_enter(event):
    begin_search_button.config(bg='#48494B')

def on_leave(event):
    begin_search_button.config(bg='#404243')

# Begin Search Button
custom_font=font.Font(family='Impact',size=55)
begin_search_button=tk.Button(root,text='Begin Search',font=custom_font,bg='#404243',fg='#FF0000',activebackground='#404243',activeforeground='#FF0000',relief='solid',command=on_click)

# Place the button in the middle and a little down
begin_search_button.place(x=(root.winfo_screenwidth()-begin_search_button.winfo_reqwidth())/2,y=(root.winfo_screenheight()-begin_search_button.winfo_reqheight())/2+250)

# Binds the functions to when the cursor enters or leaves the button's area
begin_search_button.bind('<Enter>',on_enter)
begin_search_button.bind('<Leave>',on_leave)

root.mainloop()

import pandas as pd
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import folium
import webbrowser
import matplotlib.pyplot as plt
from PIL import Image, ImageTk


def load_volcano(file_path, tree):
    # Load CSV and skip the first row
    df = pd.read_csv(file_path, skiprows=1, sep = ';',
                     names=["Region", "Number", "Name", "Country", "Location", "Latitude",
                            "Longitude", "Elevation", "Type", "Status", "Last Known Eruption"],
                     encoding = 'windows-1252')
    
    # Insert rows into the Treeview
    for _, row in df.iterrows():
        tree.insert("", "end", values=(
            row['Region'], row['Number'], row['Name'], row['Country'],
            row['Location'], row['Latitude'], row['Longitude'],
            row['Elevation'], row['Type'], row['Status'], row['Last Known Eruption']
        ))
    return df


def revert_tree(df, tree, btn, country_combobox):
    # Clear the Treeview
    for row in tree.get_children():
        tree.delete(row)
            
    # Populate the Treeview with filtered data
    for _, row in df.iterrows():
        tree.insert("", "end", values=(
            row['Region'], row['Number'], row['Name'], row['Country'],
            row['Location'], row['Latitude'], row['Longitude'],
            row['Elevation'], row['Type'], row['Status'], row['Last Known Eruption']
        ))

    country_combobox.set("Select a country")
    btn.destroy()
            
def filter_table_by_country(selected_country, df, tree, control_frame, country_combobox):
    # Clear current data in Treeview
    for row in tree.get_children():
        tree.delete(row)

    # Filter DataFrame and insert rows into Treeview
    filtered_df = df[df['Country'] == selected_country]
    for _, row in filtered_df.iterrows():
        tree.insert("", "end", values=(
            row['Region'], row['Number'], row['Name'], row['Country'],
            row['Location'], row['Latitude'], row['Longitude'],
            row['Elevation'], row['Type'], row['Status'], row['Last Known Eruption']
        ))
        
    # Adding a revert button to revert the table to its original state
    rvt_btn = Button(control_frame, text="Revert Tree", activebackground = "lightblue", activeforeground = "white", command = lambda : revert_tree(df, tree, rvt_btn, country_combobox))
    rvt_btn.grid(row = 0, column = 5, padx = 10, pady = 5, sticky = "e")

def create_map(latitude, longitude, volcano):
    mymap = folium.Map(location=[latitude, longitude], zoom_start=12)

    folium.Marker(
        location = [latitude, longitude],
        popup = "volcano",
        icon = folium.Icon(color = "red")
    ).add_to(mymap)
    print("creating map")
    map_file = "volcano_map.html"
    mymap.save(map_file)
    print(f"Map saved as {map_file}")
    
    # Open the map in the default web browser
    webbrowser.open(map_file)

    
def map_window(volcano, df):
    # Create the Tkinter window
    
    
    volcano_data = df[df['Name'] == volcano]
    print(volcano_data)
    print(volcano)
    if volcano_data.empty:
        print("Enter valid volcano name")
        return None, None
    else:
        # Extract latitude and longitude
        latitude = float(str(volcano_data['Latitude'].values[0]).replace(',', '.'))
        longitude = float(str(volcano_data['Longitude'].values[0]).replace(',', '.'))
        create_map(latitude, longitude, volcano)

def elevation_by_region(df):
    # Group data by region and calculate the average elevation
    avg_elevation = df.groupby('Region')['Elevation'].mean().sort_values()

    # Plotting
    plt.figure(figsize=(10, 6))
    avg_elevation.plot(kind='barh', color='skyblue')
    plt.title("Average Elevation by Region", fontsize=16)
    plt.xlabel("Average Elevation (meters)", fontsize=14)
    plt.ylabel("Regions", fontsize=14)
    plt.tight_layout()
    plt.show()
    
def clear_placeholder(event, entry, placeholder):
    if entry.get() == placeholder:
        entry.delete(0, END)
        entry.config(foreground="black")

def restore_placeholder(event, entry, placeholder):
    if entry.get() == "":
        entry.insert(0, placeholder)
        entry.config(foreground="gray")

def data_window():
    root = Tk()
    root.title("Data Analysis")
    width = 1000
    height = 700
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w / 2) - (width / 2)
    y = (screen_h / 2) - (height / 2)
    root.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    #Defining custom style
    style = ttk.Style()
    style.configure("TLabel", font=("Comic Sans MS", 14, "italic"), foreground = "purple")
    style.configure("TButton", font=("Helvetica", 12, "bold"), background="#ff6347", foreground="white")
    style.configure("TEntry", font=("Courier", 12), padding=10)
    style.configure("TFrame", background="lightyellow")
    style.configure("Vertical.TScrollbar", background="#8a2be2", troughcolor="#eee")

    

    # Frame for the table (Treeview)
    table_frame = Frame(root, padx = 10, pady = 10)
    table_frame.grid(row = 1, column = 0, sticky="nsew")

    scrollbarx = Scrollbar(table_frame, orient = HORIZONTAL)
    scrollbary = Scrollbar(table_frame, orient = VERTICAL)

    tree = ttk.Treeview(
        table_frame,
        columns = (
            "Region", "Number", "Name", "Country", "Location", "Latitude", "Longitude", 
            "Elevation", "Type", "Status", "Last Known Eruption"
        ),
        height = 20,  
        selectmode = "extended",
        yscrollcommand=scrollbary.set,
        xscrollcommand=scrollbarx.set
    )

    # Configure scrollbars
    scrollbary.config(command = tree.yview)
    scrollbarx.config(command = tree.xview)

    # Place scrollbars around the Treeview
    scrollbary.pack(side=RIGHT, fill=Y)
    scrollbarx.pack(side=BOTTOM, fill=X)

    # Pack the Treeview
    tree.pack(side=LEFT, fill=BOTH, expand=True)

    # Set table headings
    for col in [
        "Region", "Number", "Name", "Country", "Location", "Latitude", "Longitude", 
        "Elevation", "Type", "Status", "Last Known Eruption"
    ]:
        tree.heading(col, text=col, anchor=W)
        tree.column(col, minwidth=0, width=150)
    tree.column('#0', stretch=NO, minwidth=0, width=0)

    # Adjust root to make the table frame expandable
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Remove visibility to avoid focus issue
    root.withdraw()
    
    # Open file dialog and load CSV
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        df = load_volcano(file_path, tree)
        print("file_path found")

    # Frame for top controls
    control_frame = Frame(root, padx=10, pady=10)
    control_frame.grid(row = 0, column = 0, sticky = "ew")

    countries = df['Country'].dropna().unique()
    countries.sort()
    countries = [str(country).strip("'").strip() for country in countries]
    country_combobox = ttk.Combobox(control_frame, values=countries, state="readonly", width=30)
    country_combobox.set("Select a country")  # Placeholder text
    country_combobox.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    country_combobox.bind("<<ComboboxSelected>>", lambda e: filter_table_by_country(country_combobox.get(), df, tree, control_frame, country_combobox))

    # Entry 2 with placeholder
    entry_2 = ttk.Entry(control_frame, style="TEntry", foreground="gray")
    placeholder_2 = "Enter volcano"
    entry_2.insert(0, placeholder_2)
    entry_2.bind("<FocusIn>", lambda e: clear_placeholder(e, entry_2, placeholder_2))
    entry_2.bind("<FocusOut>", lambda e: restore_placeholder(e, entry_2, placeholder_2))
    entry_2.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    btn_2 = Button(control_frame, text = "Select", activebackground = "lightblue", activeforeground = "white", command = lambda: map_window(entry_2.get(), df))
    btn_2.grid(row = 1, column = 1, padx = 10, pady = 5, sticky = "w")

    btn_3 = Button(control_frame, text = "Plot average elevation grouped by Region", activebackground = "lightblue", activeforeground = "white", command = lambda: elevation_by_region(df))
    btn_3.grid(row = 2, column = 0, padx = 10, pady = 5, sticky = "w")
    
    # Restoring visibility to avoid focus issue
    root.deiconify() 
    print("running mainloop")
    root.mainloop()


def main_window():
    root = Tk()
    root.title("VOLCANO SEARCHER")
    width = 1000
    height = 700
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w / 2) - (width / 2)
    y = (screen_h / 2) - (height / 2)
    root.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    frame = Frame(root, bg="orange")
    frame.pack(fill="both", expand=True)
    
    try:
        original_img1 = Image.open(r"B:\Python uvic\Images\volcano_1.png")
        resized_img1 = original_img1.resize((320, 180))  # Resize to 150x150 pixels
        volcano_1_img = ImageTk.PhotoImage(resized_img1)

        original_img2 = Image.open(r"B:\Python uvic\Images\volcano_2.png")
        resized_img2 = original_img2.resize((320, 180))  # Resize to 150x150 pixels
        volcano_2_img = ImageTk.PhotoImage(resized_img2)
    except Exception as e:
        print(f"Error loading images: {e}")

    label_1 = Label(frame, image=volcano_1_img, bg="orange")
    label_2 = Label(frame, image=volcano_2_img, bg="orange")

    label_1.grid(row=1, column=0, padx=10, pady=10)
    label_2.grid(row=1, column=1, padx=10, pady=10)

    btn = Button(frame, text="Open Data Window", command = data_window, padx=10, pady=5, activebackground = "lightblue", activeforeground = "white")
    label_1.place(relx=0.2, rely=0.5, anchor="center")
    label_2.place(relx=0.8, rely=0.5, anchor="center")
    btn.place(relx=0.5, rely=0.1, anchor="center")

    root.mainloop()


if __name__ == "__main__":
    main_window()


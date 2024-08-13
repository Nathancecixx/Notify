import tkinter as tk
import threading
from tkinter import ttk
from tkcalendar import DateEntry
from PIL import Image, ImageDraw
from pystray import Icon, MenuItem, Menu
from html import escape
from bs4 import BeautifulSoup

class NoteifyUI:
    def __init__(self, root, reminder_handler, notes_handler):
        self.reminder_handler = reminder_handler
        self.notes_handler = notes_handler
        self.root = root
        self.root.title("Noteify")
        self.root.geometry("800x400")
        self.style = ttk.Style()

        # Set theme and customize styles
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Helvetica', 10), padding=5)
        self.style.configure('TLabel', font=('Helvetica', 10))
        self.style.configure('TEntry', font=('Helvetica', 10), padding=5)
        self.style.configure('TCheckbutton', font=('Helvetica', 10))

        # Set global font and color options
        root.option_add("*Font", "Helvetica 10")
        root.option_add("*Background", "#f0f0f0")
        root.option_add("*Foreground", "#333333")
        root.option_add("*TButton*Font", "Helvetica 10 bold")
        root.option_add("*TButton*Background", "#4CAF50")
        root.option_add("*TButton*Foreground", "#ffffff")

        # Initialize formatting state flags
        self.bold_on = False
        self.italic_on = False
        self.underline_on = False

        # Create the main layout
        self.create_main_layout()

        # Bind the window close event to minimize to tray
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        # Create a system tray icon
        self.tray_icon = None
        self.create_tray_icon()

    def create_main_layout(self):
        """Create the main layout including the note list and text area."""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Create a frame for the tree view (list of notes)
        tree_frame = ttk.Frame(main_frame, width=200)
        tree_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Create the tree view
        self.tree = ttk.Treeview(tree_frame, columns=("title",), show="tree", selectmode="browse")
        self.tree.heading("#0", text="Notes")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Load notes into the tree view
        self.load_notes()

        # Bind the tree view selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_note_select)

        # Create a frame for the text area and formatting toolbar
        editor_frame = ttk.Frame(main_frame)
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create the formatting toolbar
        self.create_formatting_toolbar(editor_frame)

        # Create the text widget for note content
        self.text_area = tk.Text(editor_frame, height=15, wrap="word", font=("Helvetica", 12))
        self.text_area.pack(pady=10, padx=10, fill="both", expand=True)

        # Add scrollbar
        scroll = ttk.Scrollbar(editor_frame, command=self.text_area.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scroll.set)

        # Create the Save button
        save_button = ttk.Button(editor_frame, text="Save", command=self.save_note)
        save_button.pack(pady=10)

        # Bind the text widget to detect changes and apply active formatting
        self.text_area.bind("<KeyRelease>", self.apply_active_formatting)

        # Bind keyboard shortcuts
        self.root.bind('<Control-b>', lambda event: self.toggle_bold())
        self.root.bind('<Control-i>', lambda event: self.toggle_italic())
        self.root.bind('<Control-u>', lambda event: self.toggle_underline())
        self.root.bind('<Control-s>', lambda event: self.save_note())

    def load_notes(self):
        """Load notes from the database and insert them into the tree view."""
        self.tree.delete(*self.tree.get_children())  # Clear existing items

        notes = self.notes_handler.fetch_notes()

        for note in notes:
            print(note)
            self.tree.insert("", "end", iid=note[0], text=note[1], values=(note[1],))

        # Add a button to create a new note
        self.tree.insert("", "end", iid="new", text="[New Note]", values=("[New Note]",))

    def on_note_select(self, event):
        """Load the selected note's content and its tags into the text area."""
        selected_items = self.tree.selection()

        if selected_items:
            selected_item = selected_items[0]

            if selected_item == "new":
                self.text_area.delete("1.0", tk.END)
            else:
                note_id = int(selected_item)
                print("Getting note id: ", note_id)
                
                # Fetch the note and its tags
                note_data, tag_data = self.notes_handler.get_note_by_id(note_id)
                print("Note: ", note_data)
                print("Tags: ", tag_data)
                
                if note_data:
                    self.text_area.delete("1.0", tk.END)
                    
                    # Insert the note content into the text area
                    self.text_area.insert(tk.END, note_data["content"])
                    
                    # Reapply tags to the text
                    for tag in tag_data:
                        tag_name = tag["tag_name"]
                        start_index = tag["start_index"]
                        end_index = tag["end_index"]
                        
                        # Configure tags if needed
                        if tag_name == "bold":
                            self.text_area.tag_configure(tag_name, font=("Helvetica", 12, "bold"))
                        elif tag_name == "italic":
                            self.text_area.tag_configure(tag_name, font=("Helvetica", 12, "italic"))
                        elif tag_name == "underline":
                            self.text_area.tag_configure(tag_name, font=("Helvetica", 12, "underline"))
                        
                        # Add the tag back to the text area
                        self.text_area.tag_add(tag_name, start_index, end_index)
        else:
            print("No item selected.")



    def create_formatting_toolbar(self, parent_frame):
        """Create a toolbar for text formatting options."""
        toolbar = ttk.Frame(parent_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Bold button
        bold_btn = ttk.Button(toolbar, text="B", width=2, command=self.toggle_bold)
        bold_btn.pack(side=tk.LEFT, padx=5)

        # Italic button
        italic_btn = ttk.Button(toolbar, text="I", width=2, command=self.toggle_italic)
        italic_btn.pack(side=tk.LEFT, padx=5)

        # Underline button
        underline_btn = ttk.Button(toolbar, text="U", width=2, command=self.toggle_underline)
        underline_btn.pack(side=tk.LEFT, padx=5)

    def toggle_bold(self):
        """Toggle bold formatting on/off."""
        self.bold_on = not self.bold_on
        self.toggle_tag("bold", ("Helvetica", 12, "bold"))

    def toggle_italic(self):
        """Toggle italic formatting on/off."""
        self.italic_on = not self.italic_on
        self.toggle_tag("italic", ("Helvetica", 12, "italic"))

    def toggle_underline(self):
        """Toggle underline formatting on/off."""
        self.underline_on = not self.underline_on
        self.toggle_tag("underline", ("Helvetica", 12, "underline"))

    def toggle_tag(self, tag_name, font):
        """Toggle a text tag on the selected text."""
        try:
            start_index = self.text_area.index(tk.SEL_FIRST)
            end_index = self.text_area.index(tk.SEL_LAST)
            current_tags = self.text_area.tag_names(start_index)

            if tag_name in current_tags:
                self.text_area.tag_remove(tag_name, start_index, end_index)
            else:
                self.text_area.tag_add(tag_name, start_index, end_index)
                self.text_area.tag_configure(tag_name, font=font)
        except tk.TclError:
            pass

    def apply_active_formatting(self, event=None):
        """Apply active formatting to newly inserted text."""
        current_index = self.text_area.index(tk.INSERT)
        if self.bold_on:
            self.text_area.tag_add("bold", current_index + "-1c", current_index)
            self.text_area.tag_configure("bold", font=("Helvetica", 12, "bold"))
        if self.italic_on:
            self.text_area.tag_add("italic", current_index + "-1c", current_index)
            self.text_area.tag_configure("italic", font=("Helvetica", 12, "italic"))
        if self.underline_on:
            self.text_area.tag_add("underline", current_index + "-1c", current_index)
            self.text_area.tag_configure("underline", font=("Helvetica", 12, "underline"))

    def save_note(self):
        """Save the current note to the database."""
        selected_items = self.tree.selection()

        if selected_items:
            selected_item = selected_items[0]
            if selected_item == "new":
                title = "Untitled Note"
            else:
                title = self.tree.item(selected_item, "text")
            
            # Get the content from the Text widget
            content = self.text_area.get("1.0", tk.END).strip()
            
            tags = []
            for tag in self.text_area.tag_names():
                tag_ranges = self.text_area.tag_ranges(tag)
                for i in range(0, len(tag_ranges), 2):
                    start_index = self.text_area.index(tag_ranges[i])
                    end_index = self.text_area.index(tag_ranges[i+1])
                    tags.append({
                        "tag_name": tag,
                        "start_index": start_index,
                        "end_index": end_index
                    })

            # Use the Notes_Handler to save the note
            if selected_item == "new":
                # Save the new note
                self.notes_handler.save_note(title, content, tags)
            else:
                # Update the existing note
                note_id = int(selected_item)
                self.notes_handler.update_note(note_id, title, content, tags)

            print(f"Note saved: {title}")

            # Refresh the notes list
            self.load_notes()
        else:
            # Handle the case for a new, unsaved note
            # title = "Untitled Note"
            # content = self.text_area.get("1.0", tk.END).strip()

            # Save the new note
            # self.notes_handler.save_note(title, content, html_content, media_files)

            # print(f"New note saved: {title}")

            # Refresh the notes list
            self.load_notes()

    def open_reminder_screen(self):
        """Open the reminder setting screen."""
        reminder_window = tk.Toplevel(self.root)
        reminder_window.title("Set Reminder")
        reminder_window.geometry("400x300")

        input_frame = ttk.Frame(reminder_window, padding="10")
        input_frame.pack(pady=10, padx=10, fill="x", expand=True)

        # Title
        title_label = ttk.Label(input_frame, text="Title:")
        title_label.grid(row=0, column=0, pady=5, padx=10, sticky="w")
        self.reminder_title_entry = ttk.Entry(input_frame)
        self.reminder_title_entry.grid(row=0, column=1, pady=5, padx=10, sticky="ew")

        # Message
        message_label = ttk.Label(input_frame, text="Message:")
        message_label.grid(row=1, column=0, pady=5, padx=10, sticky="w")
        self.reminder_message_entry = ttk.Entry(input_frame)
        self.reminder_message_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")

        # Date (using DateEntry widget)
        date_label = ttk.Label(input_frame, text="Date:")
        date_label.grid(row=2, column=0, pady=5, padx=10, sticky="w")
        self.reminder_date_entry = DateEntry(input_frame, width=12, background='darkblue',
                                             foreground='white', borderwidth=2, year=2024)
        self.reminder_date_entry.grid(row=2, column=1, pady=5, padx=10, sticky="ew")

        # Time (using Comboboxes for 12-hour format and AM/PM selector)
        time_label = ttk.Label(input_frame, text="Time:")
        time_label.grid(row=3, column=0, pady=5, padx=10, sticky="w")

        self.hour_var = tk.StringVar()
        self.minute_var = tk.StringVar()
        self.ampm_var = tk.StringVar(value="AM")

        self.hour_combobox = ttk.Combobox(input_frame, textvariable=self.hour_var, width=5)
        self.hour_combobox['values'] = [f'{i:02}' for i in range(1, 13)]
        self.hour_combobox.grid(row=3, column=1, pady=5, padx=(10, 2), sticky="w")

        self.minute_combobox = ttk.Combobox(input_frame, textvariable=self.minute_var, width=5)
        self.minute_combobox['values'] = [f'{i:02}' for i in range(0, 60)]
        self.minute_combobox.grid(row=3, column=1, pady=5, padx=(70, 2), sticky="w")

        self.ampm_combobox = ttk.Combobox(input_frame, textvariable=self.ampm_var, values=["AM", "PM"], width=5)
        self.ampm_combobox.grid(row=3, column=1, pady=5, padx=(130, 10), sticky="w")

        # Recurring checkbox
        self.recurring_var = tk.BooleanVar()
        self.recurring_checkbox = ttk.Checkbutton(input_frame, text="Recurring", variable=self.recurring_var, command=self.toggle_date_entry)
        self.recurring_checkbox.grid(row=4, column=0, pady=5, padx=10, sticky="w")

        # Set Reminder button
        set_button = ttk.Button(reminder_window, text="Set", command=self.set_reminder)
        set_button.pack(pady=10, padx=10)

        # Adjust column size for better layout
        input_frame.grid_columnconfigure(1, weight=1)

    def toggle_date_entry(self):
        """Disable the date entry and simulate a cross-out effect if recurring is checked."""
        if self.recurring_var.get():
            self.reminder_date_entry.config(state=tk.DISABLED, foreground='gray')  # Simulate cross-out by graying out
        else:
            self.reminder_date_entry.config(state=tk.NORMAL, foreground='black')

    def set_reminder(self):
        """Set the reminder using the reminder handler."""
        title = self.reminder_title_entry.get()
        message = self.reminder_message_entry.get()
        date = str(self.reminder_date_entry.get_date())  # Get the date from the DateEntry
        hour = int(self.hour_combobox.get())
        minute = self.minute_combobox.get()
        ampm = self.ampm_var.get()

        # Convert 12-hour time to 24-hour format
        if ampm == "PM" and hour != 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0
        time = f"{hour:02}:{minute}"  # Convert to 24-hour format

        recurring = self.recurring_var.get()

        # If recurring is selected, ignore the date
        if recurring:
            date = None

        print(date)
        reminder = {
            "title": title,
            "message": message,
            "date": date,
            "time": time,
            "recurring": recurring
        }

        # Here you would use the reminder handler to save the reminder
        self.reminder_handler.create_reminder(reminder)
        print(f"Reminder set: {reminder}")

    # The rest of your methods for the tray icon and background tasks...

    def hide_window(self):
        """Hide the main window and show the tray icon."""
        self.root.withdraw()
        # self.tray_icon.visible = True

    def show_window(self, icon, item):
        """Show the main window and hide the tray icon."""
        self.root.deiconify()
        # self.tray_icon.visible = False

    def on_left_click(self, item):
        self.root.deiconify()
        # self.tray_icon.visible = False

    def create_tray_icon(self):
        """Create a system tray icon with a menu."""
        # Create a simple icon for the tray (a blank white image in this case)
        image = Image.new('RGB', (64, 64), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), "N", fill=(0, 0, 0))

        # Create the menu for the tray icon
        menu = Menu(
            MenuItem(text="Open", action=self.show_window, default=True),
            MenuItem(text="Set Reminder", action=self.open_reminder_screen),
            MenuItem(text="Exit", action=self.exit_app)
        )

        # Create the tray icon
        self.tray_icon = Icon(name="Noteify", 
                              icon=image, 
                              title="Noteify", 
                              menu=menu)

        self.tray_icon.run_detached(self.on_left_click)
        self.tray_icon.visible = True


    def exit_app(self, icon, item):
        """Exit the application."""
        self.tray_icon.stop()
        self.root.quit()

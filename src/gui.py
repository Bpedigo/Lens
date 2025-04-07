import customtkinter as ctk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from src.prompt_handler import PromptHandler
from src.re_writer import Rewriter
import pyperclip
import os
import openai
import tkinter as tk
from tkinter import messagebox
import threading
from queue import Queue
from dotenv import load_dotenv

class TextEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Lens Editor")
        self.geometry("1200x800")
        self.text_size = 12
        self.current_file = None
        # Initialize PromptHandler
        self.prompt_handler = PromptHandler()
        self.setup_messages()
        self.setup_ui()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        # Initialize a single Rewriter instance
        self.rwwriter = Rewriter()
        # Create loading overlay (initially hidden)
        self.create_loading_overlay()
        # Create a queue for thread communication
        self.result_queue = Queue()
        
        # Load environment variables
        load_dotenv()

    def setup_messages(self):
        """Initialize all system message templates"""
        # Single prompt templates
        self.single_prompt1 = self.prompt_handler.read_file("button1.txt")
        self.single_prompt2 = self.prompt_handler.read_file("button3.txt")
        
        # Multiple prompt templates
        self.multiple_prompt1 = self.prompt_handler.read_file_to_array("button2.txt")
        self.multiple_prompt2 = self.prompt_handler.read_file_to_array("button4.txt")
        
        # Search prompt template
        self.search_prompt = self.prompt_handler.read_file("button5.txt")

    def setup_ui(self):
        # Create main container
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)
        
        # Logo label
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Lens", 
                                     font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10))
        
        # App settings dropdown
        self.file_menu = ctk.CTkOptionMenu(self.sidebar_frame, 
                                         values=["App Settings", "Open", "Save", "Save As", "Theme: Dark", "Theme: Light"],
                                         command=self.handle_file_operation)
        self.file_menu.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="ew")
        self.file_menu.set("App Settings")
        
        # Analysis section
        self.analysis_label = ctk.CTkLabel(self.sidebar_frame, text="Analysis Tools",
                                         font=ctk.CTkFont(weight="bold"))
        self.analysis_label.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 10))
        
        # Analysis buttons
        self.create_analysis_buttons()
        
        # Add Copy and Clear buttons at the bottom of the sidebar
        self.copy_button = ctk.CTkButton(self.sidebar_frame, text="Copy",
                                       command=self.copy_to_clipboard,
                                       width=120, height=35,
                                       font=("Arial", 12))
        self.copy_button.grid(row=8, column=0, columnspan=2, padx=20, pady=(10, 5), sticky="ew")
        
        self.clear_button = ctk.CTkButton(self.sidebar_frame, text="Clear",
                                        command=self.clear_text,
                                        width=120, height=35,
                                        font=("Arial", 12),
                                        fg_color="#FF4444")  # Red color for clear button
        self.clear_button.grid(row=9, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="ew")
        
        # Main text area with tabs
        self.text_frame = ctk.CTkFrame(self)
        self.text_frame.grid(row=0, column=1, padx=(0, 0), pady=(0, 0), sticky="nsew")
        self.text_frame.grid_columnconfigure(0, weight=1)
        self.text_frame.grid_rowconfigure(0, weight=1)
        
        # Create tab view
        self.tab_view = ctk.CTkTabview(self.text_frame)
        self.tab_view.grid(row=0, column=0, padx=0, pady=(0, 20), sticky="nsew")
        
        # Add tabs
        self.original_tab = self.tab_view.add("Original")
        self.responses_tab = self.tab_view.add("Responses")
        
        # Configure tab grid
        self.original_tab.grid_columnconfigure(0, weight=1)
        self.original_tab.grid_rowconfigure(0, weight=1)
        self.responses_tab.grid_columnconfigure(0, weight=1)
        self.responses_tab.grid_rowconfigure(0, weight=1)
        
        # Create text editors for each tab
        self.original_editor = ctk.CTkTextbox(self.original_tab, wrap="word")
        self.original_editor.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        
        self.responses_editor = ctk.CTkTextbox(self.responses_tab, wrap="word")
        self.responses_editor.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        
        # Bottom controls frame
        self.controls_frame = ctk.CTkFrame(self.text_frame)
        self.controls_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Font size controls
        self.font_frame = ctk.CTkFrame(self.controls_frame)
        self.font_frame.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        self.font_size_label = ctk.CTkLabel(self.font_frame, text="Font Size:")
        self.font_size_label.pack(side="left", padx=5)
        
        self.font_size_slider = ctk.CTkSlider(self.font_frame, from_=8, to=24, 
                                            number_of_steps=16,
                                            command=self.change_font_size)
        self.font_size_slider.pack(side="left", padx=5, fill="x", expand=True)
        self.font_size_slider.set(12)

    def handle_file_operation(self, choice):
        if choice == "Open":
            self.open_file()
        elif choice == "Save":
            self.save_file()
        elif choice == "Save As":
            self.save_file_as()
        elif choice.startswith("Theme:"):
            theme = choice.split(": ")[1].lower()
            self.change_theme(theme)
        self.file_menu.set("App Settings")  # Reset dropdown
        
    def save_file_as(self):
        file_path = asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.original_editor.get("1.0", "end-1c"))
            self.title(f"Lens Editor - {os.path.basename(file_path)}")
        
    def create_analysis_buttons(self):
        """Create and configure analysis buttons"""
        # Define button configurations
        buttons = [
            {
                "text": "Single Prompt 1",
                "command": lambda: self.analyze_text(self.single_prompt1),
                "color": "#1f538d",  # Blue for single prompts
                "group": "single"
            },
            {
                "text": "Single Prompt 2",
                "command": lambda: self.analyze_text(self.single_prompt2),
                "color": "#1f538d",  # Blue for single prompts
                "group": "single"
            },
            {
                "text": "Multiple Prompt 1",
                "command": lambda: self.analyze_multiple_prompts(self.multiple_prompt1),
                "color": "#8b1f8d",  # Purple for multiple prompts
                "group": "multiple"
            },
            {
                "text": "Multiple Prompt 2",
                "command": lambda: self.analyze_multiple_prompts(self.multiple_prompt2),
                "color": "#8b1f8d",  # Purple for multiple prompts
                "group": "multiple"
            }
        ]
        
        # Create buttons in a single column
        for i, button_config in enumerate(buttons):
            # Action button
            action_button = ctk.CTkButton(
                self.sidebar_frame,
                text=button_config["text"],
                command=button_config["command"],
                height=35,
                font=("Arial", 12),
                fg_color=button_config["color"],
                hover_color=self.adjust_color(button_config["color"], -20)  # Darker on hover
            )
            action_button.grid(row=i+3, column=0, padx=(20, 2), pady=(0, 2), sticky="ew")
            
            # Edit button
            edit_button = ctk.CTkButton(
                self.sidebar_frame,
                text="Edit",
                command=lambda t=button_config["text"]: self.edit_analysis(t),
                height=25,
                width=60,
                font=("Arial", 10),
                fg_color="#FF8C00"  # Orange color for edit buttons
            )
            edit_button.grid(row=i+3, column=1, padx=(2, 20), pady=(0, 2), sticky="e")

    def adjust_color(self, color, amount):
        """Adjust a hex color by a given amount"""
        # Convert hex to RGB
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # Adjust each component
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def edit_analysis(self, analysis_type):
        """Open a popup window to edit the prompt for the specified analysis type.
        
        Args:
            analysis_type (str): The type of analysis (e.g., "Single Prompt 1")
        """
        # Create popup window
        popup = ctk.CTkToplevel(self)
        popup.title(f"Edit {analysis_type} Prompt")
        popup.geometry("600x400")
        popup.transient(self)  # Make window modal
        popup.grab_set()  # Make window modal
        
        # Create main frame
        main_frame = ctk.CTkFrame(popup)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add title
        title_label = ctk.CTkLabel(main_frame, 
                                 text=f"Edit {analysis_type} Prompt",
                                 font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(0, 10))
        
        # Add instructions for multiple prompts
        if analysis_type.startswith("Multiple"):
            instructions = ctk.CTkLabel(main_frame,
                                      text="Use '--------' to separate different prompts",
                                      font=ctk.CTkFont(size=12))
            instructions.pack(pady=(0, 5))
        
        # Create text editor
        text_editor = ctk.CTkTextbox(main_frame, wrap="word")
        text_editor.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Load current prompt
        try:
            if analysis_type.startswith("Multiple"):
                if analysis_type == "Multiple Prompt 1":
                    current_prompt = "\n--------\n".join(self.multiple_prompt1)
                else:
                    current_prompt = "\n--------\n".join(self.multiple_prompt2)
            else:
                if analysis_type == "Single Prompt 1":
                    current_prompt = self.prompt_handler.read_file("button1.txt")
                else:
                    current_prompt = self.prompt_handler.read_file("button3.txt")
            text_editor.insert("1.0", current_prompt)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load prompt: {str(e)}")
            popup.destroy()
            return
        
        # Create button frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Save button
        def save_prompt():
            try:
                new_prompt = text_editor.get("1.0", "end-1c")
                if analysis_type.startswith("Multiple"):
                    if analysis_type == "Multiple Prompt 1":
                        with open(self.prompt_handler.prompts_dir / "button2.txt", "w", encoding="utf-8") as f:
                            f.write(new_prompt)
                        self.multiple_prompt1 = self.prompt_handler.read_file_to_array("button2.txt")
                    else:
                        with open(self.prompt_handler.prompts_dir / "button4.txt", "w", encoding="utf-8") as f:
                            f.write(new_prompt)
                        self.multiple_prompt2 = self.prompt_handler.read_file_to_array("button4.txt")
                else:
                    if analysis_type == "Single Prompt 1":
                        with open(self.prompt_handler.prompts_dir / "button1.txt", "w", encoding="utf-8") as f:
                            f.write(new_prompt)
                        self.single_prompt1 = self.prompt_handler.read_file("button1.txt")
                    else:
                        with open(self.prompt_handler.prompts_dir / "button3.txt", "w", encoding="utf-8") as f:
                            f.write(new_prompt)
                        self.single_prompt2 = self.prompt_handler.read_file("button3.txt")
                messagebox.showinfo("Success", "Prompt saved successfully!")
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save prompt: {str(e)}")
        
        save_button = ctk.CTkButton(button_frame, text="Save",
                                  command=save_prompt,
                                  width=100)
        save_button.pack(side="right", padx=5)
        
        # Clear button
        def clear_editor():
            text_editor.delete("1.0", "end")
        
        clear_button = ctk.CTkButton(button_frame, text="Clear",
                                   command=clear_editor,
                                   width=100,
                                   fg_color="#FF4444")
        clear_button.pack(side="right", padx=5)
        
        # Cancel button
        cancel_button = ctk.CTkButton(button_frame, text="Cancel",
                                    command=popup.destroy,
                                    width=100)
        cancel_button.pack(side="right", padx=5)
        
        # Center the popup window
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

    def change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme.lower())
        
    def change_font_size(self, size):
        self.text_size = int(size)
        self.original_editor.configure(font=("Arial", self.text_size))
        self.responses_editor.configure(font=("Arial", self.text_size))
        
    def open_file(self):
        file_path = askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            with open(file_path, 'r', encoding='utf-8') as file:
                self.original_editor.delete("1.0", "end")
                self.original_editor.insert("1.0", file.read())
            self.title(f"Lens Editor - {os.path.basename(file_path)}")
            
    def save_file(self):
        if self.current_file:
            file_path = self.current_file
        else:
            file_path = asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
        if file_path:
            self.current_file = file_path
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.original_editor.get("1.0", "end-1c"))
            self.title(f"Lens Editor - {os.path.basename(file_path)}")
            
    def copy_to_clipboard(self):
        """Copy text from the active tab to clipboard"""
        active_tab = self.tab_view.get()
        if active_tab == "Original":
            text = self.original_editor.get("1.0", "end-1c")
        else:
            text = self.responses_editor.get("1.0", "end-1c")
        pyperclip.copy(text)
        
    def create_loading_overlay(self):
        """Create a loading overlay that can be shown during API calls"""
        self.loading_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.loading_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        
        # Create a semi-transparent background using a dark color
        self.loading_bg = ctk.CTkFrame(self.loading_frame, fg_color="#000000")
        self.loading_bg.pack(fill="both", expand=True)
        
        # Create loading content
        self.loading_content = ctk.CTkFrame(self.loading_bg, fg_color="transparent")
        self.loading_content.place(relx=0.5, rely=0.5, anchor="center")
        
        # Loading text
        self.loading_label = ctk.CTkLabel(self.loading_content, 
                                        text="Processing",
                                        font=("Arial", 16, "bold"))
        self.loading_label.pack(pady=(0, 10))
        
        # Progress text for multiple prompts
        self.progress_label = ctk.CTkLabel(self.loading_content,
                                         text="",
                                         font=("Arial", 12))
        self.progress_label.pack(pady=(0, 10))
        
        # Spinner label for animation
        self.spinner_label = ctk.CTkLabel(self.loading_content,
                                        text="",
                                        font=("Arial", 24))  # Larger font for spinner
        self.spinner_label.pack(pady=(0, 10))
        
        # Initially hide the overlay
        self.loading_frame.grid_remove()
        
        # Animation state
        self.animation_running = False
        self.spinner_index = 0
        # Unicode spinner characters
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def animate_spinner(self):
        """Animate the loading spinner"""
        if not self.animation_running:
            return
            
        self.spinner_label.configure(text=self.spinner_chars[self.spinner_index])
        self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)
        self.update_idletasks()  # Force update of the GUI
        self.after(100, self.animate_spinner)  # Schedule next update

    def show_loading(self):
        """Show the loading overlay and start the animation"""
        self.loading_frame.grid()
        self.animation_running = True
        self.spinner_index = 0
        self.animate_spinner()
        self.update_idletasks()  # Force update of the GUI

    def hide_loading(self):
        """Hide the loading overlay and stop the animation"""
        self.animation_running = False
        self.loading_frame.grid_remove()
        self.update_idletasks()  # Force update of the GUI

    def analyze_text(self, prompt_template):
        """Analyze text using the specified prompt template.
        
        Args:
            prompt_template (str): The system message to be used for analysis.
        """
        try:
            # Get the user's text from the original editor
            user_text = self.original_editor.get("1.0", "end-1c")
            if not user_text.strip():
                messagebox.showwarning("Warning", "Please enter some text to analyze.")
                return
            
            # Show loading overlay
            self.show_loading()
            
            # Start the analysis in a separate thread
            thread = threading.Thread(target=self._analyze_text_thread, 
                                   args=(prompt_template, user_text))
            thread.daemon = True  # Thread will exit when main program exits
            thread.start()
            
            # Start checking for results
            self.check_analysis_result()
            
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Failed to analyze text: {str(e)}")

    def _analyze_text_thread(self, prompt_template, user_text):
        """Run the analysis in a separate thread"""
        try:
            # Clear previous conversation
            self.rwwriter.clear_conversation()
            
            # Process the message
            self.rwwriter.append_system_message(prompt_template)
            self.rwwriter.append_user_message(user_text)
            
            # Get the analysis from OpenAI
            response = self.rwwriter.rewriter("gpt-4-turbo")
            
            # Put the result in the queue
            self.result_queue.put(("success", response))
            
        except Exception as e:
            self.result_queue.put(("error", str(e)))

    def check_analysis_result(self):
        """Check for analysis results and update the UI"""
        try:
            # Check if there's a result in the queue
            if not self.result_queue.empty():
                status, result = self.result_queue.get()
                
                # Hide loading overlay
                self.hide_loading()
                
                if status == "success":
                    if result:
                        # Append the new result to the responses tab
                        current_text = self.responses_editor.get("1.0", "end-1c")
                        if current_text.strip():
                            self.responses_editor.insert("end", "\n\n--------\n\n")
                        self.responses_editor.insert("end", result)
                        
                        # Switch to the responses tab
                        self.tab_view.set("Responses")
                    else:
                        messagebox.showwarning("Warning", "No response received from the analysis.")
                else:
                    messagebox.showerror("Error", f"Failed to analyze text: {result}")
                
                return  # Stop checking for results
            
            # If no result yet, check again in 100ms
            self.after(100, self.check_analysis_result)
            
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Failed to process result: {str(e)}")

    def analyze_multiple_prompts(self, prompts):
        """Analyze text using multiple prompts in sequence.
        
        Args:
            prompts (list): List of system messages to be used for analysis.
        """
        try:
            # Get the user's text from the original editor
            user_text = self.original_editor.get("1.0", "end-1c")
            if not user_text.strip():
                messagebox.showwarning("Warning", "Please enter some text to analyze.")
                return
            
            # Show loading overlay
            self.show_loading()
            
            # Start the analysis in a separate thread
            thread = threading.Thread(target=self._analyze_multiple_prompts_thread, 
                                   args=(prompts, user_text))
            thread.daemon = True
            thread.start()
            
            # Start checking for results
            self.check_analysis_result()
            
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Failed to analyze text: {str(e)}")

    def update_progress(self, current, total):
        """Update the progress label with current prompt status"""
        self.progress_label.configure(text=f"Processing prompt {current} of {total}")
        self.update_idletasks()

    def _analyze_multiple_prompts_thread(self, prompts, user_text):
        """Run the multiple prompts analysis in a separate thread"""
        try:
            total_prompts = len(prompts)
            responses = []
            
            # Process each prompt in sequence
            for i, prompt in enumerate(prompts, 1):
                # Update progress in the main thread
                self.after(0, self.update_progress, i, total_prompts)
                
                # Clear previous conversation
                self.rwwriter.clear_conversation()
                
                # Process the current prompt
                self.rwwriter.append_system_message(prompt)
                self.rwwriter.append_user_message(user_text)
                response = self.rwwriter.rewriter("gpt-4-turbo")
                if response:
                    responses.append(response)
            
            # Combine all responses with a separator
            if responses:
                final_response = "\n\n--------\n\n".join(responses)
                self.result_queue.put(("success", final_response))
            else:
                self.result_queue.put(("error", "No responses received from the analysis."))
            
        except Exception as e:
            self.result_queue.put(("error", str(e)))

    def clear_text(self):
        """Clear the text editor content"""
        self.original_editor.delete("1.0", "end")
        self.responses_editor.delete("1.0", "end")

    def test_web_search(self):
        """Test the web search functionality"""
        try:
            # Get the user's text from the original editor
            search_query = self.original_editor.get("1.0", "end-1c")
            if not search_query.strip():
                messagebox.showwarning("Warning", "Please enter a search query.")
                return
            
            # Show loading overlay
            self.show_loading()
            
            # Start the web search in a separate thread
            thread = threading.Thread(target=self._test_web_search_thread, 
                                   args=(search_query,))
            thread.daemon = True
            thread.start()
            
            # Start checking for results
            self.check_analysis_result()
            
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Failed to perform web search: {str(e)}")

    def _test_web_search_thread(self, search_query):
        """Run the web search in a separate thread"""
        try:
            # Perform web search
            results = self.rwwriter.web_search(search_query, max_results=5)
            
            # Format results for display
            if results:
                formatted_results = "Web Search Results:\n\n"
                for i, result in enumerate(results, 1):
                    formatted_results += f"Result {i}:\n{result}\n\n"
                self.result_queue.put(("success", formatted_results))
            else:
                self.result_queue.put(("error", "No results found. The web search tool might not be available or the query returned no results."))
            
        except Exception as e:
            self.result_queue.put(("error", f"Web search failed: {str(e)}"))

    def smart_search(self):
        """Perform a smart search using the input text"""
        try:
            # Get the user's text from the original editor
            user_text = self.original_editor.get("1.0", "end-1c")
            if not user_text.strip():
                messagebox.showwarning("Warning", "Please enter some text to analyze.")
                return
            
            # Show loading overlay
            self.show_loading()
            
            # Start the smart search in a separate thread
            thread = threading.Thread(target=self._smart_search_thread, 
                                   args=(user_text,))
            thread.daemon = True
            thread.start()
            
            # Start checking for results
            self.check_analysis_result()
            
        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"Failed to perform smart search: {str(e)}")

    def _smart_search_thread(self, user_text):
        """Run the smart search in a separate thread"""
        try:
            # First, generate a search query from the input text
            search_query = self.rwwriter.analyze_text(user_text, self.search_prompt)
            
            # Then perform web search with the generated query
            results = self.rwwriter.web_search(search_query)
            
            # Format results for display
            if results:
                formatted_results = "Smart Search Results:\n\n"
                for result in results:
                    formatted_results += f"Title: {result['title']}\n"
                    formatted_results += f"🔗 {result['link']}\n"
                    formatted_results += f"Snippet: {result['snippet']}\n\n"
                self.result_queue.put(("success", formatted_results))
            else:
                self.result_queue.put(("error", "No results found. The web search tool might not be available or the query returned no results."))
            
        except Exception as e:
            self.result_queue.put(("error", f"Smart search failed: {str(e)}"))

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    app = TextEditorApp()
    app.mainloop()



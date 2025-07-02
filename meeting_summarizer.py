import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import os
import threading
from pathlib import Path
from vtt_parser import VTTParser
from gemini_summarizer import GeminiSummarizer, Config

class MeetingSummarizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Meeting Summarizer")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize components
        self.parser = VTTParser()
        self.summarizer = None
        self.selected_files = []
        
        # Try to load API key
        self.api_key = Config.load_api_key_from_file() or os.getenv('GEMINI_API_KEY')
        
        self.setup_ui()
        self.check_api_key()
        
    def setup_ui(self):
        """Create the main UI components"""
        
        # Title
        title_label = tk.Label(
            self.root, 
            text="AI Meeting Summarizer", 
            font=("Arial", 18, "bold"),
            bg='#f0f0f0',
            fg='#333'
        )
        title_label.pack(pady=10)
        
        # API Status frame
        api_frame = ttk.LabelFrame(self.root, text="API Configuration", padding=10)
        api_frame.pack(fill='x', padx=20, pady=5)
        
        self.api_status_label = tk.Label(
            api_frame, 
            text="🔴 API Key Not Configured", 
            bg='#f0f0f0',
            fg='red'
        )
        self.api_status_label.pack(side='left')
        
        self.setup_api_btn = ttk.Button(
            api_frame, 
            text="Setup API Key", 
            command=self.setup_api_key
        )
        self.setup_api_btn.pack(side='right')
        
        # File selection frame
        file_frame = ttk.LabelFrame(self.root, text="Select VTT Files", padding=10)
        file_frame.pack(fill='x', padx=20, pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill='x')
        
        # Select files button
        self.select_btn = ttk.Button(
            button_frame, 
            text="Select VTT Files", 
            command=self.select_files
        )
        self.select_btn.pack(side='left', padx=(0, 10))
        
        # Clear selection button
        self.clear_btn = ttk.Button(
            button_frame, 
            text="Clear Selection", 
            command=self.clear_selection
        )
        self.clear_btn.pack(side='left')
        
        # Process button
        self.process_btn = ttk.Button(
            button_frame, 
            text="🤖 AI Summarize", 
            command=self.process_files,
            state='disabled'
        )
        self.process_btn.pack(side='right')
        
        # Selected files display
        self.files_label = tk.Label(
            file_frame, 
            text="No files selected", 
            bg='white',
            relief='sunken',
            anchor='w',
            padx=10,
            pady=5
        )
        self.files_label.pack(fill='x', pady=(10, 0))
        
        # Progress bar
        self.progress_frame = ttk.Frame(self.root)
        self.progress_frame.pack(fill='x', padx=20, pady=5)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            mode='indeterminate'
        )
        self.progress_bar.pack(fill='x')
        
        self.status_label = tk.Label(
            self.progress_frame, 
            text="Ready", 
            bg='#f0f0f0'
        )
        self.status_label.pack(pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.root, text="AI-Generated Summaries", padding=10)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(
            results_frame, 
            wrap=tk.WORD,
            font=("Arial", 11),
            bg='white'
        )
        self.results_text.pack(fill='both', expand=True)
        
        # Save results button
        self.save_btn = ttk.Button(
            results_frame, 
            text="💾 Save Summaries", 
            command=self.save_results,
            state='disabled'
        )
        self.save_btn.pack(pady=(10, 0))
        
        # Initially hide progress bar
        self.progress_bar.pack_forget()
        
    def check_api_key(self):
        """Check if API key is configured and update UI"""
        if self.api_key:
            try:
                self.summarizer = GeminiSummarizer(self.api_key)
                if self.summarizer.test_api_connection():
                    self.api_status_label.config(
                        text="🟢 API Connected", 
                        fg='green'
                    )
                    self.setup_api_btn.config(text="Change API Key")
                else:
                    self.api_status_label.config(
                        text="🔴 API Key Invalid", 
                        fg='red'
                    )
            except Exception as e:
                self.api_status_label.config(
                    text="🔴 API Error", 
                    fg='red'
                )
        
    def setup_api_key(self):
        """Setup or change API key"""
        dialog_text = """
To use AI summarization, you need a free Google Gemini API key.

Steps to get your API key:
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API key"
4. Copy the API key

Enter your API key below:
        """
        
        api_key = simpledialog.askstring(
            "Gemini API Key", 
            dialog_text,
            show='*'  # Hide the API key input
        )
        
        if api_key and api_key.strip():
            self.api_key = api_key.strip()
            
            # Test the API key
            try:
                test_summarizer = GeminiSummarizer(self.api_key)
                if test_summarizer.test_api_connection():
                    self.summarizer = test_summarizer
                    
                    # Save API key
                    save_key = messagebox.askyesno(
                        "Save API Key", 
                        "API key is valid! Save it for future use?"
                    )
                    if save_key:
                        Config.save_api_key_to_file(self.api_key)
                    
                    self.check_api_key()
                    messagebox.showinfo("Success", "API key configured successfully!")
                    
                else:
                    messagebox.showerror("Invalid API Key", "The API key is not valid. Please check and try again.")
                    
            except Exception as e:
                messagebox.showerror("API Error", f"Error testing API key:\n{str(e)}")
        
    def select_files(self):
        """Open file dialog to select VTT files"""
        files = filedialog.askopenfilenames(
            title="Select VTT Files",
            filetypes=[
                ("VTT files", "*.vtt"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            self.selected_files = list(files)
            self.update_files_display()
            self.update_process_button_state()
        
    def clear_selection(self):
        """Clear selected files"""
        self.selected_files = []
        self.update_files_display()
        self.update_process_button_state()
        self.results_text.delete(1.0, tk.END)
        self.save_btn.config(state='disabled')
        
    def update_files_display(self):
        """Update the display of selected files"""
        if not self.selected_files:
            self.files_label.config(text="No files selected")
        else:
            file_names = [Path(f).name for f in self.selected_files]
            if len(file_names) <= 3:
                display_text = ", ".join(file_names)
            else:
                display_text = f"{', '.join(file_names[:3])} ... (+{len(file_names)-3} more)"
            
            self.files_label.config(text=f"Selected: {display_text}")
    
    def update_process_button_state(self):
        """Enable/disable process button based on conditions"""
        if self.selected_files and self.summarizer:
            self.process_btn.config(state='normal')
        else:
            self.process_btn.config(state='disabled')
    
    def process_files(self):
        """Process selected VTT files and generate AI summaries"""
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select VTT files first.")
            return
            
        if not self.summarizer:
            messagebox.showwarning("No API Key", "Please setup your Gemini API key first.")
            return
        
        # Disable buttons during processing
        self.process_btn.config(state='disabled')
        self.select_btn.config(state='disabled')
        self.clear_btn.config(state='disabled')
        
        # Show progress bar
        self.progress_bar.pack(fill='x')
        self.progress_bar.start(10)
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Start processing in background thread
        thread = threading.Thread(target=self._process_files_worker)
        thread.daemon = True
        thread.start()
    
    def _process_files_worker(self):
        """Worker function to process files and generate AI summaries"""
        all_results = []
        
        try:
            for i, file_path in enumerate(self.selected_files):
                # Update status
                file_name = Path(file_path).name
                self.root.after(0, lambda: self.status_label.config(text=f"Processing: {file_name}"))
                
                # Parse VTT file
                parsed_data = self.parser.parse_vtt_file(file_path)
                
                if parsed_data:
                    # Get conversation text and stats
                    conversation_text = self.parser.get_conversation_text(parsed_data)
                    stats = self.parser.get_meeting_stats(parsed_data)
                    
                    # Update status for AI processing
                    self.root.after(0, lambda: self.status_label.config(text=f"AI Summarizing: {file_name}"))
                    
                    # Generate AI summary
                    ai_summary = self.summarizer.summarize_meeting(conversation_text, stats)
                    
                    # Format result
                    result = self._format_ai_summary(file_name, parsed_data, stats, ai_summary)
                    all_results.append(result)
                    
                    # Update results display
                    self.root.after(0, lambda r=result: self._append_result(r))
                else:
                    error_msg = f"❌ Failed to parse: {file_name}\n\n"
                    all_results.append(error_msg)
                    self.root.after(0, lambda e=error_msg: self._append_result(e))
            
            # Processing complete
            self.root.after(0, self._processing_complete)
            
        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Processing Error", error_msg))
            self.root.after(0, self._processing_complete)
    
    def _format_ai_summary(self, file_name, parsed_data, stats, ai_summary):
        """Format the AI summary with meeting metadata"""
        result = f"""
{'='*70}
📄 MEETING: {file_name}
{'='*70}

📊 MEETING INFO:
Duration: {stats.get('duration', 'Unknown')}
Participants: {', '.join(stats.get('speaker_word_counts', {}).keys())}
Total Entries: {stats.get('total_entries', 0)}

🤖 AI SUMMARY:
{ai_summary}

{'='*70}

"""
        return result
    
    def _append_result(self, text):
        """Append text to results area"""
        self.results_text.insert(tk.END, text)
        self.results_text.see(tk.END)
        self.save_btn.config(state='normal')
    
    def _processing_complete(self):
        """Clean up after processing is complete"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.status_label.config(text="✅ AI summarization complete!")
        
        # Re-enable buttons
        self.update_process_button_state()
        self.select_btn.config(state='normal')
        self.clear_btn.config(state='normal')
    
    def save_results(self):
        """Save results to a text file"""
        if not self.results_text.get(1.0, tk.END).strip():
            messagebox.showwarning("No Results", "No results to save.")
            return
        
        # Generate default filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"meeting_summaries_{timestamp}.txt"
        
        file_path = filedialog.asksaveasfilename(
            title="Save Meeting Summaries",
            defaultextension=".txt",
            initialvalue=default_name,
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                messagebox.showinfo("Saved", f"Meeting summaries saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file:\n{str(e)}")


def main():
    root = tk.Tk()
    app = MeetingSummarizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
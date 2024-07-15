import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import math
import textwrap
from PIL import Image
import time
import threading

FILENAME = "nested_dictionary.json"

class RevisionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Concept Revision App")
        self.master.geometry("1000x700")

        self.is_rendering = False
        self.export_after_render = False
        self.export_format = None

        self.data = self.load_data()
        self.create_widgets()
        self.add_search_functionality()
        self.create_mind_map_view()


    # ... (load_data and save_data methods remain the same)
    def load_data(self):
        if os.path.exists(FILENAME):
            with open(FILENAME, 'r') as file:
                return json.load(file)
        return {}

    def save_data(self):
        with open(FILENAME, 'w') as file:
            json.dump(self.data, file, indent=2)

    def on_tree_double_click(self, event):
        item = self.tree.selection()[0]
        key = self.tree.item(item, "text")
        self.show_concept_details(key)

    def create_widgets(self):
        # Main frame to hold everything
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame for search functionality
        self.search_frame = ttk.Frame(main_frame)
        self.search_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Notebook for different views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create frames for different views
        self.tree_frame = ttk.Frame(self.notebook)
        self.mind_map_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.tree_frame, text="Tree View")
        self.notebook.add(self.mind_map_frame, text="Mind Map")

        # Paned window to split the UI in Tree View
        self.paned_window = ttk.PanedWindow(self.tree_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Left frame for tree view
        left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(left_frame, weight=1)

        # Tree view for displaying the nested structure
        self.tree = ttk.Treeview(left_frame)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # Scrollbar for the tree view
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Right frame for concept details
        self.right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame, weight=1)

        # Frame for input fields and buttons
        self.input_frame = ttk.Frame(main_frame)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Initial key input
        ttk.Label(self.input_frame, text="Key:").grid(row=0, column=0, padx=5, pady=5)
        self.key_entry = ttk.Entry(self.input_frame)
        self.key_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.input_frame, text="Enter", command=self.enter_key).grid(row=0, column=2, padx=5, pady=5)

        self.refresh_tree()

    def add_search_functionality(self):
        # Add search entry and button
        self.search_entry = ttk.Entry(self.search_frame)
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        ttk.Button(self.search_frame, text="Search", command=self.perform_search).pack(side=tk.RIGHT)


    def create_mind_map_view(self):
        # Create a frame to hold the canvas and scrollbars
        self.mind_map_frame = ttk.Frame(self.mind_map_frame)
        self.mind_map_frame.pack(fill=tk.BOTH, expand=True)

        # Create canvas and scrollbars
        self.mind_map_canvas = tk.Canvas(self.mind_map_frame)
        self.x_scrollbar = ttk.Scrollbar(self.mind_map_frame, orient=tk.HORIZONTAL, command=self.mind_map_canvas.xview)
        self.y_scrollbar = ttk.Scrollbar(self.mind_map_frame, orient=tk.VERTICAL, command=self.mind_map_canvas.yview)

        # Configure canvas
        self.mind_map_canvas.configure(xscrollcommand=self.x_scrollbar.set, yscrollcommand=self.y_scrollbar.set)
        self.mind_map_canvas.bind('<Configure>', self.on_canvas_configure)

        # Pack canvas and scrollbars
        self.mind_map_canvas.grid(row=0, column=0, sticky="nsew")
        self.y_scrollbar.grid(row=0, column=1, sticky="ns")
        self.x_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure grid weights
        self.mind_map_frame.grid_rowconfigure(0, weight=1)
        self.mind_map_frame.grid_columnconfigure(0, weight=1)

        # Create a frame inside the canvas to hold the matplotlib figure
        self.mind_map_inner_frame = ttk.Frame(self.mind_map_canvas)
        self.canvas_window = self.mind_map_canvas.create_window((0, 0), window=self.mind_map_inner_frame, anchor=tk.NW)

        # Bind events for scrolling
        self.mind_map_inner_frame.bind("<Configure>", self.on_frame_configure)
        self.mind_map_canvas.bind('<Configure>', self.on_canvas_configure)

        # Create matplotlib figure and canvas
        self.figure, self.ax = plt.subplots(figsize=(16, 9))
        self.mpl_canvas = FigureCanvasTkAgg(self.figure, master=self.mind_map_inner_frame)
        self.mpl_canvas.draw()
        self.mpl_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Add matplotlib navigation toolbar
        toolbar = NavigationToolbar2Tk(self.mpl_canvas, self.mind_map_inner_frame)
        toolbar.update()
        toolbar.pack(fill=tk.X)

        # Connect the click event to the highlight function
        self.mpl_canvas.mpl_connect('button_press_event', self.on_node_click)

        # Add export button
        self.export_button = ttk.Button(self.mind_map_frame, text="Export Mind Map", command=self.show_export_options)
        self.export_button.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        self.update_mind_map()

    def on_frame_configure(self, event):
        self.mind_map_canvas.configure(scrollregion=self.mind_map_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        # Update the size of the canvas window to encompass the inner frame
        self.mind_map_canvas.itemconfig(self.canvas_window, width=event.width)



    def on_canvas_configure(self, event):
        self.mind_map_canvas.configure(scrollregion=self.mind_map_canvas.bbox("all"))

    
    def on_node_click(self, event):
        if event.xdata is None or event.ydata is None:
            return

        # Find the closest node to the click
        clicked_node = min(self.pos, key=lambda n: (self.pos[n][0] - event.xdata)**2 + (self.pos[n][1] - event.ydata)**2)

        # Highlight the clicked node and its neighbors
        self.highlight_node_and_neighbors(clicked_node)

    def highlight_node_and_neighbors(self, node):
        # Reset all nodes and edges to their original appearance
        nx.draw_networkx_nodes(self.G, self.pos, ax=self.ax, node_color='lightblue', 
                               node_size=3000, alpha=0.8)
        nx.draw_networkx_edges(self.G, self.pos, ax=self.ax, edge_color='gray', 
                               width=1, alpha=0.7, arrows=True, arrowsize=10)

        # Highlight the clicked node
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=[node], ax=self.ax, 
                               node_color='red', node_size=3000, alpha=0.8)

        # Highlight the neighboring nodes
        neighbors = list(self.G.neighbors(node))
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=neighbors, ax=self.ax, 
                               node_color='yellow', node_size=3000, alpha=0.8)

        # Highlight the edges connected to the clicked node
        edge_list = [(node, neighbor) for neighbor in neighbors]
        nx.draw_networkx_edges(self.G, self.pos, edgelist=edge_list, ax=self.ax, 
                               edge_color='red', width=2, alpha=1, arrows=True, arrowsize=15)

        # Redraw the canvas
        self.mpl_canvas.draw()




    def enter_key(self):
        key = self.key_entry.get()
        if key:
            if key not in self.data:
                self.data[key] = {'next': [], 'text': []}
                self.save_data()
                self.refresh_tree()
                self.update_mind_map()
            self.show_concept_details(key)
        else:
            messagebox.showwarning("Input Error", "Please enter a key.")

    def show_concept_details(self, key):
        # Clear previous widgets in right frame
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.right_frame, text=f"Concept: {key}", font=('Helvetica', 16, 'bold')).pack(pady=10)

        # Next concepts
        ttk.Label(self.right_frame, text="Related Concepts:").pack(anchor='w', padx=10, pady=5)
        for next_item in self.data[key]['next']:
            ttk.Button(self.right_frame, text=next_item, command=lambda k=next_item: self.show_concept_details(k)).pack(anchor='w', padx=20)

        ttk.Button(self.right_frame, text="Add Related Concept", command=lambda: self.add_related_concept(key)).pack(anchor='w', padx=10, pady=5)

        # Text information
        ttk.Label(self.right_frame, text="Information:").pack(anchor='w', padx=10, pady=5)
        text_widget = tk.Text(self.right_frame, height=10, width=40)
        text_widget.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        for text_item in self.data[key]['text']:
            text_widget.insert(tk.END, f"- {text_item}\n")
        
        ttk.Button(self.right_frame, text="Add Information", command=lambda: self.add_information(key)).pack(anchor='w', padx=10, pady=5)



    def add_related_concept(self, key):
        dialog = tk.Toplevel(self.master)
        dialog.title("Add Related Concept")
        dialog.geometry("300x100")

        ttk.Label(dialog, text="Related Concept:").pack(pady=5)
        entry = ttk.Entry(dialog, width=40)
        entry.pack(pady=5)

        def submit():
            related_concept = entry.get()
            if related_concept:
                if related_concept not in self.data:
                    self.data[related_concept] = {'next': [], 'text': []}
                self.data[key]['next'].append(related_concept)
                self.save_data()
                self.refresh_tree()
                self.update_mind_map()
                self.show_concept_details(key)
                dialog.destroy()
            else:
                messagebox.showwarning("Input Error", "Please enter a related concept.")

        ttk.Button(dialog, text="Add", command=submit).pack(pady=10)

    # ... (other methods remain the same)
    def add_information(self, key):
        dialog = tk.Toplevel(self.master)
        dialog.title("Add Information")
        dialog.geometry("400x200")

        ttk.Label(dialog, text="Information:").pack(pady=5)
        text_widget = tk.Text(dialog, height=5, width=40)
        text_widget.pack(pady=5)

        def submit():
            info = text_widget.get("1.0", tk.END).strip()
            if info:
                self.data[key]['text'].append(info)
                self.save_data()
                self.show_concept_details(key)
                dialog.destroy()
            else:
                messagebox.showwarning("Input Error", "Please enter some information.")

        ttk.Button(dialog, text="Add", command=submit).pack(pady=10)

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for key in self.data:
            self.tree.insert("", "end", text=key)

    def on_tree_double_click(self, event):
        item = self.tree.selection()[0]
        key = self.tree.item(item, "text")
        self.show_concept_details(key)

    def perform_search(self):
        query = self.search_entry.get().lower()
        if not query:
            messagebox.showinfo("Search", "Please enter a search term.")
            return

        results = self.search_data(query)
        self.display_search_results(results)

    def search_data(self, query):
        results = []
        for key, value in self.data.items():
            if query in key.lower():
                results.append((key, "Key", key))
            for next_item in value['next']:
                if query in next_item.lower():
                    results.append((key, "Next", next_item))
            for text_item in value['text']:
                if query in text_item.lower():
                    results.append((key, "Text", text_item))
        return results

    def display_search_results(self, results):
        result_window = tk.Toplevel(self.master)
        result_window.title("Search Results")
        result_window.geometry("400x300")

        result_tree = ttk.Treeview(result_window, columns=("Type", "Content"), show="headings")
        result_tree.heading("Type", text="Type")
        result_tree.heading("Content", text="Content")
        result_tree.pack(fill=tk.BOTH, expand=True)

        for key, item_type, content in results:
            result_tree.insert("", "end", values=(f"{key} ({item_type})", content))

        if not results:
            messagebox.showinfo("Search Results", "No matches found.")
            result_window.destroy()

    def show_export_options(self):
        export_window = tk.Toplevel(self.master)
        export_window.title("Export Mind Map")
        export_window.geometry("300x150")

        ttk.Label(export_window, text="Choose export format:").pack(pady=10)

        ttk.Button(export_window, text="Export as PDF", command=lambda: self.prepare_export("pdf")).pack(pady=5)
        ttk.Button(export_window, text="Export as PNG", command=lambda: self.prepare_export("png")).pack(pady=5)

    def prepare_export(self, format):
        self.export_format = format
        self.export_after_render = True
        self.update_mind_map()



    def update_mind_map(self):
        if self.is_rendering:
            return

        self.is_rendering = True
        self.show_loading_indicator()

        # Run the rendering in a separate thread
        threading.Thread(target=self._render_mind_map, daemon=True).start()

    def _finish_rendering(self):
        self.mpl_canvas.draw()
        self.mind_map_inner_frame.update_idletasks()
        self.mind_map_canvas.configure(scrollregion=self.mind_map_canvas.bbox("all"))
        
        self.is_rendering = False
        self.hide_loading_indicator()

        if self.export_after_render:
            self.export_mind_map()

    def show_loading_indicator(self):
        self.loading_window = tk.Toplevel(self.master)
        self.loading_window.title("Loading")
        self.loading_window.geometry("200x100")
        ttk.Label(self.loading_window, text="Rendering mind map...").pack(pady=20)
        self.loading_window.update()

    def hide_loading_indicator(self):
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()

    def export_mind_map(self):
        if self.export_format == "pdf":
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if file_path:
                self.figure.savefig(file_path, format="pdf", bbox_inches="tight", dpi=300)
                messagebox.showinfo("Export Successful", f"Mind map exported as PDF to {file_path}")
        elif self.export_format == "png":
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if file_path:
                self.figure.savefig(file_path, format="png", dpi=300, bbox_inches="tight")
                messagebox.showinfo("Export Successful", f"Mind map exported as PNG to {file_path}")

        self.export_after_render = False
        self.export_format = None

    # ... (rest of the code remains the same)

    def load_data(self):
        if os.path.exists(FILENAME):
            with open(FILENAME, 'r') as file:
                return json.load(file)
        return {}

    def save_data(self):
        with open(FILENAME, 'w') as file:
            json.dump(self.data, file, indent=2)

    # ... (other methods remain the same)

    def enter_key(self):
        key = self.key_entry.get()
        if key:
            if key not in self.data:
                self.data[key] = {'next': [], 'text': []}
                self.save_data()
                self.refresh_tree()
                self.update_mind_map()
            self.show_concept_details(key)
        else:
            messagebox.showwarning("Input Error", "Please enter a key.")

    def add_related_concept(self, key):
        dialog = tk.Toplevel(self.master)
        dialog.title("Add Related Concept")
        dialog.geometry("300x100")

        ttk.Label(dialog, text="Related Concept:").pack(pady=5)
        entry = ttk.Entry(dialog, width=40)
        entry.pack(pady=5)

        def submit():
            related_concept = entry.get()
            if related_concept:
                if related_concept not in self.data:
                    self.data[related_concept] = {'next': [], 'text': []}
                if related_concept not in self.data[key]['next']:
                    self.data[key]['next'].append(related_concept)
                self.save_data()
                self.refresh_tree()
                self.update_mind_map()
                self.show_concept_details(key)
                dialog.destroy()
            else:
                messagebox.showwarning("Input Error", "Please enter a related concept.")

        ttk.Button(dialog, text="Add", command=submit).pack(pady=10)

    def update_mind_map(self):
        if self.is_rendering:
            return

        self.is_rendering = True
        self.show_loading_indicator()

        # Run the rendering in a separate thread
        threading.Thread(target=self._render_mind_map, daemon=True).start()

    
    def custom_tree_layout(self, G):
        if not G.nodes():
            return {}

        def bfs_tree(root):
            tree = nx.bfs_tree(G, root)
            return tree

        def assign_positions(tree, root):
            pos = {}
            level_width = {}
            max_depth = 0

            def dfs(node, depth, order):
                nonlocal max_depth
                max_depth = max(max_depth, depth)
                if depth not in level_width:
                    level_width[depth] = 0
                level_width[depth] += 1
                children = list(tree.successors(node))
                if not children:
                    pos[node] = (order, -depth)
                    return order + 1
                
                start = order
                for child in children:
                    order = dfs(child, depth + 1, order)
                pos[node] = (start + (order - start - 1) / 2, -depth)
                return order

            dfs(root, 0, 0)

            # Normalize positions
            max_width = max(level_width.values()) if level_width else 1
            for node in pos:
                x, y = pos[node]
                pos[node] = (x / max_width, y / max_depth if max_depth != 0 else 0)

            return pos

        # Handle disconnected components
        components = list(nx.connected_components(G))
        if not components:
            return {}

        pos = {}
        y_offset = 0
        for component in components:
            subgraph = G.subgraph(component)
            root = max(subgraph.nodes(), key=lambda n: subgraph.degree(n))
            tree = bfs_tree(root)
            component_pos = assign_positions(tree, root)
            
            # Adjust y-positions for each component
            for node, (x, y) in component_pos.items():
                pos[node] = (x, y + y_offset)
            
            y_offset -= 1.5  # Increase vertical separation between components

        return pos

    def _render_mind_map(self):
        self.G = nx.Graph()
        for key, value in self.data.items():
            self.G.add_node(key)
            for next_item in value['next']:
                if next_item in self.data:  # Only add edges for existing nodes
                    self.G.add_edge(key, next_item)

        self.ax.clear()
        self.pos = self.custom_tree_layout(self.G)
        
        # Dynamically adjust figure size based on number of nodes
        node_count = len(self.G.nodes())
        figsize = (max(8, min(20, node_count)), max(6, min(15, node_count * 0.75)))
        self.figure.set_size_inches(figsize)

        # Adjust node size and font size based on number of nodes
        node_size = max(1000, min(3000, 20000 / node_count)) if node_count > 0 else 3000
        font_size = max(6, min(10, 100 / node_count)) if node_count > 0 else 10

        if self.G.nodes():  # Only draw if there are nodes
            self.nodes = nx.draw_networkx_nodes(self.G, self.pos, ax=self.ax, node_color='lightblue', 
                                                node_size=node_size, alpha=0.8)
            self.edges = nx.draw_networkx_edges(self.G, self.pos, ax=self.ax, edge_color='gray', 
                                                width=1, alpha=0.7, arrows=True, arrowsize=10)

            # Custom label drawing with adjusted font size
            for node, (x, y) in self.pos.items():
                lines = textwrap.wrap(node, width=10)
                line_height = 0.03 * (font_size / 8)  # Adjust line height based on font size
                start_y = y + (len(lines) - 1) * line_height / 2

                for i, line in enumerate(lines):
                    self.ax.text(x, start_y - i * line_height, line, 
                                 horizontalalignment='center', verticalalignment='center',
                                 fontsize=font_size, fontweight='bold')

            # Adjust plot limits to ensure all nodes are visible
            x_values, y_values = zip(*self.pos.values())
            x_margin = (max(x_values) - min(x_values)) * 0.1
            y_margin = (max(y_values) - min(y_values)) * 0.1
            self.ax.set_xlim(min(x_values) - x_margin, max(x_values) + x_margin)
            self.ax.set_ylim(min(y_values) - y_margin, max(y_values) + y_margin)
        else:
            self.ax.text(0.5, 0.5, "No data to display", 
                         horizontalalignment='center', verticalalignment='center',
                         fontsize=12, fontweight='bold')
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)

        self.ax.axis('off')

        self.master.after(0, self._finish_rendering)

  

if __name__ == "__main__":
    root = tk.Tk()
    app = RevisionApp(root)
    root.mainloop()
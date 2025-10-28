import threading
import tkinter as tk
import time
from tkinter import ttk, messagebox, filedialog

from index.document_query import Query
from index.eval_interface import preprocess_document, preprocess_query, process_tfidf, process_boolean
from index.index import OwnIndex
from utils.utils import load_data


# Class for IndexViewerApp
class IndexViewerApp:
    # list of indexes
    indexes = list[OwnIndex]

    def __init__(self, root):
        self.root = root
        self.root.title("IR App")
        self.root.geometry("800x800")

        self.indexes = list()
        self.search_model = None
        self.tree = None
        self.query_entry = None
        self.results_count_label = None
        self.results_console = None
        self.results_spinbox = None
        self.result_limit = None

        self.create_index_treeview_section()
        self.create_query_section()
        self.create_results_console()

        root.mainloop()

    # Function for creating Indexes view
    def create_index_treeview_section(self):
        # Tree View
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(top_frame, text="Indexes", font=("Arial", 12, "bold")).pack(fill="x", padx=5, pady=(0, 5))

        columns = ("name", "content", "path", "status")
        self.tree = ttk.Treeview(top_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text="Name")
        self.tree.heading("path", text="File Path")
        self.tree.heading("content", text="Content to index")
        self.tree.heading("status", text="Status")

        self.tree.column("name", width=150)
        self.tree.column("content", width=100)
        self.tree.column("path", width=300)
        self.tree.column("status", width=100)

        # TreeView scrollbars
        scrollbar_y = ttk.Scrollbar(top_frame, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(top_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        self.tree.pack(fill="x", expand=True)

        # Buttons for controlling tree view
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=(5, 10))

        ttk.Button(button_frame, text="Remove Index", command=self.remove_index).pack(side="right", padx=5)

        ttk.Button(button_frame, text="Add Index", command=self.add_index_action).pack(side="right", padx=5)

    # Function for creating new window with adding index
    def add_index_action(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Add Index")
        add_win.geometry("500x220")
        add_win.resizable(False, False)

        # Label and Button for select file action
        ttk.Label(add_win, text="Select file:").pack(anchor="w", padx=10, pady=(10, 0))
        file_path_var = tk.StringVar()

        file_frame = ttk.Frame(add_win)
        file_frame.pack(fill="x", padx=10)

        file_entry = ttk.Entry(file_frame, textvariable=file_path_var, width=50)
        file_entry.pack(side="left", fill="x", expand=True)

        # Function for browse button
        def browse_file():
            path = filedialog.askopenfilename(filetypes=[("JSON and JSONL files", "*.json *.jsonl"),
                                                         ("JSON files", "*.json"),
                                                         ("JSONL files", "*.jsonl"),
                                                         ("All Files", "*.*")])
            if path:
                file_path_var.set(path)

        ttk.Button(file_frame, text="Browse", command=browse_file).pack(side="right", padx=(5, 0))

        ttk.Label(add_win, text="Index name:").pack(anchor="w", padx=10, pady=(10, 0))

        name_var = tk.StringVar()
        name_entry = ttk.Entry(add_win, textvariable=name_var)
        name_entry.pack(fill="x", padx=10)

        # Text input for content to index
        temp_part = ttk.Label(add_win, text="Content to index:")
        temp_part.pack(anchor="w", padx=10, pady=(10, 0))

        section_var = tk.StringVar()
        section_entry = ttk.Entry(add_win, textvariable=section_var)
        section_entry.pack(fill="x", padx=10)

        # Function for added button function
        def confirm_add():
            path = file_path_var.get()
            content = section_var.get()
            name = name_var.get()
            if not path:
                messagebox.showerror("Error", "Please select a file.")
                return

            if not content or not name:
                messagebox.showerror("Error", f"Please fill content to index and name.")
                return

            if name == "eval":
                messagebox.showinfo("Info", f"Name \"eval\" is reserved.\n Choose another name.")
                return

            for index in self.indexes:
                if index.name == name:
                    messagebox.showinfo("Info", f"Name {name} is already used.\n Choose another name.")
                    return

            add_win.destroy()

            status = "Not ready yet"

            item_id = self.tree.insert("", tk.END, values=(name, content, path, status))

            content = content.replace(" ", "")

            if ',' in content:
                contents = content.split(',')
            else:
                contents = [content]

            index = OwnIndex(name, contents)

            self.indexes.append(index)

            # Function for indexing in a new Thread
            def index_task():
                try:
                    data = load_data(path)
                except FileNotFoundError:
                    self.results_console.after(0, lambda: self.results_console.insert(tk.END, "File not found.\n"))
                    self.tree.after(0, lambda: self.indexes.remove(index))
                    self.tree.after(0, lambda: self.tree.delete(item_id))
                    return
                except ValueError:
                    self.results_console.after(0,
                                               lambda: self.results_console.insert(tk.END, "Wrong file extension.\n"))
                    self.tree.after(0, lambda: self.indexes.remove(index))
                    self.tree.after(0, lambda: self.tree.delete(item_id))
                    return

                try:
                    index.add_documents_json(data)
                except KeyError:
                    self.results_console.after(0, lambda: self.results_console.insert(tk.END,
                                                                                      f"Content to index doesn't exist: {content}\n"))
                    self.tree.after(0, lambda: self.indexes.remove(index))
                    self.tree.after(0, lambda: self.tree.delete(item_id))
                    return

                start = time.time()
                preprocess_document(index)
                end = time.time()
                time_elapsed = end - start

                self.tree.after(0, lambda: self.tree.item(item_id, values=(
                    name, content, path, f"Indexed ({time_elapsed:.2f} s)")))
                return

            threading.Thread(target=index_task).start()

        ttk.Button(add_win, text="Add", command=confirm_add).pack(pady=15)

    # Function for removing Index from TreeView
    def remove_index(self):
        selected_items = self.tree.selection()

        if not selected_items:
            messagebox.showinfo("Info", "Please select an index to remove.")
            return

        item = selected_items[0]
        values = self.tree.item(item, "values")

        for index in self.indexes:
            if index.name == values[0]:
                self.indexes.remove(index)

        self.tree.delete(item)

        self.results_count_label.config(text="Results: 0")

    # Function for creating a query section
    def create_query_section(self):
        # Frame for query input and search button
        query_search_frame = ttk.Frame(self.root)
        query_search_frame.pack(fill="x", padx=10, pady=(5, 10))

        search_model_title = ttk.Label(query_search_frame, text="Query", font=("Arial", 12, "bold"))
        search_model_title.pack(fill="x", padx=5, pady=(0, 5))

        ttk.Label(query_search_frame, text="Search model:", font=("Arial", 10)).pack(side="left", padx=5)

        # Variable to hold the selected model
        self.search_model = tk.StringVar(value="vector_space")

        # Create radio buttons for selecting the search model
        ttk.Radiobutton(query_search_frame, text="Vector Space Model",
                        variable=self.search_model,
                        value="vector_space").pack(side="left", padx=10)

        ttk.Radiobutton(query_search_frame, text="Boolean Model", variable=self.search_model,
                        value="boolean").pack(side="left", padx=10)

        # Search button to trigger query search
        ttk.Button(query_search_frame, text="Search", command=self.search_action).pack(side="right", padx=5)

        # Entry for the query
        self.query_entry = ttk.Entry(query_search_frame)
        self.query_entry.pack(side="right", fill="x", expand=True, padx=5)

        ttk.Label(query_search_frame, text="Query:", font=("Arial", 10)).pack(side="right", padx=5)

        separator = ttk.Separator(query_search_frame, orient="vertical")
        separator.pack(side="right", fill="y", padx=5)

        # Limit top K
        limit_frame = ttk.Frame(self.root)
        limit_frame.pack(fill="x", padx=10, pady=(5, 10))

        ttk.Label(limit_frame, text="Results to display:").pack(side="left", padx=5)

        self.result_limit = tk.IntVar(value=10)
        self.results_spinbox = ttk.Spinbox(limit_frame, from_=0, to=100, textvariable=self.result_limit, width=5)
        self.results_spinbox.pack(side="left", padx=5)

    # Function for search action
    def search_action(self):
        query_text = self.query_entry.get()
        selected_model = self.search_model.get()
        results_count = self.get_spinbox_value()

        query = Query("q1", query_text)

        try:
            index = self.get_index()
        except ValueError:
            return

        if index is None:
            messagebox.showerror("Error", "Index is not ready yet.")
            return

        # Choosing a search model
        if selected_model == "vector_space":
            preprocess_query(query, index, True)

            process_tfidf(index, query)

            sorted_documents = index.sort_documents_by_similarity()

            i = 1
            j = 0

            self.results_console.delete("1.0", tk.END)
            self.results_count_label.config(text="Results: 0")

            print(f"Query: {query.text}\n")

            for doc in sorted_documents:
                if doc.similarity == 0:
                    break

                if results_count != 0:
                    if i <= results_count:
                        self.print_console(
                            f"Document ID: {doc.id}, Similarity: {doc.similarity:.4f}, Text: {doc.text}")
                    i += 1
                else:
                    self.print_console(f"Document ID: {doc.id}, Similarity: {doc.similarity:.4f}, Text: {doc.text}")

                j += 1

            self.update_num_results(j)

            print()
            print("-" * 100)
            print()
        else:
            self.results_console.delete("1.0", tk.END)
            self.results_count_label.config(text="Results: 0")

            if any(op in query.text.split() for op in ["AND", "OR", "NOT", "(", ")"]) or len(query.text.split()) == 1:
                preprocess_query(query, index)

                result = process_boolean(index, query)

                print(f"Query: {query.text}\n")

                if results_count != 0:
                    self.print_console(f"Documents (id):\n {list(result)[:results_count]}")
                else:
                    self.print_console(f"Documents (id):\n {list(result)}")

                print()
                print("-" * 100)
                print()

                self.update_num_results(len(result))

            else:
                self.print_console(f"Query: {query.text} is not valid boolean query.")

    # Function for getting spinbox value (Top K)
    def get_spinbox_value(self):
        try:
            return int(self.results_spinbox.get())
        except ValueError:
            return 0

    # Function for getting index
    def get_index(self):
        selected_items = self.tree.selection()

        if not selected_items:
            messagebox.showinfo("Info", "Please select an index.")
            raise ValueError

        item = selected_items[0]
        values = self.tree.item(item, "values")

        for index in self.indexes:
            if index.name == values[0] and values[3] != "Not ready yet":
                return index

        return None

    # Function for creating a console section
    def create_results_console(self):
        # Frame for the result console
        console_frame = ttk.Frame(self.root)
        console_frame.pack(fill="both", padx=10, pady=(5, 10), expand=True)

        ttk.Label(console_frame, text="Console", font=("Arial", 12, "bold")).pack(fill="x", padx=5, pady=(0, 5))

        # Inner frame to contain text and scrollbars
        inner_console_frame = ttk.Frame(console_frame)
        inner_console_frame.pack(fill="both", expand=True)

        # Text widget for displaying results (acts as console)
        self.results_console = tk.Text(inner_console_frame, wrap="none", height=10, width=60)
        self.results_console.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(inner_console_frame, orient="vertical", command=self.results_console.yview)
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        scrollbar_x = ttk.Scrollbar(inner_console_frame, orient="horizontal", command=self.results_console.xview)
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        self.results_console.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        # Grid config
        inner_console_frame.rowconfigure(0, weight=1)
        inner_console_frame.columnconfigure(0, weight=1)

        # Frame for displaying the result count label
        count_frame = ttk.Frame(self.root)
        count_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Label to display the number of results
        self.results_count_label = ttk.Label(count_frame, text="Results count: 0", font=("Arial", 10))
        self.results_count_label.pack(fill="x", padx=5)

    # Function for printing console output
    def print_console(self, text: str):
        self.results_console.insert(tk.END, text + "\n")
        self.results_console.yview(tk.END)

        print(text)

    # Function for setting and printing final result count
    def update_num_results(self, num: int):
        self.results_count_label.config(text=f"Results count: {num}")

        print()
        print(f"Results count: {num}")


# Function for initializing GUI
def run_gui():
    root = tk.Tk()
    IndexViewerApp(root)

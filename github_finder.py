
import tkinter as tk
from tkinter import ttk, messagebox, Listbox
import requests
import json
import os
import webbrowser

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")

        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
        self.current_user_data = None

        # --- Основные фреймы ---
        top_frame = tk.Frame(root, padx=10, pady=10)
        top_frame.pack(fill=tk.X)

        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        result_frame = tk.LabelFrame(main_frame, text="Результат поиска", padx=10, pady=10)
        result_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.result_frame = result_frame # Сохраняем ссылку

        favorites_frame = tk.LabelFrame(main_frame, text="Избранное", padx=10, pady=10)
        favorites_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        favorites_frame.grid_rowconfigure(0, weight=1)
        favorites_frame.grid_columnconfigure(0, weight=1)

        # --- Виджеты поиска ---
        tk.Label(top_frame, text="Имя пользователя GitHub:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = tk.Entry(top_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.search_entry.bind("<Return>", self.search_user_event)

        search_button = tk.Button(top_frame, text="Найти", command=self.search_user)
        search_button.pack(side=tk.LEFT, padx=(5, 0))

        # --- Виджеты избранного ---
        self.favorites_listbox = Listbox(favorites_frame)
        self.favorites_listbox.grid(row=0, column=0, columnspan=2, sticky="nsew")
        fav_scrollbar = ttk.Scrollbar(favorites_frame, orient=tk.VERTICAL, command=self.favorites_listbox.yview)
        self.favorites_listbox.configure(yscrollcommand=fav_scrollbar.set)
        fav_scrollbar.grid(row=0, column=2, sticky="ns")

        remove_fav_button = tk.Button(favorites_frame, text="Удалить из избранного", command=self.remove_favorite)
        remove_fav_button.grid(row=1, column=0, columnspan=2, pady=(5,0), sticky="ew")

        self.update_favorites_listbox()

    def search_user_event(self, event):
        self.search_user()

    def search_user(self):
        username = self.search_entry.get().strip()
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым.")
            return

        # Очистка предыдущего результата
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        tk.Label(self.result_frame, text=f"Идет поиск {username}...").pack()

        try:
            response = requests.get(f"https://api.github.com/users/{username}")
            # Очистка снова перед отображением результата
            for widget in self.result_frame.winfo_children():
                widget.destroy()

            if response.status_code == 200:
                self.current_user_data = response.json()
                self.display_user_data(self.current_user_data)
            elif response.status_code == 404:
                messagebox.showwarning("Не найдено", f"Пользователь '{username}' не найден.")
            else:
                messagebox.showerror("Ошибка API", f"Произошла ошибка: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка сети", f"Не удалось подключиться к GitHub API: {e}")

    def display_user_data(self, data):
        name = data.get("name") or "Имя не указано"
        login = data.get("login")
        bio = data.get("bio") or "Биография отсутствует"
        url = data.get("html_url")
        
        tk.Label(self.result_frame, text=name, font=("Arial", 16, "bold")).pack(pady=5)
        
        link = tk.Label(self.result_frame, text=f"@{login}", fg="blue", cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda e: webbrowser.open_new(url))
        
        tk.Label(self.result_frame, text=f"{data.get('followers', 0)} подписчиков · {data.get('following', 0)} подписок").pack(pady=5)
        tk.Label(self.result_frame, text=bio, wraplength=300, justify=tk.LEFT).pack(pady=10, fill=tk.X)

        add_fav_button = tk.Button(self.result_frame, text="Добавить в избранное", command=self.add_to_favorites)
        add_fav_button.pack(pady=10)

    def add_to_favorites(self):
        if self.current_user_data:
            login = self.current_user_data.get("login")
            if login and login not in self.favorites:
                self.favorites.append(login)
                self.save_favorites()
                self.update_favorites_listbox()
                messagebox.showinfo("Успех", f"Пользователь {login} добавлен в избранное.")
            elif login in self.favorites:
                 messagebox.showinfo("Информация", f"Пользователь {login} уже в избранном.")

    def remove_favorite(self):
        selected_indices = self.favorites_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Ошибка", "Выберите пользователя для удаления.")
            return
        
        selected_user = self.favorites_listbox.get(selected_indices[0])
        self.favorites.remove(selected_user)
        self.save_favorites()
        self.update_favorites_listbox()

    def update_favorites_listbox(self):
        self.favorites_listbox.delete(0, tk.END)
        for user in sorted(self.favorites):
            self.favorites_listbox.insert(tk.END, user)

    def load_favorites(self):
        if not os.path.exists(self.favorites_file):
            return []
        try:
            with open(self.favorites_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_favorites(self):
        with open(self.favorites_file, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()

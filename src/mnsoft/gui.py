import threading
import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk

from mnsoft.news import CATEGORIES, get_headlines, search_headlines


class NewsApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("오늘의 이슈 - 분야별 뉴스")
        self.root.geometry("420x560")

        search_frame = tk.Frame(root)
        search_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind("<Return>", lambda _event: self.search())

        search_button = tk.Button(search_frame, text="검색", command=self.search)
        search_button.pack(side=tk.LEFT, padx=(6, 0))

        self.refresh_button = tk.Button(root, text="새로고침", command=self.refresh_categories)
        self.refresh_button.pack(pady=8)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.listboxes: dict[str, tk.Listbox] = {}
        for category in CATEGORIES:
            self._add_tab(category)

        self.refresh_categories()

    def _add_tab(self, title: str) -> None:
        frame = tk.Frame(self.notebook)
        listbox = tk.Listbox(frame, font=("Malgun Gothic", 11))
        listbox.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(frame, text=title)
        self.listboxes[title] = listbox

    def _tab_id_for(self, title: str) -> str:
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == title:
                return tab_id
        raise ValueError(title)

    def refresh_categories(self) -> None:
        self.refresh_button.config(state=tk.DISABLED, text="불러오는 중...")
        threading.Thread(target=self._load_categories, daemon=True).start()

    def _load_categories(self) -> None:
        for category in CATEGORIES:
            self._fetch_and_show(category, lambda c=category: get_headlines(c))
        self.root.after(0, lambda: self.refresh_button.config(state=tk.NORMAL, text="새로고침"))

    def search(self) -> None:
        query = self.search_var.get().strip()
        if not query:
            return
        if query not in self.listboxes:
            self._add_tab(query)
        self.notebook.select(self._tab_id_for(query))
        threading.Thread(
            target=self._fetch_and_show, args=(query, lambda: search_headlines(query)), daemon=True
        ).start()

    def _fetch_and_show(self, key: str, fetch: Callable[[], list[str]]) -> None:
        try:
            headlines = fetch()
            error = None
        except Exception as exc:  # noqa: BLE001 - surface any failure in the GUI dialog
            headlines = []
            error = str(exc)
        self.root.after(0, self._on_loaded, key, headlines, error)

    def _on_loaded(self, key: str, headlines: list[str], error: str | None) -> None:
        listbox = self.listboxes[key]
        listbox.delete(0, tk.END)
        if error:
            messagebox.showerror("불러오기 실패", f"[{key}] 소식을 가져오지 못했습니다.\n\n{error}")
            return
        for i, headline in enumerate(headlines, start=1):
            listbox.insert(tk.END, f"{i}. {headline}")


def main() -> None:
    root = tk.Tk()
    NewsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

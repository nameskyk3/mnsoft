import threading
import tkinter as tk
from tkinter import messagebox, ttk

from mnsoft.news import CATEGORIES, get_headlines


class NewsApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("오늘의 이슈 - 분야별 뉴스")
        self.root.geometry("420x520")

        self.refresh_button = tk.Button(root, text="새로고침", command=self.refresh)
        self.refresh_button.pack(pady=8)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.listboxes: dict[str, tk.Listbox] = {}
        for category in CATEGORIES:
            frame = tk.Frame(self.notebook)
            listbox = tk.Listbox(frame, font=("Malgun Gothic", 11))
            listbox.pack(fill=tk.BOTH, expand=True)
            self.notebook.add(frame, text=category)
            self.listboxes[category] = listbox

        self.refresh()

    def refresh(self) -> None:
        self.refresh_button.config(state=tk.DISABLED, text="불러오는 중...")
        for listbox in self.listboxes.values():
            listbox.delete(0, tk.END)
        threading.Thread(target=self._load_all, daemon=True).start()

    def _load_all(self) -> None:
        for category in CATEGORIES:
            try:
                headlines = get_headlines(category)
                error = None
            except Exception as exc:  # noqa: BLE001 - surface any failure in the GUI dialog
                headlines = []
                error = str(exc)
            self.root.after(0, self._on_loaded, category, headlines, error)
        self.root.after(0, lambda: self.refresh_button.config(state=tk.NORMAL, text="새로고침"))

    def _on_loaded(self, category: str, headlines: list[str], error: str | None) -> None:
        if error:
            messagebox.showerror("불러오기 실패", f"[{category}] 소식을 가져오지 못했습니다.\n\n{error}")
            return
        listbox = self.listboxes[category]
        for i, headline in enumerate(headlines, start=1):
            listbox.insert(tk.END, f"{i}. {headline}")


def main() -> None:
    root = tk.Tk()
    NewsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

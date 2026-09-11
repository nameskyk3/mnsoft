import threading
import tkinter as tk
from tkinter import messagebox

from mnsoft.trends import get_trending_keywords


class TrendsApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("요즘 트렌드 - 실시간 인기 검색어")
        self.root.geometry("360x480")

        self.refresh_button = tk.Button(root, text="새로고침", command=self.refresh)
        self.refresh_button.pack(pady=8)

        self.listbox = tk.Listbox(root, font=("Malgun Gothic", 12))
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.refresh()

    def refresh(self) -> None:
        self.refresh_button.config(state=tk.DISABLED, text="불러오는 중...")
        self.listbox.delete(0, tk.END)
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self) -> None:
        try:
            keywords = get_trending_keywords()
            error = None
        except Exception as exc:  # noqa: BLE001 - surface any failure in the GUI dialog
            keywords = []
            error = str(exc)
        self.root.after(0, self._on_loaded, keywords, error)

    def _on_loaded(self, keywords: list[str], error: str | None) -> None:
        self.refresh_button.config(state=tk.NORMAL, text="새로고침")
        if error:
            messagebox.showerror("불러오기 실패", f"트렌드를 가져오지 못했습니다.\n\n{error}")
            return
        for i, keyword in enumerate(keywords, start=1):
            self.listbox.insert(tk.END, f"{i}. {keyword}")


def main() -> None:
    root = tk.Tk()
    TrendsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

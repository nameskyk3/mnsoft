import io
import threading
import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk

import anthropic
from PIL import Image, ImageTk

from mnsoft.images import download_image_bytes, search_images
from mnsoft.news import CATEGORIES, get_headlines, search_headlines
from mnsoft.summarize import generate_report

_IMAGE_WIDTH = 400


class NewsApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("오늘의 이슈 - 분야별 뉴스")
        self.root.geometry("420x600")
        self._photo_refs: list[ImageTk.PhotoImage] = []

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
        self.apply_buttons: dict[str, tk.Button] = {}
        for category in CATEGORIES:
            self._add_tab(category)

        self.refresh_categories()

    def _add_tab(self, title: str) -> None:
        frame = tk.Frame(self.notebook)
        listbox = tk.Listbox(frame, font=("Malgun Gothic", 11), selectmode=tk.EXTENDED)
        listbox.pack(fill=tk.BOTH, expand=True)
        apply_button = tk.Button(frame, text="적용", command=lambda: self.apply_selected(title))
        apply_button.pack(fill=tk.X, pady=(4, 0))
        self.notebook.add(frame, text=title)
        self.listboxes[title] = listbox
        self.apply_buttons[title] = apply_button

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

    def apply_selected(self, tab_key: str) -> None:
        listbox = self.listboxes[tab_key]
        selection = listbox.curselection()
        if not selection:
            messagebox.showinfo("알림", "먼저 목록에서 이슈를 선택해주세요 (여러 개 선택 가능).")
            return
        headlines = []
        for index in selection:
            raw_text = listbox.get(index)
            headline = raw_text.split(". ", 1)[1] if ". " in raw_text else raw_text
            headlines.append(headline)

        button = self.apply_buttons[tab_key]
        button.config(state=tk.DISABLED, text=f"생성 중... (0/{len(headlines)})")
        threading.Thread(target=self._generate_reports, args=(tab_key, headlines), daemon=True).start()

    def _generate_reports(self, tab_key: str, headlines: list[str]) -> None:
        total = len(headlines)
        for i, headline in enumerate(headlines, start=1):
            self.root.after(0, self._update_progress, tab_key, i - 1, total)
            self._generate_one_report(tab_key, headline)
        self.root.after(0, self._finish_apply, tab_key)

    def _update_progress(self, tab_key: str, done: int, total: int) -> None:
        self.apply_buttons[tab_key].config(text=f"생성 중... ({done}/{total})")

    def _finish_apply(self, tab_key: str) -> None:
        self.apply_buttons[tab_key].config(state=tk.NORMAL, text="적용")

    def _generate_one_report(self, tab_key: str, headline: str) -> None:
        title = paragraphs = images = None
        error = None
        try:
            document = generate_report(headline)
            title, _, body = document.strip().partition("\n\n")
            title = title.strip() or headline
            paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
            images = self._fetch_images(headline)
        except anthropic.AuthenticationError:
            error = (
                "Claude API 키가 없거나 올바르지 않습니다.\n"
                "환경변수 ANTHROPIC_API_KEY를 설정한 뒤 다시 실행해주세요."
            )
        except anthropic.RateLimitError:
            error = "요청이 너무 많습니다. 잠시 후 다시 시도해주세요."
        except anthropic.APIStatusError as exc:
            error = f"API 오류: {exc.message}"
        except anthropic.APIConnectionError:
            error = "네트워크 연결을 확인해주세요."
        except Exception as exc:  # noqa: BLE001 - surface any failure in the GUI dialog
            error = str(exc)
        self.root.after(0, self._on_report_ready, tab_key, title, paragraphs, images, error)

    def _fetch_images(self, query: str) -> list[dict]:
        try:
            photos = search_images(query)
        except Exception:  # noqa: BLE001 - photos are a nice-to-have, never block the report
            return []
        images = []
        for photo in photos:
            try:
                photo["bytes"] = download_image_bytes(photo["url"])
                images.append(photo)
            except Exception:  # noqa: BLE001, S112 - skip any photo that fails to download
                continue
        return images

    def _on_report_ready(
        self,
        tab_key: str,
        title: str | None,
        paragraphs: list[str] | None,
        images: list[dict] | None,
        error: str | None,
    ) -> None:
        if error:
            messagebox.showerror("문서 생성 실패", error)
            return
        self._show_report_window(title, paragraphs, images)

    def _show_report_window(self, title: str, paragraphs: list[str], images: list[dict]) -> None:
        window = tk.Toplevel(self.root)
        window.title(title[:40])
        window.geometry("480x640")

        text_widget = tk.Text(window, wrap=tk.WORD, font=("Malgun Gothic", 11))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.tag_configure("title", font=("Malgun Gothic", 13, "bold"))
        text_widget.tag_configure("credit", font=("Malgun Gothic", 8), foreground="#888888")

        text_widget.insert(tk.END, f"{title}\n\n", "title")

        slots = len(images)
        group_size = max(1, len(paragraphs) // (slots + 1)) if slots else len(paragraphs)

        para_index = 0
        for i in range(slots):
            for _ in range(group_size):
                if para_index >= len(paragraphs):
                    break
                text_widget.insert(tk.END, paragraphs[para_index] + "\n\n")
                para_index += 1
            self._insert_image(text_widget, images[i])

        while para_index < len(paragraphs):
            text_widget.insert(tk.END, paragraphs[para_index] + "\n\n")
            para_index += 1

        text_widget.config(state=tk.DISABLED)

    def _insert_image(self, text_widget: tk.Text, photo: dict) -> None:
        try:
            image = Image.open(io.BytesIO(photo["bytes"]))
            ratio = _IMAGE_WIDTH / image.width
            image = image.resize((_IMAGE_WIDTH, int(image.height * ratio)))
            tk_image = ImageTk.PhotoImage(image)
        except Exception:  # noqa: BLE001 - skip a photo that fails to render
            return
        self._photo_refs.append(tk_image)
        text_widget.image_create(tk.END, image=tk_image)
        text_widget.insert(tk.END, f"\n사진: Pexels / {photo['photographer']}\n\n", "credit")


def main() -> None:
    root = tk.Tk()
    NewsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

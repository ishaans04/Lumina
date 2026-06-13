import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from WriteMain import backend

# Configure appearance
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

# ─── Typography ───────────────────────────────────────────────
FONT_FAMILY = "Segoe UI"
FONT_XS = 11
FONT_SM = 12
FONT_BASE = 14
FONT_LG = 16
FONT_XL = 18
FONT_2XL = 24
FONT_3XL = 36
FONT_5XL = 48

# ─── Spacing ─────────────────────────────────────────────────
RADIUS_SM = 4
RADIUS_MD = 8
RADIUS_LG = 12
RADIUS_XL = 16
RADIUS_FULL = 9999

SP_1 = 2
SP_2 = 4
SP_3 = 6
SP_4 = 8
SP_5 = 10
SP_6 = 12
SP_8 = 16
SP_10 = 20
SP_12 = 24
SP_16 = 32
SP_20 = 48
SP_24 = 80

# ─── Semantic Colors ─────────────────────────────────────────
ACCENT = "#C8864A"
ACCENT_HOVER = "#B5743D"
ACCENT_SUBTLE = "#F5EDE4"

TEXT_PRIMARY = "#2C2C2C"
TEXT_SECONDARY = "#6B6B6B"
TEXT_MUTED = "#9A9A9A"

BG_BASE = "#F5F3EF"
BG_SURFACE = "#EDE9E3"
BG_ELEVATED = "#FFFFFF"
BG_PANEL = "#F0EDE8"
BG_BREADCRUMB = "#FAF8F5"

BORDER_DEFAULT = "#D9D4CC"
BORDER_SUBTLE = "#E5E1DB"

# ─── Sizes ────────────────────────────────────────────────────
ICON_XS = 11
ICON_SM = 14
ICON_DEFAULT = 16
ICON_MD = 20
ICON_LG = 28

RIGHT_PANEL_WIDTH = 340
STATUS_BAR_HEIGHT = 32
SIDEBAR_WIDTH = 256


class WriteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Lumina")

        # Full viewport dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")
        try:
            self.state("zoomed")
        except tk.TclError:
            pass

        self.backend = backend
        ctk.set_appearance_mode(self.backend.data["settings"].get("theme", "light").title())
        self.current_page_id = self.backend.data["session"]["last_open_page_id"]
        self.current_page = self.backend.get_page(self.current_page_id)

        self.breadcrumb_title_label = None
        self.theme_label = None
        self.theme_icon = None
        self.status_theme_label = None
        self.status_theme_icon = None
        self.context_tag_frame = None
        self.sidebar_pages_frame = None
        self.sidebar_page_widgets = {}
        self.search_entry = None
        self.score_badge = None
        self.saved_label = None
        self.page_count_label = None
        self.word_count_label = None
        self.title_entry = None
        self.text_area = None
        self.messages_frame = None
        self.ask_entry = None
        self.pdf_btn = None
        self.send_btn = None
        self.action_buttons = {}
        self.slash_menu = None
        self.slash_trigger_index = None
        self.pdf_context_text = ""
        self.pdf_context_name = ""

        self.configure(fg_color=BG_BASE)
        self.backend.start_autosave()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_ui()
        self._refresh_all()
        self._bind_shortcuts()

    def _build_ui(self):
        # App container: flexbox column layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)  # Main content area flex: 1
        self.rowconfigure(1, weight=0)  # Status bar fixed

        # Main content area: flexbox row layout
        main_content = ctk.CTkFrame(self, fg_color=BG_BASE, corner_radius=0)
        main_content.grid(row=0, column=0, sticky="nsew", padx=SP_10, pady=(SP_5, SP_5))
        main_content.columnconfigure(0, weight=0)  # Sidebar fixed
        main_content.columnconfigure(1, weight=1)  # Editor flex: 1
        main_content.columnconfigure(2, weight=0)  # Right panel fixed
        main_content.rowconfigure(0, weight=1)

        # Left sidebar — rounded card
        sidebar = ctk.CTkFrame(
            main_content, fg_color=BG_SURFACE,
            corner_radius=RADIUS_LG, border_width=1, border_color=BORDER_SUBTLE
        )
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, SP_5))
        sidebar.grid_propagate(False)
        sidebar.configure(width=SIDEBAR_WIDTH)
        self._build_sidebar(sidebar)

        # Main editor area
        main_area = ctk.CTkFrame(main_content, fg_color=BG_BASE, corner_radius=0)
        main_area.grid(row=0, column=1, sticky="nsew", padx=(0, SP_5))
        main_area.columnconfigure(0, weight=1)
        main_area.rowconfigure(0, weight=1)
        self._build_editor(main_area)

        # Right panel — rounded card
        right_panel = ctk.CTkFrame(
            main_content, fg_color=BG_PANEL,
            corner_radius=RADIUS_LG, border_width=1, border_color=BORDER_SUBTLE
        )
        right_panel.grid(row=0, column=2, sticky="nsew")
        right_panel.grid_propagate(False)
        right_panel.configure(width=RIGHT_PANEL_WIDTH)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(4, weight=1)
        self._build_aipanel(right_panel)

        # Status bar
        status_bar = ctk.CTkFrame(self, fg_color=BG_BASE, corner_radius=0, height=STATUS_BAR_HEIGHT)
        status_bar.grid(row=1, column=0, sticky="ew", padx=SP_10, pady=(0, SP_4))
        status_bar.grid_propagate(False)
        status_bar.columnconfigure(0, weight=1)
        status_bar.columnconfigure(1, weight=1)
        status_bar.columnconfigure(2, weight=1)
        self._build_statusbar(status_bar)

    def _build_titlebar(self, title_bar):
        # Row 0: Window Title Bar (height 44px)
        window_title = ctk.CTkFrame(title_bar, fg_color=BG_BASE, corner_radius=0, border_width=0, height=44)
        window_title.grid(row=0, column=0, sticky="ew")
        window_title.grid_propagate(False)
        window_title.columnconfigure(0, weight=0)
        window_title.columnconfigure(1, weight=1)
        window_title.columnconfigure(2, weight=0)

        # Title text: 13px semibold for better presence
        title_text = ctk.CTkLabel(
            window_title, text="Lumina",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=TEXT_PRIMARY, fg_color=BG_BASE
        )
        title_text.grid(row=0, column=0, sticky="w", padx=SP_8, pady=14)

        # Window control buttons: 28×28, rounded
        controls_frame = ctk.CTkFrame(window_title, fg_color=BG_BASE, corner_radius=0, border_width=0)
        controls_frame.grid(row=0, column=2, sticky="e", padx=SP_8, pady=14)

        controls = [
            ("-", self.iconify),
            ("□", lambda: self.state("zoomed")),
            ("x", self._on_close),
        ]
        for i, (symbol, command) in enumerate(controls):
            btn = ctk.CTkButton(
                controls_frame, text=symbol, width=28, height=28,
                fg_color="transparent", text_color=TEXT_SECONDARY,
                font=ctk.CTkFont(size=ICON_SM),
                hover_color=BORDER_SUBTLE, corner_radius=RADIUS_SM,
                command=command
            )
            btn.grid(row=0, column=i, padx=1)

        # Row 1: Breadcrumb Bar — warm background, subtle top border
        breadcrumb_bar = ctk.CTkFrame(
            title_bar, fg_color=BG_BREADCRUMB, corner_radius=0,
            border_width=0, height=36
        )
        breadcrumb_bar.grid(row=1, column=0, sticky="ew")
        breadcrumb_bar.grid_propagate(False)
        breadcrumb_bar.columnconfigure(0, weight=1)

        top_rule = ctk.CTkFrame(breadcrumb_bar, fg_color=BORDER_SUBTLE, height=1, corner_radius=0)
        top_rule.grid(row=0, column=0, sticky="ew")

        breadcrumb_frame = ctk.CTkFrame(breadcrumb_bar, fg_color=BG_BREADCRUMB, corner_radius=0, border_width=0)
        breadcrumb_frame.grid(row=1, column=0, sticky="w", padx=SP_12, pady=SP_3)

        # Breadcrumb items: last item bold
        breadcrumb_items = ["Personal", "Projects", "Untitled"]
        for i, item in enumerate(breadcrumb_items):
            if i > 0:
                chevron = ctk.CTkLabel(
                    breadcrumb_frame, text="›",
                    font=ctk.CTkFont(size=ICON_XS), text_color=TEXT_MUTED,
                    fg_color=BG_BREADCRUMB
                )
                chevron.grid(row=0, column=i * 2 - 1, padx=SP_3)

            is_last = (i == len(breadcrumb_items) - 1)
            item_color = TEXT_PRIMARY if is_last else TEXT_SECONDARY
            item_weight = "bold" if is_last else "normal"
            item_label = ctk.CTkLabel(
                breadcrumb_frame, text=item,
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SM, weight=item_weight),
                text_color=item_color, fg_color=BG_BREADCRUMB
            )
            item_label.grid(row=0, column=i * 2)
            if is_last:
                self.breadcrumb_title_label = item_label

    def _build_sidebar(self, sidebar):
        sidebar.rowconfigure((0, 1, 2, 3), weight=0)
        sidebar.rowconfigure(4, weight=1)
        sidebar.rowconfigure(5, weight=0)

        # Logo section: "L" monogram + title
        top_bar = ctk.CTkFrame(sidebar, fg_color=BG_SURFACE, corner_radius=0, border_width=0)
        top_bar.grid(row=0, column=0, sticky="ew", padx=SP_10, pady=(SP_10, SP_8))
        top_bar.columnconfigure(1, weight=0)

        monogram = ctk.CTkFrame(
            top_bar, width=30, height=30,
            fg_color=ACCENT_SUBTLE, corner_radius=RADIUS_MD
        )
        monogram.grid(row=0, column=0, sticky="w")
        monogram.grid_propagate(False)
        monogram_label = ctk.CTkLabel(
            monogram, text="L",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BASE, weight="bold"),
            text_color=ACCENT, fg_color=ACCENT_SUBTLE
        )
        monogram_label.place(relx=0.5, rely=0.5, anchor="center")

        title_label = ctk.CTkLabel(
            top_bar, text="Lumina",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XL, weight="bold"),
            text_color=TEXT_PRIMARY, fg_color=BG_SURFACE
        )
        title_label.grid(row=0, column=1, sticky="w", padx=(SP_4, 0))

        # New Page Button
        new_page_btn = ctk.CTkButton(
            sidebar, text="+ New Page",
            fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="white",
            corner_radius=RADIUS_MD,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SM),
            height=36,
            command=self._create_new_page
        )
        new_page_btn.grid(row=1, column=0, sticky="ew", padx=SP_8, pady=(0, SP_5))

        # Search Bar
        search_entry = ctk.CTkEntry(
            sidebar, placeholder_text="Search pages...",
            fg_color=BG_ELEVATED, text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
            border_width=1, border_color=BORDER_SUBTLE,
            corner_radius=RADIUS_MD, height=34,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SM)
        )
        search_entry.grid(row=2, column=0, sticky="ew", padx=SP_8, pady=(0, SP_4))
        self.search_entry = search_entry
        search_entry.bind("<KeyRelease>", lambda event: self._refresh_sidebar())

        # Separator
        separator = ctk.CTkFrame(sidebar, fg_color=BORDER_SUBTLE, corner_radius=0, border_width=0, height=1)
        separator.grid(row=3, column=0, sticky="ew", padx=SP_8, pady=SP_4)

        # Pages List — scrollable with refined scrollbar
        list_frame = ctk.CTkScrollableFrame(
            sidebar, fg_color=BG_SURFACE, border_width=0, corner_radius=0,
            scrollbar_button_color=BORDER_DEFAULT,
            scrollbar_button_hover_color=TEXT_MUTED
        )
        list_frame.grid(row=4, column=0, sticky="nsew", padx=SP_3, pady=0)
        list_frame.columnconfigure(0, weight=1)
        self.sidebar_pages_frame = list_frame

        # Footer with separator
        footer = ctk.CTkFrame(sidebar, fg_color=BG_SURFACE, corner_radius=0, border_width=0)
        footer.grid(row=5, column=0, sticky="ew", padx=SP_8, pady=SP_8)
        footer.columnconfigure(0, weight=1)

        footer_sep = ctk.CTkFrame(footer, fg_color=BORDER_SUBTLE, height=1, corner_radius=0)
        footer_sep.grid(row=0, column=0, sticky="ew", pady=(0, SP_4))

        # Focus Score row
        score_row = ctk.CTkFrame(footer, fg_color=BG_SURFACE, corner_radius=0)
        score_row.grid(row=1, column=0, sticky="ew", pady=SP_1)
        score_row.columnconfigure(0, weight=1)

        score_label = ctk.CTkLabel(
            score_row, text="Focus Score",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SM),
            text_color=TEXT_SECONDARY, fg_color=BG_SURFACE
        )
        score_label.grid(row=0, column=0, sticky="w", pady=SP_3)

        self.score_badge = ctk.CTkLabel(
            score_row, text=" 85 ", width=36, height=22,
            fg_color=ACCENT, text_color="white", corner_radius=RADIUS_FULL,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS, weight="bold")
        )
        self.score_badge.grid(row=0, column=1, sticky="e", pady=SP_1)
        for widget in (score_row, score_label, self.score_badge):
            widget.configure(cursor="hand2")
            widget.bind("<Button-1>", lambda event: self._open_focus_score())

        # Light mode row
        light_row = ctk.CTkFrame(footer, fg_color=BG_SURFACE, corner_radius=0)
        light_row.grid(row=2, column=0, sticky="ew", pady=SP_1)
        light_row.columnconfigure(1, weight=1)

        self.theme_label = ctk.CTkLabel(
            light_row, text="Light",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SM),
            text_color=TEXT_SECONDARY, fg_color=BG_SURFACE
        )
        self.theme_label.grid(row=0, column=0, sticky="w", pady=SP_3)

        self.theme_icon = ctk.CTkLabel(
            light_row, text="☀",
            font=ctk.CTkFont(size=ICON_DEFAULT),
            fg_color=BG_SURFACE, text_color=TEXT_SECONDARY
        )
        self.theme_icon.grid(row=0, column=1, sticky="e", pady=SP_3)
        for widget in (light_row, self.theme_label, self.theme_icon):
            widget.bind("<Button-1>", lambda event: self._toggle_theme())

        # Settings row
        settings_row = ctk.CTkFrame(footer, fg_color=BG_SURFACE, corner_radius=0)
        settings_row.grid(row=3, column=0, sticky="ew", pady=SP_1)
        settings_row.columnconfigure(1, weight=1)

        settings_label = ctk.CTkLabel(
            settings_row, text="Settings",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SM),
            text_color=TEXT_SECONDARY, fg_color=BG_SURFACE
        )
        settings_label.grid(row=0, column=0, sticky="w", pady=SP_3)

        settings_icon = ctk.CTkLabel(
            settings_row, text="⚙",
            font=ctk.CTkFont(size=ICON_DEFAULT),
            fg_color=BG_SURFACE, text_color=TEXT_SECONDARY
        )
        settings_icon.grid(row=0, column=1, sticky="e", pady=SP_3)
        for widget in (settings_row, settings_label, settings_icon):
            widget.bind("<Button-1>", lambda event: self._open_settings())

    def _build_editor(self, main_area):
        # Editor container
        editor_frame = ctk.CTkFrame(main_area, fg_color=BG_BASE, corner_radius=0, border_width=0)
        editor_frame.grid(row=0, column=0, sticky="nsew")
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)

        # Content column: max width constrained, top aligned
        content_wrapper = ctk.CTkFrame(editor_frame, fg_color=BG_BASE, corner_radius=0, border_width=0)
        content_wrapper.grid(row=0, column=0, sticky="nsew", padx=SP_24, pady=(SP_20, SP_10))

        # Page icon — refined sizing
        icon_box = ctk.CTkLabel(
            content_wrapper, text="📝",
            font=ctk.CTkFont(size=48),
            fg_color=BG_BASE, width=56, height=56
        )
        icon_box.pack(anchor="w", pady=(0, SP_6))

        # Title input with subtle underline
        title_wrapper = ctk.CTkFrame(content_wrapper, fg_color=BG_BASE, corner_radius=0, border_width=0)
        title_wrapper.pack(fill="x", pady=(0, SP_2))

        self.title_entry = ctk.CTkEntry(
            title_wrapper, placeholder_text="Untitled",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_3XL, weight="bold"),
            fg_color=BG_BASE, border_width=0,
            text_color=TEXT_PRIMARY, placeholder_text_color=TEXT_MUTED
        )
        self.title_entry.pack(fill="x", pady=(0, SP_4))
        self.title_entry.bind("<KeyRelease>", lambda event: self._save_title())

        # Subtle rule below title for visual grounding
        title_rule = ctk.CTkFrame(title_wrapper, fg_color=BORDER_SUBTLE, height=1, corner_radius=0)
        title_rule.pack(fill="x", pady=(0, SP_10))

        # Body text area with minimum height
        self.text_area = ctk.CTkTextbox(
            content_wrapper,
            font=ctk.CTkFont(family=self._editor_font_family(), size=self._editor_font_size()),
            fg_color="transparent",
            text_color=TEXT_PRIMARY,
            border_width=0,
            corner_radius=0,
            wrap="word",
            scrollbar_button_color=BORDER_DEFAULT,
            scrollbar_button_hover_color=TEXT_MUTED,
            width=880,
            height=720
        )
        self.text_area.pack(fill="both", expand=True)
        try:
            self.text_area._textbox.configure(undo=True, autoseparators=True, maxundo=-1)
        except tk.TclError:
            pass
        self.text_area.bind("<KeyPress>", self._handle_text_keypress)
        self.text_area.bind("<KeyRelease>", lambda event: self._handle_body_keyrelease())

    def _build_aipanel(self, right_panel):
        # Header with accent-tinted icon
        header = ctk.CTkFrame(right_panel, fg_color=BG_PANEL, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=SP_8, pady=(SP_8, 0))
        header.columnconfigure(0, weight=0)
        header.columnconfigure(1, weight=1)

        header_icon_box = ctk.CTkFrame(
            header, width=28, height=28,
            fg_color=ACCENT_SUBTLE, corner_radius=RADIUS_MD
        )
        header_icon_box.grid(row=0, column=0, sticky="w")
        header_icon_box.grid_propagate(False)
        header_icon = ctk.CTkLabel(
            header_icon_box, text="✦",
            font=ctk.CTkFont(size=ICON_DEFAULT),
            fg_color=ACCENT_SUBTLE, text_color=ACCENT
        )
        header_icon.place(relx=0.5, rely=0.5, anchor="center")

        header_label = ctk.CTkLabel(
            header, text="AI Assistant",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BASE, weight="bold"),
            fg_color="transparent", text_color=TEXT_PRIMARY
        )
        header_label.grid(row=0, column=1, sticky="w", padx=(SP_4, 0))

        # Header separator
        header_bottom = ctk.CTkFrame(right_panel, fg_color=BORDER_SUBTLE, corner_radius=0, height=1)
        header_bottom.grid(row=1, column=0, sticky="ew", padx=SP_8, pady=(SP_6, 0))

        # Context section
        context_section = ctk.CTkFrame(right_panel, fg_color=BG_PANEL, corner_radius=0)
        context_section.grid(row=2, column=0, sticky="ew", padx=SP_8, pady=(SP_6, 0))
        context_section.columnconfigure(0, weight=1)

        context_label = ctk.CTkLabel(
            context_section, text="Context",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS),
            text_color=TEXT_MUTED, fg_color=BG_PANEL
        )
        context_label.grid(row=0, column=0, sticky="w", pady=(0, SP_3))

        self.context_tag_frame = ctk.CTkFrame(context_section, fg_color=BG_PANEL, corner_radius=0)
        self.context_tag_frame.grid(row=1, column=0, sticky="ew")

        # Quick Actions section
        quick_section = ctk.CTkFrame(right_panel, fg_color=BG_PANEL, corner_radius=0)
        quick_section.grid(row=3, column=0, sticky="ew", padx=SP_8, pady=(SP_8, 0))
        quick_section.columnconfigure(0, weight=1)

        quick_label = ctk.CTkLabel(
            quick_section, text="Quick Actions",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS),
            text_color=TEXT_MUTED, fg_color=BG_PANEL
        )
        quick_label.grid(row=0, column=0, sticky="w", pady=(0, SP_3))

        action_grid = ctk.CTkFrame(quick_section, fg_color=BG_PANEL, corner_radius=0)
        action_grid.grid(row=1, column=0, sticky="ew")
        action_grid.columnconfigure((0, 1), weight=1)

        actions = [
            ("📝", "Summarize"),
            ("✓", "Fix Grammar"),
            ("↗", "Expand"),
            ("🌐", "Translate"),
        ]
        for index, (icon_char, label) in enumerate(actions):
            btn = ctk.CTkButton(
                action_grid, text=f"{icon_char}  {label}",
                fg_color=BG_SURFACE, border_width=1, border_color=BORDER_SUBTLE,
                text_color=TEXT_PRIMARY, corner_radius=RADIUS_MD,
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SM),
                hover_color=BORDER_SUBTLE,
                command=lambda action=label.lower().replace(" ", "_"): self._run_quick_action(action)
            )
            self.action_buttons[label] = btn
            btn.grid(row=index // 2, column=index % 2, sticky="ew", padx=SP_1, pady=SP_1, ipady=SP_5)

        # Chat section
        chat_section = ctk.CTkFrame(right_panel, fg_color=BG_PANEL, corner_radius=0)
        chat_section.grid(row=4, column=0, sticky="nsew", padx=SP_8, pady=(SP_8, 0))
        chat_section.columnconfigure(0, weight=1)
        chat_section.rowconfigure(0, weight=1)

        self.messages_frame = ctk.CTkScrollableFrame(
            chat_section,
            fg_color=BG_PANEL,
            corner_radius=0,
            border_width=0,
            scrollbar_button_color=BORDER_DEFAULT,
            scrollbar_button_hover_color=TEXT_MUTED
        )
        self.messages_frame.grid(row=0, column=0, sticky="nsew")
        self.messages_frame.columnconfigure(0, weight=1)

        # Input section
        input_section = ctk.CTkFrame(right_panel, fg_color=BG_PANEL, corner_radius=0)
        input_section.grid(row=5, column=0, sticky="ew", padx=SP_8, pady=(SP_6, SP_8))
        input_section.columnconfigure(0, weight=1)

        input_top_border = ctk.CTkFrame(input_section, fg_color=BORDER_SUBTLE, height=1, corner_radius=0)
        input_top_border.grid(row=0, column=0, sticky="ew", pady=(0, SP_6))

        input_label = ctk.CTkLabel(
            input_section, text="Ask something",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS),
            text_color=TEXT_MUTED, fg_color=BG_PANEL
        )
        input_label.grid(row=1, column=0, sticky="w", pady=(0, SP_3))

        input_row = ctk.CTkFrame(input_section, fg_color=BG_PANEL, corner_radius=0)
        input_row.grid(row=2, column=0, sticky="ew")
        input_row.columnconfigure(1, weight=1)

        self.pdf_btn = ctk.CTkButton(
            input_row, text="+",
            fg_color=BG_SURFACE, border_width=1, border_color=BORDER_SUBTLE,
            hover_color=BORDER_SUBTLE, text_color=TEXT_PRIMARY,
            width=36, height=36, corner_radius=RADIUS_MD,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BASE),
            command=self._show_pdf_menu
        )
        self.pdf_btn.grid(row=0, column=0, padx=(0, SP_3))

        self.ask_entry = ctk.CTkEntry(
            input_row, placeholder_text="Type your question…",
            fg_color=BG_ELEVATED, border_width=1, border_color=BORDER_SUBTLE,
            text_color=TEXT_PRIMARY, placeholder_text_color=TEXT_MUTED,
            corner_radius=RADIUS_MD,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BASE)
        )
        self.ask_entry.grid(row=0, column=1, sticky="ew", ipady=SP_4)
        self.ask_entry.bind("<Return>", lambda event: self._send_chat_message())

        # Send button — radius matches input
        self.send_btn = ctk.CTkButton(
            input_row, text="→",
            fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="white",
            width=36, height=36, corner_radius=RADIUS_MD,
            font=ctk.CTkFont(size=ICON_SM),
            command=self._send_chat_message
        )
        self.send_btn.grid(row=0, column=2, padx=(SP_3, 0))

    def _build_statusbar(self, status_bar):
        # Top border
        top_border = ctk.CTkFrame(status_bar, fg_color=BORDER_SUBTLE, height=1, corner_radius=0)
        top_border.grid(row=0, column=0, columnspan=3, sticky="ew")

        # Left: Active indicator with green dot frame
        left_item = ctk.CTkFrame(status_bar, fg_color=BG_BASE, corner_radius=0)
        left_item.grid(row=1, column=0, sticky="w", padx=(0, SP_10), pady=(SP_3, 0))

        dot = ctk.CTkFrame(left_item, width=6, height=6, fg_color="#4CAF50", corner_radius=RADIUS_FULL)
        dot.grid(row=0, column=0)
        dot.grid_propagate(False)

        left_status = ctk.CTkLabel(
            left_item, text="Active", text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS), fg_color=BG_BASE
        )
        left_status.grid(row=0, column=1, padx=(SP_3, 0))

        # Middle: Page & word count — text only
        middle_item = ctk.CTkFrame(status_bar, fg_color=BG_BASE, corner_radius=0)
        middle_item.grid(row=1, column=1, sticky="w", padx=(0, SP_10), pady=(SP_3, 0))

        self.page_count_label = ctk.CTkLabel(
            middle_item, text="0 pages", text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS), fg_color=BG_BASE
        )
        self.page_count_label.grid(row=0, column=0)

        sep = ctk.CTkFrame(middle_item, fg_color=BORDER_DEFAULT, width=1, height=10, corner_radius=0)
        sep.grid(row=0, column=1, padx=SP_4)

        self.word_count_label = ctk.CTkLabel(
            middle_item, text="0 words", text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS), fg_color=BG_BASE
        )
        self.word_count_label.grid(row=0, column=2)

        # Right: Theme + saved status
        right_item = ctk.CTkFrame(status_bar, fg_color=BG_BASE, corner_radius=0)
        right_item.grid(row=1, column=2, sticky="e", pady=(SP_3, 0))

        self.status_theme_icon = ctk.CTkLabel(
            right_item, text="☀",
            font=ctk.CTkFont(size=FONT_XS),
            fg_color=BG_BASE, text_color=TEXT_SECONDARY
        )
        self.status_theme_icon.grid(row=0, column=0)

        self.status_theme_label = ctk.CTkLabel(
            right_item, text="Light", text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS), fg_color=BG_BASE
        )
        self.status_theme_label.grid(row=0, column=1, padx=(SP_1, 0))

        right_sep = ctk.CTkFrame(right_item, fg_color=BORDER_DEFAULT, width=1, height=10, corner_radius=0)
        right_sep.grid(row=0, column=2, padx=SP_4)

        self.saved_label = ctk.CTkLabel(
            right_item, text="Saved just now", text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS), fg_color=BG_BASE
        )
        self.saved_label.grid(row=0, column=3)

    def _refresh_all(self):
        self._refresh_sidebar()
        self._load_current_page()
        self._refresh_context_tags()
        self._refresh_chat()
        self._refresh_theme_labels()
        self._refresh_status()

    def _bind_shortcuts(self):
        self.bind_all("<Control-s>", self._save_page_to_file)
        self.bind_all("<Control-S>", self._save_page_to_file)
        self.bind_all("<Control-z>", self._undo_editor)
        self.bind_all("<Control-Z>", self._undo_editor)
        self.bind_all("<Control-f>", self._find_in_page)
        self.bind_all("<Control-F>", self._find_in_page)

    def _refresh_sidebar(self):
        if not self.sidebar_pages_frame:
            return

        for widget in self.sidebar_pages_frame.winfo_children():
            widget.destroy()
        self.sidebar_page_widgets = {}

        search_query = self.search_entry.get().strip() if self.search_entry else ""
        pages = self.backend.list_pages(search=search_query)

        for page in pages:
            is_selected = page["id"] == self.current_page_id
            item_bg = ACCENT if is_selected else BG_SURFACE
            item_text = "white" if is_selected else TEXT_PRIMARY

            item_frame = ctk.CTkFrame(self.sidebar_pages_frame, fg_color=item_bg, corner_radius=RADIUS_MD, height=36)
            item_frame.grid(sticky="ew", pady=1)
            item_frame.grid_columnconfigure(1, weight=1)

            icon = ctk.CTkLabel(
                item_frame, text="📄",
                font=ctk.CTkFont(size=ICON_DEFAULT),
                fg_color=item_bg, text_color=item_text
            )
            icon.grid(row=0, column=0, padx=(SP_5, 0), pady=SP_4)

            label = ctk.CTkLabel(
                item_frame, text=page["title"],
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BASE),
                text_color=item_text, fg_color=item_bg
            )
            label.grid(row=0, column=1, sticky="w", padx=(SP_4, SP_5), pady=SP_4)

            item_frame.bind("<Button-1>", lambda event, page_id=page["id"]: self._load_page(page_id))
            for child in [icon, label]:
                child.bind("<Button-1>", lambda event, page_id=page["id"]: self._load_page(page_id))
                child.bind("<Double-Button-1>", lambda event, page_id=page["id"]: self._rename_page(page_id))

            item_frame.bind("<Double-Button-1>", lambda event, page_id=page["id"]: self._rename_page(page_id))
            for widget in [item_frame, icon, label]:
                widget.bind("<Button-3>", lambda event, page_id=page["id"]: self._show_page_menu(event, page_id))

            self.sidebar_page_widgets[page["id"]] = {
                "frame": item_frame,
                "icon": icon,
                "label": label,
            }
            self._style_sidebar_item(page["id"], is_selected)

    def _style_sidebar_item(self, page_id, is_selected):
        widgets = self.sidebar_page_widgets.get(page_id)
        if not widgets:
            return

        item_bg = ACCENT if is_selected else BG_SURFACE
        item_text = "white" if is_selected else TEXT_PRIMARY
        widgets["frame"].configure(fg_color=item_bg)
        widgets["icon"].configure(fg_color=item_bg, text_color=item_text)
        widgets["label"].configure(fg_color=item_bg, text_color=item_text)

        for widget in widgets.values():
            widget.unbind("<Enter>")
            widget.unbind("<Leave>")

        if not is_selected:
            def on_enter(_event, row=widgets):
                row["frame"].configure(fg_color=BORDER_SUBTLE)
                row["icon"].configure(fg_color=BORDER_SUBTLE)
                row["label"].configure(fg_color=BORDER_SUBTLE)

            def on_leave(_event, row=widgets):
                row["frame"].configure(fg_color=BG_SURFACE)
                row["icon"].configure(fg_color=BG_SURFACE)
                row["label"].configure(fg_color=BG_SURFACE)

            for widget in widgets.values():
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)

    def _refresh_sidebar_selection(self):
        for page_id in self.sidebar_page_widgets:
            self._style_sidebar_item(page_id, page_id == self.current_page_id)

    def _update_sidebar_title(self, page_id, title):
        widgets = self.sidebar_page_widgets.get(page_id)
        if widgets:
            widgets["label"].configure(text=title)

    def _page_text(self):
        return self.text_area.get("1.0", "end").strip("\n") if self.text_area else ""

    def _save_page_to_file(self, event=None):
        title = (self.current_page or {}).get("title") or "Untitled"
        initial_name = re.sub(r'[<>:"/\\|?*]+', "_", title).strip() or "Untitled"
        path = filedialog.asksaveasfilename(
            title="Save Page",
            initialfile=f"{initial_name}.txt",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")],
        )
        if not path:
            return "break"

        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(self._page_text())
        except OSError as exc:
            messagebox.showerror("Save Page", str(exc))
        return "break"

    def _undo_editor(self, event=None):
        focused = self.focus_get()
        editor_widget = getattr(self.text_area, "_textbox", None)
        if focused != editor_widget:
            return None

        try:
            editor_widget.edit_undo()
            self._save_body()
            self._apply_markdown_formatting()
        except tk.TclError:
            pass
        return "break"

    def _find_in_page(self, event=None):
        if not self.text_area:
            return "break"

        dialog = ctk.CTkInputDialog(text="Find text", title="Find")
        query = dialog.get_input()
        if not query:
            return "break"

        editor_widget = self.text_area._textbox
        self.text_area.tag_remove("find_match", "1.0", "end")
        editor_widget.tag_configure("find_match", background=ACCENT_SUBTLE, foreground=TEXT_PRIMARY)

        start = self.text_area.index("insert")
        index = editor_widget.search(query, start, stopindex="end", nocase=True)
        if not index:
            index = editor_widget.search(query, "1.0", stopindex=start, nocase=True)
        if not index:
            messagebox.showinfo("Find", f"No match found for '{query}'.")
            return "break"

        end = f"{index} + {len(query)}c"
        self.text_area.tag_add("find_match", index, end)
        self.text_area.tag_add("sel", index, end)
        self.text_area.mark_set("insert", end)
        self.text_area.see(index)
        self.text_area.focus_set()
        return "break"

    def _show_page_menu(self, event, page_id):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Open", command=lambda: self._load_page(page_id))
        menu.add_command(label="Rename", command=lambda: self._rename_page(page_id))
        menu.add_command(label="Add to AI Context", command=lambda: self._add_context_page(page_id))
        menu.add_separator()
        menu.add_command(label="Delete Page", command=lambda: self._delete_page(page_id))
        menu.tk_popup(event.x_root, event.y_root)

    def _rename_page(self, page_id):
        page = self.backend.get_page(page_id)
        if not page:
            return

        dialog = ctk.CTkInputDialog(text="Page name", title="Rename Page")
        title = dialog.get_input()
        if not title:
            return

        self.backend.set_title(page_id, title.strip() or "Untitled")
        if page_id == self.current_page_id:
            self.current_page = self.backend.get_page(page_id)
            self._update_sidebar_title(page_id, self.current_page.get("title") or "Untitled")
            self._load_current_page()
        else:
            self._refresh_sidebar()

    def _delete_page(self, page_id):
        page = self.backend.get_page(page_id)
        if not page:
            return

        if not messagebox.askyesno("Delete Page", f"Delete '{page.get('title', 'Untitled')}'?"):
            return

        result = self.backend.delete_page(page_id)
        self.current_page_id = result["active_page_id"]
        self.current_page = self.backend.get_page(self.current_page_id)
        self._refresh_all()

    def _add_context_page(self, page_id):
        try:
            self.backend.add_ai_context_page(page_id)
        except KeyError as exc:
            self._append_chat_message("assistant", str(exc))
            return
        self._refresh_context_tags()

    def _load_page(self, page_id):
        try:
            self.backend.select_page(page_id)
        except KeyError:
            return

        self.current_page_id = page_id
        self.current_page = self.backend.get_page(page_id)
        self._load_current_page()

    def _load_current_page(self):
        if not self.current_page:
            self.current_page = self.backend.get_page(self.current_page_id)

        if not self.current_page:
            return

        self.current_page_id = self.current_page["id"]
        self._hide_slash_menu()
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, self.current_page["title"])

        self.text_area.delete("1.0", "end")
        content = "\n".join(block.get("content", "") for block in self.current_page.get("blocks") or [])
        self.text_area.insert("1.0", content)
        self._apply_markdown_formatting()

        self._refresh_status()
        self._refresh_sidebar_selection()
        self._refresh_context_tags()
        self._refresh_breadcrumb()

    def _editor_font_size(self):
        try:
            return max(8, int(self.backend.data["settings"].get("font_size") or FONT_XL))
        except (TypeError, ValueError):
            return FONT_XL

    def _editor_font_family(self):
        return self.backend.data["settings"].get("font_family") or FONT_FAMILY

    def _apply_editor_font_size(self):
        if self.text_area:
            self.text_area.configure(font=ctk.CTkFont(family=self._editor_font_family(), size=self._editor_font_size()))
            self._apply_markdown_formatting()

    def _handle_body_keyrelease(self):
        self._save_body()
        self._apply_markdown_formatting()

    def _apply_markdown_formatting(self):
        if not self.text_area:
            return

        try:
            self.text_area._textbox.tag_configure(
                "markdown_bold",
                font=ctk.CTkFont(family=self._editor_font_family(), size=self._editor_font_size(), weight="bold"),
            )
            self.text_area._textbox.tag_configure("markdown_marker", elide=True)
            self.text_area.tag_remove("markdown_bold", "1.0", "end")
            self.text_area.tag_remove("markdown_marker", "1.0", "end")
        except tk.TclError:
            return

        content = self.text_area.get("1.0", "end-1c")
        for match in re.finditer(r"\*\*(.+?)\*\*", content):
            start = f"1.0 + {match.start()}c"
            content_start = f"1.0 + {match.start() + 2}c"
            content_end = f"1.0 + {match.end() - 2}c"
            end = f"1.0 + {match.end()}c"
            self.text_area.tag_add("markdown_marker", start, content_start)
            self.text_area.tag_add("markdown_bold", content_start, content_end)
            self.text_area.tag_add("markdown_marker", content_end, end)

    def _handle_text_keypress(self, event):
        if event.keysym == "Escape":
            self._hide_slash_menu()
            return None

        if event.char == "\\" or event.keysym == "backslash":
            self.after_idle(self._show_slash_menu)
        else:
            self._hide_slash_menu()

        return None

    def _show_slash_menu(self):
        if not self.text_area:
            return

        self._hide_slash_menu()
        self.slash_trigger_index = self.text_area.index("insert - 1c")
        menu = tk.Menu(self, tearoff=0)
        for option in self.backend.slash_menu_options():
            label = option.get("label") or option.get("type", "").title()
            command_type = option.get("type")
            menu.add_command(
                label=label,
                command=lambda command_type=command_type: self._run_slash_command(command_type),
            )

        self.slash_menu = menu
        bbox = self.text_area.bbox("insert")
        if bbox:
            x, y, _width, height = bbox
            x_root = self.text_area.winfo_rootx() + x
            y_root = self.text_area.winfo_rooty() + y + height
        else:
            x_root = self.text_area.winfo_pointerx()
            y_root = self.text_area.winfo_pointery()

        try:
            menu.tk_popup(x_root, y_root)
        finally:
            menu.grab_release()

    def _hide_slash_menu(self):
        if self.slash_menu:
            try:
                self.slash_menu.unpost()
            except tk.TclError:
                pass
        self.slash_menu = None

    def _remove_slash_trigger(self):
        index = self.slash_trigger_index
        self.slash_trigger_index = None
        if not index:
            return self.text_area.index("insert")

        if self.text_area.get(index, f"{index} + 1c") == "\\":
            self.text_area.delete(index, f"{index} + 1c")
            return index

        return self.text_area.index("insert")

    def _run_slash_command(self, command_type):
        if not command_type:
            return

        insert_index = self._remove_slash_trigger()
        if command_type == "bold":
            if self.text_area.tag_ranges("sel"):
                selected = self.text_area.get("sel.first", "sel.last")
                self.text_area.delete("sel.first", "sel.last")
                self.text_area.insert(insert_index, f"**{selected}**")
                self.text_area.mark_set("insert", f"{insert_index} + {len(selected) + 4}c")
            else:
                self.text_area.insert(insert_index, "****")
                self.text_area.mark_set("insert", f"{insert_index} + 2c")
            self.text_area.focus_set()
            self._save_body()
            self._apply_markdown_formatting()
            return

        if command_type == "summarize":
            self._save_body()
        try:
            result = self.backend.run_slash_command(command_type, self.current_page_id)
        except Exception as exc:
            self._save_body()
            self._append_chat_message("assistant", str(exc))
            return

        if result.get("type") == "summary":
            self._save_body()
            self._refresh_chat()
            return

        content = result.get("content", "")
        if content:
            self.text_area.insert(insert_index, content)
            if command_type == "code":
                self.text_area.mark_set("insert", f"{insert_index} + 10c")
            elif command_type in {"heading", "title"}:
                self.text_area.tag_add("sel", f"{insert_index} + 3c", f"{insert_index} lineend")
                self.text_area.mark_set("insert", f"{insert_index} lineend")
            else:
                self.text_area.mark_set("insert", f"{insert_index} + {len(content)}c")
        else:
            self.text_area.mark_set("insert", insert_index)

        self.text_area.focus_set()
        self._save_body()
        self._apply_markdown_formatting()

    def _save_title(self):
        if not self.current_page_id:
            return

        title = self.title_entry.get().strip() or "Untitled"
        self.backend.set_title(self.current_page_id, title)
        self.current_page = self.backend.get_page(self.current_page_id)
        self._update_sidebar_title(self.current_page_id, title)
        self._refresh_breadcrumb()
        self._refresh_status()

    def _save_body(self):
        if not self.current_page_id:
            return

        content = self.text_area.get("1.0", "end").strip("\n")
        blocks = []
        if content:
            block_id = None
            if self.current_page and self.current_page.get("blocks"):
                block_id = self.current_page["blocks"][0]["id"]
            blocks.append({
                "id": block_id or "",
                "type": "paragraph",
                "content": content,
                "checked": False,
                "language": None,
            })

        self.backend.set_blocks(self.current_page_id, blocks)
        self.current_page = self.backend.get_page(self.current_page_id)

        words = self.backend.word_count(self.current_page_id)
        self.backend.update_focus_score(words_written=words, idle_seconds=0)
        self._refresh_status()

    def _refresh_status(self):
        page_count = self.backend.total_page_count()
        words = self.backend.word_count(self.current_page_id)
        focus_score = self.backend.focus_metrics(self.current_page_id)["score"]

        if self.page_count_label:
            self.page_count_label.configure(text=f"{page_count} pages")
        if self.word_count_label:
            self.word_count_label.configure(text=f"{words} words")
        if self.score_badge:
            self.score_badge.configure(text=f" {focus_score} ")

        status = self.backend.save(force=True)
        if self.saved_label:
            self.saved_label.configure(text="Saved just now")

    def _format_duration(self, total_seconds):
        minutes, seconds = divmod(int(total_seconds), 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}h {minutes}m"
        if minutes:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    def _open_focus_score(self):
        metrics = self.backend.focus_metrics(self.current_page_id)
        score = metrics["score"]

        window = ctk.CTkToplevel(self)
        window.title("Focus Score")
        window.geometry("320x360")
        window.transient(self)
        window.grab_set()
        window.columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(window, fg_color=BG_ELEVATED, corner_radius=RADIUS_LG)
        frame.grid(row=0, column=0, sticky="nsew", padx=SP_10, pady=SP_10)
        frame.columnconfigure(0, weight=1)

        canvas = tk.Canvas(frame, width=170, height=170, bg=BG_ELEVATED, highlightthickness=0)
        canvas.grid(row=0, column=0, pady=(SP_12, SP_6))
        canvas.create_oval(20, 20, 150, 150, outline=BORDER_SUBTLE, width=12)
        canvas.create_arc(
            20, 20, 150, 150,
            start=90,
            extent=-(score / 100) * 360,
            outline=ACCENT,
            width=12,
            style="arc",
        )
        canvas.create_text(
            85, 78,
            text=str(score),
            fill=TEXT_PRIMARY,
            font=(FONT_FAMILY, 32, "bold"),
        )
        canvas.create_text(
            85, 108,
            text="/100",
            fill=TEXT_SECONDARY,
            font=(FONT_FAMILY, 13),
        )

        attention = self._format_duration(metrics["attention_seconds"])
        speed = metrics["words_per_second"]
        rows = [
            ("Attention Span", attention),
            ("Writing Speed", f"{speed:.2f} words/sec"),
            ("Words Written", str(metrics["words"])),
        ]

        for index, (label, value) in enumerate(rows, start=1):
            stat = ctk.CTkFrame(frame, fg_color=BG_ELEVATED, corner_radius=0)
            stat.grid(row=index, column=0, sticky="ew", padx=SP_12, pady=SP_3)
            stat.columnconfigure(1, weight=1)
            ctk.CTkLabel(
                stat,
                text=label,
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SM),
                text_color=TEXT_SECONDARY,
                fg_color=BG_ELEVATED,
            ).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(
                stat,
                text=value,
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SM, weight="bold"),
                text_color=TEXT_PRIMARY,
                fg_color=BG_ELEVATED,
            ).grid(row=0, column=1, sticky="e")

    def _refresh_breadcrumb(self):
        if self.breadcrumb_title_label and self.current_page:
            self.breadcrumb_title_label.configure(text=self.current_page.get("title") or "Untitled")

    def _refresh_theme_labels(self):
        theme = (self.backend.data["settings"].get("theme") or "light").lower()
        label = "Dark" if theme == "dark" else "Light"
        icon = "◐" if theme == "dark" else "☀"

        if self.theme_label:
            self.theme_label.configure(text=label)
        if self.theme_icon:
            self.theme_icon.configure(text=icon)
        if self.status_theme_label:
            self.status_theme_label.configure(text=label)
        if self.status_theme_icon:
            self.status_theme_icon.configure(text=icon)

    def _refresh_context_tags(self):
        if not self.context_tag_frame:
            return

        for widget in self.context_tag_frame.winfo_children():
            widget.destroy()

        context_pages = self.backend.get_ai_context_pages()
        if not context_pages:
            label = ctk.CTkLabel(
                self.context_tag_frame, text="Right-click pages to add context",
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS),
                fg_color=BG_PANEL, text_color=TEXT_MUTED
            )
            label.grid(row=0, column=0, sticky="w")
            return

        for index, page in enumerate(context_pages):
            chip = self._create_chip(
                self.context_tag_frame,
                page.get("title") or "Untitled",
                close_command=lambda page_id=page["id"]: self._remove_context_page(page_id),
            )
            chip.grid(row=0, column=index, sticky="w", padx=(0, SP_2))

    def _remove_context_page(self, page_id):
        self.backend.remove_ai_context_page(page_id)
        self._refresh_context_tags()

    def _refresh_chat(self):
        if not self.messages_frame:
            return

        for widget in self.messages_frame.winfo_children():
            widget.destroy()

        for message in self.backend.chat_history():
            owner = "assistant" if message["role"] == "assistant" else "user"
            self._create_message(self.messages_frame, message["content"], owner=owner)

    def _append_chat_message(self, role, content):
        self.backend.append_chat(role, content)
        self._refresh_chat()
        self._scroll_chat_to_bottom()

    def _show_pdf_menu(self):
        if not self.pdf_btn:
            return

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Insert PDF", command=self._insert_pdf)
        x_root = self.pdf_btn.winfo_rootx()
        y_root = self.pdf_btn.winfo_rooty() - 28
        try:
            menu.tk_popup(x_root, y_root)
        finally:
            menu.grab_release()

    def _insert_pdf(self):
        path = filedialog.askopenfilename(
            title="Insert PDF",
            filetypes=[("PDF files", "*.pdf")],
        )
        if not path:
            return

        try:
            text = self._extract_pdf_text(path)
        except Exception as exc:
            messagebox.showerror("Insert PDF", str(exc))
            return

        if not text.strip():
            messagebox.showerror("Insert PDF", "The selected PDF has no extractable text.")
            return

        self.pdf_context_text = text
        self.pdf_context_name = path.split("/")[-1].split("\\")[-1]
        self._append_chat_message("assistant", f"PDF inserted: {self.pdf_context_name}. Type what you want to do with it.")

    def _extract_pdf_text(self, path):
        try:
            import fitz
        except ImportError as exc:
            raise RuntimeError("PyMuPDF is required to insert PDFs. Install it with: pip install PyMuPDF") from exc

        parts = []
        document = fitz.open(path)
        try:
            for page in document:
                page_text = page.get_text("text")
                if page_text:
                    parts.append(page_text)
        finally:
            document.close()

        return "\n\n".join(parts).strip()

    def _insert_ai_response_into_editor(self, content):
        if not content:
            return

        current = self.text_area.get("1.0", "end").strip("\n")
        separator = "\n\n" if current else ""
        self.text_area.insert("end", f"{separator}{content}")
        self._save_body()
        self._apply_markdown_formatting()

    def _scroll_chat_to_bottom(self):
        if not self.messages_frame:
            return

        def scroll():
            canvas = getattr(self.messages_frame, "_parent_canvas", None)
            if canvas and canvas.bbox("all"):
                canvas.update_idletasks()
                canvas.yview_moveto(1.0)

        self.after(50, scroll)

    def _run_quick_action(self, action):
        selection = self.text_area.get("sel.first", "sel.last") if self.text_area.tag_ranges("sel") else ""
        source_text = selection.strip() or self.text_area.get("1.0", "end").strip("\n")

        if action == "expand" and not selection.strip():
            self._create_message(self.messages_frame, "Select text to expand.", owner="assistant")
            return

        language = None
        if action == "translate":
            dialog = ctk.CTkInputDialog(text="Translate to which language?", title="Translate")
            language = dialog.get_input()
            if not language:
                return
            language = language.strip()

        loading = self._create_message(self.messages_frame, "Thinking...", owner="assistant")
        self._scroll_chat_to_bottom()
        self.update_idletasks()
        for button in self.action_buttons.values():
            button.configure(state="disabled")

        def finish(error=None):
            if loading.winfo_exists():
                loading.destroy()
            if error:
                self._append_chat_message("assistant", str(error))
            else:
                self._refresh_chat()
                self._scroll_chat_to_bottom()
            for button in self.action_buttons.values():
                button.configure(state="normal")

        def worker():
            try:
                if action == "summarize":
                    self.backend.summarize_page(self.current_page_id)
                elif action == "fix_grammar":
                    self.backend.fix_grammar(source_text, self.current_page_id)
                elif action == "expand":
                    self.backend.expand_text(source_text)
                elif action == "translate":
                    self.backend.translate_text(source_text, language)
                else:
                    self.after(0, lambda: finish("Unsupported action"))
                    return
            except Exception as exc:
                self.after(0, lambda exc=exc: finish(exc))
                return
            self.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def _send_chat_message(self):
        question = self.ask_entry.get().strip()
        if not question:
            return

        self.ask_entry.delete(0, "end")
        self.backend.append_chat("user", question)
        self._refresh_chat()
        loading = self._create_message(self.messages_frame, "Thinking...", owner="assistant")
        self._scroll_chat_to_bottom()
        self.update_idletasks()
        if self.send_btn:
            self.send_btn.configure(state="disabled")

        def finish(error=None):
            if loading.winfo_exists():
                loading.destroy()
            if error:
                self._append_chat_message("assistant", str(error))
            else:
                self._refresh_chat()
                self._scroll_chat_to_bottom()
            if self.send_btn:
                self.send_btn.configure(state="normal")

        def worker():
            try:
                if self.pdf_context_text:
                    result = self.backend.ask_pdf_question(question, self.pdf_context_text)
                    self.after(0, lambda content=result.get("content", ""): self._insert_ai_response_into_editor(content))
                else:
                    self.backend.ask_question(question, self.current_page_id, persist_user=False)
            except Exception as exc:
                self.after(0, lambda exc=exc: finish(exc))
                return
            self.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def _create_new_page(self):
        new_page = self.backend.create_page("Untitled")
        self.current_page_id = new_page["id"]
        self.current_page = new_page
        self._refresh_all()

    def _toggle_theme(self):
        current = (self.backend.data["settings"].get("theme") or "light").lower()
        next_theme = "dark" if current == "light" else "light"
        self.backend.set_theme(next_theme)
        ctk.set_appearance_mode(next_theme.title())
        self._refresh_theme_labels()

    def _open_settings(self):
        settings = self.backend.data["settings"]
        window = ctk.CTkToplevel(self)
        window.title("Settings")
        window.geometry("420x470")
        window.transient(self)
        window.grab_set()
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        frame = ctk.CTkScrollableFrame(
            window,
            fg_color=BG_ELEVATED,
            corner_radius=RADIUS_LG,
            scrollbar_button_color=BORDER_DEFAULT,
            scrollbar_button_hover_color=TEXT_MUTED
        )
        frame.grid(row=0, column=0, sticky="nsew", padx=SP_10, pady=SP_10)
        frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame, text="Settings",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XL, weight="bold"),
            text_color=TEXT_PRIMARY, fg_color=BG_ELEVATED
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=SP_8, pady=(SP_8, SP_6))

        theme_var = tk.StringVar(value=(settings.get("theme") or "light").title())
        provider_var = tk.StringVar(value=(settings.get("ai_provider") or "openai").title())
        font_family_var = tk.StringVar(value=settings.get("font_family") or FONT_FAMILY)

        rows = [
            ("Theme", ctk.CTkOptionMenu(frame, values=["Light", "Dark"], variable=theme_var)),
            ("Provider", ctk.CTkOptionMenu(frame, values=["Openai", "Anthropic", "Nvidia"], variable=provider_var)),
            ("Font", ctk.CTkOptionMenu(
                frame,
                values=["Segoe UI", "Arial", "Calibri", "Cambria", "Consolas", "Georgia", "Times New Roman", "Verdana"],
                variable=font_family_var,
            )),
            ("Font Size", ctk.CTkEntry(frame)),
            ("Autosave Seconds", ctk.CTkEntry(frame)),
            ("API Key", ctk.CTkEntry(frame, show="*")),
        ]

        rows[3][1].insert(0, str(settings.get("font_size") or 13))
        rows[4][1].insert(0, str(settings.get("autosave_interval_sec") or 30))
        rows[5][1].insert(0, settings.get("ai_api_key") or "")

        for index, (label_text, control) in enumerate(rows, start=1):
            ctk.CTkLabel(
                frame, text=label_text,
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SM),
                text_color=TEXT_SECONDARY, fg_color=BG_ELEVATED
            ).grid(row=index, column=0, sticky="w", padx=SP_8, pady=SP_4)
            control.grid(row=index, column=1, sticky="ew", padx=SP_8, pady=SP_4)

        shortcut_start = len(rows) + 1
        ctk.CTkLabel(
            frame, text="Shortcuts",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SM, weight="bold"),
            text_color=TEXT_PRIMARY, fg_color=BG_ELEVATED
        ).grid(row=shortcut_start, column=0, columnspan=2, sticky="w", padx=SP_8, pady=(SP_8, SP_2))

        shortcuts = [
            ("Save file anywhere", "Ctrl+S"),
            ("Undo", "Ctrl+Z"),
            ("Find in page", "Ctrl+F"),
        ]
        for offset, (name, shortcut) in enumerate(shortcuts, start=1):
            ctk.CTkLabel(
                frame, text=name,
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS),
                text_color=TEXT_SECONDARY, fg_color=BG_ELEVATED
            ).grid(row=shortcut_start + offset, column=0, sticky="w", padx=SP_8, pady=SP_2)
            ctk.CTkLabel(
                frame, text=shortcut,
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS, weight="bold"),
                text_color=TEXT_PRIMARY, fg_color=BG_ELEVATED
            ).grid(row=shortcut_start + offset, column=1, sticky="e", padx=SP_8, pady=SP_2)

        def save_settings():
            try:
                self.backend.set_theme(theme_var.get().lower())
                self.backend.set_ai_provider(provider_var.get().lower())
                self.backend.set_font_family(font_family_var.get())
                font_size = int(rows[3][1].get())
                if font_size < 8:
                    raise ValueError("Font size must be at least 8.")
                self.backend.set_font_size(font_size)
                self.backend.set_autosave_interval(int(rows[4][1].get()))
                self.backend.set_api_key(rows[5][1].get().strip())
            except ValueError as exc:
                messagebox.showerror("Settings", str(exc))
                return

            ctk.set_appearance_mode(theme_var.get())
            self._apply_editor_font_size()
            self._refresh_theme_labels()
            window.destroy()

        ctk.CTkButton(
            frame, text="Save",
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            command=save_settings
        ).grid(row=shortcut_start + len(shortcuts) + 1, column=1, sticky="e", padx=SP_8, pady=(SP_8, SP_10))

    def _on_close(self):
        self.backend.clear_chat_history()
        self.backend.save(force=True)
        self.backend.stop_autosave()
        self.destroy()

    def _create_chip(self, parent, text, close_command=None):
        chip = ctk.CTkFrame(
            parent, fg_color=BG_ELEVATED, corner_radius=RADIUS_MD,
            border_width=1, border_color=BORDER_SUBTLE
        )
        chip.grid_propagate(False)
        chip.configure(height=26)
        chip.rowconfigure(0, weight=1)

        chip_label = ctk.CTkLabel(
            chip, text=text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS),
            fg_color=BG_ELEVATED, text_color=TEXT_PRIMARY
        )
        chip_label.grid(row=0, column=0, sticky="w", padx=(SP_4, SP_1), pady=SP_1)

        close_label = ctk.CTkLabel(
            chip, text="✕",
            font=ctk.CTkFont(size=ICON_XS),
            fg_color=BG_ELEVATED, text_color=TEXT_MUTED,
            width=14, height=14
        )
        close_label.grid(row=0, column=1, sticky="e", padx=(0, SP_3), pady=SP_1)
        if close_command:
            close_label.configure(cursor="hand2")
            close_label.bind("<Button-1>", lambda event: close_command())
        return chip

    def _create_message(self, parent, text, owner="assistant"):
        if owner == "assistant" and str(text).startswith("PDF inserted:"):
            return self._create_pdf_attached_message(parent, text)

        bg = BG_ELEVATED if owner == "assistant" else ACCENT_SUBTLE
        align = "w" if owner == "assistant" else "e"
        bubble = ctk.CTkFrame(
            parent, fg_color=bg, corner_radius=RADIUS_LG,
            border_width=1, border_color=BORDER_SUBTLE
        )
        bubble.grid(sticky=align, pady=SP_2, padx=0)
        bubble.grid_propagate(True)
        wrap_len = RIGHT_PANEL_WIDTH - SP_20 - SP_16
        label = ctk.CTkLabel(
            bubble, text=self._wrap_chat_text(text), wraplength=wrap_len, justify="left",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SM),
            fg_color=bg, text_color=TEXT_PRIMARY
        )
        label.grid(row=0, column=0, sticky="w", padx=SP_5, pady=(SP_4, SP_2))
        if owner == "assistant":
            copy_label = ctk.CTkLabel(
                bubble, text="⧉",
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BASE),
                fg_color=bg, text_color=TEXT_SECONDARY,
                cursor="hand2"
            )
            copy_label.grid(row=1, column=0, sticky="e", padx=SP_5, pady=(0, SP_4))
            copy_label.bind("<Button-1>", lambda _event, value=text: self._copy_chat_message(value))
        return bubble

    def _create_pdf_attached_message(self, parent, text):
        filename = str(text).replace("PDF inserted:", "", 1).split(". Type what", 1)[0].strip()
        bubble = ctk.CTkFrame(
            parent, fg_color=BG_ELEVATED, corner_radius=RADIUS_LG,
            border_width=1, border_color=BORDER_SUBTLE
        )
        bubble.grid(sticky="w", pady=SP_2, padx=0)
        bubble.columnconfigure(1, weight=1)

        badge = ctk.CTkLabel(
            bubble, text="PDF",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS, weight="bold"),
            fg_color=ACCENT_SUBTLE, text_color=ACCENT,
            width=38, height=28, corner_radius=RADIUS_SM
        )
        badge.grid(row=0, column=0, rowspan=2, sticky="n", padx=(SP_5, SP_4), pady=SP_5)

        title = ctk.CTkLabel(
            bubble, text="PDF attached",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SM, weight="bold"),
            fg_color=BG_ELEVATED, text_color=TEXT_PRIMARY
        )
        title.grid(row=0, column=1, sticky="w", padx=(0, SP_5), pady=(SP_5, 0))

        detail = ctk.CTkLabel(
            bubble,
            text=f"{filename}\nAsk for a summary, translation, notes, or edits.",
            wraplength=RIGHT_PANEL_WIDTH - 96,
            justify="left",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS),
            fg_color=BG_ELEVATED, text_color=TEXT_SECONDARY
        )
        detail.grid(row=1, column=1, sticky="w", padx=(0, SP_5), pady=(0, SP_5))
        return bubble

    def _copy_chat_message(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)

    def _wrap_chat_text(self, text, chunk_size=36):
        parts = []
        for line in str(text).splitlines() or [""]:
            words = line.split(" ")
            wrapped_words = []
            for word in words:
                if len(word) <= chunk_size:
                    wrapped_words.append(word)
                    continue
                chunks = [word[index:index + chunk_size] for index in range(0, len(word), chunk_size)]
                wrapped_words.append("\n".join(chunks))
            parts.append(" ".join(wrapped_words))
        return "\n".join(parts)

    def _add_command_row(self, parent, icon_char, name, desc, shortcut):
        row = ctk.CTkFrame(parent, fg_color=BG_ELEVATED, corner_radius=RADIUS_LG, border_width=0)
        row.grid(sticky="ew", padx=SP_5, pady=SP_2)
        row.columnconfigure(1, weight=1)

        icon = ctk.CTkLabel(
            row, text=icon_char,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BASE),
            fg_color=BG_ELEVATED, text_color=TEXT_PRIMARY
        )
        icon.grid(row=0, column=0, padx=(SP_6, SP_5), pady=SP_6)

        text_frame = ctk.CTkFrame(row, fg_color=BG_ELEVATED, corner_radius=0, border_width=0)
        text_frame.grid(row=0, column=1, sticky="ew", pady=SP_5)
        text_frame.columnconfigure(0, weight=1)

        name_label = ctk.CTkLabel(
            text_frame, text=name,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color=BG_ELEVATED, text_color=TEXT_PRIMARY
        )
        name_label.grid(row=0, column=0, sticky="w")

        desc_label = ctk.CTkLabel(
            text_frame, text=desc,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS),
            fg_color=BG_ELEVATED, text_color=TEXT_SECONDARY
        )
        desc_label.grid(row=1, column=0, sticky="w")

        if shortcut:
            shortcut_label = ctk.CTkLabel(
                row, text=shortcut,
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_XS),
                fg_color=BG_ELEVATED, text_color=TEXT_MUTED
            )
            shortcut_label.grid(row=0, column=2, padx=(0, SP_6), sticky="e")

        row.bind("<Enter>", lambda e, w=row: w.configure(fg_color=BORDER_SUBTLE))
        row.bind("<Leave>", lambda e, w=row: w.configure(fg_color=BG_ELEVATED))

        for widget in row.winfo_children():
            widget.bind("<Enter>", lambda e, w=row: w.configure(fg_color=BORDER_SUBTLE))
            widget.bind("<Leave>", lambda e, w=row: w.configure(fg_color=BG_ELEVATED))

        return row


def main():
    app = WriteApp()
    app.mainloop()


if __name__ == "__main__":
    main()

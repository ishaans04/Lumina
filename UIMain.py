import customtkinter as ctk

# Configure appearance
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

# Common spacing, radius, and typography tokens
RADIUS_SMALL = 4
RADIUS_MEDIUM = 8
RADIUS_LARGE = 12
RADIUS_XL = 16
RADIUS_FULL = 9999

GAP_XS = 4
GAP_SM = 6
GAP = 8
GAP_MD = 10
GAP_L = 12
GAP_XL = 20

P_0_5 = 2
P_1 = 4
P_1_5 = 6
P_2 = 8
P_2_5 = 10
P_3 = 12
P_4 = 16
P_5 = 20
P_6 = 24
P_8 = 32
P_12 = 48
P_20 = 80

FONT_XS = 12
FONT_SM = 12
FONT_BASE = 16
FONT_LG = 18
FONT_XL = 20
FONT_2XL = 24
FONT_5XL = 48

# Icon sizes
ICON_XS = 12
ICON_SM = 14
ICON_DEFAULT = 16
ICON_MD = 20
ICON_LG = 28

RIGHT_PANEL_WIDTH = 340
STATUS_BAR_HEIGHT = 30
STATUS_BAR_GAP = GAP_XL

class WriteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Write")
        
        # Full viewport dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")
        
        self.configure(fg_color="#F5F3EF")
        self._build_ui()

    def _build_ui(self):
        # App container: flexbox column layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # Title bar fixed
        self.rowconfigure(1, weight=1)  # Main content area flex: 1
        self.rowconfigure(2, weight=0)  # Status bar fixed

        # Title bar
        title_bar = ctk.CTkFrame(self, fg_color="#F5F3EF", corner_radius=0, border_width=0)
        title_bar.grid(row=0, column=0, sticky="ew")
        title_bar.columnconfigure(0, weight=1)
        title_bar.rowconfigure(0, weight=0)
        title_bar.rowconfigure(1, weight=0)
        self._build_titlebar(title_bar)

        # Main content area: flexbox row layout
        main_content = ctk.CTkFrame(self, fg_color="#F5F3EF", corner_radius=0)
        main_content.grid(row=1, column=0, sticky="nsew", padx=P_5, pady=P_5)
        main_content.columnconfigure(0, weight=0)  # Sidebar fixed
        main_content.columnconfigure(1, weight=1)  # Editor flex: 1
        main_content.columnconfigure(2, weight=0)  # Right panel fixed
        main_content.rowconfigure(0, weight=1)

        # Left sidebar
        sidebar = ctk.CTkFrame(main_content, fg_color="#EDE9E3", corner_radius=0, border_width=1, border_color="#D9D4CC")
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, P_2_5))
        sidebar.grid_propagate(False)
        sidebar.configure(width=256)
        self._build_sidebar(sidebar)

        # Main editor area
        main_area = ctk.CTkFrame(main_content, fg_color="#F5F3EF", corner_radius=0)
        main_area.grid(row=0, column=1, sticky="nsew", padx=(0, P_2_5))
        main_area.columnconfigure(0, weight=1)
        main_area.rowconfigure(0, weight=1)
        self._build_editor(main_area)

        # Right panel container with left border
        right_panel_container = ctk.CTkFrame(main_content, fg_color="#F5F3EF", corner_radius=0)
        right_panel_container.grid(row=0, column=2, sticky="nsew")
        right_panel_container.columnconfigure(0, weight=0)
        right_panel_container.columnconfigure(1, weight=1)
        right_panel_container.rowconfigure(0, weight=1)

        left_border = ctk.CTkFrame(right_panel_container, fg_color="#D9D4CC", width=1, corner_radius=0)
        left_border.grid(row=0, column=0, sticky="ns")

        right_panel = ctk.CTkFrame(right_panel_container, fg_color="#F0EDE8", corner_radius=0)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_propagate(False)
        right_panel.configure(width=RIGHT_PANEL_WIDTH)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(4, weight=1)
        self._build_aipanel(right_panel)

        # Status bar
        status_bar = ctk.CTkFrame(self, fg_color="#F5F3EF", corner_radius=0, height=STATUS_BAR_HEIGHT)
        status_bar.grid(row=2, column=0, sticky="ew", padx=P_5, pady=(0, P_5))
        status_bar.grid_propagate(False)
        status_bar.columnconfigure(0, weight=1)
        status_bar.columnconfigure(1, weight=1)
        status_bar.columnconfigure(2, weight=1)

        top_border = ctk.CTkFrame(status_bar, fg_color="#D9D4CC", height=1, corner_radius=0)
        top_border.grid(row=0, column=0, columnspan=3, sticky="ew")

        left_item = ctk.CTkFrame(status_bar, fg_color="#F5F3EF", corner_radius=0)
        left_item.grid(row=1, column=0, sticky="w", padx=(0, STATUS_BAR_GAP), pady=(P_1_5, 0))
        left_icon = ctk.CTkLabel(left_item, text="●", font=ctk.CTkFont(size=FONT_XS), fg_color="#F5F3EF", text_color="#888888")
        left_icon.grid(row=0, column=0)
        left_status = ctk.CTkLabel(left_item, text="Active", text_color="#888888", font=ctk.CTkFont(family="Segoe UI", size=FONT_XS), fg_color="#F5F3EF")
        left_status.grid(row=0, column=1, padx=(P_1_5, 0))

        middle_item = ctk.CTkFrame(status_bar, fg_color="#F5F3EF", corner_radius=0)
        middle_item.grid(row=1, column=1, sticky="w", padx=(0, STATUS_BAR_GAP), pady=(P_1_5, 0))
        mid_icon = ctk.CTkLabel(middle_item, text="📄", font=ctk.CTkFont(size=FONT_XS), fg_color="#F5F3EF", text_color="#888888")
        mid_icon.grid(row=0, column=0)
        mid_status_1 = ctk.CTkLabel(middle_item, text="6 pages", text_color="#888888", font=ctk.CTkFont(family="Segoe UI", size=FONT_XS), fg_color="#F5F3EF")
        mid_status_1.grid(row=0, column=1, padx=(P_1_5, 0))
        separator = ctk.CTkFrame(middle_item, fg_color="#D9D4CC", width=1, height=P_3, corner_radius=0)
        separator.grid(row=0, column=2, padx=(P_3, P_3))
        mid_status_2 = ctk.CTkLabel(middle_item, text="1,248 words", text_color="#888888", font=ctk.CTkFont(family="Segoe UI", size=FONT_XS), fg_color="#F5F3EF")
        mid_status_2.grid(row=0, column=3)

        right_item = ctk.CTkFrame(status_bar, fg_color="#F5F3EF", corner_radius=0)
        right_item.grid(row=1, column=2, sticky="e", pady=(P_1_5, 0))
        light_icon = ctk.CTkLabel(right_item, text="☀", font=ctk.CTkFont(size=FONT_XS), fg_color="#F5F3EF", text_color="#888888")
        light_icon.grid(row=0, column=0)
        light_label = ctk.CTkLabel(right_item, text="Light", text_color="#888888", font=ctk.CTkFont(family="Segoe UI", size=FONT_XS), fg_color="#F5F3EF")
        light_label.grid(row=0, column=1, padx=(P_1_5, 0))
        right_separator = ctk.CTkFrame(right_item, fg_color="#D9D4CC", width=1, height=P_3, corner_radius=0)
        right_separator.grid(row=0, column=2, padx=(P_3, P_3))
        saved_label = ctk.CTkLabel(right_item, text="Saved 2m ago", text_color="#888888", font=ctk.CTkFont(family="Segoe UI", size=FONT_XS), fg_color="#F5F3EF")
        saved_label.grid(row=0, column=3)

    def _build_titlebar(self, title_bar):
        # Row 0: Window Title Bar (height 44px)
        window_title = ctk.CTkFrame(title_bar, fg_color="#F5F3EF", corner_radius=0, border_width=0, height=44)
        window_title.grid(row=0, column=0, sticky="ew")
        window_title.grid_propagate(False)
        window_title.columnconfigure(0, weight=0)
        window_title.columnconfigure(1, weight=1)
        window_title.columnconfigure(2, weight=0)

        # Title text: font 12px, gap 8px
        title_text = ctk.CTkLabel(window_title, text="Write", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#3D3D3D", fg_color="#F5F3EF")
        title_text.grid(row=0, column=0, sticky="w", padx=16, pady=15)

        # Window Control Buttons: padding 6px, icon 14px, gap 4px
        controls_frame = ctk.CTkFrame(window_title, fg_color="#F5F3EF", corner_radius=0, border_width=0)
        controls_frame.grid(row=0, column=2, sticky="e", padx=16, pady=15)
        
        min_btn = ctk.CTkButton(controls_frame, text="−", width=26, height=26, fg_color="transparent", text_color="#3D3D3D", font=ctk.CTkFont(size=ICON_SM), hover_color="#E0DDD8")
        min_btn.grid(row=0, column=0, padx=2)
        max_btn = ctk.CTkButton(controls_frame, text="□", width=26, height=26, fg_color="transparent", text_color="#3D3D3D", font=ctk.CTkFont(size=ICON_SM), hover_color="#E0DDD8")
        max_btn.grid(row=0, column=1, padx=2)
        close_btn = ctk.CTkButton(controls_frame, text="✕", width=26, height=26, fg_color="transparent", text_color="#3D3D3D", font=ctk.CTkFont(size=ICON_SM), hover_color="#E0DDD8")
        close_btn.grid(row=0, column=2, padx=2)

        # Row 1: Breadcrumb Bar (height 36px)
        breadcrumb_bar = ctk.CTkFrame(title_bar, fg_color="#FAFBFC", corner_radius=0, border_width=1, border_color="#E5EAEF", height=36)
        breadcrumb_bar.grid(row=1, column=0, sticky="ew")
        breadcrumb_bar.grid_propagate(False)
        breadcrumb_bar.columnconfigure(0, weight=1)

        breadcrumb_frame = ctk.CTkFrame(breadcrumb_bar, fg_color="#FAFBFC", corner_radius=0, border_width=0)
        breadcrumb_frame.grid(row=0, column=0, sticky="w", padx=24, pady=8)

        # Breadcrumb items: text 12px, gap 6px, chevron 12px
        breadcrumb_items = ["Personal", "Projects", "Untitled"]
        for i, item in enumerate(breadcrumb_items):
            if i > 0:
                chevron = ctk.CTkLabel(breadcrumb_frame, text="›", font=ctk.CTkFont(size=ICON_XS), text_color="#888888", fg_color="#FAFBFC")
                chevron.grid(row=0, column=i*2-1, padx=6)
            item_label = ctk.CTkLabel(breadcrumb_frame, text=item, font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#3D3D3D", fg_color="#FAFBFC")
            item_label.grid(row=0, column=i*2, padx=0)

    def _build_sidebar(self, sidebar):
        sidebar.rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=0)
        sidebar.rowconfigure(7, weight=1)
        sidebar.rowconfigure(8, weight=0)

        # Logo section: padding 20px all, gap 10px
        top_bar = ctk.CTkFrame(sidebar, fg_color="#EDE9E3", corner_radius=0, border_width=0)
        top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        top_bar.columnconfigure(1, weight=0)

        # Logo icon box: 32×32, radius 8
        icon_square = ctk.CTkLabel(top_bar, text="", width=32, height=32, fg_color="transparent", corner_radius=8)
        icon_square.grid(row=0, column=0, sticky="w")
        # Logo text: 18px
        title_label = ctk.CTkLabel(top_bar, text="Write", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color="#3D3D3D", fg_color="#EDE9E3")
        title_label.grid(row=0, column=1, sticky="w", padx=(30, 0))

        # New Page Button: padding 16px horizontal, 12px bottom
        new_page_btn = ctk.CTkButton(sidebar, text="+ New Page", fg_color="#C8864A", hover_color="#b46d3f", text_color="white", corner_radius=8, font=ctk.CTkFont(family="Segoe UI", size=12), height=36)
        new_page_btn.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))

        # Search Bar: padding 16px horizontal, 8px bottom, input padding left 36px right 12px vertical 8px, text 14px
        search_entry = ctk.CTkEntry(sidebar, placeholder_text="Search pages...", fg_color="#FFFFFF", text_color="#3D3D3D", placeholder_text_color="#AAAAAA", border_width=1, border_color="#D9D4CC", corner_radius=8, height=32)
        search_entry.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))

        # Separator: margin 16px horizontal, 1px height, 8px vertical
        separator = ctk.CTkFrame(sidebar, fg_color="#D9D4CC", corner_radius=0, border_width=0, height=1)
        separator.grid(row=3, column=0, sticky="ew", padx=16, pady=8)

        # Pages List: padding 16px 8px, space 2px between items
        list_frame = ctk.CTkScrollableFrame(sidebar, fg_color="#EDE9E3", border_width=0, corner_radius=0)
        list_frame.grid(row=4, column=0, sticky="nsew", padx=8, pady=0)
        list_frame.columnconfigure(0, weight=1)

        pages = ["Untitled", "Project Ideas", "Meeting Notes", "Draft Essay", "Research Notes", "Weekly Journal"]
        for page in pages:
            selected = page == "Untitled"
            item_bg = "#C8864A" if selected else "#EDE9E3"
            item_text = "white" if selected else "#3D3D3D"
            # Item padding: 12px 10px, icon 16px, gap 12px, text 14px, radius 8px
            item_frame = ctk.CTkFrame(list_frame, fg_color=item_bg, corner_radius=8, height=32)
            item_frame.grid(sticky="ew", pady=1)
            item_frame.grid_columnconfigure(1, weight=1)
            icon = ctk.CTkLabel(item_frame, text="📄", font=ctk.CTkFont(size=ICON_DEFAULT), fg_color=item_bg, text_color=item_text)
            icon.grid(row=0, column=0, padx=(10, 0), pady=8)
            label = ctk.CTkLabel(item_frame, text=page, font=ctk.CTkFont(family="Segoe UI", size=14), text_color=item_text, fg_color=item_bg)
            label.grid(row=0, column=1, sticky="w", padx=(12, 10), pady=8)

        # Bottom Options: padding 16px, space 4px between items
        footer = ctk.CTkFrame(sidebar, fg_color="#EDE9E3", corner_radius=0, border_width=0)
        footer.grid(row=8, column=0, sticky="ew", padx=16, pady=16)

        # Score row: button padding 12px 10px, icon 16px, gap 12px, badge padding 8px 2px, text 12px
        score_row = ctk.CTkFrame(footer, fg_color="#EDE9E3", corner_radius=0)
        score_row.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        score_row.columnconfigure(0, weight=1)
        score_label = ctk.CTkLabel(score_row, text="Focus Score", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#3D3D3D", fg_color="#EDE9E3")
        score_label.grid(row=0, column=0, sticky="w", padx=0, pady=8)
        score_badge = ctk.CTkLabel(score_row, text="  85  ", width=32, height=18, fg_color="#C8864A", text_color="white", corner_radius=8, font=ctk.CTkFont(family="Segoe UI", size=12))
        score_badge.grid(row=0, column=1, sticky="e", padx=(20,0), pady=2)

        # Light row
        light_row = ctk.CTkFrame(footer, fg_color="#EDE9E3", corner_radius=0)
        light_row.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        light_row.columnconfigure(1, weight=1)
        light_label = ctk.CTkLabel(light_row, text="Light", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#3D3D3D", fg_color="#EDE9E3")
        light_label.grid(row=0, column=0, sticky="w", padx=0, pady=8)
        light_icon = ctk.CTkLabel(light_row, text="☀", font=ctk.CTkFont(size=ICON_DEFAULT), fg_color="#EDE9E3", text_color="#3D3D3D")
        light_icon.grid(row=0, column=1, sticky="e", padx=0, pady=8)

        # Settings row
        settings_row = ctk.CTkFrame(footer, fg_color="#EDE9E3", corner_radius=0)
        settings_row.grid(row=2, column=0, sticky="ew")
        settings_row.columnconfigure(1, weight=1)
        settings_label = ctk.CTkLabel(settings_row, text="Settings", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#3D3D3D", fg_color="#EDE9E3")
        settings_label.grid(row=0, column=0, sticky="w", padx=0, pady=8)
        settings_icon = ctk.CTkLabel(settings_row, text="⚙", font=ctk.CTkFont(size=ICON_DEFAULT), fg_color="#EDE9E3", text_color="#3D3D3D")
        settings_icon.grid(row=0, column=1, sticky="e", padx=0, pady=8)

    def _build_editor(self, main_area):
        # Editor container: flex 1, auto overflow vertically
        editor_scroll = ctk.CTkScrollableFrame(main_area, fg_color="#F5F3EF", corner_radius=0, border_width=0)
        editor_scroll.grid(row=0, rowspan=3, column=0, sticky="nsew")
        editor_scroll.columnconfigure(0, weight=1)
        editor_scroll.rowconfigure(0, weight=0)
        
        # Content column: max width 680px, top aligned, padding 48px horizontal 80px vertical
        content_wrapper = ctk.CTkFrame(editor_scroll, fg_color="#F5F3EF", corner_radius=0, border_width=0)
        content_wrapper.grid(row=0, column=0, sticky="n", padx=80, pady=(48, 20))

        spacer = ctk.CTkFrame(editor_scroll, fg_color="#F5F3EF", corner_radius=0)
        spacer.grid(row=1, column=0, sticky="nsew")

        # Emoji icon: 64×64, text 48px, radius 8px
        icon_frame = ctk.CTkFrame(content_wrapper, fg_color="#F5F3EF", corner_radius=0, border_width=0)
        icon_frame.pack(fill="x", pady=(0, 12))

        icon_box = ctk.CTkLabel(content_wrapper, text="📝", font=ctk.CTkFont(size=64), fg_color="#F5F3EF", text_color="#C8864A", width=64, height=64, corner_radius=8)
        icon_box.pack(anchor="w", pady=(0, 12))

        # Title input wrapper: gap 12px below, margin bottom 32px
        title_wrapper = ctk.CTkFrame(content_wrapper, fg_color="#F5F3EF", corner_radius=0, border_width=0)
        title_wrapper.pack(fill="x", pady=(0, 32))

        # Title: 48px font (approx 36 in tkinter scale), weight 600, tight line height
        title_entry = ctk.CTkEntry(title_wrapper, placeholder_text="Untitled", font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"), fg_color="#F5F3EF", border_width=0, text_color="#3D3D3D", placeholder_text_color="#AAAAAA")
        title_entry.pack(fill="x", pady=(0, 16))

        text_area = ctk.CTkTextbox(
            content_wrapper,
            font=ctk.CTkFont(family="Segoe UI", size=18),
            fg_color="transparent",
            text_color="#3D3D3D",
            border_width=0,
            corner_radius=0
        )

        text_area.pack(fill="both", expand=True)
        

    def _build_aipanel(self, right_panel):
        header = ctk.CTkFrame(right_panel, fg_color="#F0EDE8", corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 0))
        header.columnconfigure(0, weight=0)
        header.columnconfigure(1, weight=1)

        header_icon_box = ctk.CTkFrame(header, width=28, height=28, fg_color="transparent", corner_radius=10, border_width=1, border_color="#D9D4CC")
        header_icon_box.grid(row=0, column=0, sticky="w")
        header_icon_box.grid_propagate(False)
        header_icon = ctk.CTkLabel(header_icon_box, text="★", font=ctk.CTkFont(size=ICON_LG),fg_color="transparent", text_color="#C8864A")
        header_icon.place(relx=0.5, rely=0.5, anchor="center")

        header_label = ctk.CTkLabel(header, text="AI Assistant", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), fg_color="transparent", text_color="#3D3D3D")
        header_label.grid(row=0, column=1, sticky="w", padx=(8, 0))

        header_bottom = ctk.CTkFrame(right_panel, fg_color="#D9D4CC", corner_radius=0, height=1)
        header_bottom.grid(row=1, column=0, sticky="ew", padx=16, pady=(16, 0))

        context_section = ctk.CTkFrame(right_panel, fg_color="#F0EDE8", corner_radius=0)
        context_section.grid(row=2, column=0, sticky="ew", padx=16, pady=(12, 0))
        context_section.columnconfigure(0, weight=1)

        context_label = ctk.CTkLabel(context_section, text="Context", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#888888", fg_color="#F0EDE8")
        context_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        tag_frame = ctk.CTkFrame(context_section, fg_color="#F0EDE8", corner_radius=0)
        tag_frame.grid(row=1, column=0, sticky="ew")
        tag_frame.columnconfigure((0, 1, 2), weight=1)

        chip1 = self._create_chip(tag_frame, "Project Ideas")
        chip1.grid(row=0, column=0, sticky="w", padx=(0, GAP_SM))
        chip2 = self._create_chip(tag_frame, "Draft Essay")
        chip2.grid(row=0, column=1, sticky="w", padx=(0, GAP_SM))
        chip3 = self._create_chip(tag_frame, "Research")
        chip3.grid(row=0, column=2, sticky="w")

        quick_section = ctk.CTkFrame(right_panel, fg_color="#F0EDE8", corner_radius=0)
        quick_section.grid(row=3, column=0, sticky="ew", padx=16, pady=(20, 0))
        quick_section.columnconfigure(0, weight=1)

        quick_label = ctk.CTkLabel(quick_section, text="Quick Actions", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#888888", fg_color="#F0EDE8")
        quick_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        action_grid = ctk.CTkFrame(quick_section, fg_color="#F0EDE8", corner_radius=0)
        action_grid.grid(row=1, column=0, sticky="ew")
        action_grid.columnconfigure((0, 1), weight=1)

        actions = [
            ("📝", "Summarize"),
            ("✓", "Fix Grammar"),
            ("↗", "Expand"),
            ("🌐", "Translate"),
        ]
        for index, (icon_char, label) in enumerate(actions):
            btn = ctk.CTkButton(action_grid, text=f"{icon_char} {label}", fg_color="#FFFFFF", border_width=1, border_color="#D9D4CC", text_color="#3D3D3D", corner_radius=8, font=ctk.CTkFont(family="Segoe UI", size=12), hover_color="#F2F0EC")
            btn.grid(row=index // 2, column=index % 2, sticky="ew", padx=4, pady=4, ipady=10)

        chat_section = ctk.CTkFrame(right_panel, fg_color="#F0EDE8", corner_radius=0)
        chat_section.grid(row=4, column=0, sticky="nsew", padx=16, pady=(20, 0))
        chat_section.columnconfigure(0, weight=1)
        chat_section.rowconfigure(0, weight=1)

        messages_frame = ctk.CTkFrame(chat_section, fg_color="#F0EDE8", corner_radius=0)
        messages_frame.grid(row=0, column=0, sticky="nsew")
        messages_frame.columnconfigure(0, weight=1)

        self._create_message(messages_frame, "Hi! I can help you with quick edits or brainstorming suggestions.", owner="assistant")

        input_section = ctk.CTkFrame(right_panel, fg_color="#F0EDE8", corner_radius=0)
        input_section.grid(row=5, column=0, sticky="ew", padx=16, pady=(16, 16))
        input_section.columnconfigure(0, weight=1)

        input_top_border = ctk.CTkFrame(input_section, fg_color="#D9D4CC", height=1, corner_radius=0)
        input_top_border.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        input_label = ctk.CTkLabel(input_section, text="Ask something", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#888888", fg_color="#F0EDE8")
        input_label.grid(row=1, column=0, sticky="w", pady=(0, 8))

        input_row = ctk.CTkFrame(input_section, fg_color="#F0EDE8", corner_radius=0)
        input_row.grid(row=2, column=0, sticky="ew")
        input_row.columnconfigure(0, weight=1)

        ask_entry = ctk.CTkEntry(input_row, placeholder_text="Type your question…", fg_color="#FFFFFF", border_width=1, border_color="#D9D4CC", text_color="#3D3D3D", placeholder_text_color="#AAAAAA", corner_radius=8, font=ctk.CTkFont(family="Segoe UI", size=14))
        ask_entry.grid(row=0, column=0, sticky="ew", ipady=8)

        send_btn = ctk.CTkButton(input_row, text="→", fg_color="#C8864A", hover_color="#b46d3f", text_color="white", width=36, height=36, corner_radius=12, font=ctk.CTkFont(size=ICON_SM))
        send_btn.grid(row=0, column=1, padx=(8, 0))

    def _create_chip(self, parent, text):
        chip = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=RADIUS_MEDIUM, border_width=1, border_color="#D9D4CC")
        chip.grid_propagate(False)
        chip.configure(height=28)
        chip.rowconfigure(0, weight=1)
        pad_h = P_2_5 if len(text) < 10 else P_3
        chip_label = ctk.CTkLabel(chip, text=text, font=ctk.CTkFont(family="Segoe UI", size=FONT_XS), fg_color="#FFFFFF", text_color="#3D3D3D")
        chip_label.grid(row=0, column=0, sticky="w", padx=(pad_h, P_1), pady=P_1)
        close_label = ctk.CTkLabel(chip, text="✕", font=ctk.CTkFont(size=ICON_XS), fg_color="#FFFFFF", text_color="#888888", width=ICON_XS, height=ICON_XS)
        close_label.grid(row=0, column=1, sticky="e", padx=(0, P_2_5), pady=P_1)
        return chip

    def _create_message(self, parent, text, owner="assistant"):
        bg = "#FFFFFF" if owner == "assistant" else "#E7F4FF"
        align = "w" if owner == "assistant" else "e"
        bubble = ctk.CTkFrame(parent, fg_color=bg, corner_radius=16, border_width=1, border_color="#D9D4CC")
        bubble.grid(sticky=align, pady=4, padx=(0, 0))
        bubble.grid_propagate(True)
        wrap_len = RIGHT_PANEL_WIDTH - P_4
        label = ctk.CTkLabel(bubble, text=text, wraplength=wrap_len, justify="left", font=ctk.CTkFont(family="Segoe UI", size=FONT_SM), fg_color=bg, text_color="#3D3D3D")
        label.grid(row=0, column=0, sticky="w", padx=P_2, pady=P_1)
        return bubble

    def _add_command_row(self, parent, icon_char, name, desc, shortcut):
        row = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=12, border_width=0)
        row.grid(sticky="ew", padx=10, pady=6)
        row.columnconfigure(1, weight=1)

        icon = ctk.CTkLabel(row, text=icon_char, font=ctk.CTkFont(family="Segoe UI", size=14), fg_color="#FFFFFF", text_color="#3D3D3D")
        icon.grid(row=0, column=0, padx=(12, 10), pady=12)

        text_frame = ctk.CTkFrame(row, fg_color="#FFFFFF", corner_radius=0, border_width=0)
        text_frame.grid(row=0, column=1, sticky="ew", pady=10)
        text_frame.columnconfigure(0, weight=1)
        name_label = ctk.CTkLabel(text_frame, text=name, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), fg_color="#FFFFFF", text_color="#3D3D3D")
        name_label.grid(row=0, column=0, sticky="w")
        desc_label = ctk.CTkLabel(text_frame, text=desc, font=ctk.CTkFont(family="Segoe UI", size=11), fg_color="#FFFFFF", text_color="#888888")
        desc_label.grid(row=1, column=0, sticky="w")

        if shortcut:
            shortcut_label = ctk.CTkLabel(row, text=shortcut, font=ctk.CTkFont(family="Segoe UI", size=11), fg_color="#FFFFFF", text_color="#888888")
            shortcut_label.grid(row=0, column=2, padx=(0, 12), sticky="e")

        row.bind("<Enter>", lambda e, w=row: w.configure(fg_color="#F2F0EC"))
        row.bind("<Leave>", lambda e, w=row: w.configure(fg_color="#FFFFFF"))

        for widget in row.winfo_children():
            widget.bind("<Enter>", lambda e, w=row: w.configure(fg_color="#F2F0EC"))
            widget.bind("<Leave>", lambda e, w=row: w.configure(fg_color="#FFFFFF"))

        return row

if __name__ == "__main__":
    app = WriteApp()
    app.mainloop()

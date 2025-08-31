import sys
import os
import json
import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, List


class ConfigPreset:
    """Configuration preset data class"""
    
    def __init__(self, name: str, auth_token: str, base_url: str, 
                 model: str, small_fast_model: str):
        self.name = name
        self.auth_token = auth_token
        self.base_url = base_url
        self.model = model
        self.small_fast_model = small_fast_model
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'auth_token': self.auth_token,
            'base_url': self.base_url,
            'model': self.model,
            'small_fast_model': self.small_fast_model
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConfigPreset':
        return cls(
            data['name'],
            data['auth_token'],
            data['base_url'],
            data['model'],
            data['small_fast_model']
        )


class ConfigManager:
    """Manages configuration presets and environment variables"""
    
    def __init__(self):
        self.config_file = 'env_config.json'
        self.presets = self._load_presets()
    
    def _load_presets(self) -> List[ConfigPreset]:
        """Load presets from file or create default ones"""
        default_presets = [
            ConfigPreset(
                "测试",
                "sk-6jwTXRuJ02L5rvKEXa8uiSjErD5sGJwdfIi9r6tohQKgGU4g",
                "https://api.test.com/anthropic",
                "deepseek-chat",
                "deepseek-chat"
            )
        ]
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return [ConfigPreset.from_dict(preset) for preset in data]
            except Exception:
                return default_presets
        else:
            self._save_presets(default_presets)
            return default_presets
    
    def _save_presets(self, presets: List[ConfigPreset]):
        """Save presets to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump([preset.to_dict() for preset in presets], f, 
                     indent=2, ensure_ascii=False)
    
    def add_preset(self, preset: ConfigPreset):
        """Add new preset"""
        self.presets.append(preset)
        self._save_presets(self.presets)
    
    def delete_preset(self, index: int):
        """Delete preset by index"""
        if 0 <= index < len(self.presets):
            self.presets.pop(index)
            self._save_presets(self.presets)
    
    def apply_preset(self, preset: ConfigPreset):
        """Apply preset to environment variables"""
        os.environ['ANTHROPIC_AUTH_TOKEN'] = preset.auth_token
        os.environ['ANTHROPIC_BASE_URL'] = preset.base_url
        os.environ['ANTHROPIC_MODEL'] = preset.model
        os.environ['ANTHROPIC_SMALL_FAST_MODEL'] = preset.small_fast_model
        
        # For Windows, also set system environment variables permanently
        if sys.platform == 'win32':
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                  'Environment', 0, winreg.KEY_ALL_ACCESS) as key:
                    winreg.SetValueEx(key, 'ANTHROPIC_AUTH_TOKEN', 0, 
                                    winreg.REG_SZ, preset.auth_token)
                    winreg.SetValueEx(key, 'ANTHROPIC_BASE_URL', 0, 
                                    winreg.REG_SZ, preset.base_url)
                    winreg.SetValueEx(key, 'ANTHROPIC_MODEL', 0, 
                                    winreg.REG_SZ, preset.model)
                    winreg.SetValueEx(key, 'ANTHROPIC_SMALL_FAST_MODEL', 0, 
                                    winreg.REG_SZ, preset.small_fast_model)
            except Exception as e:
                print(f"Warning: Could not set system environment variables: {e}")


class EnvManagerApp:
    """Main application class with full dark mode support"""
    
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("🔧 环境变量配置管理器")
        self.root.geometry("1300x850")
        self.root.minsize(1200, 800)
        
        # Configure window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        
        # Set initial appearance
        self.current_appearance = "浅色"
        
        # Create UI
        self.create_widgets()
        
        # Show presets page by default
        self.show_presets_page()
    
    def create_widgets(self):
        """Create the main UI widgets with full dark mode support"""
        # Create sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        
        # Sidebar header
        self.sidebar_header = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.sidebar_header.grid(row=0, column=0, padx=20, pady=30, sticky="ew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_header, text="🔧", 
                                      font=ctk.CTkFont(size=32))
        self.logo_label.pack()
        
        self.app_name_label = ctk.CTkLabel(self.sidebar_header, text="环境变量管理器",
                                          font=ctk.CTkFont(size=18, weight="bold"))
        self.app_name_label.pack(pady=(10, 0))
        
        # Navigation buttons
        self.presets_button = ctk.CTkButton(self.sidebar_frame, 
                                           text="⚙️ 配置预设",
                                           height=45, corner_radius=8,
                                           command=self.show_presets_page)
        self.presets_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.current_button = ctk.CTkButton(self.sidebar_frame, 
                                           text="📊 当前配置",
                                           height=45, corner_radius=8,
                                           command=self.show_current_page)
        self.current_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.add_button = ctk.CTkButton(self.sidebar_frame, 
                                       text="➕ 添加配置",
                                       height=45, corner_radius=8,
                                       command=self.add_new_preset)
        self.add_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        # Spacer
        spacer = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        spacer.grid(row=4, column=0, sticky="nsew")
        
        # Theme options
        self.theme_label = ctk.CTkLabel(self.sidebar_frame, text="🎨 外观设置",
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.theme_label.grid(row=5, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, 
                                                            values=["浅色", "深色", "系统"],
                                                            command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
        
        # Footer
        self.footer_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.footer_frame.grid(row=7, column=0, padx=20, pady=20, sticky="ew")
        
        self.version_label = ctk.CTkLabel(self.footer_frame, text="v2.4",
                                         font=ctk.CTkFont(size=12))
        self.version_label.pack()
        
        # Create main content area
        self.main_content = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)
        
        # Create content frame that will hold all pages
        self.content_frame = ctk.CTkFrame(self.main_content, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Create home frame
        self.home_frame = ctk.CTkFrame(self.content_frame, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_rowconfigure(1, weight=1)
        
        # Home frame header
        self.home_header = ctk.CTkFrame(self.home_frame, corner_radius=0, height=80)
        self.home_header.grid(row=0, column=0, sticky="ew")
        self.home_header.grid_columnconfigure(1, weight=1)
        
        self.home_title = ctk.CTkLabel(self.home_header, text="⚙️ 配置预设管理",
                                      font=ctk.CTkFont(size=24, weight="bold"))
        self.home_title.grid(row=0, column=0, padx=30, pady=25, sticky="w")
        
        self.home_add_button = ctk.CTkButton(self.home_header, text="➕ 添加新配置",
                                            height=40, corner_radius=8,
                                            command=self.add_new_preset)
        self.home_add_button.grid(row=0, column=1, padx=30, pady=20, sticky="e")
        
        # Home content area
        self.home_content = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        self.home_content.grid(row=1, column=0, sticky="nsew")
        self.home_content.grid_columnconfigure(0, weight=1)
        self.home_content.grid_rowconfigure(0, weight=1)
        
        # Home scrollable frame
        self.home_scrollable = ctk.CTkScrollableFrame(self.home_content, fg_color="transparent")
        self.home_scrollable.grid(row=0, column=0, padx=25, pady=25, sticky="nsew")
        self.home_scrollable.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")
        
        # Create current config frame
        self.current_config_frame = ctk.CTkFrame(self.content_frame, corner_radius=0, fg_color="transparent")
        self.current_config_frame.grid_columnconfigure(0, weight=1)
        self.current_config_frame.grid_rowconfigure(1, weight=1)
        
        # Current config header
        self.current_header = ctk.CTkFrame(self.current_config_frame, corner_radius=0, height=80)
        self.current_header.grid(row=0, column=0, sticky="ew")
        self.current_header.grid_columnconfigure(1, weight=1)
        
        self.current_title = ctk.CTkLabel(self.current_header, text="📊 当前环境变量配置",
                                         font=ctk.CTkFont(size=24, weight="bold"))
        self.current_title.grid(row=0, column=0, padx=30, pady=25, sticky="w")
        
        self.current_refresh_button = ctk.CTkButton(self.current_header, text="🔄 刷新状态",
                                                   height=40, corner_radius=8,
                                                   command=self.refresh_current_config)
        self.current_refresh_button.grid(row=0, column=1, padx=30, pady=20, sticky="e")
        
        # Current config content area
        self.current_content = ctk.CTkFrame(self.current_config_frame, fg_color="transparent")
        self.current_content.grid(row=1, column=0, sticky="nsew")
        self.current_content.grid_columnconfigure(0, weight=1)
        self.current_content.grid_rowconfigure(0, weight=1)
        
        # Current config scrollable frame
        self.current_scrollable = ctk.CTkScrollableFrame(self.current_content, fg_color="transparent")
        self.current_scrollable.grid(row=0, column=0, padx=25, pady=25, sticky="nsew")
        self.current_scrollable.grid_columnconfigure((0, 1), weight=1, uniform="config")
    
    def change_appearance_mode_event(self, new_appearance_mode: str):
        """Change appearance mode with full theme adaptation"""
        self.current_appearance = new_appearance_mode
        mode_map = {"浅色": "light", "深色": "dark", "系统": "system"}
        ctk.set_appearance_mode(mode_map[new_appearance_mode])
        
        # Update UI elements based on appearance mode
        if new_appearance_mode == "深色":
            self.update_ui_for_dark_mode()
        else:
            self.update_ui_for_light_mode()
    
    def update_ui_for_dark_mode(self):
        """Update UI elements for dark mode"""
        # Update sidebar
        self.sidebar_frame.configure(fg_color="#1a1a1a")
        self.sidebar_header.configure(fg_color="transparent")
        self.logo_label.configure(text_color="#e0e0e0")
        self.app_name_label.configure(text_color="#e0e0e0")
        self.theme_label.configure(text_color="#e0e0e0")
        self.version_label.configure(text_color="#a0a0a0")
        
        # Update navigation buttons
        self.presets_button.configure(fg_color="#2d2d2d", hover_color="#3d3d3d", text_color="#e0e0e0")
        self.current_button.configure(fg_color="#2d2d2d", hover_color="#3d3d3d", text_color="#e0e0e0")
        self.add_button.configure(fg_color="#2d2d2d", hover_color="#3d3d3d", text_color="#e0e0e0")
        
        # Update option menu
        self.appearance_mode_optionemenu.configure(fg_color="#2d2d2d", button_color="#3d3d3d", 
                                                  button_hover_color="#4d4d4d", text_color="#e0e0e0")
        
        # Update headers
        self.home_header.configure(fg_color="#252525")
        self.home_title.configure(text_color="#e0e0e0")
        self.home_add_button.configure(fg_color="#2d2d2d", hover_color="#3d3d3d", text_color="#e0e0e0")
        
        self.current_header.configure(fg_color="#252525")
        self.current_title.configure(text_color="#e0e0e0")
        self.current_refresh_button.configure(fg_color="#2d2d2d", hover_color="#3d3d3d", text_color="#e0e0e0")
    
    def update_ui_for_light_mode(self):
        """Update UI elements for light mode"""
        # Reset to default colors
        self.sidebar_frame.configure(fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        self.sidebar_header.configure(fg_color="transparent")
        self.logo_label.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        self.app_name_label.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        self.theme_label.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        self.version_label.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"][1])  # Light mode color
        
        # Update navigation buttons
        self.presets_button.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], 
                                     hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"],
                                     text_color=ctk.ThemeManager.theme["CTkButton"]["text_color"])
        self.current_button.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], 
                                     hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"],
                                     text_color=ctk.ThemeManager.theme["CTkButton"]["text_color"])
        self.add_button.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], 
                                 hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"],
                                 text_color=ctk.ThemeManager.theme["CTkButton"]["text_color"])
        
        # Update option menu
        self.appearance_mode_optionemenu.configure(fg_color=ctk.ThemeManager.theme["CTkOptionMenu"]["fg_color"], 
                                                 button_color=ctk.ThemeManager.theme["CTkOptionMenu"]["button_color"],
                                                 button_hover_color=ctk.ThemeManager.theme["CTkOptionMenu"]["button_hover_color"],
                                                 text_color=ctk.ThemeManager.theme["CTkOptionMenu"]["text_color"])
        
        # Update headers
        self.home_header.configure(fg_color=ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"])
        self.home_title.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        self.home_add_button.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], 
                                      hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"],
                                      text_color=ctk.ThemeManager.theme["CTkButton"]["text_color"])
        
        self.current_header.configure(fg_color=ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"])
        self.current_title.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        self.current_refresh_button.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], 
                                             hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"],
                                             text_color=ctk.ThemeManager.theme["CTkButton"]["text_color"])
    
    def show_presets_page(self):
        """Show presets management page"""
        # Update button states
        if self.current_appearance == "深色":
            self.presets_button.configure(fg_color="#3d3d3d")
            self.current_button.configure(fg_color="#2d2d2d")
        else:
            self.presets_button.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
            self.current_button.configure(fg_color="transparent")
        
        # Show home frame
        self.home_frame.grid(row=0, column=0, sticky="nsew")
        self.current_config_frame.grid_forget()
        
        # Refresh presets
        self.refresh_presets_list()
    
    def show_current_page(self):
        """Show current configuration page"""
        # Update button states
        if self.current_appearance == "深色":
            self.current_button.configure(fg_color="#3d3d3d")
            self.presets_button.configure(fg_color="#2d2d2d")
        else:
            self.current_button.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
            self.presets_button.configure(fg_color="transparent")
        
        # Show current config frame
        self.current_config_frame.grid(row=0, column=0, sticky="nsew")
        self.home_frame.grid_forget()
        
        # Refresh current config
        self.refresh_current_config()
    
    def refresh_presets_list(self):
        """Refresh the presets list display"""
        # Clear existing widgets
        for widget in self.home_scrollable.winfo_children():
            widget.destroy()
        
        # Add preset cards in a grid layout
        for i, preset in enumerate(self.config_manager.presets):
            row = i // 3
            col = i % 3
            self.create_preset_card(preset, i, row, col)
    
    def create_preset_card(self, preset: ConfigPreset, index: int, row: int, col: int):
        """Create a card widget for a preset in grid layout with dark mode support"""
        # Card frame
        card_frame = ctk.CTkFrame(self.home_scrollable, corner_radius=12)
        card_frame.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
        
        # Card header
        if self.current_appearance == "深色":
            card_header = ctk.CTkFrame(card_frame, corner_radius=10, fg_color="#2d2d2d", height=50)
        else:
            card_header = ctk.CTkFrame(card_frame, corner_radius=10, height=50)
        card_header.pack(fill="x", padx=2, pady=(2, 0))
        
        # Name in header
        if self.current_appearance == "深色":
            name_label = ctk.CTkLabel(card_header, text=preset.name,
                                     font=ctk.CTkFont(size=16, weight="bold"),
                                     text_color="#e0e0e0")
        else:
            name_label = ctk.CTkLabel(card_header, text=preset.name,
                                     font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(pady=12)
        
        # Card content
        if self.current_appearance == "深色":
            card_content = ctk.CTkFrame(card_frame, corner_radius=10, fg_color="#252525")
        else:
            card_content = ctk.CTkFrame(card_frame, corner_radius=10)
        card_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Model
        if self.current_appearance == "深色":
            model_label = ctk.CTkLabel(card_content, text=f"🤖 模型: {preset.model}",
                                      font=ctk.CTkFont(size=13), 
                                      text_color="#c0c0c0")
        else:
            model_label = ctk.CTkLabel(card_content, text=f"🤖 模型: {preset.model}",
                                      font=ctk.CTkFont(size=13))
        model_label.pack(anchor="w", pady=2)
        
        # URL
        if self.current_appearance == "深色":
            url_label = ctk.CTkLabel(card_content, text=f"🌐 地址: {preset.base_url}",
                                    font=ctk.CTkFont(size=13),
                                    text_color="#c0c0c0")
        else:
            url_label = ctk.CTkLabel(card_content, text=f"🌐 地址: {preset.base_url}",
                                    font=ctk.CTkFont(size=13))
        url_label.pack(anchor="w", pady=2)
        
        # Token (masked)
        token_display = f"{preset.auth_token[:8]}...{preset.auth_token[-6:]}" if len(preset.auth_token) > 14 else preset.auth_token
        if self.current_appearance == "深色":
            token_label = ctk.CTkLabel(card_content, text=f"🔑 令牌: {token_display}",
                                      font=ctk.CTkFont(size=13),
                                      text_color="#c0c0c0")
        else:
            token_label = ctk.CTkLabel(card_content, text=f"🔑 令牌: {token_display}",
                                      font=ctk.CTkFont(size=13))
        token_label.pack(anchor="w", pady=2)
        
        # Small model
        if self.current_appearance == "深色":
            small_model_label = ctk.CTkLabel(card_content, text=f"⚡ 快速模型: {preset.small_fast_model}",
                                            font=ctk.CTkFont(size=13),
                                            text_color="#c0c0c0")
        else:
            small_model_label = ctk.CTkLabel(card_content, text=f"⚡ 快速模型: {preset.small_fast_model}",
                                            font=ctk.CTkFont(size=13))
        small_model_label.pack(anchor="w", pady=2)
        
        # Card footer with buttons
        card_footer = ctk.CTkFrame(card_frame, corner_radius=10, fg_color="transparent")
        card_footer.pack(fill="x", padx=15, pady=(0, 15))
        
        # Button frame
        button_frame = ctk.CTkFrame(card_footer, fg_color="transparent")
        button_frame.pack(pady=5)
        
        # Apply button
        if self.current_appearance == "深色":
            apply_button = ctk.CTkButton(button_frame, text="应用", 
                                        width=70, height=30, corner_radius=6,
                                        fg_color="#3d3d3d", hover_color="#4d4d4d",
                                        text_color="#e0e0e0",
                                        command=lambda p=preset: self.apply_preset(p))
        else:
            apply_button = ctk.CTkButton(button_frame, text="应用", 
                                        width=70, height=30, corner_radius=6,
                                        command=lambda p=preset: self.apply_preset(p))
        apply_button.pack(side="left", padx=(0, 8))
        
        # Delete button
        if self.current_appearance == "深色":
            delete_button = ctk.CTkButton(button_frame, text="删除",
                                         width=70, height=30, corner_radius=6,
                                         fg_color="#2d2d2d", hover_color="#3d3d3d",
                                         text_color="#c0c0c0",
                                         command=lambda idx=index: self.delete_preset(idx))
        else:
            delete_button = ctk.CTkButton(button_frame, text="删除",
                                         width=70, height=30, corner_radius=6,
                                         fg_color="transparent",
                                         command=lambda idx=index: self.delete_preset(idx))
        delete_button.pack(side="left")
    
    def refresh_current_config(self):
        """Refresh the current configuration display"""
        # Clear existing widgets
        for widget in self.current_scrollable.winfo_children():
            widget.destroy()
        
        # Environment variables
        env_vars = [
            ('ANTHROPIC_AUTH_TOKEN', '🔑 认证令牌', os.environ.get('ANTHROPIC_AUTH_TOKEN', '未设置')),
            ('ANTHROPIC_BASE_URL', '🌐 API地址', os.environ.get('ANTHROPIC_BASE_URL', '未设置')),
            ('ANTHROPIC_MODEL', '🤖 主要模型', os.environ.get('ANTHROPIC_MODEL', '未设置')),
            ('ANTHROPIC_SMALL_FAST_MODEL', '⚡ 快速模型', os.environ.get('ANTHROPIC_SMALL_FAST_MODEL', '未设置'))
        ]
        
        # Add config items in a grid layout
        for i, (var_name, display_name, var_value) in enumerate(env_vars):
            row = i // 2
            col = i % 2
            self.create_config_item(var_name, display_name, var_value, row, col)
    
    def create_config_item(self, var_name: str, display_name: str, var_value: str, row: int, col: int):
        """Create a config item widget in grid layout with dark mode support"""
        # Card frame
        card_frame = ctk.CTkFrame(self.current_scrollable, corner_radius=12)
        card_frame.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
        
        # Card header
        if self.current_appearance == "深色":
            card_header = ctk.CTkFrame(card_frame, corner_radius=10, fg_color="#2d2d2d", height=50)
        else:
            card_header = ctk.CTkFrame(card_frame, corner_radius=10, height=50)
        card_header.pack(fill="x", padx=2, pady=(2, 0))
        
        # Display name in header
        if self.current_appearance == "深色":
            name_label = ctk.CTkLabel(card_header, text=display_name,
                                     font=ctk.CTkFont(size=16, weight="bold"),
                                     text_color="#e0e0e0")
        else:
            name_label = ctk.CTkLabel(card_header, text=display_name,
                                     font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(pady=12)
        
        # Card content
        if self.current_appearance == "深色":
            card_content = ctk.CTkFrame(card_frame, corner_radius=10, fg_color="#252525")
        else:
            card_content = ctk.CTkFrame(card_frame, corner_radius=10)
        card_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Technical name
        if self.current_appearance == "深色":
            tech_label = ctk.CTkLabel(card_content, text=var_name,
                                     font=ctk.CTkFont(size=12),
                                     text_color="#a0a0a0")
        else:
            tech_label = ctk.CTkLabel(card_content, text=var_name,
                                     font=ctk.CTkFont(size=12),
                                     text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"][1])
        tech_label.pack(anchor="w", pady=(0, 10))
        
        # Value display with status color
        if var_value == '未设置':
            value_text = "❌ 未设置"
            if self.current_appearance == "深色":
                value_color = "#a0a0a0"
            else:
                value_color = "gray"
        else:
            # Mask sensitive token
            if 'TOKEN' in var_name and var_value != '未设置':
                if len(var_value) > 20:
                    value_text = f"✅ {var_value[:10]}...{var_value[-10:]}"
                else:
                    value_text = f"✅ {var_value}"
            else:
                value_text = f"✅ {var_value}"
            if self.current_appearance == "深色":
                value_color = "#c0c0c0"
            else:
                value_color = "gray"
        
        if self.current_appearance == "深色":
            value_label = ctk.CTkLabel(card_content, text=value_text,
                                      font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
                                      text_color=value_color)
        else:
            value_label = ctk.CTkLabel(card_content, text=value_text,
                                      font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
                                      text_color=value_color)
        value_label.pack(anchor="w")
    
    def add_new_preset(self):
        """Add new preset configuration"""
        # Create a dialog to get preset details
        dialog = PresetDialog(self.root, self.current_appearance)
        self.root.wait_window(dialog.top)
        
        if dialog.result:
            name, token, url, model, small_model = dialog.result
            if all([name, token, url, model, small_model]):
                preset = ConfigPreset(name, token, url, model, small_model)
                self.config_manager.add_preset(preset)
                self.refresh_presets_list()
                messagebox.showinfo("成功", "新配置已添加！")
            else:
                messagebox.showwarning("警告", "请填写所有字段！")
    
    def apply_preset(self, preset: ConfigPreset):
        """Apply selected preset"""
        try:
            self.config_manager.apply_preset(preset)
            messagebox.showinfo("成功", f"已应用配置: {preset.name}")
            # Refresh current config display if on that page
            if self.current_config_frame.winfo_viewable():
                self.refresh_current_config()
        except Exception as e:
            messagebox.showerror("错误", f"应用配置失败: {str(e)}")
    
    def delete_preset(self, index: int):
        """Delete preset configuration"""
        preset_name = self.config_manager.presets[index].name
        result = messagebox.askyesno("确认删除", f"确定要删除配置 '{preset_name}' 吗？")
        if result:
            self.config_manager.delete_preset(index)
            self.refresh_presets_list()
            messagebox.showinfo("已删除", f"配置 '{preset_name}' 已删除")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


class PresetDialog:
    """Dialog for adding new preset configuration with dark mode support"""
    
    def __init__(self, parent, appearance_mode):
        self.appearance_mode = appearance_mode
        self.top = ctk.CTkToplevel(parent)
        self.top.title("添加新配置")
        self.top.geometry("600x600")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()
        
        # Center the dialog
        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.top.winfo_screenheight() // 2) - (600 // 2)
        self.top.geometry(f"600x600+{x}+{y}")
        
        self.result = None
        
        # Create form with dark mode support
        if self.appearance_mode == "深色":
            form_frame = ctk.CTkFrame(self.top, corner_radius=12, fg_color="#252525")
        else:
            form_frame = ctk.CTkFrame(self.top, corner_radius=12)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        if self.appearance_mode == "深色":
            title_label = ctk.CTkLabel(form_frame, text="添加新配置",
                                      font=ctk.CTkFont(size=22, weight="bold"),
                                      text_color="#e0e0e0")
        else:
            title_label = ctk.CTkLabel(form_frame, text="添加新配置",
                                      font=ctk.CTkFont(size=22, weight="bold"))
        title_label.pack(pady=(30, 30))
        
        # Form fields
        fields_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fields_frame.pack(fill="x", padx=35, pady=10)
        fields_frame.grid_columnconfigure(0, weight=1)
        
        # Name field
        if self.appearance_mode == "深色":
            self.name_entry = ctk.CTkEntry(fields_frame, placeholder_text="配置名称", height=45, corner_radius=8,
                                          fg_color="#2d2d2d", border_color="#3d3d3d", text_color="#e0e0e0")
        else:
            self.name_entry = ctk.CTkEntry(fields_frame, placeholder_text="配置名称", height=45, corner_radius=8)
        self.name_entry.pack(fill="x", pady=10)
        
        # Token field
        if self.appearance_mode == "深色":
            self.token_entry = ctk.CTkEntry(fields_frame, placeholder_text="认证令牌", height=45, corner_radius=8,
                                           fg_color="#2d2d2d", border_color="#3d3d3d", text_color="#e0e0e0")
        else:
            self.token_entry = ctk.CTkEntry(fields_frame, placeholder_text="认证令牌", height=45, corner_radius=8)
        self.token_entry.pack(fill="x", pady=10)
        
        # URL field
        if self.appearance_mode == "深色":
            self.url_entry = ctk.CTkEntry(fields_frame, placeholder_text="API基础URL", height=45, corner_radius=8,
                                         fg_color="#2d2d2d", border_color="#3d3d3d", text_color="#e0e0e0")
        else:
            self.url_entry = ctk.CTkEntry(fields_frame, placeholder_text="API基础URL", height=45, corner_radius=8)
        self.url_entry.pack(fill="x", pady=10)
        
        # Model field
        if self.appearance_mode == "深色":
            self.model_entry = ctk.CTkEntry(fields_frame, placeholder_text="主要模型", height=45, corner_radius=8,
                                           fg_color="#2d2d2d", border_color="#3d3d3d", text_color="#e0e0e0")
        else:
            self.model_entry = ctk.CTkEntry(fields_frame, placeholder_text="主要模型", height=45, corner_radius=8)
        self.model_entry.pack(fill="x", pady=10)
        
        # Small model field
        if self.appearance_mode == "深色":
            self.small_model_entry = ctk.CTkEntry(fields_frame, placeholder_text="小型快速模型", height=45, corner_radius=8,
                                                 fg_color="#2d2d2d", border_color="#3d3d3d", text_color="#e0e0e0")
        else:
            self.small_model_entry = ctk.CTkEntry(fields_frame, placeholder_text="小型快速模型", height=45, corner_radius=8)
        self.small_model_entry.pack(fill="x", pady=10)
        
        # Buttons frame
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=30)
        
        # OK button
        if self.appearance_mode == "深色":
            ok_button = ctk.CTkButton(button_frame, text="确定", 
                                     width=100, height=40, corner_radius=8,
                                     fg_color="#3d3d3d", hover_color="#4d4d4d",
                                     text_color="#e0e0e0",
                                     command=self.ok)
        else:
            ok_button = ctk.CTkButton(button_frame, text="确定", 
                                     width=100, height=40, corner_radius=8,
                                     command=self.ok)
        ok_button.pack(side="left", padx=10)
        
        # Cancel button
        if self.appearance_mode == "深色":
            cancel_button = ctk.CTkButton(button_frame, text="取消",
                                         width=100, height=40, corner_radius=8,
                                         fg_color="#2d2d2d", hover_color="#3d3d3d",
                                         text_color="#c0c0c0",
                                         command=self.cancel)
        else:
            cancel_button = ctk.CTkButton(button_frame, text="取消",
                                         width=100, height=40, corner_radius=8,
                                         fg_color="transparent",
                                         command=self.cancel)
        cancel_button.pack(side="left", padx=10)
        
        # Focus on first entry
        self.name_entry.focus()
        
        # Bind Enter key to OK
        self.top.bind('<Return>', lambda e: self.ok())
    
    def ok(self):
        """Handle OK button click"""
        name = self.name_entry.get()
        token = self.token_entry.get()
        url = self.url_entry.get()
        model = self.model_entry.get()
        small_model = self.small_model_entry.get()
        
        self.result = (name, token, url, model, small_model)
        self.top.destroy()
    
    def cancel(self):
        """Handle Cancel button click"""
        self.top.destroy()


def main():
    app = EnvManagerApp()
    app.run()


if __name__ == '__main__':
    main()
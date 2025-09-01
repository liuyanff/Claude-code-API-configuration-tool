#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
from typing import Dict, List
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                            QLineEdit, QScrollArea, QFrame, QDialog, QMessageBox,
                            QComboBox, QSizePolicy, QTableWidget, QTableWidgetItem,
                            QHeaderView, QSplitter, QToolBar, QStatusBar, QMenu,
                            QAbstractItemView)
from PyQt6.QtCore import (Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer, QUrl,
                         QAbstractTableModel, QModelIndex, QSortFilterProxyModel, QEvent)
from PyQt6.QtGui import (QFont, QPalette, QColor, QPainter, QPen, QBrush, QIcon, QAction, QPixmap,
                        QEnterEvent, QMouseEvent)

class ConfigPreset:
    """配置预设数据类"""
    
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
    """管理配置预设和环境变量"""
    
    def __init__(self):
        self.config_file = 'env_config.json'
        self.presets = self._load_presets()
    
    def _load_presets(self) -> List[ConfigPreset]:
        """从文件加载预设或创建默认预设"""
        default_presets = [
            ConfigPreset(
                "测试配置",
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
        """保存预设到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump([preset.to_dict() for preset in presets], f, 
                     indent=2, ensure_ascii=False)
    
    def add_preset(self, preset: ConfigPreset):
        """添加新预设"""
        self.presets.append(preset)
        self._save_presets(self.presets)
    
    def delete_preset(self, index: int):
        """按索引删除预设"""
        if 0 <= index < len(self.presets):
            self.presets.pop(index)
            self._save_presets(self.presets)
    
    def apply_preset(self, preset: ConfigPreset):
        """将预设应用到环境变量"""
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
                print(f"警告: 无法设置系统环境变量: {e}")

class AnimatedCardWidget(QWidget):
    """带有悬停效果的动画卡片组件"""
    
    apply_clicked = pyqtSignal(object)
    delete_clicked = pyqtSignal(int)
    
    def __init__(self, preset: ConfigPreset, index: int, parent=None):
        super().__init__(parent)
        self.preset = preset
        self.index = index
        self.is_hovered = False
        self.setFixedSize(300, 220)
        self.setStyleSheet("""
            AnimatedCardWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)
        
        # Create animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Title
        title_label = QLabel(self.preset.name)
        title_label.setStyleSheet("color: #2c3e50; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Separator
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        layout.addWidget(separator)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)
        
        # Model info
        model_label = QLabel(f"🤖 模型: {self.preset.model}")
        model_label.setStyleSheet("color: #34495e; font-size: 13px;")
        content_layout.addWidget(model_label)
        
        # Small model info
        small_model_label = QLabel(f"⚡ 快速模型: {self.preset.small_fast_model}")
        small_model_label.setStyleSheet("color: #34495e; font-size: 13px;")
        content_layout.addWidget(small_model_label)
        
        # URL info
        url_label = QLabel(f"🌐 地址: {self.preset.base_url}")
        url_label.setStyleSheet("color: #34495e; font-size: 13px;")
        content_layout.addWidget(url_label)
        
        # Token info
        token_display = f"{self.preset.auth_token[:8]}...{self.preset.auth_token[-6:]}" if len(self.preset.auth_token) > 14 else self.preset.auth_token
        token_label = QLabel(f"🔑 令牌: {token_display}")
        token_label.setStyleSheet("color: #34495e; font-size: 13px;")
        content_layout.addWidget(token_label)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        # Button area
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        apply_btn = QPushButton("应用")
        apply_btn.setFixedWidth(80)
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        apply_btn.clicked.connect(lambda: self.apply_clicked.emit(self.preset))
        
        delete_btn = QPushButton("删除")
        delete_btn.setFixedWidth(80)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.index))
        
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def enterEvent(self, event: QEnterEvent):
        self.is_hovered = True
        self.start_hover_animation()
        super().enterEvent(event)
    
    def leaveEvent(self, event: QEvent):
        self.is_hovered = False
        self.start_leave_animation()
        super().leaveEvent(event)
    
    def start_hover_animation(self):
        """悬停动画"""
        current_geometry = self.geometry()
        new_geometry = current_geometry.adjusted(-3, -3, 3, 3)
        
        self.animation.setStartValue(current_geometry)
        self.animation.setEndValue(new_geometry)
        self.animation.start()
    
    def start_leave_animation(self):
        """离开动画"""
        current_geometry = self.geometry()
        new_geometry = current_geometry.adjusted(3, 3, -3, -3)
        
        self.animation.setStartValue(current_geometry)
        self.animation.setEndValue(new_geometry)
        self.animation.start()

class EnvVarTableModel(QAbstractTableModel):
    """使用Qt模型/视图架构的环境变量数据模型"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.headers = ['变量名称', '值', '状态']
        self.refresh_data()
    
    def refresh_data(self):
        """刷新环境变量数据"""
        self.env_vars = [
            ('ANTHROPIC_AUTH_TOKEN', os.environ.get('ANTHROPIC_AUTH_TOKEN', '未设置')),
            ('ANTHROPIC_BASE_URL', os.environ.get('ANTHROPIC_BASE_URL', '未设置')),
            ('ANTHROPIC_MODEL', os.environ.get('ANTHROPIC_MODEL', '未设置')),
            ('ANTHROPIC_SMALL_FAST_MODEL', os.environ.get('ANTHROPIC_SMALL_FAST_MODEL', '未设置'))
        ]
        self.layoutChanged.emit()
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.env_vars)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.env_vars)):
            return None
        
        var_name, var_value = self.env_vars[index.row()]
        
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return var_name
            elif index.column() == 1:
                # Mask sensitive information
                if 'TOKEN' in var_name and var_value != '未设置':
                    display_value = f"{var_value[:10]}...{var_value[-10:]}" if len(var_value) > 20 else var_value
                else:
                    display_value = var_value
                return display_value
            elif index.column() == 2:
                return "✅ 已设置" if var_value != '未设置' else "❌ 未设置"
        elif role == Qt.ItemDataRole.ForegroundRole:
            if index.column() == 2:
                return QColor(0, 150, 0) if var_value != '未设置' else QColor(200, 0, 0)
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

class PresetDialog(QDialog):
    """添加新预设配置的对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新配置")
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        # Set style
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border-radius: 12px;
            }
        """)
        
        self.result_data = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("添加新配置")
        title_label.setStyleSheet("color: #2c3e50; font-size: 20px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Form fields
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        self.name_entry = QLineEdit()
        self.name_entry.setPlaceholderText("配置名称")
        self.name_entry.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d1d8e0;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addWidget(self.name_entry)
        
        self.token_entry = QLineEdit()
        self.token_entry.setPlaceholderText("身份认证令牌")
        self.token_entry.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d1d8e0;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addWidget(self.token_entry)
        
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("API 基础地址")
        self.url_entry.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d1d8e0;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addWidget(self.url_entry)
        
        self.model_entry = QLineEdit()
        self.model_entry.setPlaceholderText("主模型")
        self.model_entry.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d1d8e0;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addWidget(self.model_entry)
        
        self.small_model_entry = QLineEdit()
        self.small_model_entry.setPlaceholderText("小型快速模型")
        self.small_model_entry.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d1d8e0;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addWidget(self.small_model_entry)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        ok_btn = QPushButton("确定")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        ok_btn.clicked.connect(self.accept_dialog)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Focus on first entry
        self.name_entry.setFocus()
    
    def accept_dialog(self):
        name = self.name_entry.text().strip()
        token = self.token_entry.text().strip()
        url = self.url_entry.text().strip()
        model = self.model_entry.text().strip()
        small_model = self.small_model_entry.text().strip()
        
        if all([name, token, url, model, small_model]):
            self.result_data = (name, token, url, model, small_model)
            self.accept()
        else:
            QMessageBox.warning(self, "警告", "请填写所有字段！")

class EnvManagerApp(QMainWindow):
    """具有现代设计的主应用程序"""
    
    # Custom signals
    presetApplied = pyqtSignal(str)  # 配置应用信号
    configModified = pyqtSignal()    # 配置修改信号
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.sidebar_expanded = True  # 侧边栏展开状态
        self.init_ui()
        self.setup_navigation()
        self.show_presets_interface()
        
        # Connect custom signals
        self.presetApplied.connect(self.on_preset_applied)
        self.configModified.connect(self.on_config_modified)
        
        # Apply custom styles
        self.apply_custom_styles()
    
    def init_ui(self):
        self.setWindowTitle("🔧 环境变量管理器")
        self.setGeometry(100, 100, 1300, 850)
        self.setMinimumSize(1200, 800)
        
        # Create interfaces
        self.presets_interface = QWidget()
        self.env_interface = QWidget()
        
        self.setup_presets_interface()
        self.setup_env_interface()
    
    def setup_navigation(self):
        """设置可收放的导航栏"""
        # Create navigation bar
        self.nav_bar = QWidget()
        self.nav_bar.setFixedWidth(250)
        self.nav_bar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
        """)
        
        # Create sidebar animation
        self.sidebar_animation = QPropertyAnimation(self.nav_bar, b"minimumWidth")
        self.sidebar_animation.setDuration(300)
        self.sidebar_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        nav_layout = QVBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(20, 20, 20, 30)
        nav_layout.setSpacing(15)
        
        # Header with toggle button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        self.title_label = QLabel("🔧 环境管理器")
        self.title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(self.title_label)
        
        # Toggle button
        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        header_layout.addWidget(self.toggle_btn)
        
        nav_layout.addLayout(header_layout)
        
        # Separator
        self.separator = QWidget()
        self.separator.setFixedHeight(1)
        self.separator.setStyleSheet("background-color: #34495e;")
        nav_layout.addWidget(self.separator)
        
        # Navigation buttons
        self.presets_btn = QPushButton("⚙️ 配置预设")
        self.presets_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.presets_btn.clicked.connect(self.show_presets_interface)
        nav_layout.addWidget(self.presets_btn)
        
        self.env_btn = QPushButton("📊 当前配置")
        self.env_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        self.env_btn.clicked.connect(self.show_env_interface)
        nav_layout.addWidget(self.env_btn)
        
        # Add config button
        self.add_btn = QPushButton("➕ 添加配置")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        self.add_btn.clicked.connect(self.add_new_preset)
        nav_layout.addWidget(self.add_btn)
        
        nav_layout.addStretch()
        
        # Create central widget
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        main_layout.addWidget(self.nav_bar)
        main_layout.addWidget(self.presets_interface, 1)
        main_layout.addWidget(self.env_interface, 1)
        
        self.setCentralWidget(central_widget)
        
        # Initially hide environment interface
        self.env_interface.hide()
    
    def toggle_sidebar(self):
        """切换侧边栏展开/收起状态"""
        if self.sidebar_expanded:
            # 收起侧边栏
            self.collapse_sidebar()
        else:
            # 展开侧边栏
            self.expand_sidebar()
    
    def collapse_sidebar(self):
        """收起侧边栏"""
        self.sidebar_expanded = False
        
        # 改变按钮文本和箭头方向
        self.toggle_btn.setText("▶")
        
        # 隐藏标题和分隔线
        self.title_label.hide()
        self.separator.hide()
        
        # 改变按钮样式为只显示图标
        self.presets_btn.setText("⚙️")
        self.presets_btn.setToolTip("配置预设")
        self.presets_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                text-align: center;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.env_btn.setText("📊")
        self.env_btn.setToolTip("当前配置")
        self.env_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                text-align: center;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        
        self.add_btn.setText("➕")
        self.add_btn.setToolTip("添加配置")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                text-align: center;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        
        # 动画收起侧边栏
        self.sidebar_animation.setStartValue(self.nav_bar.width())
        self.sidebar_animation.setEndValue(80)
        self.sidebar_animation.start()
        
        # 同时设置最大宽度
        self.nav_bar.setMaximumWidth(80)
    
    def expand_sidebar(self):
        """展开侧边栏"""
        self.sidebar_expanded = True
        
        # 改变按钮文本和箭头方向
        self.toggle_btn.setText("◀")
        
        # 显示标题和分隔线
        self.title_label.show()
        self.separator.show()
        
        # 恢复按钮样式显示完整文本
        self.presets_btn.setText("⚙️ 配置预设")
        self.presets_btn.setToolTip("")
        self.presets_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.env_btn.setText("📊 当前配置")
        self.env_btn.setToolTip("")
        self.env_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        
        self.add_btn.setText("➕ 添加配置")
        self.add_btn.setToolTip("")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        
        # 动画展开侧边栏
        self.sidebar_animation.setStartValue(self.nav_bar.width())
        self.sidebar_animation.setEndValue(250)
        self.sidebar_animation.start()
        
        # 同时设置最大宽度
        self.nav_bar.setMaximumWidth(250)
    
    def setup_presets_interface(self):
        """设置配置预设界面"""
        layout = QVBoxLayout(self.presets_interface)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("⚙️ 配置预设管理")
        title_label.setStyleSheet("color: #2c3e50; font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        add_btn = QPushButton("➕ 添加新配置")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        add_btn.clicked.connect(self.add_new_preset)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Create card grid layout
        self.presets_container = QWidget()
        self.presets_grid = QGridLayout(self.presets_container)
        self.presets_grid.setSpacing(20)
        self.presets_grid.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(0, 0, 0, 0.4);
            }
        """)
        scroll_area.setWidget(self.presets_container)
        
        layout.addWidget(scroll_area)
        
        # Initial refresh
        self.refresh_presets_cards()
    
    def setup_env_interface(self):
        """设置环境变量界面"""
        layout = QVBoxLayout(self.env_interface)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("📊 当前环境变量")
        title_label.setStyleSheet("color: #2c3e50; font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 刷新状态")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_env_vars)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Create table
        self.refresh_env_table()
        
        self.env_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.env_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.env_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.env_table.setAlternatingRowColors(True)
        self.env_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.env_table.verticalHeader().setVisible(False)
        self.env_table.setShowGrid(False)
        self.env_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.1);
                alternate-background-color: rgba(245, 247, 250, 0.8);
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            }
            QTableWidget::item:selected {
                background-color: rgba(52, 152, 219, 0.1);
            }
            QHeaderView::section {
                background-color: transparent;
                border: none;
                padding: 10px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        
        layout.addWidget(self.env_table)
    
    def show_presets_interface(self):
        """显示配置预设界面"""
        self.presets_interface.show()
        self.env_interface.hide()
        
        # Update button styles
        if self.sidebar_expanded:
            # 展开状态的按钮样式
            self.presets_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            self.env_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7f8c8d;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #95a5a6;
                }
            """)
        else:
            # 收起状态的按钮样式
            self.presets_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: center;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            self.env_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7f8c8d;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: center;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #95a5a6;
                }
            """)
    
    def show_env_interface(self):
        """显示环境变量界面"""
        self.presets_interface.hide()
        self.env_interface.show()
        self.refresh_env_vars()
        
        # Update button styles
        if self.sidebar_expanded:
            # 展开状态的按钮样式
            self.env_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            self.presets_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7f8c8d;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #95a5a6;
                }
            """)
        else:
            # 收起状态的按钮样式
            self.env_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: center;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            self.presets_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7f8c8d;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: center;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #95a5a6;
                }
            """)
    
    def refresh_presets_cards(self):
        """刷新配置卡片"""
        # Clear existing cards
        for i in reversed(range(self.presets_grid.count())):
            widget = self.presets_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Add new cards
        for i, preset in enumerate(self.config_manager.presets):
            row = i // 3
            col = i % 3
            
            card = AnimatedCardWidget(preset, i)
            card.apply_clicked.connect(self.apply_preset)
            card.delete_clicked.connect(self.delete_preset)
            
            self.presets_grid.addWidget(card, row, col)
        
        # Add stretch to fill remaining space
        self.presets_grid.setRowStretch(self.presets_grid.rowCount(), 1)
    
    def refresh_env_table(self):
        """刷新环境变量表格"""
        # Create table if it doesn't exist
        if not hasattr(self, 'env_table'):
            self.env_table = QTableWidget()
        
        self.env_model = EnvVarTableModel()
        self.env_model.refresh_data()
        self.env_table.setRowCount(len(self.env_model.env_vars))
        self.env_table.setColumnCount(3)
        self.env_table.setHorizontalHeaderLabels(['变量名称', '值', '状态'])
        
        for i, (var_name, var_value) in enumerate(self.env_model.env_vars):
            # Variable name
            name_item = QTableWidgetItem(var_name)
            self.env_table.setItem(i, 0, name_item)
            
            # Value
            if 'TOKEN' in var_name and var_value != 'Not Set':
                display_value = f"{var_value[:10]}...{var_value[-10:]}" if len(var_value) > 20 else var_value
            else:
                display_value = var_value
            value_item = QTableWidgetItem(display_value)
            self.env_table.setItem(i, 1, value_item)
            
            # Status
            status_item = QTableWidgetItem()
            if var_value == '未设置':
                status_item.setText("❌ 未设置")
                status_item.setForeground(QColor(200, 0, 0))
            else:
                status_item.setText("✅ 已设置")
                status_item.setForeground(QColor(0, 150, 0))
            self.env_table.setItem(i, 2, status_item)
    
    def refresh_env_vars(self):
        """刷新环境变量显示"""
        self.refresh_env_table()
    
    def add_new_preset(self):
        """添加新配置"""
        dialog = PresetDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.result_data:
            name, token, url, model, small_model = dialog.result_data
            preset = ConfigPreset(name, token, url, model, small_model)
            self.config_manager.add_preset(preset)
            self.refresh_presets_cards()
            
            # Emit configuration modified signal
            self.configModified.emit()
            
            # Show success message
            QMessageBox.information(self, '成功', f"新配置 '{name}' 已添加！")
    
    def apply_preset(self, preset: ConfigPreset):
        """应用配置"""
        try:
            self.config_manager.apply_preset(preset)
            
            # Emit configuration applied signal
            self.presetApplied.emit(preset.name)
            self.configModified.emit()
            
            # Show success message
            QMessageBox.information(self, '成功', f"配置已应用: {preset.name}")
            
            # Refresh environment variables display
            self.refresh_env_vars()
        except Exception as e:
            # Show error message
            QMessageBox.critical(self, '错误', f"配置应用失败: {str(e)}")
    
    def delete_preset(self, index: int):
        """删除配置"""
        if 0 <= index < len(self.config_manager.presets):
            preset_name = self.config_manager.presets[index].name
            reply = QMessageBox.question(
                self, 
                '确认删除', 
                f"确定要删除配置 '{preset_name}' 吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.config_manager.delete_preset(index)
                self.refresh_presets_cards()
                
                # Emit configuration modified signal
                self.configModified.emit()
                
                # Show success message
                QMessageBox.information(self, '已删除', f"配置 '{preset_name}' 已被删除")
    
    def apply_custom_styles(self):
        """应用自定义样式表"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #f0f4f8, stop:1 #e6e9f0);
            }
            QLabel {
                color: #2c3e50;
            }
        """)
    

    
    def on_preset_applied(self, preset_name):
        """配置应用信号处理器"""
        print(f"配置 '{preset_name}' 已应用")
    

    
    def on_config_modified(self):
        """配置修改信号处理器"""
        print("配置已修改")

def main():
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = EnvManagerApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
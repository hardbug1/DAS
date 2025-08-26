"""
테마 및 스타일링 관리

다양한 테마와 스타일을 제공합니다.
"""

import gradio as gr
from typing import Dict, Any


class ThemeManager:
    """테마 관리 시스템"""
    
    def __init__(self):
        self.current_theme = "light"
        self.themes = {
            "light": self._create_light_theme(),
            "dark": self._create_dark_theme(),
            "blue": self._create_blue_theme(),
            "green": self._create_green_theme()
        }
    
    def get_theme(self, theme_name: str = "light") -> gr.Theme:
        """테마 가져오기"""
        return self.themes.get(theme_name, self.themes["light"])
    
    def get_custom_css(self, theme_name: str = "light") -> str:
        """테마별 커스텀 CSS 가져오기"""
        css_map = {
            "light": self._get_light_css(),
            "dark": self._get_dark_css(),
            "blue": self._get_blue_css(),
            "green": self._get_green_css()
        }
        return css_map.get(theme_name, css_map["light"])
    
    def _create_light_theme(self) -> gr.Theme:
        """라이트 테마 생성"""
        return gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="purple",
            neutral_hue="gray",
            font=gr.themes.GoogleFont("Inter"),
            text_size="sm"
        )
    
    def _create_dark_theme(self) -> gr.Theme:
        """다크 테마 생성"""
        return gr.themes.Monochrome(
            primary_hue="blue",
            secondary_hue="purple",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter"),
            text_size="sm"
        )
    
    def _create_blue_theme(self) -> gr.Theme:
        """블루 테마 생성"""
        return gr.themes.Ocean(
            primary_hue="blue",
            secondary_hue="cyan",
            neutral_hue="blue",
            font=gr.themes.GoogleFont("Inter"),
            text_size="sm"
        )
    
    def _create_green_theme(self) -> gr.Theme:
        """그린 테마 생성"""
        return gr.themes.Base(
            primary_hue="green",
            secondary_hue="emerald",
            neutral_hue="green",
            font=gr.themes.GoogleFont("Inter"),
            text_size="sm"
        )
    
    def _get_light_css(self) -> str:
        """라이트 테마 CSS"""
        return """
        /* 라이트 테마 전용 스타일 */
        .gradio-container {
            background: #ffffff;
            color: #1f2937;
        }
        
        .gr-button-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
        }
        
        .chat-container {
            background: #f9fafb;
            border-color: #e5e7eb;
        }
        
        .sidebar-panel {
            background: #ffffff;
            border-color: #e5e7eb;
        }
        """
    
    def _get_dark_css(self) -> str:
        """다크 테마 CSS"""
        return """
        /* 다크 테마 전용 스타일 */
        .gradio-container {
            background: #1f2937;
            color: #f9fafb;
        }
        
        .gr-button-primary {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
            color: white !important;
        }
        
        .chat-container {
            background: #374151;
            border-color: #4b5563;
        }
        
        .sidebar-panel {
            background: #374151;
            border-color: #4b5563;
        }
        
        .gr-textbox {
            background: #374151 !important;
            border-color: #4b5563 !important;
            color: #f9fafb !important;
        }
        """
    
    def _get_blue_css(self) -> str:
        """블루 테마 CSS"""
        return """
        /* 블루 테마 전용 스타일 */
        .gradio-container {
            background: #f0f9ff;
            color: #1e3a8a;
        }
        
        .gr-button-primary {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
            color: white !important;
        }
        
        .chat-container {
            background: #dbeafe;
            border-color: #93c5fd;
        }
        
        .sidebar-panel {
            background: #ffffff;
            border-color: #93c5fd;
        }
        """
    
    def _get_green_css(self) -> str:
        """그린 테마 CSS"""
        return """
        /* 그린 테마 전용 스타일 */
        .gradio-container {
            background: #f0fdf4;
            color: #14532d;
        }
        
        .gr-button-primary {
            background: linear-gradient(135deg, #16a34a 0%, #15803d 100%) !important;
            color: white !important;
        }
        
        .chat-container {
            background: #dcfce7;
            border-color: #86efac;
        }
        
        .sidebar-panel {
            background: #ffffff;
            border-color: #86efac;
        }
        """


class AnimationCSS:
    """애니메이션 CSS 모음"""
    
    @staticmethod
    def get_animations() -> str:
        """모든 애니메이션 CSS 반환"""
        return """
        /* 페이드 인 애니메이션 */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* 슬라이드 인 애니메이션 */
        @keyframes slideInFromRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .slide-in-right {
            animation: slideInFromRight 0.3s ease-out;
        }
        
        /* 펄스 애니메이션 */
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        /* 로딩 스피너 */
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .spinner {
            animation: spin 1s linear infinite;
        }
        
        /* 타이핑 애니메이션 */
        @keyframes typing {
            0%, 80%, 100% { 
                transform: scale(0);
                opacity: 0.5;
            }
            40% { 
                transform: scale(1);
                opacity: 1;
            }
        }
        
        .typing-dot {
            animation: typing 1.4s infinite ease-in-out both;
        }
        
        .typing-dot:nth-child(1) { animation-delay: 0s; }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        
        /* 호버 효과 */
        .hover-lift {
            transition: all 0.3s ease;
        }
        
        .hover-lift:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        
        /* 글로우 효과 */
        .glow {
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
            transition: box-shadow 0.3s ease;
        }
        
        .glow:hover {
            box-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
        }
        
        /* 반응형 그리드 */
        .responsive-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }
        
        @media (max-width: 768px) {
            .responsive-grid {
                grid-template-columns: 1fr;
            }
        }
        """


class ColorPalette:
    """색상 팔레트 정의"""
    
    BRAND_COLORS = {
        "primary": "#667eea",
        "secondary": "#764ba2", 
        "accent": "#f093fb",
        "success": "#28a745",
        "warning": "#ffc107",
        "error": "#dc3545",
        "info": "#17a2b8"
    }
    
    NEUTRAL_COLORS = {
        "white": "#ffffff",
        "gray_50": "#f9fafb",
        "gray_100": "#f3f4f6",
        "gray_200": "#e5e7eb",
        "gray_300": "#d1d5db",
        "gray_400": "#9ca3af",
        "gray_500": "#6b7280",
        "gray_600": "#4b5563",
        "gray_700": "#374151",
        "gray_800": "#1f2937",
        "gray_900": "#111827",
        "black": "#000000"
    }
    
    DATA_VIZ_COLORS = [
        "#667eea", "#764ba2", "#f093fb", "#f5576c",
        "#4ecdc4", "#45b7d1", "#96ceb4", "#ffeaa7",
        "#dda0dd", "#98d8c8", "#f7dc6f", "#bb8fce"
    ]
    
    @classmethod
    def get_color(cls, color_name: str, category: str = "brand") -> str:
        """색상 가져오기"""
        if category == "brand":
            return cls.BRAND_COLORS.get(color_name, cls.BRAND_COLORS["primary"])
        elif category == "neutral":
            return cls.NEUTRAL_COLORS.get(color_name, cls.NEUTRAL_COLORS["gray_500"])
        else:
            return cls.BRAND_COLORS["primary"]


# 전역 테마 관리자 인스턴스
theme_manager = ThemeManager()
animation_css = AnimationCSS()
color_palette = ColorPalette()

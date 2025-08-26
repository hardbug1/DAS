"""
반응형 디자인 및 접근성 테스트

UI의 반응형 디자인과 접근성 기능을 테스트합니다.
"""

import pytest
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.ui.responsive import ResponsiveDesign, AccessibilityFeatures, DeviceDetection


class TestResponsiveDesign:
    """반응형 디자인 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출"""
        self.responsive = ResponsiveDesign()
    
    def test_responsive_css_generation(self):
        """반응형 CSS 생성 테스트"""
        css = self.responsive.get_responsive_css()
        
        assert isinstance(css, str)
        assert len(css) > 0
        
        # 필수 미디어 쿼리 포함 확인
        assert "@media (max-width: 640px)" in css  # 모바일
        assert "@media (min-width: 641px) and (max-width: 1024px)" in css  # 태블릿
        assert "@media (min-width: 1025px)" in css  # 데스크톱
    
    def test_mobile_specific_styles(self):
        """모바일 전용 스타일 테스트"""
        css = self.responsive.get_responsive_css()
        
        # 모바일 스타일 확인
        assert "flex-direction: column" in css
        assert ".gr-chatbot" in css
        assert "height: 300px" in css
    
    def test_orientation_media_queries(self):
        """화면 방향 미디어 쿼리 테스트"""
        css = self.responsive.get_responsive_css()
        
        assert "@media (orientation: portrait)" in css
        assert "@media (orientation: landscape)" in css
    
    def test_accessibility_preference_queries(self):
        """접근성 선호도 미디어 쿼리 테스트"""
        css = self.responsive.get_responsive_css()
        
        assert "@media (prefers-color-scheme: dark)" in css
        assert "@media (prefers-reduced-motion: reduce)" in css
        assert "@media (prefers-contrast: high)" in css


class TestAccessibilityFeatures:
    """접근성 기능 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출"""
        self.accessibility = AccessibilityFeatures()
    
    def test_accessibility_css_generation(self):
        """접근성 CSS 생성 테스트"""
        css = self.accessibility.get_accessibility_css()
        
        assert isinstance(css, str)
        assert len(css) > 0
        
        # 필수 접근성 스타일 확인
        assert "focus" in css
        assert "outline" in css
        assert ".sr-only" in css  # 스크린 리더 전용
    
    def test_focus_styles(self):
        """포커스 스타일 테스트"""
        css = self.accessibility.get_accessibility_css()
        
        # 포커스 관련 스타일 확인
        assert ".gr-textbox:focus" in css
        assert ".gr-button:focus" in css
        assert "outline: 3px solid" in css
    
    def test_minimum_touch_target_size(self):
        """최소 터치 타겟 크기 테스트"""
        css = self.accessibility.get_accessibility_css()
        
        # 44px 최소 터치 타겟 크기 확인
        assert "min-height: 44px" in css
        assert "min-width: 44px" in css
    
    def test_high_contrast_styles(self):
        """고대비 스타일 테스트"""
        css = self.accessibility.get_accessibility_css()
        
        assert ".high-contrast" in css
        assert "color: #000000" in css
        assert "background: #ffffff" in css
    
    def test_accessibility_controls_generation(self):
        """접근성 컨트롤 생성 테스트"""
        controls = self.accessibility.create_accessibility_controls()
        
        assert controls is not None
        # Gradio HTML 컴포넌트인지 확인
        assert hasattr(controls, 'value')
        
        # HTML 내용 확인
        html_content = controls.value
        assert "accessibility-controls" in html_content
        assert "고대비 모드" in html_content
        assert "큰 텍스트" in html_content
        assert "애니메이션 감소" in html_content
    
    def test_skip_links_generation(self):
        """건너뛰기 링크 생성 테스트"""
        skip_links = self.accessibility.create_skip_links()
        
        assert skip_links is not None
        assert hasattr(skip_links, 'value')
        
        html_content = skip_links.value
        assert "skip-link" in html_content
        assert "메인 콘텐츠로 건너뛰기" in html_content
        assert "채팅 입력으로 건너뛰기" in html_content
    
    def test_javascript_functions(self):
        """JavaScript 함수 포함 테스트"""
        controls = self.accessibility.create_accessibility_controls()
        html_content = controls.value
        
        # JavaScript 함수들이 포함되어 있는지 확인
        assert "toggleHighContrast" in html_content
        assert "toggleLargeText" in html_content
        assert "toggleReducedMotion" in html_content
        assert "resetAccessibilitySettings" in html_content


class TestDeviceDetection:
    """디바이스 감지 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출"""
        self.device_detection = DeviceDetection()
    
    def test_device_optimization_script_generation(self):
        """디바이스 최적화 스크립트 생성 테스트"""
        script = self.device_detection.get_device_optimization_script()
        
        assert isinstance(script, str)
        assert len(script) > 0
        assert "<script>" in script
        assert "</script>" in script
    
    def test_device_detection_logic(self):
        """디바이스 감지 로직 테스트"""
        script = self.device_detection.get_device_optimization_script()
        
        # 디바이스 감지 관련 코드 확인
        assert "detectDevice" in script
        assert "isMobile" in script
        assert "isTablet" in script
        assert "isDesktop" in script
        assert "isTouchDevice" in script
    
    def test_viewport_class_management(self):
        """뷰포트 클래스 관리 테스트"""
        script = self.device_detection.get_device_optimization_script()
        
        # 뷰포트 클래스 관련 코드 확인
        assert "updateViewportClasses" in script
        assert "viewport-xs" in script
        assert "viewport-sm" in script
        assert "viewport-md" in script
        assert "viewport-lg" in script
        assert "viewport-xl" in script
    
    def test_network_optimization(self):
        """네트워크 최적화 테스트"""
        script = self.device_detection.get_device_optimization_script()
        
        # 네트워크 관련 코드 확인
        assert "handleNetworkChange" in script
        assert "connection" in script
        assert "slow-connection" in script
    
    def test_battery_optimization(self):
        """배터리 최적화 테스트"""
        script = self.device_detection.get_device_optimization_script()
        
        # 배터리 관련 코드 확인
        assert "handleBatteryChange" in script
        assert "getBattery" in script
        assert "low-battery" in script
    
    def test_color_scheme_detection(self):
        """색상 체계 감지 테스트"""
        script = self.device_detection.get_device_optimization_script()
        
        # 다크 모드 감지 관련 코드 확인
        assert "handleColorSchemeChange" in script
        assert "prefers-color-scheme: dark" in script
        assert "prefers-dark" in script
    
    def test_motion_preference_detection(self):
        """모션 선호도 감지 테스트"""
        script = self.device_detection.get_device_optimization_script()
        
        # 모션 감소 선호도 관련 코드 확인
        assert "handleMotionPreference" in script
        assert "prefers-reduced-motion: reduce" in script
        assert "prefers-reduced-motion" in script
    
    def test_event_listeners(self):
        """이벤트 리스너 설정 테스트"""
        script = self.device_detection.get_device_optimization_script()
        
        # 이벤트 리스너 관련 코드 확인
        assert "addEventListener" in script
        assert "resize" in script
        assert "DOMContentLoaded" in script


class TestIntegration:
    """통합 테스트"""
    
    def test_all_components_integration(self):
        """모든 컴포넌트 통합 테스트"""
        responsive = ResponsiveDesign()
        accessibility = AccessibilityFeatures()
        device_detection = DeviceDetection()
        
        # 모든 CSS가 정상적으로 생성되는지 확인
        responsive_css = responsive.get_responsive_css()
        accessibility_css = accessibility.get_accessibility_css()
        
        assert len(responsive_css) > 0
        assert len(accessibility_css) > 0
        
        # CSS 충돌이 없는지 확인 (기본적인 문법 체크)
        combined_css = responsive_css + accessibility_css
        
        # 중괄호 매칭 확인
        open_braces = combined_css.count('{')
        close_braces = combined_css.count('}')
        assert open_braces == close_braces
    
    def test_html_components_validity(self):
        """HTML 컴포넌트 유효성 테스트"""
        accessibility = AccessibilityFeatures()
        
        controls = accessibility.create_accessibility_controls()
        skip_links = accessibility.create_skip_links()
        
        # HTML 컴포넌트가 정상적으로 생성되는지 확인
        assert controls is not None
        assert skip_links is not None
        
        # HTML 내용이 비어있지 않은지 확인
        assert len(controls.value) > 0
        assert len(skip_links.value) > 0
    
    def test_css_selector_validity(self):
        """CSS 선택자 유효성 테스트"""
        responsive = ResponsiveDesign()
        accessibility = AccessibilityFeatures()
        
        responsive_css = responsive.get_responsive_css()
        accessibility_css = accessibility.get_accessibility_css()
        
        # 기본적인 CSS 선택자 패턴 확인
        import re
        
        # 클래스 선택자 패턴
        class_pattern = r'\.[a-zA-Z][a-zA-Z0-9_-]*'
        assert re.search(class_pattern, responsive_css)
        assert re.search(class_pattern, accessibility_css)
        
        # 미디어 쿼리 패턴
        media_pattern = r'@media\s*\([^)]+\)'
        assert re.search(media_pattern, responsive_css)
    
    def test_javascript_syntax_basic(self):
        """JavaScript 기본 문법 테스트"""
        device_detection = DeviceDetection()
        script = device_detection.get_device_optimization_script()
        
        # 기본적인 JavaScript 문법 확인
        assert "function" in script
        assert "var " in script or "let " in script or "const " in script
        
        # 괄호 매칭 확인
        open_parens = script.count('(')
        close_parens = script.count(')')
        assert open_parens == close_parens
        
        open_braces = script.count('{')
        close_braces = script.count('}')
        assert open_braces == close_braces


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
반응형 디자인 및 접근성 기능

모바일, 태블릿, 데스크톱 환경에 최적화된 UI와 접근성 기능을 제공합니다.
"""

import gradio as gr
from typing import Dict, List


class ResponsiveDesign:
    """반응형 디자인 관리"""
    
    @staticmethod
    def get_responsive_css() -> str:
        """반응형 CSS 반환"""
        return """
        /* 기본 반응형 설정 */
        .gradio-container {
            width: 100% !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding: 0 20px !important;
        }
        
        /* 모바일 우선 접근법 */
        @media (max-width: 640px) {
            .gradio-container {
                padding: 0 10px !important;
            }
            
            /* 모바일에서 컬럼을 세로로 배치 */
            .gr-row {
                flex-direction: column !important;
                gap: 15px !important;
            }
            
            .gr-column {
                width: 100% !important;
                margin: 0 !important;
            }
            
            /* 채팅 영역 높이 조정 */
            .gr-chatbot {
                height: 300px !important;
            }
            
            /* 입력창 여백 조정 */
            .message-input {
                margin-bottom: 10px !important;
            }
            
            /* 버튼 크기 조정 */
            .gr-button {
                width: 100% !important;
                margin: 5px 0 !important;
                padding: 12px !important;
                font-size: 16px !important;
            }
            
            /* 사이드바 패널 간격 */
            .sidebar-panel {
                margin-bottom: 20px !important;
            }
            
            /* 텍스트 크기 조정 */
            .panel-header {
                font-size: 16px !important;
            }
            
            /* 파일 업로드 영역 */
            .upload-area {
                padding: 20px !important;
                font-size: 14px !important;
            }
            
            /* 빠른 액션 버튼들 */
            .responsive-grid {
                grid-template-columns: 1fr !important;
                gap: 8px !important;
            }
            
            /* 헤더 조정 */
            .header-container h1 {
                font-size: 1.5rem !important;
            }
            
            .header-container p {
                font-size: 0.9rem !important;
            }
        }
        
        /* 태블릿 화면 */
        @media (min-width: 641px) and (max-width: 1024px) {
            .gradio-container {
                padding: 0 15px !important;
            }
            
            /* 태블릿에서는 2:1 비율로 유지하되 간격 조정 */
            .gr-row {
                gap: 20px !important;
            }
            
            .gr-chatbot {
                height: 400px !important;
            }
            
            /* 버튼 크기 조정 */
            .gr-button {
                padding: 10px 16px !important;
                font-size: 14px !important;
            }
            
            /* 빠른 액션 버튼들 */
            .responsive-grid {
                grid-template-columns: repeat(2, 1fr) !important;
            }
        }
        
        /* 데스크톱 화면 */
        @media (min-width: 1025px) {
            .gr-chatbot {
                height: 450px !important;
            }
            
            /* 빠른 액션 버튼들 */
            .responsive-grid {
                grid-template-columns: repeat(3, 1fr) !important;
            }
            
            /* 호버 효과 활성화 (터치 디바이스가 아닌 경우) */
            .hover-lift:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
            }
        }
        
        /* 초고해상도 화면 */
        @media (min-width: 1440px) {
            .gradio-container {
                max-width: 1400px !important;
            }
            
            .gr-chatbot {
                height: 500px !important;
            }
        }
        
        /* 세로 모드 조정 */
        @media (orientation: portrait) and (max-width: 768px) {
            .gr-chatbot {
                height: 350px !important;
            }
            
            .sidebar-panel {
                margin-bottom: 25px !important;
            }
        }
        
        /* 가로 모드 조정 */
        @media (orientation: landscape) and (max-height: 500px) {
            .gr-chatbot {
                height: 250px !important;
            }
            
            .header-container {
                padding: 15px !important;
            }
            
            .header-container h1 {
                font-size: 1.3rem !important;
            }
        }
        
        /* 다크 모드 미디어 쿼리 */
        @media (prefers-color-scheme: dark) {
            .auto-theme .gradio-container {
                background: #1f2937 !important;
                color: #f9fafb !important;
            }
            
            .auto-theme .sidebar-panel {
                background: #374151 !important;
                border-color: #4b5563 !important;
            }
        }
        
        /* 모션 감소 설정을 선호하는 사용자 */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
        
        /* 고대비 모드 */
        @media (prefers-contrast: high) {
            .gr-button-primary {
                background: #000000 !important;
                color: #ffffff !important;
                border: 2px solid #ffffff !important;
            }
            
            .sidebar-panel {
                border: 2px solid #000000 !important;
            }
        }
        """


class AccessibilityFeatures:
    """접근성 기능"""
    
    @staticmethod
    def get_accessibility_css() -> str:
        """접근성 CSS 반환"""
        return """
        /* 포커스 가시성 향상 */
        .gr-textbox:focus,
        .gr-button:focus,
        .gr-dropdown:focus {
            outline: 3px solid #667eea !important;
            outline-offset: 2px !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3) !important;
        }
        
        /* 스크린 리더를 위한 숨김 텍스트 */
        .sr-only {
            position: absolute !important;
            width: 1px !important;
            height: 1px !important;
            padding: 0 !important;
            margin: -1px !important;
            overflow: hidden !important;
            clip: rect(0, 0, 0, 0) !important;
            white-space: nowrap !important;
            border: 0 !important;
        }
        
        /* 건너뛰기 링크 */
        .skip-link {
            position: absolute;
            top: -40px;
            left: 6px;
            background: #667eea;
            color: white;
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 1000;
            transition: top 0.3s;
        }
        
        .skip-link:focus {
            top: 6px;
        }
        
        /* 최소 터치 타겟 크기 (44px) */
        .gr-button,
        .gr-file,
        .clickable {
            min-height: 44px !important;
            min-width: 44px !important;
        }
        
        /* 텍스트 대비 향상 */
        .high-contrast {
            color: #000000 !important;
            background: #ffffff !important;
        }
        
        .high-contrast .gr-button-primary {
            background: #000000 !important;
            color: #ffffff !important;
            border: 2px solid #000000 !important;
        }
        
        /* 애니메이션 제어 */
        .reduced-motion * {
            animation: none !important;
            transition: none !important;
        }
        
        /* 더 큰 텍스트 크기 옵션 */
        .large-text {
            font-size: 1.2em !important;
            line-height: 1.6 !important;
        }
        
        .large-text .gr-button {
            font-size: 1.1em !important;
            padding: 12px 20px !important;
        }
        
        /* 키보드 내비게이션 표시 */
        .keyboard-nav .gr-button:focus,
        .keyboard-nav .gr-textbox:focus {
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.5) !important;
        }
        
        /* 에러 상태 접근성 */
        .error-state {
            border: 2px solid #dc3545 !important;
            background: #f8d7da !important;
        }
        
        .error-text {
            color: #721c24 !important;
            font-weight: 600 !important;
        }
        
        /* 성공 상태 접근성 */
        .success-state {
            border: 2px solid #28a745 !important;
            background: #d4edda !important;
        }
        
        .success-text {
            color: #155724 !important;
            font-weight: 600 !important;
        }
        """
    
    @staticmethod
    def create_accessibility_controls() -> gr.HTML:
        """접근성 컨트롤 패널 생성"""
        return gr.HTML("""
        <div id="accessibility-controls" style="
            position: fixed;
            top: 80px;
            right: 20px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            z-index: 999;
            display: none;
            min-width: 280px;
        ">
            <div style="font-weight: 600; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;">
                <span>♿ 접근성 설정</span>
                <button onclick="document.getElementById('accessibility-controls').style.display='none'" style="
                    background: none;
                    border: none;
                    font-size: 18px;
                    cursor: pointer;
                    color: #666;
                ">×</button>
            </div>
            
            <div style="margin-bottom: 12px;">
                <label style="display: flex; align-items: center; cursor: pointer;">
                    <input type="checkbox" id="high-contrast-toggle" style="margin-right: 8px;" onchange="toggleHighContrast()">
                    <span>고대비 모드</span>
                </label>
            </div>
            
            <div style="margin-bottom: 12px;">
                <label style="display: flex; align-items: center; cursor: pointer;">
                    <input type="checkbox" id="large-text-toggle" style="margin-right: 8px;" onchange="toggleLargeText()">
                    <span>큰 텍스트</span>
                </label>
            </div>
            
            <div style="margin-bottom: 12px;">
                <label style="display: flex; align-items: center; cursor: pointer;">
                    <input type="checkbox" id="reduced-motion-toggle" style="margin-right: 8px;" onchange="toggleReducedMotion()">
                    <span>애니메이션 감소</span>
                </label>
            </div>
            
            <div style="margin-bottom: 12px;">
                <label style="display: flex; align-items: center; cursor: pointer;">
                    <input type="checkbox" id="keyboard-nav-toggle" style="margin-right: 8px;" onchange="toggleKeyboardNav()">
                    <span>키보드 내비게이션 강조</span>
                </label>
            </div>
            
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e0e0e0;">
                <button onclick="resetAccessibilitySettings()" style="
                    background: #f8f9fa;
                    border: 1px solid #e0e0e0;
                    padding: 8px 12px;
                    border-radius: 6px;
                    cursor: pointer;
                    width: 100%;
                ">기본값으로 재설정</button>
            </div>
        </div>
        
        <!-- 접근성 토글 버튼 -->
        <button id="accessibility-toggle" onclick="toggleAccessibilityPanel()" style="
            position: fixed;
            top: 20px;
            right: 80px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            z-index: 1000;
            transition: all 0.3s ease;
        " title="접근성 설정 열기">
            ♿
        </button>
        
        <script>
        function toggleAccessibilityPanel() {
            const panel = document.getElementById('accessibility-controls');
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        }
        
        function toggleHighContrast() {
            const body = document.body;
            const checkbox = document.getElementById('high-contrast-toggle');
            if (checkbox.checked) {
                body.classList.add('high-contrast');
                localStorage.setItem('high-contrast', 'true');
            } else {
                body.classList.remove('high-contrast');
                localStorage.removeItem('high-contrast');
            }
        }
        
        function toggleLargeText() {
            const body = document.body;
            const checkbox = document.getElementById('large-text-toggle');
            if (checkbox.checked) {
                body.classList.add('large-text');
                localStorage.setItem('large-text', 'true');
            } else {
                body.classList.remove('large-text');
                localStorage.removeItem('large-text');
            }
        }
        
        function toggleReducedMotion() {
            const body = document.body;
            const checkbox = document.getElementById('reduced-motion-toggle');
            if (checkbox.checked) {
                body.classList.add('reduced-motion');
                localStorage.setItem('reduced-motion', 'true');
            } else {
                body.classList.remove('reduced-motion');
                localStorage.removeItem('reduced-motion');
            }
        }
        
        function toggleKeyboardNav() {
            const body = document.body;
            const checkbox = document.getElementById('keyboard-nav-toggle');
            if (checkbox.checked) {
                body.classList.add('keyboard-nav');
                localStorage.setItem('keyboard-nav', 'true');
            } else {
                body.classList.remove('keyboard-nav');
                localStorage.removeItem('keyboard-nav');
            }
        }
        
        function resetAccessibilitySettings() {
            document.getElementById('high-contrast-toggle').checked = false;
            document.getElementById('large-text-toggle').checked = false;
            document.getElementById('reduced-motion-toggle').checked = false;
            document.getElementById('keyboard-nav-toggle').checked = false;
            
            document.body.classList.remove('high-contrast', 'large-text', 'reduced-motion', 'keyboard-nav');
            
            localStorage.removeItem('high-contrast');
            localStorage.removeItem('large-text');
            localStorage.removeItem('reduced-motion');
            localStorage.removeItem('keyboard-nav');
        }
        
        // 페이지 로드 시 저장된 설정 복원
        document.addEventListener('DOMContentLoaded', function() {
            if (localStorage.getItem('high-contrast')) {
                document.getElementById('high-contrast-toggle').checked = true;
                document.body.classList.add('high-contrast');
            }
            if (localStorage.getItem('large-text')) {
                document.getElementById('large-text-toggle').checked = true;
                document.body.classList.add('large-text');
            }
            if (localStorage.getItem('reduced-motion')) {
                document.getElementById('reduced-motion-toggle').checked = true;
                document.body.classList.add('reduced-motion');
            }
            if (localStorage.getItem('keyboard-nav')) {
                document.getElementById('keyboard-nav-toggle').checked = true;
                document.body.classList.add('keyboard-nav');
            }
        });
        
        // 키보드 접근성
        document.addEventListener('keydown', function(e) {
            // Alt + A: 접근성 패널 토글
            if (e.altKey && e.key === 'a') {
                e.preventDefault();
                toggleAccessibilityPanel();
            }
        });
        </script>
        """)
    
    @staticmethod
    def create_skip_links() -> gr.HTML:
        """건너뛰기 링크 생성"""
        return gr.HTML("""
        <div class="skip-links">
            <a href="#main-content" class="skip-link">메인 콘텐츠로 건너뛰기</a>
            <a href="#chat-input" class="skip-link">채팅 입력으로 건너뛰기</a>
            <a href="#file-upload" class="skip-link">파일 업로드로 건너뛰기</a>
            <a href="#settings" class="skip-link">설정으로 건너뛰기</a>
        </div>
        """)


class DeviceDetection:
    """디바이스 감지 및 최적화"""
    
    @staticmethod
    def get_device_optimization_script() -> str:
        """디바이스별 최적화 스크립트"""
        return """
        <script>
        (function() {
            // 디바이스 타입 감지
            function detectDevice() {
                const userAgent = navigator.userAgent;
                const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
                const isTablet = /iPad|Android(?=.*\\bMobile\\b)/i.test(userAgent);
                const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
                
                return {
                    isMobile: isMobile && !isTablet,
                    isTablet: isTablet,
                    isDesktop: !isMobile && !isTablet,
                    isTouchDevice: isTouchDevice
                };
            }
            
            // 디바이스별 클래스 추가
            function applyDeviceClasses() {
                const device = detectDevice();
                const body = document.body;
                
                if (device.isMobile) {
                    body.classList.add('mobile-device');
                } else if (device.isTablet) {
                    body.classList.add('tablet-device');
                } else {
                    body.classList.add('desktop-device');
                }
                
                if (device.isTouchDevice) {
                    body.classList.add('touch-device');
                } else {
                    body.classList.add('no-touch-device');
                }
            }
            
            // 뷰포트 크기 감지 및 클래스 적용
            function updateViewportClasses() {
                const width = window.innerWidth;
                const body = document.body;
                
                // 기존 뷰포트 클래스 제거
                body.classList.remove('viewport-xs', 'viewport-sm', 'viewport-md', 'viewport-lg', 'viewport-xl');
                
                if (width < 480) {
                    body.classList.add('viewport-xs');
                } else if (width < 768) {
                    body.classList.add('viewport-sm');
                } else if (width < 1024) {
                    body.classList.add('viewport-md');
                } else if (width < 1440) {
                    body.classList.add('viewport-lg');
                } else {
                    body.classList.add('viewport-xl');
                }
            }
            
            // 네트워크 상태 감지 (지원되는 경우)
            function handleNetworkChange() {
                if ('connection' in navigator) {
                    const connection = navigator.connection;
                    const body = document.body;
                    
                    // 느린 연결 감지
                    if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
                        body.classList.add('slow-connection');
                        // 애니메이션 비활성화
                        body.classList.add('reduced-motion');
                    } else {
                        body.classList.remove('slow-connection');
                    }
                }
            }
            
            // 배터리 상태 감지 (지원되는 경우)
            function handleBatteryChange() {
                if ('getBattery' in navigator) {
                    navigator.getBattery().then(function(battery) {
                        const body = document.body;
                        
                        function updateBatteryStatus() {
                            if (battery.level < 0.2 && !battery.charging) {
                                // 배터리 부족 시 성능 최적화
                                body.classList.add('low-battery');
                                body.classList.add('reduced-motion');
                            } else {
                                body.classList.remove('low-battery');
                            }
                        }
                        
                        battery.addEventListener('levelchange', updateBatteryStatus);
                        battery.addEventListener('chargingchange', updateBatteryStatus);
                        updateBatteryStatus();
                    });
                }
            }
            
            // 다크 모드 선호도 감지
            function handleColorSchemeChange() {
                const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
                
                function updateColorScheme(e) {
                    const body = document.body;
                    if (e.matches) {
                        body.classList.add('prefers-dark');
                    } else {
                        body.classList.remove('prefers-dark');
                    }
                }
                
                darkModeQuery.addListener(updateColorScheme);
                updateColorScheme(darkModeQuery);
            }
            
            // 모션 선호도 감지
            function handleMotionPreference() {
                const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
                
                function updateMotionPreference(e) {
                    const body = document.body;
                    if (e.matches) {
                        body.classList.add('prefers-reduced-motion');
                    } else {
                        body.classList.remove('prefers-reduced-motion');
                    }
                }
                
                reducedMotionQuery.addListener(updateMotionPreference);
                updateMotionPreference(reducedMotionQuery);
            }
            
            // 초기화
            function init() {
                applyDeviceClasses();
                updateViewportClasses();
                handleNetworkChange();
                handleBatteryChange();
                handleColorSchemeChange();
                handleMotionPreference();
                
                // 리사이즈 이벤트 리스너
                let resizeTimeout;
                window.addEventListener('resize', function() {
                    clearTimeout(resizeTimeout);
                    resizeTimeout = setTimeout(updateViewportClasses, 150);
                });
                
                // 네트워크 변경 이벤트 리스너
                if ('connection' in navigator) {
                    navigator.connection.addEventListener('change', handleNetworkChange);
                }
            }
            
            // DOM 로드 완료 후 실행
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', init);
            } else {
                init();
            }
        })();
        </script>
        """


# 전역 인스턴스들
responsive_design = ResponsiveDesign()
accessibility_features = AccessibilityFeatures()
device_detection = DeviceDetection()

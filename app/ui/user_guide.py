"""
사용자 가이드 및 도움말 시스템

사용자가 애플리케이션을 쉽게 사용할 수 있도록 도움말과 가이드를 제공합니다.
"""

import gradio as gr
from typing import Dict, List, Any
from app.config.settings import settings


class UserGuide:
    """사용자 가이드 관리"""
    
    @staticmethod
    def create_welcome_guide() -> gr.HTML:
        """환영 가이드 생성"""
        return gr.HTML(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            text-align: center;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        ">
            <h1 style="margin: 0 0 15px 0; font-size: 2.2em;">🎉 환영합니다!</h1>
            <p style="margin: 0 0 20px 0; font-size: 1.2em; opacity: 0.9;">
                <strong>{settings.app_name}</strong>에 오신 것을 환영합니다!
            </p>
            <div style="
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
            ">
                <h3 style="margin: 0 0 10px 0;">🚀 현재 단계: Week 2</h3>
                <p style="margin: 0; font-size: 0.95em;">
                    LangChain과 OpenAI가 연동되어 실제 AI와 대화할 수 있습니다!<br>
                    아래 가이드를 따라 설정을 완료하고 AI 분석 비서를 활용해보세요.
                </p>
            </div>
        </div>
        """)
    
    @staticmethod
    def create_quick_start_guide() -> gr.HTML:
        """빠른 시작 가이드"""
        return gr.HTML("""
        <div style="
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
        ">
            <h2 style="margin: 0 0 20px 0; color: #495057;">🚀 빠른 시작 가이드</h2>
            
            <div style="display: grid; gap: 15px;">
                <div style="
                    background: #e3f2fd;
                    border-left: 4px solid #2196F3;
                    padding: 15px;
                    border-radius: 8px;
                ">
                    <h3 style="margin: 0 0 10px 0; color: #1976D2;">
                        <span style="
                            background: #2196F3;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 50%;
                            font-size: 14px;
                            margin-right: 10px;
                        ">1</span>
                        OpenAI API 키 설정
                    </h3>
                    <p style="margin: 0; color: #555;">
                        <strong>설정 → AI 설정</strong>에서 OpenAI API 키를 입력하세요.<br>
                        API 키가 없다면 <a href="https://platform.openai.com/api-keys" target="_blank">OpenAI 웹사이트</a>에서 발급받을 수 있습니다.
                    </p>
                </div>
                
                <div style="
                    background: #e8f5e8;
                    border-left: 4px solid #4CAF50;
                    padding: 15px;
                    border-radius: 8px;
                ">
                    <h3 style="margin: 0 0 10px 0; color: #2E7D32;">
                        <span style="
                            background: #4CAF50;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 50%;
                            font-size: 14px;
                            margin-right: 10px;
                        ">2</span>
                        연결 테스트
                    </h3>
                    <p style="margin: 0; color: #555;">
                        API 키 입력 후 <strong>"연결 테스트"</strong> 버튼을 클릭하여 정상 연결을 확인하세요.
                    </p>
                </div>
                
                <div style="
                    background: #fff3e0;
                    border-left: 4px solid #FF9800;
                    padding: 15px;
                    border-radius: 8px;
                ">
                    <h3 style="margin: 0 0 10px 0; color: #F57C00;">
                        <span style="
                            background: #FF9800;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 50%;
                            font-size: 14px;
                            margin-right: 10px;
                        ">3</span>
                        AI와 대화 시작
                    </h3>
                    <p style="margin: 0; color: #555;">
                        채팅창에서 자연어로 질문해보세요!<br>
                        예: "안녕하세요", "데이터 분석 방법을 알려주세요", "SQL 쿼리 작성법은?"
                    </p>
                </div>
                
                <div style="
                    background: #f3e5f5;
                    border-left: 4px solid #9C27B0;
                    padding: 15px;
                    border-radius: 8px;
                ">
                    <h3 style="margin: 0 0 10px 0; color: #7B1FA2;">
                        <span style="
                            background: #9C27B0;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 50%;
                            font-size: 14px;
                            margin-right: 10px;
                        ">4</span>
                        기능 탐색
                    </h3>
                    <p style="margin: 0; color: #555;">
                        다양한 질문으로 AI의 능력을 테스트해보세요. 현재는 기본 대화가 가능하며, 
                        Week 3-5에서 SQL, Excel 분석, 시각화 기능이 추가될 예정입니다.
                    </p>
                </div>
            </div>
        </div>
        """)
    
    @staticmethod
    def create_feature_overview() -> gr.HTML:
        """기능 개요"""
        return gr.HTML(f"""
        <div style="
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
        ">
            <h2 style="margin: 0 0 20px 0; color: #495057;">✨ 주요 기능</h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div style="
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid #e9ecef;
                ">
                    <div style="
                        background: #007bff;
                        color: white;
                        width: 50px;
                        height: 50px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 24px;
                        margin-bottom: 15px;
                    ">💬</div>
                    <h3 style="margin: 0 0 10px 0; color: #007bff;">AI 채팅</h3>
                    <p style="margin: 0; color: #6c757d; font-size: 14px; line-height: 1.5;">
                        OpenAI GPT-4와 자연어로 대화하며 데이터 분석에 대한 조언과 가이드를 받을 수 있습니다.
                    </p>
                    <div style="margin-top: 10px;">
                        <span style="
                            background: #28a745;
                            color: white;
                            padding: 2px 8px;
                            border-radius: 12px;
                            font-size: 12px;
                            font-weight: 600;
                        ">Week 2 구현 완료</span>
                    </div>
                </div>
                
                <div style="
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid #e9ecef;
                ">
                    <div style="
                        background: #28a745;
                        color: white;
                        width: 50px;
                        height: 50px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 24px;
                        margin-bottom: 15px;
                    ">🗄️</div>
                    <h3 style="margin: 0 0 10px 0; color: #28a745;">SQL 데이터베이스 질의</h3>
                    <p style="margin: 0; color: #6c757d; font-size: 14px; line-height: 1.5;">
                        자연어로 질문하면 자동으로 SQL 쿼리를 생성하여 데이터베이스를 조회합니다.
                    </p>
                    <div style="margin-top: 10px;">
                        <span style="
                            background: #ffc107;
                            color: #212529;
                            padding: 2px 8px;
                            border-radius: 12px;
                            font-size: 12px;
                            font-weight: 600;
                        ">Week 3 구현 예정</span>
                    </div>
                </div>
                
                <div style="
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid #e9ecef;
                ">
                    <div style="
                        background: #fd7e14;
                        color: white;
                        width: 50px;
                        height: 50px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 24px;
                        margin-bottom: 15px;
                    ">📊</div>
                    <h3 style="margin: 0 0 10px 0; color: #fd7e14;">Excel 데이터 분석</h3>
                    <p style="margin: 0; color: #6c757d; font-size: 14px; line-height: 1.5;">
                        Excel이나 CSV 파일을 업로드하여 AI가 자동으로 분석하고 인사이트를 제공합니다.
                    </p>
                    <div style="margin-top: 10px;">
                        <span style="
                            background: #ffc107;
                            color: #212529;
                            padding: 2px 8px;
                            border-radius: 12px;
                            font-size: 12px;
                            font-weight: 600;
                        ">Week 4 구현 예정</span>
                    </div>
                </div>
                
                <div style="
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid #e9ecef;
                ">
                    <div style="
                        background: #e83e8c;
                        color: white;
                        width: 50px;
                        height: 50px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 24px;
                        margin-bottom: 15px;
                    ">📈</div>
                    <h3 style="margin: 0 0 10px 0; color: #e83e8c;">자동 시각화</h3>
                    <p style="margin: 0; color: #6c757d; font-size: 14px; line-height: 1.5;">
                        분석 결과를 자동으로 차트와 그래프로 시각화하여 직관적으로 이해할 수 있습니다.
                    </p>
                    <div style="margin-top: 10px;">
                        <span style="
                            background: #ffc107;
                            color: #212529;
                            padding: 2px 8px;
                            border-radius: 12px;
                            font-size: 12px;
                            font-weight: 600;
                        ">Week 5 구현 예정</span>
                    </div>
                </div>
            </div>
        </div>
        """)
    
    @staticmethod
    def create_tips_and_tricks() -> gr.HTML:
        """팁과 요령"""
        return gr.HTML("""
        <div style="
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
        ">
            <h2 style="margin: 0 0 20px 0; color: #495057;">💡 사용 팁</h2>
            
            <div style="display: grid; gap: 15px;">
                <div style="
                    background: #e3f2fd;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #2196F3;
                ">
                    <h4 style="margin: 0 0 8px 0; color: #1976D2;">💬 효과적인 질문 방법</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                        <li>구체적이고 명확한 질문을 하세요</li>
                        <li>맥락을 제공하면 더 정확한 답변을 받을 수 있습니다</li>
                        <li>단계별로 복잡한 문제를 나누어 질문하세요</li>
                    </ul>
                </div>
                
                <div style="
                    background: #e8f5e8;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #4CAF50;
                ">
                    <h4 style="margin: 0 0 8px 0; color: #2E7D32;">⚙️ 설정 최적화</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                        <li>창의적 답변을 원하면 Temperature를 높이세요 (0.7-1.0)</li>
                        <li>일관적 답변을 원하면 Temperature를 낮추세요 (0.1-0.3)</li>
                        <li>긴 답변을 원하면 최대 토큰 수를 늘리세요</li>
                    </ul>
                </div>
                
                <div style="
                    background: #fff3e0;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #FF9800;
                ">
                    <h4 style="margin: 0 0 8px 0; color: #F57C00;">🔧 문제 해결</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                        <li>응답이 느리면 인터넷 연결을 확인하세요</li>
                        <li>오류가 발생하면 대화 기록을 초기화해보세요</li>
                        <li>API 사용량이 초과되면 잠시 후 다시 시도하세요</li>
                    </ul>
                </div>
                
                <div style="
                    background: #f3e5f5;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #9C27B0;
                ">
                    <h4 style="margin: 0 0 8px 0; color: #7B1FA2;">⌨️ 키보드 단축키</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                        <li><strong>Ctrl + Enter:</strong> 메시지 전송</li>
                        <li><strong>Ctrl + L:</strong> 대화 초기화</li>
                        <li><strong>Ctrl + /:</strong> 단축키 도움말</li>
                        <li><strong>Alt + A:</strong> 접근성 설정</li>
                    </ul>
                </div>
            </div>
        </div>
        """)
    
    @staticmethod
    def create_example_conversations() -> gr.HTML:
        """예시 대화"""
        return gr.HTML("""
        <div style="
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
        ">
            <h2 style="margin: 0 0 20px 0; color: #495057;">💬 예시 대화</h2>
            
            <div style="display: grid; gap: 20px;">
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    <h4 style="margin: 0 0 10px 0; color: #007bff;">🤖 일반 대화</h4>
                    <div style="background: #e3f2fd; padding: 10px; border-radius: 6px; margin: 5px 0;">
                        <strong>👤 사용자:</strong> 안녕하세요! 데이터 분석이 처음인데 어떻게 시작하면 좋을까요?
                    </div>
                    <div style="background: #e8f5e8; padding: 10px; border-radius: 6px; margin: 5px 0;">
                        <strong>🤖 AI:</strong> 안녕하세요! 데이터 분석을 시작하려면 먼저 목표를 명확히 하는 것이 중요합니다. 어떤 질문에 답하고 싶으신가요? 예를 들어 매출 증가 요인을 찾거나 고객 패턴을 분석하는 등의 구체적인 목표가 있으면 도와드릴 수 있습니다.
                    </div>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    <h4 style="margin: 0 0 10px 0; color: #28a745;">🗄️ SQL 관련 질문 (Week 3 구현 예정)</h4>
                    <div style="background: #e3f2fd; padding: 10px; border-radius: 6px; margin: 5px 0;">
                        <strong>👤 사용자:</strong> 지난 3개월 동안 가장 많이 팔린 제품 TOP 10을 알고 싶습니다.
                    </div>
                    <div style="background: #e8f5e8; padding: 10px; border-radius: 6px; margin: 5px 0;">
                        <strong>🤖 AI:</strong> 다음 SQL 쿼리로 확인할 수 있습니다:<br>
                        <code>SELECT product_name, SUM(quantity) as total_sales FROM sales WHERE sale_date >= DATE_SUB(NOW(), INTERVAL 3 MONTH) GROUP BY product_name ORDER BY total_sales DESC LIMIT 10;</code>
                    </div>
                </div>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    <h4 style="margin: 0 0 10px 0; color: #fd7e14;">📊 데이터 분석 질문</h4>
                    <div style="background: #e3f2fd; padding: 10px; border-radius: 6px; margin: 5px 0;">
                        <strong>👤 사용자:</strong> 월별 매출 트렌드를 분석하는 좋은 방법이 있을까요?
                    </div>
                    <div style="background: #e8f5e8; padding: 10px; border-radius: 6px; margin: 5px 0;">
                        <strong>🤖 AI:</strong> 월별 매출 트렌드 분석을 위해서는 다음과 같은 방법들을 사용할 수 있습니다: 1) 시계열 분석으로 계절성 파악 2) 이동평균으로 노이즈 제거 3) 전년 동월 대비 성장률 계산 4) 선형 회귀로 전반적인 트렌드 확인. 어떤 방법에 대해 더 자세히 알고 싶으신가요?
                    </div>
                </div>
            </div>
        </div>
        """)
    
    @staticmethod
    def create_troubleshooting_guide() -> gr.HTML:
        """문제 해결 가이드"""
        return gr.HTML("""
        <div style="
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
        ">
            <h2 style="margin: 0 0 20px 0; color: #495057;">🔧 문제 해결 가이드</h2>
            
            <div style="display: grid; gap: 15px;">
                <details style="
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #dee2e6;
                ">
                    <summary style="
                        font-weight: 600;
                        cursor: pointer;
                        color: #495057;
                        margin-bottom: 10px;
                    ">❌ AI가 응답하지 않아요</summary>
                    <div style="margin-top: 10px; color: #6c757d;">
                        <strong>가능한 원인:</strong>
                        <ul>
                            <li>OpenAI API 키가 설정되지 않았거나 잘못됨</li>
                            <li>네트워크 연결 문제</li>
                            <li>API 사용량 한도 초과</li>
                        </ul>
                        <strong>해결 방법:</strong>
                        <ol>
                            <li>설정에서 API 키를 다시 확인하세요</li>
                            <li>연결 테스트 버튼을 클릭하여 상태를 확인하세요</li>
                            <li>인터넷 연결을 확인하세요</li>
                            <li>OpenAI 계정의 사용량을 확인하세요</li>
                        </ol>
                    </div>
                </details>
                
                <details style="
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #dee2e6;
                ">
                    <summary style="
                        font-weight: 600;
                        cursor: pointer;
                        color: #495057;
                        margin-bottom: 10px;
                    ">⏳ 응답이 너무 느려요</summary>
                    <div style="margin-top: 10px; color: #6c757d;">
                        <strong>가능한 원인:</strong>
                        <ul>
                            <li>네트워크 속도가 느림</li>
                            <li>OpenAI 서버 부하</li>
                            <li>너무 긴 질문이나 복잡한 요청</li>
                        </ul>
                        <strong>해결 방법:</strong>
                        <ol>
                            <li>질문을 짧고 명확하게 나누어 보내세요</li>
                            <li>네트워크 연결 상태를 확인하세요</li>
                            <li>잠시 후 다시 시도하세요</li>
                        </ol>
                    </div>
                </details>
                
                <details style="
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #dee2e6;
                ">
                    <summary style="
                        font-weight: 600;
                        cursor: pointer;
                        color: #495057;
                        margin-bottom: 10px;
                    ">💰 API 사용량이 초과되었어요</summary>
                    <div style="margin-top: 10px; color: #6c757d;">
                        <strong>해결 방법:</strong>
                        <ol>
                            <li><a href="https://platform.openai.com/usage" target="_blank">OpenAI 사용량 페이지</a>에서 현재 상태를 확인하세요</li>
                            <li>요금제를 업그레이드하거나 월간 한도를 늘리세요</li>
                            <li>다음 월까지 기다리거나 추가 크레딧을 구매하세요</li>
                            <li>임시로 데모 모드를 사용하세요</li>
                        </ol>
                    </div>
                </details>
                
                <details style="
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #dee2e6;
                ">
                    <summary style="
                        font-weight: 600;
                        cursor: pointer;
                        color: #495057;
                        margin-bottom: 10px;
                    ">🔄 애플리케이션이 멈춰요</summary>
                    <div style="margin-top: 10px; color: #6c757d;">
                        <strong>해결 방법:</strong>
                        <ol>
                            <li>브라우저를 새로고침하세요 (F5 또는 Ctrl+R)</li>
                            <li>대화 기록을 초기화하세요</li>
                            <li>브라우저 캐시를 지우세요</li>
                            <li>다른 브라우저로 시도해보세요</li>
                            <li>애플리케이션을 재시작하세요</li>
                        </ol>
                    </div>
                </details>
            </div>
            
            <div style="
                margin-top: 20px;
                padding: 15px;
                background: #e3f2fd;
                border-radius: 8px;
                text-align: center;
            ">
                <h4 style="margin: 0 0 10px 0; color: #1976D2;">💬 추가 도움이 필요하신가요?</h4>
                <p style="margin: 0; color: #555;">
                    위 해결 방법으로도 문제가 해결되지 않으면, 
                    AI 채팅창에 "<strong>도움말</strong>" 또는 "<strong>문제 해결</strong>"이라고 입력하여 
                    더 구체적인 도움을 받으실 수 있습니다.
                </p>
            </div>
        </div>
        """)


class TutorialCreator:
    """튜토리얼 생성기"""
    
    @staticmethod
    def create_interactive_tutorial() -> gr.HTML:
        """인터랙티브 튜토리얼"""
        return gr.HTML("""
        <div id="interactive-tutorial" style="
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
        ">
            <h2 style="margin: 0 0 20px 0; color: #495057;">🎓 인터랙티브 튜토리얼</h2>
            
            <div id="tutorial-content">
                <div style="text-align: center; padding: 20px;">
                    <button onclick="startTutorial()" style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border: none;
                        padding: 15px 30px;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: transform 0.2s;
                    " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                        🚀 튜토리얼 시작하기
                    </button>
                </div>
            </div>
        </div>
        
        <script>
        let tutorialStep = 0;
        const tutorialSteps = [
            {
                title: "환영합니다! 🎉",
                content: "AI 데이터 분석 비서 사용법을 단계별로 알려드릴게요. 약 3분 정도 소요됩니다."
            },
            {
                title: "1단계: AI 상태 확인 🔍",
                content: "오른쪽 상단의 AI 상태 패널을 확인하세요. 녹색이면 정상, 빨간색이면 API 키 설정이 필요합니다."
            },
            {
                title: "2단계: API 키 설정 🔑",
                content: "설정 패널에서 OpenAI API 키를 입력하고 연결 테스트를 해보세요. API 키는 OpenAI 웹사이트에서 발급받을 수 있습니다."
            },
            {
                title: "3단계: 첫 대화 시작 💬",
                content: "채팅창에 '안녕하세요'라고 입력해보세요. AI가 응답하면 성공입니다!"
            },
            {
                title: "4단계: 다양한 질문 시도 🤔",
                content: "데이터 분석, SQL, Excel 관련 질문을 해보세요. 예시 질문 버튼을 클릭하면 쉽게 시작할 수 있습니다."
            },
            {
                title: "완료! 🎊",
                content: "튜토리얼을 완료했습니다! 이제 AI 데이터 분석 비서를 자유롭게 사용해보세요. 궁금한 점이 있으면 언제든 물어보세요."
            }
        ];
        
        function startTutorial() {
            tutorialStep = 0;
            showTutorialStep();
        }
        
        function showTutorialStep() {
            const step = tutorialSteps[tutorialStep];
            const content = document.getElementById('tutorial-content');
            
            content.innerHTML = `
                <div style="text-align: center;">
                    <h3 style="color: #667eea; margin-bottom: 15px;">${step.title}</h3>
                    <p style="margin-bottom: 20px; line-height: 1.6; color: #555;">${step.content}</p>
                    
                    <div style="margin: 20px 0;">
                        <div style="
                            background: #e9ecef;
                            height: 4px;
                            border-radius: 2px;
                            overflow: hidden;
                        ">
                            <div style="
                                background: linear-gradient(90deg, #667eea, #764ba2);
                                height: 100%;
                                width: ${((tutorialStep + 1) / tutorialSteps.length) * 100}%;
                                transition: width 0.3s ease;
                            "></div>
                        </div>
                        <small style="color: #6c757d;">${tutorialStep + 1} / ${tutorialSteps.length}</small>
                    </div>
                    
                    <div>
                        ${tutorialStep > 0 ? `
                            <button onclick="previousStep()" style="
                                background: #6c757d;
                                color: white;
                                border: none;
                                padding: 10px 20px;
                                border-radius: 6px;
                                margin-right: 10px;
                                cursor: pointer;
                            ">이전</button>
                        ` : ''}
                        
                        ${tutorialStep < tutorialSteps.length - 1 ? `
                            <button onclick="nextStep()" style="
                                background: #667eea;
                                color: white;
                                border: none;
                                padding: 10px 20px;
                                border-radius: 6px;
                                cursor: pointer;
                            ">다음</button>
                        ` : `
                            <button onclick="closeTutorial()" style="
                                background: #28a745;
                                color: white;
                                border: none;
                                padding: 10px 20px;
                                border-radius: 6px;
                                cursor: pointer;
                            ">완료</button>
                        `}
                    </div>
                </div>
            `;
        }
        
        function nextStep() {
            if (tutorialStep < tutorialSteps.length - 1) {
                tutorialStep++;
                showTutorialStep();
            }
        }
        
        function previousStep() {
            if (tutorialStep > 0) {
                tutorialStep--;
                showTutorialStep();
            }
        }
        
        function closeTutorial() {
            const content = document.getElementById('tutorial-content');
            content.innerHTML = `
                <div style="text-align: center; padding: 20px;">
                    <h3 style="color: #28a745; margin-bottom: 15px;">🎉 튜토리얼 완료!</h3>
                    <p style="margin-bottom: 20px; color: #555;">
                        이제 AI 데이터 분석 비서를 사용할 준비가 되었습니다!
                    </p>
                    <button onclick="startTutorial()" style="
                        background: #667eea;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 6px;
                        cursor: pointer;
                    ">다시 보기</button>
                </div>
            `;
        }
        </script>
        """)


# 전역 인스턴스들
user_guide = UserGuide()
tutorial_creator = TutorialCreator()

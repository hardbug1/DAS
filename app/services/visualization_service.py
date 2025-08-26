"""
기초 시각화 서비스

SQL 쿼리 결과를 자동으로 분석하여 적절한 차트를 생성합니다.
Week 5의 고급 시각화를 위한 기반 구조를 제공합니다.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import structlog
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

logger = structlog.get_logger()


class ChartTypeSelector:
    """차트 타입 자동 선택"""
    
    def __init__(self):
        self.rules = self._initialize_chart_rules()
    
    def _initialize_chart_rules(self) -> List[Dict[str, Any]]:
        """차트 선택 규칙 정의"""
        return [
            {
                'name': 'time_series',
                'conditions': lambda df: self._has_time_column(df) and self._has_numeric_column(df),
                'chart_type': 'line',
                'priority': 10,
                'description': '시계열 데이터 - 선 그래프'
            },
            {
                'name': 'categorical_ranking',
                'conditions': lambda df: self._has_categorical_column(df) and self._has_numeric_column(df) and len(df) <= 20,
                'chart_type': 'bar',
                'priority': 8,
                'description': '카테고리별 순위 - 막대 그래프'
            },
            {
                'name': 'distribution',
                'conditions': lambda df: len(df.select_dtypes(include=[np.number]).columns) >= 1 and len(df) > 20,
                'chart_type': 'histogram',
                'priority': 6,
                'description': '분포 분석 - 히스토그램'
            },
            {
                'name': 'correlation',
                'conditions': lambda df: len(df.select_dtypes(include=[np.number]).columns) >= 2,
                'chart_type': 'scatter',
                'priority': 5,
                'description': '상관관계 - 산점도'
            },
            {
                'name': 'proportion',
                'conditions': lambda df: self._has_categorical_column(df) and len(df) <= 10,
                'chart_type': 'pie',
                'priority': 7,
                'description': '구성비 - 파이 차트'
            },
            {
                'name': 'default_table',
                'conditions': lambda df: True,  # 항상 참
                'chart_type': 'table',
                'priority': 1,
                'description': '기본 테이블'
            }
        ]
    
    def _has_time_column(self, df: pd.DataFrame) -> bool:
        """시간 관련 컬럼 존재 여부"""
        time_patterns = ['date', 'time', 'year', 'month', 'day', '일', '월', '년']
        for col in df.columns:
            if any(pattern in col.lower() for pattern in time_patterns):
                return True
            # 데이터 타입 확인
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                return True
        return False
    
    def _has_categorical_column(self, df: pd.DataFrame) -> bool:
        """카테고리 컬럼 존재 여부"""
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        return len(categorical_cols) > 0
    
    def _has_numeric_column(self, df: pd.DataFrame) -> bool:
        """숫자 컬럼 존재 여부"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        return len(numeric_cols) > 0
    
    def select_chart_type(self, df: pd.DataFrame, query_intent: str = 'general') -> Dict[str, Any]:
        """데이터에 적합한 차트 타입 선택"""
        if df.empty:
            return {
                'chart_type': 'table',
                'reason': '데이터가 없음',
                'priority': 0
            }
        
        # 규칙 기반 선택
        applicable_rules = []
        for rule in self.rules:
            try:
                if rule['conditions'](df):
                    applicable_rules.append(rule)
            except Exception as e:
                logger.warning("차트 규칙 평가 오류", rule=rule['name'], error=str(e))
        
        # 우선순위에 따라 정렬
        applicable_rules.sort(key=lambda x: x['priority'], reverse=True)
        
        if applicable_rules:
            selected = applicable_rules[0]
            return {
                'chart_type': selected['chart_type'],
                'reason': selected['description'],
                'priority': selected['priority'],
                'alternatives': [r['chart_type'] for r in applicable_rules[1:3]]  # 대안 2개
            }
        
        return {
            'chart_type': 'table',
            'reason': '적절한 차트를 찾을 수 없음',
            'priority': 0
        }


class BasicChartGenerator:
    """기본 차트 생성기"""
    
    def __init__(self):
        self.color_palette = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    def generate_chart(self, df: pd.DataFrame, chart_type: str, **kwargs) -> Dict[str, Any]:
        """차트 생성"""
        try:
            chart_methods = {
                'bar': self._create_bar_chart,
                'line': self._create_line_chart,
                'pie': self._create_pie_chart,
                'scatter': self._create_scatter_chart,
                'histogram': self._create_histogram,
                'table': self._create_table_display
            }
            
            if chart_type not in chart_methods:
                chart_type = 'table'
            
            chart_result = chart_methods[chart_type](df, **kwargs)
            
            return {
                'success': True,
                'chart': chart_result['chart'],
                'chart_type': chart_type,
                'insights': chart_result.get('insights', []),
                'config': chart_result.get('config', {})
            }
            
        except Exception as e:
            logger.error("차트 생성 실패", chart_type=chart_type, error=str(e))
            return {
                'success': False,
                'chart': None,
                'error': str(e),
                'fallback': self._create_table_display(df)['chart']
            }
    
    def _create_bar_chart(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """막대 그래프 생성"""
        # 적절한 컬럼 선택
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(categorical_cols) == 0 or len(numeric_cols) == 0:
            raise ValueError("막대 그래프를 위한 적절한 컬럼이 없습니다.")
        
        x_col = categorical_cols[0]
        y_col = numeric_cols[0]
        
        # 상위 20개만 표시 (너무 많으면 가독성 저하)
        if len(df) > 20:
            df_plot = df.nlargest(20, y_col)
        else:
            df_plot = df.copy()
        
        fig = px.bar(
            df_plot,
            x=x_col,
            y=y_col,
            title=f"{y_col} by {x_col}",
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            showlegend=False
        )
        
        # 인사이트 생성
        insights = [
            f"총 {len(df)}개 항목 중 상위 {len(df_plot)}개 표시",
            f"최고값: {df_plot[y_col].max():,.0f}",
            f"최저값: {df_plot[y_col].min():,.0f}",
            f"평균값: {df_plot[y_col].mean():,.0f}"
        ]
        
        return {
            'chart': fig,
            'insights': insights,
            'config': {'type': 'bar', 'x': x_col, 'y': y_col}
        }
    
    def _create_line_chart(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """선 그래프 생성"""
        # 시간 컬럼과 숫자 컬럼 찾기
        time_col = None
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]) or any(t in col.lower() for t in ['date', 'time', 'year', 'month']):
                time_col = col
                break
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if time_col is None or len(numeric_cols) == 0:
            raise ValueError("선 그래프를 위한 시간 및 숫자 컬럼이 없습니다.")
        
        y_col = numeric_cols[0]
        
        # 시간 순으로 정렬
        df_plot = df.sort_values(time_col)
        
        fig = px.line(
            df_plot,
            x=time_col,
            y=y_col,
            title=f"{y_col} Over Time",
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(height=500)
        
        # 트렌드 분석
        if len(df_plot) >= 2:
            slope = (df_plot[y_col].iloc[-1] - df_plot[y_col].iloc[0]) / len(df_plot)
            trend = "증가" if slope > 0 else "감소" if slope < 0 else "안정"
        else:
            trend = "분석 불가"
        
        insights = [
            f"전체 기간: {len(df_plot)}개 데이터 포인트",
            f"트렌드: {trend}",
            f"최고값: {df_plot[y_col].max():,.0f}",
            f"최저값: {df_plot[y_col].min():,.0f}"
        ]
        
        return {
            'chart': fig,
            'insights': insights,
            'config': {'type': 'line', 'x': time_col, 'y': y_col}
        }
    
    def _create_pie_chart(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """파이 차트 생성"""
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(categorical_cols) == 0:
            raise ValueError("파이 차트를 위한 카테고리 컬럼이 없습니다.")
        
        category_col = categorical_cols[0]
        
        if len(numeric_cols) > 0:
            # 숫자 컬럼이 있으면 집계
            value_col = numeric_cols[0]
            df_plot = df.groupby(category_col)[value_col].sum().reset_index()
        else:
            # 카테고리 개수 집계
            df_plot = df[category_col].value_counts().reset_index()
            df_plot.columns = [category_col, 'count']
            value_col = 'count'
        
        # 상위 8개만 표시, 나머지는 '기타'로 합침
        if len(df_plot) > 8:
            df_top = df_plot.head(7)
            others_sum = df_plot.tail(len(df_plot) - 7)[value_col].sum()
            df_others = pd.DataFrame({category_col: ['기타'], value_col: [others_sum]})
            df_plot = pd.concat([df_top, df_others], ignore_index=True)
        
        fig = px.pie(
            df_plot,
            values=value_col,
            names=category_col,
            title=f"{category_col} Distribution",
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(height=500)
        
        insights = [
            f"총 {len(df)}개 항목을 {len(df_plot)}개 그룹으로 분류",
            f"최대 비중: {df_plot[value_col].max() / df_plot[value_col].sum() * 100:.1f}%",
            f"최소 비중: {df_plot[value_col].min() / df_plot[value_col].sum() * 100:.1f}%"
        ]
        
        return {
            'chart': fig,
            'insights': insights,
            'config': {'type': 'pie', 'category': category_col, 'value': value_col}
        }
    
    def _create_scatter_chart(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """산점도 생성"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            raise ValueError("산점도를 위한 숫자 컬럼이 2개 이상 필요합니다.")
        
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            title=f"{y_col} vs {x_col}",
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(height=500)
        
        # 상관관계 계산
        correlation = df[x_col].corr(df[y_col])
        corr_strength = "강한" if abs(correlation) > 0.7 else "보통" if abs(correlation) > 0.3 else "약한"
        corr_direction = "양의" if correlation > 0 else "음의"
        
        insights = [
            f"데이터 포인트: {len(df)}개",
            f"상관관계: {corr_strength} {corr_direction} 상관관계 (r={correlation:.3f})",
            f"{x_col} 범위: {df[x_col].min():,.0f} ~ {df[x_col].max():,.0f}",
            f"{y_col} 범위: {df[y_col].min():,.0f} ~ {df[y_col].max():,.0f}"
        ]
        
        return {
            'chart': fig,
            'insights': insights,
            'config': {'type': 'scatter', 'x': x_col, 'y': y_col, 'correlation': correlation}
        }
    
    def _create_histogram(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """히스토그램 생성"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            raise ValueError("히스토그램을 위한 숫자 컬럼이 없습니다.")
        
        col = numeric_cols[0]
        
        fig = px.histogram(
            df,
            x=col,
            title=f"Distribution of {col}",
            nbins=min(30, len(df) // 2),  # 적절한 bin 수
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_layout(height=500)
        
        # 분포 통계
        mean_val = df[col].mean()
        median_val = df[col].median()
        std_val = df[col].std()
        
        insights = [
            f"평균: {mean_val:,.2f}",
            f"중앙값: {median_val:,.2f}",
            f"표준편차: {std_val:,.2f}",
            f"분포 형태: {'정규분포에 가까움' if abs(mean_val - median_val) < std_val * 0.5 else '비대칭 분포'}"
        ]
        
        return {
            'chart': fig,
            'insights': insights,
            'config': {'type': 'histogram', 'column': col}
        }
    
    def _create_table_display(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """테이블 표시"""
        # 너무 많은 행은 상위 100개만 표시
        if len(df) > 100:
            df_display = df.head(100)
            truncated = True
        else:
            df_display = df
            truncated = False
        
        insights = [
            f"총 {len(df)}행, {len(df.columns)}열",
            f"{'상위 100행만 표시' if truncated else '전체 데이터 표시'}",
            f"숫자 컬럼: {len(df.select_dtypes(include=[np.number]).columns)}개",
            f"텍스트 컬럼: {len(df.select_dtypes(include=['object', 'category']).columns)}개"
        ]
        
        return {
            'chart': df_display,  # DataFrame 자체 반환
            'insights': insights,
            'config': {'type': 'table', 'truncated': truncated}
        }


class VisualizationService:
    """시각화 서비스 메인 클래스"""
    
    def __init__(self):
        self.chart_selector = ChartTypeSelector()
        self.chart_generator = BasicChartGenerator()
    
    def create_visualization(self, data: Dict[str, Any], query_intent: str = 'general') -> Dict[str, Any]:
        """데이터를 분석하여 시각화 생성"""
        try:
            # 데이터 검증 및 변환
            if not data or 'data' not in data:
                return {
                    'success': False,
                    'error': '시각화할 데이터가 없습니다.',
                    'chart': None
                }
            
            # DataFrame 생성
            df = pd.DataFrame(data['data'])
            
            if df.empty:
                return {
                    'success': False,
                    'error': '빈 데이터셋입니다.',
                    'chart': None
                }
            
            # 차트 타입 선택
            chart_selection = self.chart_selector.select_chart_type(df, query_intent)
            
            # 차트 생성
            chart_result = self.chart_generator.generate_chart(
                df, 
                chart_selection['chart_type']
            )
            
            if chart_result['success']:
                return {
                    'success': True,
                    'chart': chart_result['chart'],
                    'chart_type': chart_result['chart_type'],
                    'insights': chart_result['insights'],
                    'selection_reason': chart_selection['reason'],
                    'alternatives': chart_selection.get('alternatives', []),
                    'data_summary': self._generate_data_summary(df)
                }
            else:
                return {
                    'success': False,
                    'error': chart_result['error'],
                    'chart': chart_result.get('fallback'),
                    'chart_type': 'table'
                }
                
        except Exception as e:
            logger.error("시각화 생성 실패", error=str(e))
            return {
                'success': False,
                'error': f"시각화 생성 중 오류: {str(e)}",
                'chart': None
            }
    
    def _generate_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """데이터 요약 정보 생성"""
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns),
            'missing_values': df.isnull().sum().sum(),
            'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB"
        }


# 전역 시각화 서비스 인스턴스
visualization_service = VisualizationService()

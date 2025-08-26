"""
파일 검증 유틸리티

업로드된 파일의 형식, 크기, 내용을 검증하는 유틸리티 함수들을 제공합니다.
"""

import os
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
import pandas as pd
import structlog
from typing import Tuple, Dict, Any, List, Optional
from pathlib import Path
from app.config.settings import settings

logger = structlog.get_logger()


class FileValidator:
    """파일 검증 클래스"""
    
    def __init__(self):
        self.max_file_size = settings.max_excel_file_size_mb * 1024 * 1024  # MB to bytes
        self.allowed_extensions = ['.xlsx', '.xls', '.csv']
        self.allowed_mime_types = [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
            'application/vnd.ms-excel',  # .xls
            'text/csv',  # .csv
            'application/csv',  # .csv (alternative)
            'text/plain'  # .csv (sometimes detected as plain text)
        ]
    
    def validate_file(self, file_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        파일을 종합적으로 검증합니다.
        
        Args:
            file_path: 검증할 파일 경로
            
        Returns:
            (is_valid, message, file_info)
        """
        try:
            if not os.path.exists(file_path):
                return False, "파일이 존재하지 않습니다.", {}
            
            file_info = self._get_file_info(file_path)
            
            # 1. 파일 크기 검증
            size_valid, size_msg = self._validate_file_size(file_info['size'])
            if not size_valid:
                return False, size_msg, file_info
            
            # 2. 파일 확장자 검증
            ext_valid, ext_msg = self._validate_file_extension(file_info['extension'])
            if not ext_valid:
                return False, ext_msg, file_info
            
            # 3. MIME 타입 검증
            mime_valid, mime_msg = self._validate_mime_type(file_path)
            if not mime_valid:
                return False, mime_msg, file_info
            
            # 4. 파일 내용 검증 (간단한 읽기 테스트)
            content_valid, content_msg = self._validate_file_content(file_path, file_info['extension'])
            if not content_valid:
                return False, content_msg, file_info
            
            logger.info("파일 검증 성공", file_info=file_info)
            return True, "파일이 성공적으로 검증되었습니다.", file_info
            
        except Exception as e:
            logger.error("파일 검증 중 오류 발생", error=str(e))
            return False, f"파일 검증 중 오류가 발생했습니다: {str(e)}", {}
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """파일 정보 수집"""
        path_obj = Path(file_path)
        stat = os.stat(file_path)
        
        return {
            'name': path_obj.name,
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'extension': path_obj.suffix.lower(),
            'created': stat.st_ctime,
            'modified': stat.st_mtime
        }
    
    def _validate_file_size(self, file_size: int) -> Tuple[bool, str]:
        """파일 크기 검증"""
        if file_size > self.max_file_size:
            max_mb = self.max_file_size / (1024 * 1024)
            current_mb = file_size / (1024 * 1024)
            return False, f"파일 크기가 너무 큽니다. 최대 {max_mb}MB, 현재 {current_mb:.2f}MB"
        
        if file_size == 0:
            return False, "빈 파일입니다."
        
        return True, "파일 크기가 적절합니다."
    
    def _validate_file_extension(self, extension: str) -> Tuple[bool, str]:
        """파일 확장자 검증"""
        if extension not in self.allowed_extensions:
            allowed_str = ', '.join(self.allowed_extensions)
            return False, f"지원하지 않는 파일 형식입니다. 지원 형식: {allowed_str}"
        
        return True, f"지원하는 파일 형식입니다: {extension}"
    
    def _validate_mime_type(self, file_path: str) -> Tuple[bool, str]:
        """MIME 타입 검증"""
        try:
            # python-magic이 설치되어 있다면 사용
            if MAGIC_AVAILABLE:
                mime_type = magic.from_file(file_path, mime=True)
            else:
                # python-magic이 없으면 확장자 기반으로 추정
                extension = Path(file_path).suffix.lower()
                mime_type = self._get_mime_from_extension(extension)
            
            if mime_type in self.allowed_mime_types:
                return True, f"유효한 MIME 타입입니다: {mime_type}"
            
            # CSV 파일의 경우 text/plain으로 감지될 수 있으므로 추가 확인
            if 'text/' in mime_type and Path(file_path).suffix.lower() == '.csv':
                return True, f"CSV 파일로 감지되었습니다: {mime_type}"
            
            return False, f"지원하지 않는 파일 타입입니다: {mime_type}"
            
        except Exception as e:
            logger.warning("MIME 타입 검증 실패, 확장자로 대체", error=str(e))
            # MIME 타입 검증이 실패하면 확장자 검증으로 대체
            return True, "MIME 타입 검증을 건너뛰었습니다."
    
    def _get_mime_from_extension(self, extension: str) -> str:
        """확장자에서 MIME 타입 추정"""
        mime_map = {
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.csv': 'text/csv'
        }
        return mime_map.get(extension, 'application/octet-stream')
    
    def _validate_file_content(self, file_path: str, extension: str) -> Tuple[bool, str]:
        """파일 내용 검증 (간단한 읽기 테스트)"""
        try:
            if extension == '.csv':
                # CSV 파일 읽기 테스트
                df = pd.read_csv(file_path, nrows=5)  # 처음 5행만 읽기
            elif extension in ['.xlsx', '.xls']:
                # Excel 파일 읽기 테스트
                df = pd.read_excel(file_path, nrows=5)  # 처음 5행만 읽기
            else:
                return False, f"지원하지 않는 파일 형식: {extension}"
            
            if df.empty:
                return False, "파일에 데이터가 없습니다."
            
            return True, f"파일 내용이 유효합니다. {len(df)}행 확인됨"
            
        except pd.errors.EmptyDataError:
            return False, "파일이 비어있거나 읽을 수 없습니다."
        except pd.errors.ParserError as e:
            return False, f"파일 형식이 올바르지 않습니다: {str(e)}"
        except Exception as e:
            return False, f"파일 읽기 오류: {str(e)}"


class FileSecurityValidator:
    """파일 보안 검증 클래스"""
    
    def __init__(self):
        self.dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.vbs', '.js']
        self.max_filename_length = 255
    
    def validate_security(self, file_path: str) -> Tuple[bool, str]:
        """파일 보안 검증"""
        try:
            path_obj = Path(file_path)
            
            # 1. 파일명 길이 검증
            if len(path_obj.name) > self.max_filename_length:
                return False, f"파일명이 너무 깁니다. 최대 {self.max_filename_length}자"
            
            # 2. 위험한 확장자 검증
            if path_obj.suffix.lower() in self.dangerous_extensions:
                return False, "보안상 위험한 파일 형식입니다."
            
            # 3. 파일명에 특수문자 검증
            dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\x00']
            if any(char in path_obj.name for char in dangerous_chars):
                return False, "파일명에 허용되지 않는 문자가 포함되어 있습니다."
            
            # 4. 경로 조작 시도 검증
            if '..' in str(path_obj) or path_obj.is_absolute():
                return False, "잘못된 파일 경로입니다."
            
            return True, "보안 검증을 통과했습니다."
            
        except Exception as e:
            logger.error("보안 검증 중 오류", error=str(e))
            return False, f"보안 검증 오류: {str(e)}"


class DataQualityValidator:
    """데이터 품질 검증 클래스"""
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """데이터 품질 분석"""
        try:
            total_rows = len(df)
            total_cols = len(df.columns)
            
            # 결측값 분석
            missing_values = df.isnull().sum()
            missing_percentage = (missing_values / total_rows * 100).round(2)
            
            # 중복 행 분석
            duplicate_rows = df.duplicated().sum()
            duplicate_percentage = (duplicate_rows / total_rows * 100).round(2)
            
            # 데이터 타입 분석
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            text_cols = df.select_dtypes(include=['object']).columns.tolist()
            datetime_cols = df.select_dtypes(include=['datetime']).columns.tolist()
            
            # 메모리 사용량
            memory_usage = df.memory_usage(deep=True).sum()
            memory_mb = round(memory_usage / (1024 * 1024), 2)
            
            return {
                'total_rows': total_rows,
                'total_columns': total_cols,
                'missing_values': missing_values.to_dict(),
                'missing_percentage': missing_percentage.to_dict(),
                'duplicate_rows': duplicate_rows,
                'duplicate_percentage': duplicate_percentage,
                'numeric_columns': numeric_cols,
                'text_columns': text_cols,
                'datetime_columns': datetime_cols,
                'memory_usage_mb': memory_mb,
                'quality_score': self._calculate_quality_score(
                    missing_percentage.mean(), duplicate_percentage
                )
            }
            
        except Exception as e:
            logger.error("데이터 품질 분석 오류", error=str(e))
            return {'error': str(e)}
    
    def _calculate_quality_score(self, avg_missing: float, duplicate_pct: float) -> int:
        """데이터 품질 점수 계산 (0-100)"""
        score = 100
        
        # 결측값이 많을수록 점수 감소
        score -= min(avg_missing * 2, 50)
        
        # 중복 데이터가 많을수록 점수 감소
        score -= min(duplicate_pct, 30)
        
        return max(int(score), 0)


# 전역 검증기 인스턴스
file_validator = FileValidator()
security_validator = FileSecurityValidator()
quality_validator = DataQualityValidator()

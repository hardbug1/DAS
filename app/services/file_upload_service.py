"""
파일 업로드 서비스

파일 업로드, 저장, 관리를 담당하는 서비스입니다.
세션별 파일 격리, 임시 파일 정리, 업로드 진행률 추적 등을 제공합니다.
"""

import os
import shutil
import uuid
import pandas as pd
import structlog
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.config.settings import settings
from app.utils.file_validators import file_validator, security_validator, quality_validator
from app.core.error_handler import error_handler

logger = structlog.get_logger()


class FileUploadManager:
    """파일 업로드 관리자"""
    
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
        # 세션별 파일 저장소
        self.session_files: Dict[str, List[Dict[str, Any]]] = {}
        
        # 스레드 풀 (비동기 파일 처리용)
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        logger.info("FileUploadManager 초기화 완료", upload_dir=str(self.upload_dir))
    
    def create_session(self) -> str:
        """새 세션 생성"""
        session_id = str(uuid.uuid4())
        self.session_files[session_id] = []
        
        # 세션별 디렉토리 생성
        session_dir = self.upload_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        logger.info("새 파일 세션 생성", session_id=session_id)
        return session_id
    
    async def upload_file(self, file_path: str, original_filename: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        파일 업로드 처리
        
        Args:
            file_path: 임시 파일 경로
            original_filename: 원본 파일명
            session_id: 세션 ID (없으면 새로 생성)
            
        Returns:
            업로드 결과 정보
        """
        try:
            if not session_id:
                session_id = self.create_session()
            
            if session_id not in self.session_files:
                self.session_files[session_id] = []
            
            logger.info("파일 업로드 시작", 
                       filename=original_filename, 
                       session_id=session_id,
                       temp_path=file_path)
            
            # 1. 보안 검증
            security_valid, security_msg = security_validator.validate_security(file_path)
            if not security_valid:
                return {
                    'success': False,
                    'error': f'보안 검증 실패: {security_msg}',
                    'session_id': session_id
                }
            
            # 2. 파일 검증
            file_valid, file_msg, file_info = file_validator.validate_file(file_path)
            if not file_valid:
                return {
                    'success': False,
                    'error': f'파일 검증 실패: {file_msg}',
                    'session_id': session_id
                }
            
            # 3. 파일을 세션 디렉토리로 이동
            file_id = str(uuid.uuid4())
            extension = Path(original_filename).suffix.lower()
            safe_filename = f"{file_id}{extension}"
            
            session_dir = self.upload_dir / session_id
            target_path = session_dir / safe_filename
            
            # 파일 복사
            shutil.copy2(file_path, target_path)
            
            # 4. 데이터 로드 및 품질 분석
            df, load_error = await self._load_data_async(str(target_path))
            if load_error:
                return {
                    'success': False,
                    'error': f'데이터 로드 실패: {load_error}',
                    'session_id': session_id
                }
            
            data_quality = quality_validator.validate_data_quality(df)
            
            # 5. 파일 정보 기록
            file_record = {
                'file_id': file_id,
                'original_filename': original_filename,
                'safe_filename': safe_filename,
                'file_path': str(target_path),
                'upload_time': datetime.now().isoformat(),
                'file_info': file_info,
                'data_quality': data_quality,
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': df.columns.tolist(),
                'data_types': df.dtypes.astype(str).to_dict()
            }
            
            self.session_files[session_id].append(file_record)
            
            # 6. 임시 파일 정리
            try:
                os.unlink(file_path)
            except:
                pass  # 임시 파일 삭제 실패는 무시
            
            logger.info("파일 업로드 완료", 
                       file_id=file_id,
                       session_id=session_id,
                       rows=len(df),
                       cols=len(df.columns))
            
            return {
                'success': True,
                'message': '파일이 성공적으로 업로드되었습니다.',
                'session_id': session_id,
                'file_record': file_record,
                'preview_data': df.head(10).to_dict('records'),  # 미리보기용 처음 10행
                'data_summary': self._generate_data_summary(df, data_quality)
            }
            
        except Exception as e:
            app_error = error_handler.handle_error(e, "파일 업로드")
            logger.error("파일 업로드 실패", error=str(e))
            
            return {
                'success': False,
                'error': app_error.user_message,
                'session_id': session_id or 'unknown'
            }
    
    async def _load_data_async(self, file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """비동기로 데이터 로드"""
        loop = asyncio.get_event_loop()
        try:
            df = await loop.run_in_executor(self.executor, self._load_data_sync, file_path)
            return df, None
        except Exception as e:
            return None, str(e)
    
    def _load_data_sync(self, file_path: str) -> pd.DataFrame:
        """동기적으로 데이터 로드"""
        extension = Path(file_path).suffix.lower()
        
        if extension == '.csv':
            # CSV 파일 로드 (인코딩 자동 감지)
            try:
                return pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    return pd.read_csv(file_path, encoding='cp949')  # 한국어 CSV
                except UnicodeDecodeError:
                    return pd.read_csv(file_path, encoding='latin-1')
        
        elif extension in ['.xlsx', '.xls']:
            # Excel 파일 로드
            return pd.read_excel(file_path)
        
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {extension}")
    
    def _generate_data_summary(self, df: pd.DataFrame, quality_info: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 요약 정보 생성"""
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': len(df.select_dtypes(include=['number']).columns),
            'text_columns': len(df.select_dtypes(include=['object']).columns),
            'missing_values_total': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage_mb': quality_info.get('memory_usage_mb', 0),
            'quality_score': quality_info.get('quality_score', 0),
            'column_info': [
                {
                    'name': col,
                    'type': str(df[col].dtype),
                    'missing_count': df[col].isnull().sum(),
                    'unique_count': df[col].nunique()
                }
                for col in df.columns[:10]  # 처음 10개 컬럼만
            ]
        }
    
    def get_session_files(self, session_id: str) -> List[Dict[str, Any]]:
        """세션의 모든 파일 목록 반환"""
        return self.session_files.get(session_id, [])
    
    def get_file_data(self, session_id: str, file_id: str) -> Optional[pd.DataFrame]:
        """특정 파일의 데이터 반환"""
        try:
            files = self.session_files.get(session_id, [])
            for file_record in files:
                if file_record['file_id'] == file_id:
                    return self._load_data_sync(file_record['file_path'])
            return None
        except Exception as e:
            logger.error("파일 데이터 로드 실패", error=str(e))
            return None
    
    def delete_file(self, session_id: str, file_id: str) -> bool:
        """파일 삭제"""
        try:
            files = self.session_files.get(session_id, [])
            for i, file_record in enumerate(files):
                if file_record['file_id'] == file_id:
                    # 파일 시스템에서 삭제
                    file_path = file_record['file_path']
                    if os.path.exists(file_path):
                        os.unlink(file_path)
                    
                    # 메모리에서 제거
                    del files[i]
                    logger.info("파일 삭제 완료", file_id=file_id, session_id=session_id)
                    return True
            
            return False
        except Exception as e:
            logger.error("파일 삭제 실패", error=str(e))
            return False
    
    def clear_session(self, session_id: str) -> bool:
        """세션의 모든 파일 삭제"""
        try:
            if session_id in self.session_files:
                # 모든 파일 삭제
                for file_record in self.session_files[session_id]:
                    file_path = file_record['file_path']
                    if os.path.exists(file_path):
                        os.unlink(file_path)
                
                # 세션 디렉토리 삭제
                session_dir = self.upload_dir / session_id
                if session_dir.exists():
                    shutil.rmtree(session_dir)
                
                # 메모리에서 세션 제거
                del self.session_files[session_id]
                
                logger.info("세션 정리 완료", session_id=session_id)
                return True
            
            return False
        except Exception as e:
            logger.error("세션 정리 실패", error=str(e))
            return False
    
    def cleanup_old_files(self, hours: int = 24) -> int:
        """오래된 파일 자동 정리"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cleanup_count = 0
            
            sessions_to_remove = []
            for session_id, files in self.session_files.items():
                session_has_old_files = False
                
                for file_record in files:
                    upload_time = datetime.fromisoformat(file_record['upload_time'])
                    if upload_time < cutoff_time:
                        session_has_old_files = True
                        break
                
                if session_has_old_files:
                    sessions_to_remove.append(session_id)
            
            # 오래된 세션들 정리
            for session_id in sessions_to_remove:
                if self.clear_session(session_id):
                    cleanup_count += len(self.session_files.get(session_id, []))
            
            logger.info(f"오래된 파일 정리 완료", 
                       cleanup_count=cleanup_count, 
                       hours=hours)
            
            return cleanup_count
            
        except Exception as e:
            logger.error("파일 정리 실패", error=str(e))
            return 0


class UploadProgressTracker:
    """업로드 진행률 추적기"""
    
    def __init__(self):
        self.progress_data: Dict[str, Dict[str, Any]] = {}
    
    def start_upload(self, upload_id: str, filename: str, total_size: int) -> None:
        """업로드 시작"""
        self.progress_data[upload_id] = {
            'filename': filename,
            'total_size': total_size,
            'uploaded_size': 0,
            'progress_percent': 0,
            'status': 'uploading',
            'start_time': datetime.now(),
            'error': None
        }
    
    def update_progress(self, upload_id: str, uploaded_size: int) -> None:
        """진행률 업데이트"""
        if upload_id in self.progress_data:
            data = self.progress_data[upload_id]
            data['uploaded_size'] = uploaded_size
            data['progress_percent'] = min(100, (uploaded_size / data['total_size']) * 100)
    
    def complete_upload(self, upload_id: str, success: bool, error: Optional[str] = None) -> None:
        """업로드 완료"""
        if upload_id in self.progress_data:
            data = self.progress_data[upload_id]
            data['status'] = 'completed' if success else 'failed'
            data['progress_percent'] = 100 if success else data['progress_percent']
            data['end_time'] = datetime.now()
            data['error'] = error
    
    def get_progress(self, upload_id: str) -> Optional[Dict[str, Any]]:
        """진행률 조회"""
        return self.progress_data.get(upload_id)
    
    def cleanup_completed(self, max_age_minutes: int = 30) -> None:
        """완료된 업로드 기록 정리"""
        cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
        
        to_remove = []
        for upload_id, data in self.progress_data.items():
            if (data['status'] in ['completed', 'failed'] and 
                data.get('end_time', datetime.now()) < cutoff_time):
                to_remove.append(upload_id)
        
        for upload_id in to_remove:
            del self.progress_data[upload_id]


# 전역 서비스 인스턴스
file_upload_manager = FileUploadManager()
upload_progress_tracker = UploadProgressTracker()

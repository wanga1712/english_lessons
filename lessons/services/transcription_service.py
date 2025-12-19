import os
import logging
import whisper
import ffmpeg
from django.conf import settings

logger = logging.getLogger(__name__)


class TranscriptionService:
    def __init__(self, model_name=None):
        self.model_name = model_name or settings.WHISPER_MODEL
        self.model = None
        self.device = None
        self._load_model()
    
    def _load_model(self):
        try:
            import torch
            # #region agent log
            import json
            log_data = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'GPU_DETECTION',
                'location': 'transcription_service.py:17',
                'message': 'Проверка доступности GPU',
                'data': {'torch_available': True},
                'timestamp': int(__import__('time').time() * 1000)
            }
            with open(r'c:\Users\wangr\PycharmProjects\pythonProject94\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + '\n')
            # #endregion
            
            # Автоматическое определение GPU/CPU с детальной проверкой
            use_gpu = False
            gpu_name = None
            
            if torch.cuda.is_available():
                try:
                    gpu_name = torch.cuda.get_device_name(0)
                    gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
                    # Проверяем, достаточно ли памяти на GPU (минимум 2GB)
                    if gpu_memory >= 2.0:
                        use_gpu = True
                        # #region agent log
                        log_data = {
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'GPU_DETECTION',
                            'location': 'transcription_service.py:35',
                            'message': 'GPU доступен и имеет достаточно памяти',
                            'data': {'gpu_name': gpu_name, 'gpu_memory_gb': round(gpu_memory, 2)},
                            'timestamp': int(__import__('time').time() * 1000)
                        }
                        with open(r'c:\Users\wangr\PycharmProjects\pythonProject94\.cursor\debug.log', 'a', encoding='utf-8') as f:
                            f.write(json.dumps(log_data, ensure_ascii=False) + '\n')
                        # #endregion
                    else:
                        logger.warning(f'GPU доступен, но памяти недостаточно ({gpu_memory:.2f} GB). Используется CPU.')
                        # #region agent log
                        log_data = {
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'GPU_DETECTION',
                            'location': 'transcription_service.py:45',
                            'message': 'GPU доступен, но памяти недостаточно',
                            'data': {'gpu_memory_gb': round(gpu_memory, 2), 'min_required_gb': 2.0},
                            'timestamp': int(__import__('time').time() * 1000)
                        }
                        with open(r'c:\Users\wangr\PycharmProjects\pythonProject94\.cursor\debug.log', 'a', encoding='utf-8') as f:
                            f.write(json.dumps(log_data, ensure_ascii=False) + '\n')
                        # #endregion
                except Exception as gpu_error:
                    logger.warning(f'Ошибка при проверке GPU: {gpu_error}. Используется CPU.')
                    # #region agent log
                    log_data = {
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'GPU_DETECTION',
                        'location': 'transcription_service.py:55',
                        'message': 'Ошибка при проверке GPU',
                        'data': {'error': str(gpu_error)},
                        'timestamp': int(__import__('time').time() * 1000)
                    }
                    with open(r'c:\Users\wangr\PycharmProjects\pythonProject94\.cursor\debug.log', 'a', encoding='utf-8') as f:
                        f.write(json.dumps(log_data, ensure_ascii=False) + '\n')
                    # #endregion
            
            self.device = 'cuda' if use_gpu else 'cpu'
            
            if use_gpu:
                logger.info(f'✅ Используется CUDA (GPU): {gpu_name} ({gpu_memory:.2f} GB)')
            else:
                logger.info('ℹ️ Используется CPU для транскрипции')
            
            # #region agent log
            log_data = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'GPU_DETECTION',
                'location': 'transcription_service.py:70',
                'message': 'Загрузка модели Whisper',
                'data': {'device': self.device, 'model_name': self.model_name},
                'timestamp': int(__import__('time').time() * 1000)
            }
            with open(r'c:\Users\wangr\PycharmProjects\pythonProject94\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + '\n')
            # #endregion
            
            self.model = whisper.load_model(self.model_name, device=self.device)
            logger.info(f'Модель Whisper "{self.model_name}" загружена на устройство: {self.device}')
            
            # #region agent log
            log_data = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'GPU_DETECTION',
                'location': 'transcription_service.py:80',
                'message': 'Модель успешно загружена',
                'data': {'device': self.device, 'model_name': self.model_name},
                'timestamp': int(__import__('time').time() * 1000)
            }
            with open(r'c:\Users\wangr\PycharmProjects\pythonProject94\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + '\n')
            # #endregion
        except Exception as e:
            logger.error(f'Ошибка загрузки модели Whisper: {str(e)}', exc_info=True)
            # #region agent log
            log_data = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'GPU_DETECTION',
                'location': 'transcription_service.py:90',
                'message': 'Ошибка загрузки модели',
                'data': {'error': str(e)},
                'timestamp': int(__import__('time').time() * 1000)
            }
            with open(r'c:\Users\wangr\PycharmProjects\pythonProject94\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + '\n')
            # #endregion
            raise Exception(f'Ошибка загрузки модели Whisper: {str(e)}')
    
    def extract_audio_from_video(self, video_path, output_audio_path):
        try:
            file_size = os.path.getsize(video_path) if os.path.exists(video_path) else 0
            file_size_mb = file_size / (1024 * 1024)
            logger.info('Размер видеофайла: %.2f MB', file_size_mb)
            ffmpeg_binary = getattr(settings, 'FFMPEG_BINARY', 'ffmpeg')
            logger.info('Запуск FFmpeg для извлечения аудио...')
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                output_audio_path,
                acodec='pcm_s16le',
                ac=1,
                ar='16k',
            )
            ffmpeg.run(stream, cmd=ffmpeg_binary, overwrite_output=True, quiet=True)
            logger.info('Аудио успешно извлечено: %s', output_audio_path)
        except Exception as e:
            logger.error('Ошибка извлечения аудио: %s', str(e), exc_info=True)
            raise Exception(f'Ошибка извлечения аудио: {str(e)}')
    
    def transcribe(self, video_path):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f'Видеофайл не найден: {video_path}')
        temp_audio_dir = settings.TEMP_AUDIO_DIRECTORY
        os.makedirs(temp_audio_dir, exist_ok=True)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_path = os.path.join(temp_audio_dir, f'{video_name}.wav')
        try:
            logger.info('Извлечение аудио из видео: %s', video_path)
            self.extract_audio_from_video(video_path, audio_path)
            logger.info('Аудио извлечено: %s', audio_path)
            import time
            audio_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
            audio_size_mb = audio_size / (1024 * 1024)
            logger.info('Начало транскрипции аудио: %s (размер: %.2f MB)', audio_path, audio_size_mb)
            if audio_size_mb > 100:
                logger.warning('ВНИМАНИЕ: Аудиофайл очень большой (%.2f MB). Транскрипция может занять много времени (10-30+ минут на CPU).', audio_size_mb)
            elif audio_size_mb > 50:
                logger.warning('Аудиофайл большой (%.2f MB). Транскрипция может занять несколько минут.', audio_size_mb)
            start_time = time.time()
            logger.info('Запуск модели Whisper для транскрипции...')
            import torch
            if self.device == 'cuda':
                logger.info('Используется GPU (CUDA) - транскрипция будет быстрой')
            else:
                logger.info('Используется CPU - транскрипция может занять много времени. Пожалуйста, подождите...')
            result = self.model.transcribe(
                audio_path,
                language=None,
                task='transcribe',
                verbose=True,
                fp16=torch.cuda.is_available()
            )
            elapsed_time = time.time() - start_time
            logger.info('Транскрипция завершена за %.2f секунд (%.2f минут)', elapsed_time, elapsed_time / 60)
            if elapsed_time > 300 and self.device == 'cpu':
                logger.warning('Транскрипция заняла %.2f минут - это нормально для больших файлов на CPU', elapsed_time / 60)
            elif self.device == 'cuda':
                logger.info('Транскрипция выполнена на GPU - скорость значительно выше, чем на CPU')
            transcript_text = result['text'].strip()
            if os.path.exists(audio_path):
                os.remove(audio_path)
            return transcript_text
        except Exception as e:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            raise Exception(f'Ошибка транскрипции: {str(e)}')

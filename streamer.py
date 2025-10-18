
import subprocess
import threading
import yt_dlp
from PyQt6.QtCore import QObject, pyqtSignal
from config import _

class Streamer(QObject):
    log_message = pyqtSignal(str)
    stream_started = pyqtSignal()
    stream_stopped = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.streaming_process = None

    def start_streaming(self, stream_source: str, server_url: str, stream_key: str):
        self.log_message.emit(_("Starting stream..."))

        input_source = stream_source

        if stream_source.startswith("http"):
            try:
                self.log_message.emit(_("Fetching YouTube stream URL..."))
                ydl_opts = {
                    'format': 'best[ext=mp4]/best',
                    'quiet': True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(stream_source, download=False)
                    input_source = info['url']
                self.log_message.emit(_("Successfully fetched stream URL."))
            except Exception as e:
                self.log_message.emit(_(f"[ERROR] Failed to get YouTube stream URL: {e}"))
                self.stream_stopped.emit()
                return

        full_rtmp_url = f"{server_url}/{stream_key}"
        
        command = [
            "ffmpeg",
        ]

        if not stream_source.startswith("http") or "youtube.com" in stream_source or "youtu.be" in stream_source:
            command.extend(["-stream_loop", "-1"])

        command.extend([
            "-i", input_source,
            "-vcodec", "libx264",
            "-r", "30",
            "-g", "60",
            "-b:v", "10M",
            "-acodec", "aac",
            "-b:a", "128k",
            "-f", "flv",
            full_rtmp_url,
        ])

        try:
            self.streaming_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            self.log_message.emit(_(f"Streaming started with PID: {self.streaming_process.pid}"))
            self.stream_started.emit()

            thread = threading.Thread(
                target=self._stream_ffmpeg_output,
                args=(self.streaming_process,),
                daemon=True
            )
            thread.start()

        except FileNotFoundError:
            self.log_message.emit(_("[ERROR] ffmpeg not found. Check if it's installed and in PATH."))
            self.stream_stopped.emit()
        except Exception as e:
            self.log_message.emit(_(f"[ERROR] Failed to start ffmpeg: {e}"))
            self.stream_stopped.emit()

    def _stream_ffmpeg_output(self, process: subprocess.Popen):
        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                self.log_message.emit(line.strip())
            process.stdout.close()
        self.stream_stopped.emit()

    def stop_streaming(self):
        if self.streaming_process and self.streaming_process.poll() is None:
            self.log_message.emit(_("Stopping stream..."))
            self.streaming_process.terminate()
            try:
                self.streaming_process.wait(timeout=5)
                self.log_message.emit(_("Stream stopped successfully."))
            except subprocess.TimeoutExpired:
                self.log_message.emit(_("ffmpeg did not respond, forcing termination."))
                self.streaming_process.kill()
                self.log_message.emit(_("Stream forced to stop."))
            finally:
                self.streaming_process = None
        else:
            self.log_message.emit(_("No active stream to stop."))

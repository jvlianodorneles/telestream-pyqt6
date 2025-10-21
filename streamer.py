
import yt_dlp
from PyQt6.QtCore import QObject, pyqtSignal, QProcess

class Streamer(QObject):
    log_message = pyqtSignal(str)
    stream_started = pyqtSignal()
    stream_stopped = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.streaming_process = None

    def start_streaming(self, stream_source: str, server_url: str, stream_key: str, is_rpi: bool = False, loop_mode: str = "Loop Infinitely", quality_preset: str = "Source Quality"):
        self.log_message.emit("Starting stream...")

        input_source = stream_source
        is_local_file = not stream_source.startswith("http")

        if not is_local_file:
            try:
                self.log_message.emit("Fetching YouTube stream URL...")
                ydl_opts = {
                    'format': 'best[ext=mp4]/best',
                    'quiet': True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(stream_source, download=False)
                    input_source = info['url']
                self.log_message.emit("Successfully fetched stream URL.")
            except Exception as e:
                self.log_message.emit(f"[ERROR] Failed to get YouTube stream URL: {e}")
                self.stream_stopped.emit()
                return

        full_rtmp_url = f"{server_url}/{stream_key}"
        
        vcodec = "h264_v4l2m2m" if is_rpi else "libx264"
        
        command = [
            "ffmpeg",
        ]

        if is_local_file and loop_mode == "Loop Infinitely":
            command.extend(["-stream_loop", "-1"])

        command.extend([
            "-i", input_source,
            "-vcodec", vcodec,
            "-r", "30",
            "-g", "60",
        ])

        quality_params = {
            "1080p (5 Mbps)": ["-s", "1920x1080", "-b:v", "5M"],
            "720p (3 Mbps)": ["-s", "1280x720", "-b:v", "3M"],
            "480p (1.5 Mbps)": ["-s", "854x480", "-b:v", "1.5M"],
        }

        if quality_preset in quality_params:
            command.extend(quality_params[quality_preset])

        command.extend([
            "-acodec", "aac",
            "-b:a", "128k",
            "-f", "flv",
            full_rtmp_url,
        ])

        self.streaming_process = QProcess()
        self.streaming_process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        
        self.streaming_process.readyReadStandardOutput.connect(self.handle_stdout)
        self.streaming_process.finished.connect(self.handle_finished)
        self.streaming_process.errorOccurred.connect(self.handle_error)

        self.streaming_process.start("ffmpeg", command[1:])
        
        if self.streaming_process.waitForStarted():
            self.log_message.emit(f"Streaming started with PID: {self.streaming_process.processId()}")
            self.stream_started.emit()
        else:
            self.log_message.emit("[ERROR] Failed to start ffmpeg. Check if it's installed and in PATH.")
            self.stream_stopped.emit()

    def handle_stdout(self):
        data = self.streaming_process.readAllStandardOutput()
        try:
            message = data.data().decode('utf-8', errors='replace').strip()
            if message:
                self.log_message.emit(message)
        except Exception:
            # This can happen if there are decoding issues with partial data
            pass

    def handle_finished(self):
        self.log_message.emit("Stream process finished.")
        self.stream_stopped.emit()
        self.streaming_process = None

    def handle_error(self, error: QProcess.ProcessError):
        error_map = {
            QProcess.ProcessError.FailedToStart: "Failed to start",
            QProcess.ProcessError.Crashed: "Crashed",
            QProcess.ProcessError.Timedout: "Timed out",
            QProcess.ProcessError.ReadError: "Read error",
            QProcess.ProcessError.WriteError: "Write error",
            QProcess.ProcessError.UnknownError: "Unknown error",
        }
        self.log_message.emit(f"[ERROR] Process error: {error_map.get(error, 'Unknown error')}")
        self.stream_stopped.emit()
        self.streaming_process = None

    def stop_streaming(self):
        if self.streaming_process and self.streaming_process.state() == QProcess.ProcessState.Running:
            self.log_message.emit("Stopping stream...")
            self.streaming_process.terminate()
            if not self.streaming_process.waitForFinished(5000):
                self.log_message.emit("ffmpeg did not respond, forcing termination.")
                self.streaming_process.kill()
            self.log_message.emit("Stream stopped.")
        else:
            self.log_message.emit("No active stream to stop.")

import os
import ffmpeg
from typing import List, Tuple, Dict

class VideoProcessor:
    def __init__(self):
        self.supported_formats = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm')

    def get_video_info(self, file_path: str) -> Dict:
        """获取视频文件的信息"""
        try:
            probe = ffmpeg.probe(file_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            
            width = int(video_info['width'])
            height = int(video_info['height'])
            fps_str = video_info.get('r_frame_rate', '0/1')
            fps = eval(fps_str) if '/' in fps_str else float(fps_str)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            return {
                'width': width,
                'height': height,
                'fps': fps,
                'size_mb': file_size_mb,
                'path': file_path,
                'filename': os.path.basename(file_path)
            }
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None

    def scan_directory(self, directory: str) -> List[Dict]:
        """扫描目录下的所有视频文件"""
        video_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(self.supported_formats):
                    file_path = os.path.join(root, file)
                    video_info = self.get_video_info(file_path)
                    if video_info:
                        video_files.append(video_info)
        return video_files

    def filter_videos(self, videos: List[Dict], conditions: Dict) -> List[Dict]:
        """根据条件筛选视频"""
        filtered_videos = []
        logic = conditions.get('logic', 'AND')
        
        for video in videos:
            matches = []
            
            # 检查分辨率
            if conditions.get('width') and conditions.get('height'):
                matches.append(
                    video['width'] >= conditions['width'] and 
                    video['height'] >= conditions['height']
                )
            
            # 检查帧率
            if conditions.get('fps'):
                matches.append(video['fps'] >= conditions['fps'])
            
            # 检查文件大小
            if conditions.get('size_mb'):
                matches.append(video['size_mb'] >= conditions['size_mb'])
            
            # 根据逻辑运算符判断
            if logic == 'AND':
                if all(matches):
                    filtered_videos.append(video)
            else:  # OR
                if any(matches):
                    filtered_videos.append(video)
        
        return filtered_videos

    def delete_video(self, file_path: str) -> bool:
        """删除视频文件"""
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
            return False

    def move_to_recycle_bin(self, file_path: str) -> bool:
        """将视频文件移动到回收站"""
        try:
            from send2trash import send2trash
            send2trash(file_path)
            return True
        except Exception as e:
            print(f"Error moving {file_path} to recycle bin: {e}")
            return False 
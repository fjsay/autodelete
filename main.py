import os
import shutil
import time
from pathlib import Path

# ====== 配置区 ======
# 需要监控的文件夹路径
FOLDER_PATH = os.environ.get('FOLDER_PATH', 'file')
# 空间阈值（单位：MB）
THRESHOLD_MB = int(os.environ.get('THRESHOLD_MB', 500))  # 可根据需要修改
# 检查间隔（秒），即每隔多少秒检查一次空间
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', 60))
# ====================

def get_free_space_mb(folder):
    """获取文件夹所在磁盘的剩余空间（MB）"""
    total, used, free = shutil.disk_usage(folder)
    return free // (1024 * 1024)

def get_oldest_file_recursive(folder):
    """递归获取文件夹及其子文件夹下最早的文件路径，并打印所有文件及其创建时间"""
    files = []
    for root, _, filenames in os.walk(folder):
        for filename in filenames:
            filepath = Path(root) / filename
            ctime = filepath.stat().st_ctime
            print(f'文件: {filepath}, 创建时间: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ctime))}')
            files.append(filepath)
    if not files:
        return None
    oldest = min(files, key=lambda f: f.stat().st_ctime)
    return oldest

def auto_delete_until_enough_space(folder, threshold_mb):
    while get_free_space_mb(folder) < threshold_mb:
        oldest_file = get_oldest_file_recursive(folder)
        if oldest_file is None:
            print('文件夹及子文件夹已空，无法继续删除。')
            break
        print(f'空间不足，删除最早的文件: {oldest_file}')
        try:
            os.remove(oldest_file)
            # 删除完文件后，递归删除所有空的父文件夹（不删除根监控目录）
            parent = oldest_file.parent
            while parent != Path(folder):
                if not any(parent.iterdir()):
                    print(f'删除空文件夹: {parent}')
                    parent.rmdir()
                    parent = parent.parent
                else:
                    break
            # 删除后立即判断空间是否充足
            free_mb = get_free_space_mb(folder)
            print(f'删除后剩余空间: {free_mb} MB')
            if free_mb >= threshold_mb:
                print('空间已充足，停止删除。')
                break
        except Exception as e:
            print(f'删除失败: {oldest_file}, 错误: {e}')
        time.sleep(1)  # 防止过快删除

def main():
    folder = FOLDER_PATH
    threshold_mb = THRESHOLD_MB
    while True:
        free_mb = get_free_space_mb(folder)
        print(f'当前剩余空间: {free_mb} MB')
        if free_mb < threshold_mb:
            auto_delete_until_enough_space(folder, threshold_mb)
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
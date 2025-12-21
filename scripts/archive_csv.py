import os
import shutil
from datetime import datetime

def archive_csv_files():
    """
    データディレクトリ内の CSV ファイルを archive フォルダへ移動する。
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    archive_dir = os.path.join(data_dir, 'archive')

    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        print(f"Created archive directory: {archive_dir}")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found to archive.")
        return

    for filename in csv_files:
        src = os.path.join(data_dir, filename)
        # タイムスタンプを付与して移動
        name, ext = os.path.splitext(filename)
        dst_filename = f"{name}_{timestamp}{ext}"
        dst = os.path.join(archive_dir, dst_filename)
        
        shutil.move(src, dst)
        print(f"Archived: {filename} -> archive/{dst_filename}")

if __name__ == '__main__':
    archive_csv_files()

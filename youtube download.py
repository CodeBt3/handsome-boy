import ssl

ssl._create_default_https_context = ssl._create_stdlib_context

import os

# os.chdir('/content/drive/MyDrive/Colab Notebooks')  # 使用 Colab 要換路徑使用

try:
    from yt_dlp import YoutubeDL

    print('使用 yt-dlp 下載...')

    # 設定下載選項
    ydl_opts = {
        'format': 'best[ext=mp4]',  # 下載最佳 MP4 格式
        'outtmpl': 'Don′t do That.mp4',  # 輸出檔案名稱
    }

    # 下載影片
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(['https://www.youtube.com/watch?v=Bfn3BMV3LOQ&list=RDMMBfn3BMV3LOQ&start_radio=1'])

    print('下載完成！')

except ImportError:
    print('yt-dlp 未安裝，正在安裝...')
    import subprocess
    import sys

    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'yt-dlp'])
        print('安裝完成，請重新執行程式')
    except subprocess.CalledProcessError:
        print('安裝失敗，請手動執行: pip install yt-dlp')
        print('或者使用 pytube 的修復版本: pip install --upgrade pytube')
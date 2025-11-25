# 1. 屏蔽 Pydub 在 Python 3.12 下的语法警告 (放在所有 import 之前)
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

import asyncio
import edge_tts
import pygame
import os
import sys
import random
from pydub import AudioSegment

# ================= 配置区域 =================
VOICE = "ja-JP-NanamiNeural" 
RATE = "-10%" 
EXPORT_PAUSE_MS = 2000          # 停顿时间 (毫秒)
CONCURRENCY_LIMIT = 5           # 并发数
TEMP_DIR = "temp_audio_files"   # 临时文件夹，避免文件乱放
# ===========================================

def load_lines(file_path):
    """读取文件，清洗数据"""
    valid_lines = []
    if not os.path.exists(file_path):
        print(f"❌ 错误：找不到文件 {file_path}")
        sys.exit(1)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                valid_lines.append(stripped)
    return valid_lines

async def worker_download(sem, text, index):
    """
    下载单个单词 (纯文本模式，绝无 SSML 问题)
    """
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR, exist_ok=True)
        
    filename = os.path.join(TEMP_DIR, f"word_{index}.mp3")
    
    # 简单的重试机制
    for attempt in range(3):
        async with sem:
            try:
                # 纯文本请求，不使用任何 XML/SSML 标签
                communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
                await communicate.save(filename)
                
                # 验证文件是否下载成功 (防止空文件)
                if os.path.exists(filename) and os.path.getsize(filename) > 500:
                    return (index, True, filename)
                else:
                    # 如果文件太小，视为失败，重试
                    pass 
            except Exception as e:
                print(f"⚠️ [索引{index}] 下载异常: {e}")
            
            # 失败等待
            await asyncio.sleep(1)

    return (index, False, None)

async def export_full_audio(lines, output_filename):
    total = len(lines)
    print(f"🚀 启动无 SSML 纯净模式 (并发: {CONCURRENCY_LIMIT})")
    print(f"⏳ 正在初始化本地静音片段 ({EXPORT_PAUSE_MS}ms)...")
    
    # 【核心 1】在内存中生成静音，完全不需要联网，也不会报错
    try:
        silence_segment = AudioSegment.silent(duration=EXPORT_PAUSE_MS)
        combined_audio = AudioSegment.empty()
    except Exception as e:
        print(f"\n❌ Pydub 初始化失败: {e}")
        print("💡 提示: 请检查是否安装了 FFmpeg (Windows需配置环境变量)")
        return

    # 【核心 2】并发下载单词
    print(f"⬇️  开始下载 {total} 个单词...")
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)
    tasks = [worker_download(sem, line, i) for i, line in enumerate(lines)]
    results = await asyncio.gather(*tasks)

    print(f"\n🔨 下载完成，正在进行音频拼接与重采样...")

    # 【核心 3】使用 Pydub 拼接
    # 这一步非常重要，它会自动对齐采样率，避免直接二进制合并产生的爆音或变调
    success_count = 0
    
    for index, success, filename in results:
        if success and filename:
            try:
                # 读取下载好的单词
                word_segment = AudioSegment.from_mp3(filename)
                # 拼接: 单词 + 静音
                combined_audio += word_segment + silence_segment
                success_count += 1
            except Exception as e:
                print(f"❌ 拼接第 {index+1} 行失败: {e}")
            finally:
                # 清理临时文件
                if os.path.exists(filename):
                    os.remove(filename)
        else:
            print(f"⚠️ 跳过第 {index+1} 行 (下载失败)")

    # 删除临时目录
    if os.path.exists(TEMP_DIR):
        try:
            os.rmdir(TEMP_DIR)
        except:
            pass

    print(f"💾 正在导出最终 MP3...")
    combined_audio.export(output_filename, format="mp3")
    print(f"\n🎉 成功！文件已保存: {output_filename}")
    print(f"📊 统计: 共 {total} 行，成功合并 {success_count} 行")

# --- 交互模式 (保持轻量化) ---
async def play_text(text):
    temp_file = "temp_interactive_play.mp3"
    try:
        communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
        await communicate.save(temp_file)
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"播放错误: {e}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

async def interactive_dictation(lines):
    print(f"\n🚀 开始交互听写 (共 {len(lines)} 行)...")
    pygame.init()
    pygame.mixer.init()
    for i, text in enumerate(lines):
        print(f"\n[{i+1}/{len(lines)}] 🎧 {text}")
        await play_text(text)
        cmd = input("👉 回车继续 / r重听 / q退出: ").strip().lower()
        if cmd == 'q': break
        elif cmd == 'r': await play_text(text)
    pygame.mixer.quit()

def main_menu():
    if len(sys.argv) < 2:
        print("用法: python jp_dictation_final.py <单词表.txt>")
        return
    file_path = sys.argv[1]
    lines = load_lines(file_path)
    
    if input("🔀 是否打乱顺序? (y/n): ").strip().lower() == 'y':
        random.shuffle(lines)

    mode = input("\n[1] 交互听写\n[2] 导出音频 (推荐)\n请选择: ").strip()
    if mode == '1':
        asyncio.run(interactive_dictation(lines))
    elif mode == '2':
        out_name = file_path.replace(".txt", "_final.mp3")
        asyncio.run(export_full_audio(lines, out_name))

if __name__ == "__main__":
    main_menu()

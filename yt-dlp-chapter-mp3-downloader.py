import os
import subprocess
from yt_dlp import YoutubeDL
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from threading import Thread
from time import sleep
import re
def format_seconds(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hrs}:{mins:02}:{secs:02}"

def log(msg):
    output_box.insert(END, msg + '\n')
    output_box.see(END)

def set_status(msg, color="black"):
    status_var.set(msg)
    status_label.config(fg=color)

def get_video_info(url):
    ydl_opts = {'quiet': True}
    with YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def download_audio_real_progress(url):
    def run_download():
        set_status("🔽 Ses indiriliyor...", "blue")
        progress_var.set(0)
        progress_label_var.set("0%")

        def my_hook(d):
            if d['status'] == 'downloading':
                p = d.get('_percent_str', '0.0%').strip().replace('%', '')
                try:
                    progress = float(p)
                    progress_var.set(progress)
                    progress_label_var.set(f"{int(progress)}%")
                except:
                    pass
            elif d['status'] == 'finished':
                progress_var.set(100)
                progress_label_var.set("100%")
                log("✅ İndirme tamamlandı.")

        ydl_opts = {
            'format': 'ba[ext=m4a]/bestaudio/best',
            'outtmpl': 'full_audio.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [my_hook],
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        set_status("✅ Ses indirildi", "green")

    Thread(target=run_download).start()

def get_downloaded_filename():
    for ext in ["m4a", "webm"]:
        if os.path.exists(f"full_audio.{ext}"):
            return f"full_audio.{ext}"
    return None

def extract_audio_segment(start, end, title, source_file, index, output_dir):
    safe_title = title.replace("/", "-").replace("\\", "-").strip()
    output = os.path.join(output_dir, f"{index:02d} - {safe_title}.mp3")

    cmd = [
        "ffmpeg", "-y", "-i", source_file,
        "-ss", start,
        *(["-to", end] if end else []),
        "-vn", "-acodec", "libmp3lame", "-ar", "44100", "-b:a", "128k", "-ac", "2",
        output
    ]

    log(f"🎵 Bölüm: {index:02d} - {title}")

    def time_to_seconds(t):
        parts = t.split(":")
        parts = list(map(float, parts[::-1])) 
        seconds = parts[0] + parts[1]*60 + (parts[2]*3600 if len(parts)>2 else 0)
        return seconds

    duration = None
    if end:
        duration = time_to_seconds(end) - time_to_seconds(start)
    else:
        duration = 60

    pattern = re.compile(r'time=(\d+:\d+:\d+\.\d+)')
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    while True:
        line = process.stderr.readline()
        if not line:
            break
        
        match = pattern.search(line)
        if match:
            current_time = match.group(1)
            current_sec = time_to_seconds(current_time)
            progress = min(100, (current_sec / duration) * 100)
            progress_var.set(progress)
            progress_label_var.set(f"{int(progress)}%")
            root.update_idletasks()

    process.wait()

    if os.path.exists(output):
        size = os.path.getsize(output)
        log(f"    🎧 Kaydedildi: {size / 1024:.1f} KB")
    else:
        log("    ❌ Hata: Dosya oluşturulamadı!")

   
    progress_var.set(0)
    progress_label_var.set("")
    safe_title = title.replace("/", "-").replace("\\", "-").strip()
    output = os.path.join(output_dir, f"{index:02d} - {safe_title}.mp3")
    cmd = [
        "ffmpeg", "-y", "-i", source_file,
        "-ss", start, *(["-to", end] if end else []),
        "-vn", "-acodec", "libmp3lame", "-ar", "44100", "-b:a", "128k", "-ac", "2", output
    ]
    log(f"🎵 Bölüm: {index:02d} - {title}")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(output):
        size = os.path.getsize(output)
        log(f"    🎧 Kaydedildi: {size / 1024:.1f} KB")
    else:
        log("    ❌ Hata: Dosya oluşturulamadı!")

def wait_for_download_completion():
    
    while progress_var.get() < 100:
        sleep(0.2)

def process_video(url, output_dir):
    try:
        set_status("📋 Video bilgisi alınıyor...", "blue")
        info = get_video_info(url)

        if not info.get("chapters"):
            set_status("❌ Chapter bulunamadı.", "red")
            messagebox.showerror("Hata", "Video içinde chapter bulunamadı.")
            return

        chapters = info["chapters"]

    
        download_audio_real_progress(url)

   
        wait_for_download_completion()

        source_file = get_downloaded_filename()
        if not source_file:
            set_status("❌ Ses dosyası bulunamadı.", "red")
            messagebox.showerror("Hata", "Ses dosyası bulunamadı!")
            return

        for idx, chapter in enumerate(chapters, 1):
            start = format_seconds(chapter["start_time"])
            end = format_seconds(chapter["end_time"]) if "end_time" in chapter else None
            title = chapter["title"]
            extract_audio_segment(start, end, title, source_file, idx, output_dir)
            sleep(0.1)

        set_status("✅ Tüm bölümler oluşturuldu.", "green")
        messagebox.showinfo("Başarılı", "Tüm bölümler başarıyla oluşturuldu!")

    except Exception as e:
        set_status(f"💥 Hata: {e}", "red")
        messagebox.showerror("Hata", f"Bir hata oluştu:\n{e}")

def start_process():
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Hata", "Lütfen bir YouTube linki girin.")
        return

    output_dir = filedialog.askdirectory(title="Kayıt klasörü seçin")
    if not output_dir:
        return

    output_box.delete('1.0', END)
    set_status("🚀 Başlatılıyor...", "blue")
    thread = Thread(target=process_video, args=(url, output_dir))
    thread.start()


root = Tk()
root.title("🎬 YouTube Chapter MP3 Dönüştürücü")
root.geometry("700x600")
root.configure(bg="#f4f4f4")

Label(root, text="🎧 YouTube Chapter MP3 Dönüştürücü", font=("Arial", 18, "bold"), bg="#f4f4f4").pack(pady=10)
Label(root, text="YouTube linki girin. Video chapter içeriyorsa otomatik mp3'e bölünür.", font=("Arial", 11), bg="#f4f4f4", fg="gray").pack()

frame = Frame(root, bg="#f4f4f4")
frame.pack(pady=10)
url_entry = Entry(frame, width=60, font=("Arial", 12))
url_entry.pack(side="left", padx=5)
Button(frame, text="Dönüştür", command=start_process, bg="#4CAF50", fg="white", font=("Arial", 11, "bold")).pack(side="left")

status_var = StringVar()
status_label = Label(root, textvariable=status_var, font=("Arial", 11, "bold"), bg="#f4f4f4", fg="blue")
status_label.pack(pady=5)

progress_var = DoubleVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate", variable=progress_var)
progress_bar.pack(pady=5)

progress_label_var = StringVar()
progress_label = Label(root, textvariable=progress_label_var, bg="#f4f4f4", font=("Arial", 10, "bold"))
progress_label.pack(pady=2)

output_box = Text(root, height=20, width=90, font=("Courier", 10), bg="white")
output_box.pack(pady=10)
scrollbar = Scrollbar(root, command=output_box.yview)
output_box.config(yscrollcommand=scrollbar.set)
scrollbar.place(in_=output_box, relx=1.0, rely=0, relheight=1.0, anchor='ne')

root.mainloop()

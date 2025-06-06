import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import threading
import os
import platform

#Version
APP_NAME = "Youtube Downloader"
APP_VERSION = "v1.0.0"

#Globel Variables
available_formats = []
video_info = None

#Main Window
window = tk.Tk()
window.title(f"{APP_NAME}  {APP_VERSION}")
window.geometry("600x400")
window.resizable(False,False)

#Create main content frame (with left and right padding）
main_frame = tk.Frame(window)
main_frame.pack(fill="both", expand=True, padx=40, pady=20)

# --------- YouTube URL Input ---------
#InputURL_Label
label_url = tk.Label(main_frame, text="Input YouTube video URL:", anchor="w")
label_url.pack(fill="x")

#frame
frame_url = tk.Frame(main_frame)
frame_url.pack(fill="x", pady=(0,5))

#Url_TextBox
entry_url = tk.Entry(frame_url)
entry_url.pack(side=tk.LEFT, padx=(0,5), expand=True, fill="x")

#def: click "get Formats button"
def fetch_formats():
    url = entry_url.get()
    if not url:
        messagebox.showwarning("Error", "Please enter a URL")
        return
    
    listbox_format.delete(0, tk.END)
    status_text.set("Analyzing video formats...")
    progress_bar["value"] = 0

    #def: start to get the video info
    def _fetch():

        global available_formats
        global video_info

        try:
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'forcejson': True,
                'simulate': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url,download=False)
                video_info = info
                formats = info.get('formats',[])
                
                available_formats = [
                    f for f in formats
                    if f.get("vcodec") != "none" and
                    f.get("acodec") == "none"  #video only
                    and f.get("filesize")
                ]

                for fmt in available_formats:
                    resolution = fmt.get("format_note") or f"{fmt.get('height')}p"
                    size = round(fmt.get("filesize",0) / 1024 /1024, 2)
                    ext = fmt.get("ext")
                    listbox_format.insert(tk.END, f"{resolution} - {ext} - {size}MB")

                status_text.set("Please select video quality, format, and download...")

        except Exception as e:
                messagebox.showerror("ERROR",f"Fail to retrieve video formats\n{e}")
                status_text.set("An error occurred")

    threading.Thread(target=_fetch).start()


#CheckURL_Button
button_fetch = tk.Button(frame_url, text="Get Formats", command=fetch_formats, width="15")
button_fetch.pack(side=tk.RIGHT)

# --------- Video Quality Selection ---------
#SelectVideoDP_Label
label_format = tk.Label(main_frame, text="Select video quality and format:", anchor="w")
label_format.pack(fill="x")

#VideDP_Listbox
listbox_format = tk.Listbox(main_frame, height=5, width=60)
listbox_format.pack(fill="x")

# --------- mp4 or mp3 Format Selection ---------
#frame
frame_format = tk.Frame(main_frame)
frame_format.pack(pady=10, fill="x")

#Type_Radio
format_var = tk.StringVar(value="mp4") 
radio_mp4 = tk.Radiobutton(frame_format, text="MP4", variable=format_var, value="mp4")
radio_mp3 = tk.Radiobutton(frame_format, text="MP3", variable=format_var, value="mp3")

radio_mp4.pack(side=tk.LEFT, padx=(0,10))
radio_mp3.pack(side=tk.LEFT)

# --------- Save Location Selection ---------
#frame
frame_path = tk.Frame(main_frame)
frame_path.pack(pady=10, fill="x")

#SavePath_Label
label_path = tk.Label(frame_path, text="Save to:", anchor="w")
label_path.pack(fill="x")

#SavePath_TextBox
download_path = tk.StringVar()
entry_path = tk.Entry(frame_path, textvariable=download_path, state="readonly")
entry_path.pack(side=tk.LEFT, padx=(0,5), fill="x", expand=True)

#Browse_Button
#def: set the saving path for video 
def select_path():
    folder = filedialog.askdirectory()
    if folder:
        download_path.set(folder)

button_browse = tk.Button(frame_path, text="Browse Folder", command=select_path, width="15")
button_browse.pack(side=tk.RIGHT)

# --------- Status and Progress Bar ---------
#frame
frame_status = tk.Frame(main_frame)
frame_status.pack(pady=10, fill="x")

#Message_Label
status_text = tk.StringVar(value="Please enter a YouTube URL and fetch formats...")
label_status = tk.Label(frame_status, textvariable=status_text, anchor="w")
label_status.pack(fill="x")

#Progress
progress_bar = ttk.Progressbar(frame_status, orient="horizontal", mode="determinate")
progress_bar.pack(side=tk.LEFT, padx=(0,5), fill="x",expand=True)

# --------- Download Button ---------

#def: click "download button"
def download_video():

    status_text.set("Downloading...")
    progress_bar["value"] = 0

    url = entry_url.get()
    folder =download_path.get()
    fmt_idx = listbox_format.curselection()
    fmt_type = format_var.get()

    if not url or not folder or not fmt_idx:
        messagebox.showwarning("ERROR", "Please make sure to enter the URL, select quality, format, and save location")
        return
    
    fmt_selected = available_formats[fmt_idx[0]]
    out_template = os.path.join(folder, '%(title)s.%(ext)s')
    
    #def: deal with download progress
    mp4_download_count = 1
    def progress_hook(d):

        nonlocal mp4_download_count
       
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = downloaded / total * 100
                progress_bar["value"] = percent
                window.update_idletasks()

        elif d['status'] == 'finished':
            
            if fmt_type == "mp4":

                if mp4_download_count == 2:
                    status_text.set("Download Complete!")
                else:
                    mp4_download_count = mp4_download_count + 1

            else:
                status_text.set("Download Complete!")

    #def: download video by using thread
    def _download():

        #def: check if file already exists --> filename(1),(2),(3)...
        def check_filename(path):
            if not os.path.exists(path):
                return path
            
            base, ext = os.path.splitext(path)
            i = 1
            while True:
                print(f"alan1:{base}")
                print(f"alan2:{ext}")
                new_path = f"{base}({i}){ext}"
                if not os.path.exists(new_path):
                    return new_path
                i += 1
        
        title = video_info.get("title", "video") 
        file_ext = "mp4" if fmt_type == "mp4" else "mp3"
        filename = f"{title}.{file_ext}"
        full_output_path = os.path.join(folder, filename)
        new_out_path = check_filename(full_output_path)
        out_template = new_out_path.replace(f".{file_ext}", f".%(ext)s") 



        ydl_opts = {
            'format': fmt_selected['format_id'],
            'outtmpl': out_template,
            'progress_hooks': [progress_hook],
        }


        #--------------------------------------------
        #Windows--> use ffmpeg.exe in the directory
        #MacOS--> use ffmpeg installed on your system
        ffmpeg_exec = 'ffmpeg.exe'
        if platform.system() == "Windows":
            pass
        else:
            ffmpeg_exec = 'ffmpeg'
        #--------------------------------------------

        if fmt_type == "mp4":
            #+bestaudio：Automatically select the best audio source
            #merge_output_format: mp4 --> Output as mp4 after merging
            ydl_opts.update({
                'format': f"{fmt_selected['format_id']}+bestaudio/best",
                'merge_output_format': 'mp4',
                'ffmpeg_location': ffmpeg_exec
            })

        elif fmt_type == "mp3":
            ydl_opts.update({
                'format': 'bestaudio/best', #Automatically select the best audio source
                'postprocessors':[{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }],
                'ffmpeg_location': ffmpeg_exec
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            messagebox.showerror("ERROR", f"Download failed\n{e}")
            status_text.set("Download failed")

    threading.Thread(target=_download).start()


#Download Button
button_download = tk.Button(frame_status, text="Download", width=15, bg="#FF0000", fg="white", command=download_video)
button_download.pack(side=tk.RIGHT)


window.mainloop()




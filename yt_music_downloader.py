import youtube_dl
import requests
import Tkinter as tk
import errno
import os
import time
from bs4 import BeautifulSoup

# show slides of video options (Get First Result MP3s, Choose Best MP3s)

class DownloadApp:
    options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '256',
        }],
    }
    
    @classmethod
    def mkdirIfNotExists(cls, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    @classmethod
    def hasLink(cls, h3):
        h3_class = h3.get('class')
        if h3_class and h3_class[0] == 'yt-lockup-title':
            if h3.a.get("href").startswith('/watch'):
                return True
        return False

    def __init__(self, master):
        self.master = master
        master.geometry('600x400')
        master.title('YouTube MP3 Downloader')
        self.path = os.path.dirname(os.path.realpath(__file__))
        icon = tk.PhotoImage(file=os.path.join(self.path, 'icon.png')) 
        master.call('wm', 'iconphoto', master._w, icon) 

        self.explain_label = tk.Label(master, 
            text='Enter a list of video searches below.')
        self.outer_frame = tk.Frame(master)
        self.entry_frame = tk.Frame(self.outer_frame)
        
        search_entry = tk.Entry(self.entry_frame)
        self.search_entries = [search_entry]
        search_entry.pack(pady=1)
        search_entry.focus()

        self.add_btn = tk.Button(self.outer_frame, text='Add another... [Enter]', 
            command=self.addSearch)
        self.finish_btn = tk.Button(self.outer_frame, text='Get MP3s', 
            command=self.getVids)
        
        self.explain_label.pack(pady=14)
        self.outer_frame.pack()
        self.entry_frame.pack(pady=10)
        self.add_btn.pack(pady=4)
        self.finish_btn.pack()

        master.bind('<Return>', self.addSearch)
    
    def addSearch(self, event=None):
        new_search = tk.Entry(self.entry_frame)
        self.search_entries += [new_search]
        new_search.pack(pady=1)
        new_search.focus()
    
    def duringDownloadDisplay(self):
        self.master.unbind('<Return>')
        self.explain_label.config(text='Downloading and converting files...')
        self.outer_frame.pack_forget()
        self.master.update_idletasks()

    def resetAfterDownloadDisplay(self):
        self.master.bind('<Return>', self.addSearch)
        self.explain_label.config(text='Enter a list of video searches below.')
        self.outer_frame.pack()
        self.master.update_idletasks()

    def getVids(self, event=None):
        self.duringDownloadDisplay()
        file_dir = os.path.join(self.path, 'YouTube MP3s')
        self.mkdirIfNotExists(file_dir)
        os.chdir(file_dir)
        vid_names = [entry.get() for entry in self.search_entries]
        urls = []
        for vid_name in vid_names:
            q = {'search_query': vid_name}
            resp = requests.get('https://www.youtube.com/results', params=q)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                hdrs = soup.find_all('h3')
                links = [h3.a.get("href") for h3 in hdrs if self.hasLink(h3)]
                # for now, just use first result
                urls += [links[0]]
        
        youtube = youtube_dl.YoutubeDL(self.options)
        youtube.download(['http://www.youtube.com' + url for url in urls])
        
        self.search_entries[0].delete(0, tk.END)
        for entry in self.search_entries[1:]:
            entry.destroy()
        
        self.search_entries = self.search_entries[:1]
        self.resetAfterDownloadDisplay()

def main():
    root = tk.Tk()
    app = DownloadApp(root)
    root.mainloop()   

if __name__ == '__main__':
    main()
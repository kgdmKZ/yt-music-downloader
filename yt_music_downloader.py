import youtube_dl
import requests
import Tkinter as tk
import errno
import os
import time
from bs4 import BeautifulSoup
from choice_info import ChoicesInfo

class DownloadApp:
    options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '256',
        }],
        'noplaylist' : True
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
            link = h3.a.get("href")
            # use only links that are not for playlists
            if link.startswith('/watch') and '&list=' not in link[7:]:
                return True
        return False

    def __init__(self, master):
        self.master = master
        self.youtube = youtube_dl.YoutubeDL(self.options)
        master.geometry('800x600')
        master.title('YouTube MP3 Downloader')
        self.path = os.path.dirname(os.path.realpath(__file__))
        icon = tk.PhotoImage(file=os.path.join(self.path, 'icon.png')) 
        master.call('wm', 'iconphoto', master._w, icon) 
        
        self.explain_str = tk.StringVar()
        self.explain_str.set('Enter a list of video searches below.')
        self.explain_label = tk.Label(master, textvariable=self.explain_str, 
            font=(None, 12))
        self.outer_frame = tk.Frame(master)
        self.entry_frame = tk.Frame(self.outer_frame)
        
        search_entry = tk.Entry(self.entry_frame, font=(None, 10))
        self.search_entries = [search_entry]
        search_entry.pack(pady=1)
        search_entry.focus()

        self.add_btn = tk.Button(self.outer_frame, 
            text='Add another... [Enter]', command=self.addSearch, 
            font=(None, 10))
        self.finish_btn = tk.Button(self.outer_frame, 
            text='Get first result MP3s', command=lambda: self.getVids(False),
            font=(None, 10))
        self.finish_alt_btn = tk.Button(self.outer_frame,
            text='Choose each best result', command=lambda: self.getVids(True),
            font=(None, 10))
        
        self.explain_label.pack(pady=14)
        self.outer_frame.pack()
        self.entry_frame.pack(pady=10)
        self.add_btn.pack(pady=4, side=tk.LEFT)
        self.finish_btn.pack(pady=4, side=tk.LEFT)
        self.finish_alt_btn.pack(pady=4, side=tk.LEFT)
        
        self.master.update()
        master.bind('<Return>', self.addSearch)

    def addSearch(self, event=None):
        print("addSearch\n")
        new_search = tk.Entry(self.entry_frame, font=(None, 10))
        self.search_entries += [new_search]
        new_search.pack(pady=1)
        new_search.focus()
    
    def duringDownloadDisplay(self):
        self.master.unbind('<Return>')
        self.add_btn.config(state=tk.DISABLED)
        self.finish_btn.config(state=tk.DISABLED)
        self.finish_alt_btn.config(state=tk.DISABLED)
        self.explain_str.set('Getting info from YouTube searches...')
        self.outer_frame.pack_forget()
        self.master.update_idletasks()
    
    def getVidsInfo(self, urls):
        urls = ['http://youtube.com' + url for url in urls]
        return [self.youtube.extract_info(url, download=False, ) for url in urls]

    def getVids(self, alt_btn_clicked):
        print("getVids\n")
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
                links = [h3.a.get('href') for h3 in hdrs if self.hasLink(h3)]
                if alt_btn_clicked:
                    urls += [links[:5]]
                else:
                    urls += [links[0]]
        
        self.outer_frame.destroy()
        yt = youtube_dl.YoutubeDL(self.options)
        
        if not alt_btn_clicked:
            self.explain_str.set('Downloading and converting files...')
            self.master.update_idletasks()
            yt.download(['http://www.youtube.com' + url for url in urls])
            self.explain_str.set('Your MP3s are ready!')
            self.master.update_idletasks()
            time.sleep(3)
            self.master.destroy()
        else:
            vids_info = [self.getVidsInfo(alt_urls) for alt_urls in urls]
            kwargs = {'vids_data' : vids_info, 'youtube' : yt, 'urls' : urls}
            self.select_choices = ChoicesInfo(self.master, **kwargs)
            self.explain_label.destroy()
            self.select_choices.pack()

def main():
    root = tk.Tk()
    app = DownloadApp(root)
    root.mainloop()   

if __name__ == '__main__':
    main()
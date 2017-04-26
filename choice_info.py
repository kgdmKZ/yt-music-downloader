import Tkinter as tk
from PIL import ImageTk, Image
import urllib, cStringIO
import time

class ChoicesInfo(tk.Frame):
    ALTERNATIVE_COUNT = 5

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master)
        self.master = master
        self.vids_data = kwargs['vids_data']
        self.youtube = kwargs['youtube']
        self.urls = kwargs['urls']
        # start on first video search's results
        self.chosen = 0
        # start on the first alternative in results
        self.cur_option = 0
        
        self.choice_urls = []
        
        self.explain_label = tk.Label(self, 
            text='Choose from the alternatives below for each video search.',
            font=(None, 12))

        self.outer_frame = tk.Frame(self)
        self.title_label = tk.Label(self.outer_frame, font=(None, 10))
        self.thumb_label = tk.Label(self.outer_frame)
        self.uploader_label = tk.Label(self.outer_frame, font=(None, 8))
        self.desc_text = tk.Text(self.outer_frame, font=(None, 8), height=7,
            state=tk.DISABLED, borderwidth=0, relief=tk.FLAT, wrap=tk.WORD)
        self.duration_label = tk.Label(self.outer_frame, font=(None, 8))
        
        self.last_btn_frame = tk.Frame(self.outer_frame)
        self.last_btn = tk.Button(self.last_btn_frame, text='Last [Left]', 
            command=self.pressLast, font=(None, 10))
        
        self.choose_btn = tk.Button(self.outer_frame, text='Make choice [Enter]', 
            command=self.makeChoice, font=(None, 10))
        
        self.next_btn_frame = tk.Frame(self.outer_frame)
        self.next_btn = tk.Button(self.next_btn_frame, text='Next [Right]', 
            command=self.pressNext, font=(None, 10))
        
        self.explain_label.pack(pady=14)
        self.outer_frame.pack()
        self.title_label.pack(pady=6)
        self.thumb_label.pack(pady=14)
        self.uploader_label.pack()
        self.desc_text.pack()
        self.duration_label.pack(pady=6)
        self.last_btn_frame.pack(side=tk.LEFT, expand=True)
        self.choose_btn.pack(side=tk.LEFT, expand=True)
        self.next_btn_frame.pack(side=tk.LEFT, expand=True)
        self.next_btn.pack()
        self.updateVidInfo()
        self.master.update()
        self.master.bind('<Return>', self.makeChoice)
        self.master.bind('<Left>', self.pressLast)
        self.master.bind('<Right>', self.pressNext)
    
    def unbindKeys(self):
        self.master.unbind('<Left>')
        self.master.unbind('<Right>')
        self.master.unbind('<Return>')

    def bindKeys(self):
        self.master.update()
        self.master.bind('<Left>', self.pressLast)
        self.master.bind('<Right>', self.pressNext)
        self.master.bind('<Return>', self.makeChoice)

    def updateVidInfo(self):
        print("Self.chosen is %d and self.cur_option is %d\n" % (self.chosen, self.cur_option))
        vid_info = self.vids_data[self.chosen][self.cur_option]
        self.uploader_label.configure(
            text="Uploaded by " + vid_info['uploader'])
        description = vid_info['description']
        self.desc_text.configure(state=tk.NORMAL)
        self.desc_text.delete('0.0', tk.END)
        self.desc_text.insert('0.0', description)
        self.desc_text.configure(state=tk.DISABLED)
        
        thumb_url = vid_info['thumbnails'][0]['url']
        thumb_file = cStringIO.StringIO(urllib.urlopen(thumb_url).read())
        img = Image.open(thumb_file).resize((480, 270), Image.ANTIALIAS)
        self.thumbnail = ImageTk.PhotoImage(img)
        
        total_seconds = vid_info['duration']
        minutes = total_seconds/60
        rem_seconds = total_seconds % 60
        duration_minutes = "Duration: " + str(minutes) + " minutes and "
        duration = duration_minutes + str(rem_seconds) + " seconds" 
        
        self.title_label.configure(text=vid_info['title'])
        self.thumb_label.configure(image=self.thumbnail)
        self.duration_label.configure(text=duration)
    
    def pressNext(self, event=None):
        self.unbindKeys()
        if self.cur_option == 0:
            self.last_btn.pack()
        if self.cur_option == self.ALTERNATIVE_COUNT-2:
            self.next_btn.pack_forget()
        if self.cur_option < self.ALTERNATIVE_COUNT-1:
            self.cur_option += 1
        self.updateVidInfo()
        self.bindKeys()

    def pressLast(self, event=None):
        self.unbindKeys()
        if self.cur_option <= 1:
            self.last_btn.pack_forget()
        if self.cur_option == self.ALTERNATIVE_COUNT-1:
            self.next_btn.pack()
        if self.cur_option > 0:
            self.cur_option -= 1
        self.updateVidInfo()
        self.bindKeys()

    def makeChoice(self, event=None):
        print("Length of self.vids_data is %d\n" % len(self.vids_data))
        print("Length of self.vids_data[self.chosen] is %d\n" % len(self.vids_data[self.chosen]))
        print("Length of self.vids_data[self.chosen][0] is %d\n" % len(self.vids_data[self.chosen][0]))
        self.unbindKeys()
        choice = self.urls[self.chosen][self.cur_option]
        print("URL is %s\n" % choice)
        self.choice_urls += ['http://youtube.com' + choice]
        self.chosen += 1
        print("Self.chosen is %d\n" % self.chosen)
        print("length of vids data is %d\n" % len(self.vids_data))
        if self.chosen < len(self.vids_data):
            print("in if block if\n")
            self.cur_option = 0
            self.updateVidInfo()
            self.bindKeys()
        elif self.chosen == len(self.vids_data):
            print("in if block elif\n")
            self.explain_label.config(
                text='Downloading and converting files...')
            self.outer_frame.destroy()
            self.update_idletasks()
            self.youtube.download(self.choice_urls)
            self.explain_label.config(text='Your MP3s are ready!')
            self.update_idletasks()
            time.sleep(5)
            self.master.destroy()
            print("finished...\n")

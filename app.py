"""Local desktop UI. Start with `python app.py`; CLI also works without a display."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from tkinter.scrolledtext import ScrolledText
from clauses.model import load,analyze
from clauses.schema import LABELS,EXPLANATIONS,NOTICE
from clauses.export import render_html

class ClauseGuardApp:
    def __init__(self,root):
        self.root=root;self.result=None;self.bundle=None
        root.title('ClauseGuard | Understand the terms before you accept');root.geometry('1180x820');root.minsize(800,600)
        root.configure(bg='#f7f6f1')
        style=ttk.Style();style.configure('TLabel',font=('Arial',11));style.configure('Title.TLabel',font=('Arial',25,'bold'))
        top=ttk.Frame(root,padding=18);top.pack(fill='x')
        ttk.Label(top,text='ClauseGuard',style='Title.TLabel').pack(anchor='w')
        ttk.Label(top,text='Find important clauses. Check the original words.').pack(anchor='w',pady=5)
        ttk.Label(top,text=NOTICE,wraplength=1050).pack(anchor='w',pady=5)
        controls=ttk.Frame(root,padding=(18,0));controls.pack(fill='x')
        ttk.Button(controls,text='Open text file',command=self.open_text).pack(side='left')
        ttk.Button(controls,text='Load fictional example',command=self.example).pack(side='left',padx=6)
        self.run=ttk.Button(controls,text='Analyze terms',command=self.run_analysis);self.run.pack(side='left',padx=6)
        self.export_btn=ttk.Button(controls,text='Export analysis',command=self.export,state='disabled');self.export_btn.pack(side='left',padx=6)
        ttk.Label(controls,text='Category:').pack(side='left',padx=(20,5))
        self.filter=tk.StringVar(value='All sentences')
        combo=ttk.Combobox(controls,textvariable=self.filter,values=['All sentences','Flagged only',*LABELS],state='readonly',width=25)
        combo.pack(side='left');combo.bind('<<ComboboxSelected>>',lambda event:self.refresh_list())
        panes=ttk.Panedwindow(root,orient='horizontal');panes.pack(fill='both',expand=True,padx=18,pady=14)
        left=ttk.Frame(panes);right=ttk.Frame(panes);panes.add(left,weight=1);panes.add(right,weight=1)
        ttk.Label(left,text='Paste English terms').pack(anchor='w')
        self.input=ScrolledText(left,wrap='word',font=('Arial',12),undo=True);self.input.pack(fill='both',expand=True,pady=6)
        self.input.tag_configure('source',background='#fce6ab');self.input.bind('<<Modified>>',self.changed)
        ttk.Label(right,text='Select a result to inspect its source').pack(anchor='w')
        self.listbox=tk.Listbox(right,font=('Arial',11),height=12,exportselection=False)
        self.listbox.pack(fill='both',expand=True,pady=6);self.listbox.bind('<<ListboxSelect>>',self.select)
        self.detail=ScrolledText(right,wrap='word',font=('Arial',11),height=14,state='disabled');self.detail.pack(fill='both',expand=True)
        self.status=tk.StringVar(value='Local processing. Text is saved only when you explicitly export.')
        ttk.Label(root,textvariable=self.status,wraplength=1100,padding=12).pack(fill='x')

    def changed(self,event=None):
        if self.input.edit_modified():
            self.result=None;self.export_btn.configure(state='disabled');self.listbox.delete(0,'end')
            self.input.tag_remove('source','1.0','end');self.input.edit_modified(False)

    def put_text(self,text):
        self.input.delete('1.0','end');self.input.insert('1.0',text);self.changed()

    def open_text(self):
        filename=filedialog.askopenfilename(filetypes=[('UTF-8 text','*.txt'),('All files','*')])
        if filename:
            try:self.put_text(Path(filename).read_text(encoding='utf-8'))
            except (OSError,UnicodeError) as exc:messagebox.showerror('Cannot read file',str(exc))

    def example(self):
        self.put_text((Path(__file__).parent/'examples/fictional_terms.txt').read_text())

    def run_analysis(self):
        self.run.configure(state='disabled');self.status.set('Analyzing locally...');self.root.update_idletasks()
        try:
            if self.bundle is None:self.bundle=load()
            self.result=analyze(self.input.get('1.0','end-1c'),self.bundle)
            self.filter.set('All sentences');self.refresh_list();self.export_btn.configure(state='normal')
            flagged=sum(bool(x['labels']) for x in self.result['sentences'])
            self.status.set(f'{len(self.result["sentences"])} sentences; {flagged} flagged. Model {self.result["model_id"][:12]}. Review original context.')
        except Exception as exc:
            self.status.set('Analysis could not complete.');messagebox.showerror('Analysis error',str(exc))
        finally:self.run.configure(state='normal')

    def refresh_list(self):
        self.listbox.delete(0,'end');self.visible=[]
        if not self.result:return
        category=self.filter.get()
        for row in self.result['sentences']:
            if category=='Flagged only' and not row['labels']:continue
            if category in LABELS and category not in row['labels']:continue
            self.visible.append(row)
            labels=', '.join(row['labels']) if row['labels'] else 'No category flagged'
            self.listbox.insert('end',f'{row["sentence_id"]+1}. {labels}')
        if self.visible:self.listbox.selection_set(0);self.select()
        else:
            self.detail.configure(state='normal');self.detail.delete('1.0','end');self.detail.insert('end','No results for this filter. Inspect the full document.');self.detail.configure(state='disabled')

    def select(self,event=None):
        selected=self.listbox.curselection()
        if not selected or not self.result:return
        row=self.visible[selected[0]]
        self.input.tag_remove('source','1.0','end')
        # Tk 9 counts Unicode scalar values; use full-prefix indices to preserve offsets on Tk 8 builds as well.
        def tkoffset(index):
            prefix=self.input.get('1.0','end-1c')[:index]
            lines=prefix.split('\n')
            return f'{len(lines)}.{int(self.root.tk.call("string","length",lines[-1]))}'
        self.input.tag_add('source',tkoffset(row['start']),tkoffset(row['end']));self.input.see(tkoffset(row['start']))
        parts=[row['text'],'']
        for label in row['labels']:parts.append(f'{label}\n{EXPLANATIONS[label]}\nModel score: {row["scores"][label]:.3f}\n')
        if not row['labels']:parts.append('No category flagged. This is not a finding of safety.')
        if row['near_threshold']:parts.append('One score is near its decision threshold. Review context carefully.')
        self.detail.configure(state='normal');self.detail.delete('1.0','end');self.detail.insert('end','\n'.join(parts));self.detail.configure(state='disabled')

    def export(self):
        if not self.result:return
        filename=filedialog.asksaveasfilename(defaultextension='.html',filetypes=[('HTML document','*.html')])
        if filename:
            try:Path(filename).write_text(render_html(self.result),encoding='utf-8');self.status.set('Exported the analysis. The file includes the supplied text.')
            except OSError as exc:messagebox.showerror('Export error',str(exc))

if __name__=='__main__':
    try:
        root=tk.Tk();ClauseGuardApp(root);root.mainloop()
    except tk.TclError as exc:
        raise SystemExit(f'Desktop display unavailable: {exc}\nUse the CLI: python -m clauses.cli analyze --input examples/fictional_terms.txt --html-out analysis.html')

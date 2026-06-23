import customtkinter as ctk
import json
import os
import random
from tkinter import filedialog

# ---------------- STYLE ----------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DATEI = r"C:\Users\justi\Dropbox\Vokabeltrainer\lernsets.json"

if not os.path.exists(DATEI):
    with open(DATEI, "w") as f:
        json.dump({}, f)

def load():
    with open(DATEI, "r") as f:
        return json.load(f)

def save(data):
    with open(DATEI, "w") as f:
        json.dump(data, f, indent=4)

data = load()

# ---------------- APP ----------------
app = ctk.CTk()
app.geometry("1000x700")
app.title("Quizlet Trainer V4")

app.attributes("-fullscreen", True)

def exit_fs(event=None):
    app.attributes("-fullscreen", False)

app.bind("<Escape>", exit_fs)

frame = ctk.CTkScrollableFrame(app, corner_radius=30)
frame.pack(padx=40, pady=40, fill="both", expand=True)

def _on_mousewheel(event):
    try:
        frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120) * 10), "units")
    except:
        pass

app.bind_all("<MouseWheel>", _on_mousewheel)

BIG = ("Arial", 40)
MID = ("Arial", 26)
SMALL = ("Arial", 20)

# ---------------- CLEAR ----------------
def clear():
    for w in frame.winfo_children():
        w.destroy()

# ---------------- HOME ----------------
def home():
    clear()

    ctk.CTkLabel(frame, text="📚 Deine Lernsets", font=BIG).pack(pady=30)

    for name in data:
        card = ctk.CTkFrame(frame, corner_radius=25)
        card.pack(fill="x", padx=60, pady=15)

        ctk.CTkButton(card, text=name, height=70, font=MID,
                      command=lambda n=name: open_set(n)).pack(side="left", padx=15, pady=15)

        ctk.CTkButton(card, text="🗑", width=70, height=70,
                      command=lambda n=name: delete_set(n)).pack(side="right", padx=15)

    ctk.CTkButton(frame, text="+ Neues Lernset", height=70, font=MID,
                  command=new_set).pack(pady=40)

# ---------------- NEW SET ----------------
def new_set():
    clear()

    ctk.CTkLabel(frame, text="Neues Lernset", font=BIG).pack(pady=40)

    entry = ctk.CTkEntry(frame, height=60, font=MID)
    entry.pack(pady=20)

    def create(event=None):
        name = entry.get()
        if name:
            data[name] = []
            save(data)
            home()

    entry.bind("<Return>", create)

    ctk.CTkButton(frame, text="Erstellen", height=70, font=MID,
                  command=create).pack(pady=10)

    ctk.CTkButton(frame, text="Zurück", height=60,
                  command=home).pack(pady=10)


# ---------------- TEXT IMPORT ----------------
def import_from_text(name):
    win = ctk.CTkToplevel(app)
    win.title("Vokabeln einfügen")
    win.geometry("700x500")

    ctk.CTkLabel(
        win,
        text="Füge hier ChatGPT-Ausgabe ein:\nhouse - Haus",
        font=("Arial", 18)
    ).pack(pady=10)

    textbox = ctk.CTkTextbox(win)
    textbox.pack(fill="both", expand=True, padx=20, pady=20)

    def do_import():
        text = textbox.get("1.0", "end").strip()
        added = 0

        for line in text.splitlines():
            line = line.strip()

            if not line:
                continue

            if " - " in line:
                en, de = line.split(" - ", 1)
            elif "-" in line:
                en, de = line.split("-", 1)
            else:
                continue

            en = en.strip()
            de = de.strip()

            if en and de:
                data[name].append({"en": en, "de": de})
                added += 1

        save(data)
        win.destroy()

    ctk.CTkButton(
        win,
        text="Importieren",
        command=do_import
    ).pack(pady=10)


# ---------------- OPEN SET ----------------
def open_set(name):
    clear()

    ctk.CTkLabel(frame, text=name, font=BIG).pack(pady=20)

    rename_entry = ctk.CTkEntry(frame, height=60, font=MID, placeholder_text="Neuer Name")
    rename_entry.pack(pady=10)

    def rename(event=None):
        new = rename_entry.get()
        if new:
            data[new] = data.pop(name)
            save(data)
            home()

    rename_entry.bind("<Return>", rename)

    ctk.CTkButton(frame, text="Umbenennen", height=60,
                  command=rename).pack(pady=5)

    en = ctk.CTkEntry(frame, height=60, font=MID, placeholder_text="Englisch")
    de = ctk.CTkEntry(frame, height=60, font=MID, placeholder_text="Deutsch")

    en.pack(pady=10)
    de.pack(pady=10)

    def add(event=None):
        if en.get() and de.get():
            data[name].append({"en": en.get(), "de": de.get()})
            save(data)
            en.delete(0, "end")
            de.delete(0, "end")

    en.bind("<Return>", add)
    de.bind("<Return>", add)

    ctk.CTkButton(frame, text="Hinzufügen", height=60,
                  command=add).pack(pady=10)

    ctk.CTkButton(
        frame,
        text="📋 ChatGPT-Liste importieren",
        height=60,
        command=lambda: import_from_text(name)
    ).pack(pady=5)

    ctk.CTkButton(frame, text="✏ Bearbeiten", height=60,
                  command=lambda: edit_set(name)).pack(pady=5)

    ctk.CTkButton(frame, text="🃏 Karteikarten", height=60,
                  command=lambda: flashcards(name)).pack(pady=5)

    ctk.CTkButton(frame, text="🎯 Lernen", height=60,
                  command=lambda: learn(name)).pack(pady=5)

    ctk.CTkButton(frame, text="🧪 Test", height=60,
                  command=lambda: test(name)).pack(pady=5)

    ctk.CTkButton(frame, text="⬅ Zurück", height=60,
                  command=home).pack(pady=20)

# ---------------- EDIT ----------------
def edit_set(name):
    clear()

    ctk.CTkLabel(frame, text="Bearbeiten", font=BIG).pack(pady=20)

    for i, v in enumerate(data[name]):
        card = ctk.CTkFrame(frame, corner_radius=20)
        card.pack(fill="x", padx=60, pady=10)

        ctk.CTkLabel(card, text=f"{v['de']} → {v['en']}",
                     font=MID).pack(side="left", padx=15)

        def delete(i=i):
            data[name].pop(i)
            save(data)
            edit_set(name)

        ctk.CTkButton(card, text="🗑", width=60,
                      command=delete).pack(side="right", padx=10)

    ctk.CTkButton(frame, text="Zurück", height=60,
                  command=lambda: open_set(name)).pack(pady=20)

# ---------------- FLASHCARDS ----------------
def flashcards(name):
    voc = data[name][:]
    random.shuffle(voc)

    clear()

    i = 0
    show_de = True

    card = ctk.CTkFrame(frame, corner_radius=30)
    card.pack(pady=60, padx=80, fill="both", expand=True)

    label = ctk.CTkLabel(card, text="", font=BIG)
    label.pack(pady=100)

    def update():
        label.configure(text=voc[i]["de"] if show_de else voc[i]["en"])

    def flip():
        nonlocal show_de
        show_de = not show_de
        update()

    def next():
        nonlocal i, show_de
        i += 1
        show_de = True
        if i < len(voc):
            update()
        else:
            label.configure(text="Fertig!")

    ctk.CTkButton(card, text="Umdrehen", height=70, command=flip).pack(pady=10)
    ctk.CTkButton(card, text="Weiter", height=70, command=next).pack(pady=10)

    ctk.CTkButton(frame, text="Zurück", height=60, command=home).pack()

    update()


# ---------------- LEARN ----------------
def learn(name):
    clear()

    base_voc = data[name][:]
    random.shuffle(base_voc)

    # Punkte pro Vokabel
    scores = {id(v): 0 for v in base_voc}

    active = base_voc[:]
    mc_batch = []
    current_write = []
    phase = "mc"
    mc_target = random.randint(5, 7)

    label = ctk.CTkLabel(frame, text="", font=BIG)
    label.pack(pady=30)

    result = ctk.CTkLabel(frame, text="", font=MID)
    result.pack(pady=10)

    progress_label = ctk.CTkLabel(frame, text="", font=SMALL)
    progress_label.pack(pady=5)

    progress_bar = ctk.CTkProgressBar(frame, width=600)
    progress_bar.pack(pady=5)
    progress_bar.set(0)


    entry = ctk.CTkEntry(frame, height=60, font=MID)

    buttons = []

    current = None
    write_index = 0

    def get_active():
        return [v for v in active if scores[id(v)] < 3]

    
    def update_progress():
        learned = len([v for v in base_voc if scores[id(v)] >= 3])
        total = len(base_voc)

        progress_label.configure(
            text=f"{learned}/{total} gelernt ({int((learned/total)*100) if total else 0}%)"
        )

        progress_bar.set(learned / total if total else 0)


    def finish():
        clear()
        ctk.CTkLabel(frame, text="🎉 Lernen abgeschlossen!", font=BIG).pack(pady=30)
        ctk.CTkLabel(frame, text="Alle Vokabeln wurden gelernt.", font=MID).pack(pady=10)
        ctk.CTkButton(frame, text="Zurück", height=70, command=home).pack(pady=30)

    def next_mc():
        nonlocal current, mc_target, phase, current_write

        entry.pack_forget()
        update_progress()

        active_now = get_active()

        if not active_now:
            finish()
            return

        if len(mc_batch) >= mc_target:
            current_write = mc_batch[:]
            mc_batch.clear()
            phase = "write"
            start_write()
            return

        current = random.choice(active_now)

        for b in buttons:
            b.destroy()
        buttons.clear()

        label.configure(text=current["de"])

        correct = current["en"]
        options = [v["en"] for v in random.sample(base_voc, min(4, len(base_voc)))]
        if correct not in options:
            options[0] = correct

        options = list(dict.fromkeys(options))

        while len(options) < min(4, len(base_voc)):
            x = random.choice(base_voc)["en"]
            if x not in options:
                options.append(x)

        random.shuffle(options)

        def choose(ans):
            if ans == correct:
                scores[id(current)] += 1
                result.configure(text="✔ Richtig", text_color="green")
                result.after(1000, lambda: result.configure(text=""))
            else:
                scores[id(current)] -= 1
                result.configure(text=f"❌ Falsch → {correct}", text_color="red")
                result.after(1000, lambda: result.configure(text=""))

            mc_batch.append(current)
            next_mc()

        for o in options:
            btn = ctk.CTkButton(frame, text=o, height=70,
                                command=lambda x=o: choose(x))
            btn.pack(pady=8)
            buttons.append(btn)

    def start_write():
        nonlocal write_index

        for b in buttons:
            b.destroy()
        buttons.clear()

        write_index = 0
        entry.pack(pady=10)
        show_write()

    def show_write():
        nonlocal phase, mc_target

        if write_index >= len(current_write):
            phase = "mc"
            mc_target = random.randint(5, 7)
            entry.delete(0, "end")
            next_mc()
            return

        label.configure(text=current_write[write_index]["de"])
        entry.delete(0, "end")

    def check_write(event=None):
        nonlocal write_index

        voc = current_write[write_index]

        if entry.get().strip().lower() == voc["en"].strip().lower():
            scores[id(voc)] += 2
            result.configure(text="✔ Richtig", text_color="green")
            result.after(1000, lambda: result.configure(text=""))
        else:
            scores[id(voc)] -= 2
            result.configure(text=f"❌ Falsch → {voc['en']}", text_color="red")
            result.after(1000, lambda: result.configure(text=""))

        write_index += 1
        show_write()

    entry.bind("<Return>", check_write)

    next_mc()

# ---------------- TEST ----------------
def test(name):
    voc = data[name][:]
    random.shuffle(voc)

    clear()

    i = 0
    score = 0

    label = ctk.CTkLabel(frame, text=voc[0]["de"], font=BIG)
    label.pack(pady=40)

    entry = ctk.CTkEntry(frame, height=60, font=MID)
    entry.pack()

    def check(event=None):
        nonlocal i, score

        if entry.get().strip().lower() == voc[i]["en"].strip().lower():
            score += 1

        i += 1
        entry.delete(0, "end")

        if i < len(voc):
            label.configure(text=voc[i]["de"])
        else:
            label.configure(text=f"Ergebnis: {score}/{len(voc)}")

    entry.bind("<Return>", check)

    ctk.CTkButton(frame, text="Zurück", height=60,
                  command=home).pack(pady=20)

# ---------------- DELETE ----------------
def delete_set(name):
    del data[name]
    save(data)
    home()

# ---------------- START ----------------
home()
app.mainloop()
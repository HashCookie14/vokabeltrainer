import flet as ft
import json
import os
import random

DATEI = "lernsets.json"


# ---------------- DATEN ----------------
def load():
    if not os.path.exists(DATEI):
        with open(DATEI, "w", encoding="utf-8") as f:
            json.dump({}, f)

    with open(DATEI, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(DATEI, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ---------------- APP ----------------
def main(page: ft.Page):
    page.title = "Vokabeltrainer"
    page.scroll = ft.ScrollMode.AUTO

    data = load()

    def home():
        page.controls.clear()

        page.add(
            ft.Text("📚 Deine Lernsets", size=30, weight=ft.FontWeight.BOLD)
        )

        for set_name in data.keys():
            page.add(
                ft.Row([
                    ft.ElevatedButton(
                        f"{set_name} ({len(data[set_name])} Vokabeln)",
                        expand=True,
                        on_click=lambda e, n=set_name: open_set(n)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        on_click=lambda e, n=set_name: delete_set(n)
                    )
                ])
            )

        page.add(
            ft.ElevatedButton(
                "+ Neues Lernset",
                on_click=lambda e: new_set()
            )
        )

        page.update()

    # ---------------- NEUES SET ----------------
    def new_set():
        page.controls.clear()

        name_field = ft.TextField(label="Name des Lernsets")

        def create(e):
            name = name_field.value.strip()

            if name:
                data[name] = []
                save(data)
                home()

        page.add(
            ft.Text("Neues Lernset", size=25),
            name_field,
            ft.ElevatedButton("Erstellen", on_click=create),
            ft.ElevatedButton("Zurück", on_click=lambda e: home())
        )

        page.update()

    # ---------------- LERNSET ----------------
    def open_set(name):
        page.controls.clear()

        page.add(
            ft.Text(name, size=30, weight=ft.FontWeight.BOLD)
        )

        en_field = ft.TextField(label="Englisch")
        de_field = ft.TextField(label="Deutsch")

        import_field = ft.TextField(
            label="ChatGPT-Liste einfügen",
            multiline=True,
            min_lines=5,
            max_lines=10
        )


        def import_words(e):
            text = import_field.value.strip()

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

                data[name].append({
                    "en": en.strip(),
                    "de": de.strip()
                })

            save(data)
            open_set(name)

        def add_word(e):
            en = en_field.value.strip()
            de = de_field.value.strip()

            if en and de:
                data[name].append({
                    "en": en,
                    "de": de
                })

                save(data)

                en_field.value = ""
                de_field.value = ""

                page.update()


        rename_field = ft.TextField(label="Neuer Name")

        def rename_set(e):
            new_name = rename_field.value.strip()
            if new_name and new_name != name:
                data[new_name] = data.pop(name)
                save(data)
                home()

        def flashcards(e):
            page.controls.clear()
            voc = data[name][:]
            if not voc:
                page.add(ft.Text("Keine Vokabeln vorhanden"))
                page.add(ft.ElevatedButton("Zurück", on_click=lambda e: open_set(name)))
                page.update()
                return

            idx = {"i":0}
            direction = ft.Switch(label="EN → DE")

            card = ft.Text(size=30)

            def update():
                v = voc[idx["i"]]
                card.value = v["en"] if direction.value else v["de"]
                page.update()

            def show_answer(e):
                v = voc[idx["i"]]
                card.value = v["de"] if direction.value else v["en"]
                page.update()

            def next_card(e):
                idx["i"] += 1
                if idx["i"] >= len(voc):
                    open_set(name)
                    return
                update()

            page.add(direction, card,
                     ft.ElevatedButton("Antwort zeigen", on_click=show_answer),
                     ft.Row([
                        ft.ElevatedButton("✅ Gewusst", on_click=next_card),
                        ft.ElevatedButton("❌ Nicht gewusst", on_click=next_card)
                     ]))
            update()

        def test_mode(e):
            page.controls.clear()
            voc = data[name][:]
            if not voc:
                open_set(name); return

            state = {"i":0,"score":0,"wrong":[]}
            direction = ft.Switch(label="EN → DE")
            q = ft.Text(size=28)
            answer = ft.TextField()

            def update_q():
                if state["i"] >= len(voc):
                    page.controls.clear()
                    page.add(ft.Text(f"Ergebnis: {state['score']}/{len(voc)}", size=30))
                    page.add(ft.Text("Fehlerliste:", size=20))
                    for w in state["wrong"]:
                        page.add(ft.Text(w))
                    page.add(ft.ElevatedButton("Zurück", on_click=lambda e: open_set(name)))
                    page.update()
                    return
                v = voc[state["i"]]
                q.value = v["en"] if direction.value else v["de"]
                answer.value = ""
                page.update()

            def check(e):
                v = voc[state["i"]]
                correct = (v["de"] if direction.value else v["en"]).strip().lower()
                if answer.value.strip().lower() == correct:
                    state["score"] += 1
                else:
                    state["wrong"].append(f"{v['de']} → {v['en']}")
                state["i"] += 1
                update_q()

            page.add(direction,q,answer,ft.ElevatedButton("Weiter", on_click=check))
            update_q()



        
        
        def learn_mode(e):
            page.controls.clear()
            voc = data[name][:]

            if len(voc) < 4:
                page.add(ft.Text("Mindestens 4 Vokabeln benötigt"))
                page.add(ft.ElevatedButton("Zurück", on_click=lambda e: open_set(name)))
                page.update()
                return

            scores = {i: 0 for i in range(len(voc))}
            wrong = set()
            batch = []

            progress = ft.ProgressBar(width=500, value=0)
            status = ft.Text()

            def update_progress():
                learned = len([x for x in scores.values() if x >= 3])
                total = len(voc)
                progress.value = learned / total if total else 0
                pct = int((learned / total) * 100) if total else 0
                status.value = f"{learned}/{total} gelernt ({pct}%)"

            def active():
                return [i for i in range(len(voc)) if scores[i] < 3]

            def finish():
                page.controls.clear()
                page.add(ft.Text("🎉 Lernen abgeschlossen!", size=30))
                page.add(ft.Text("Fehlerliste:", size=20))
                for i in sorted(wrong):
                    page.add(ft.Text(f"{voc[i]['de']} → {voc[i]['en']}"))
                page.add(ft.ElevatedButton("Zurück", on_click=lambda e: open_set(name)))
                page.update()

            def write_phase():
                page.controls.clear()
                update_progress()

                pos = {"i": 0}
                q = ft.Text(size=30)
                answer = ft.TextField()

                def show():
                    if pos["i"] >= len(batch):
                        batch.clear()
                        mc_phase()
                        return

                    idx = batch[pos["i"]]
                    q.value = voc[idx]["de"]
                    answer.value = ""
                    page.update()

                def check(e):
                    idx = batch[pos["i"]]
                    if answer.value.strip().lower() == voc[idx]["en"].strip().lower():
                        scores[idx] += 2
                    else:
                        scores[idx] -= 1
                        wrong.add(idx)

                    pos["i"] += 1
                    show()

                page.add(progress, status, q, answer,
                         ft.ElevatedButton("Weiter", on_click=check))
                show()

            def mc_phase():
                update_progress()

                alive = active()
                if not alive:
                    finish()
                    return

                if len(batch) >= random.randint(5, 7):
                    write_phase()
                    return

                page.controls.clear()
                update_progress()

                weighted = []

                for i in alive:
                    weight = 1

                    if i in wrong:
                        weight += 3

                    weighted.extend([i] * weight)

                idx = random.choice(weighted)
                batch.append(idx)

                correct = voc[idx]["en"]

                pool = [v["en"] for n, v in enumerate(voc) if n != idx]
                random.shuffle(pool)

                options = [correct] + pool[:3]
                random.shuffle(options)

                def choose(ans):
                    if ans == correct:
                        scores[idx] += 1
                    else:
                        scores[idx] -= 1
                        wrong.add(idx)
                    mc_phase()

                page.add(progress, status, ft.Text(voc[idx]["de"], size=30))

                for o in options:
                    page.add(ft.ElevatedButton(o, on_click=lambda e, x=o: choose(x)))

                page.update()

            mc_phase()


        page.add(
            rename_field,
            ft.ElevatedButton("✏️ Umbenennen", on_click=rename_set),
            ft.ElevatedButton("🃏 Karteikarten", on_click=flashcards),
            ft.ElevatedButton("🧪 Test", on_click=test_mode),
            ft.ElevatedButton("🎯 Lernen", on_click=learn_mode),
            en_field,
            de_field,
            ft.ElevatedButton("Hinzufügen", on_click=add_word),
            ft.Divider(),
            import_field,
            ft.ElevatedButton("📋 ChatGPT Import", on_click=import_words)
        )

        page.add(
            ft.Text("Vokabeln:", size=20)
        )

        for i, v in enumerate(data[name]):

            def delete_word(e, index=i):
                data[name].pop(index)
                save(data)
                open_set(name)

            page.add(
                ft.Row([
                    ft.Text(f"{v['de']} → {v['en']}", expand=True),
                    ft.IconButton(icon=ft.Icons.DELETE, on_click=delete_word)
                ])
            )

        page.add(
            ft.ElevatedButton(
                "Zurück",
                on_click=lambda e: home()
            )
        )

        page.update()

    # ---------------- LÖSCHEN ----------------
    def delete_set(name):
        del data[name]
        save(data)
        home()

    home()


import os

ft.app(
    target=main,
    port=int(os.environ.get("PORT", 8080)),
    view=ft.AppView.WEB_BROWSER
)

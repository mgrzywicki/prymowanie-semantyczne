#Zdajemy sobie sprawę z faktu, że nie jest to projekt ukończony. Oto lista rzeczy wymagających poprawy:
#1. Dokończenie/ujednolicenie sczytywania wartości zmiennych z pliku config.
#2. Szczególniejsze opisanie poszczególnych etapów kodu.
#3. Wyczyszczenie kodu z niewykorzystywanych zmiennych i poleceń.
#4. Określanie ścieżki dostępu do pliku z kodem i zapisywanie wyników do pliku w tym samym katalogu.
#5. Estetyka komunikatów.
#6. Estetyka kodu.

import codecs, random, string, csv, yaml #os?
from psychopy import visual, core, event, gui, logging
from typing import Dict

#wczytywanie pliku konfiguracyjnego
konf: Dict = yaml.load(open('config.yaml', encoding='utf-8'), Loader=yaml.SafeLoader)

def check_exit(key='f7'):  # przerwanie badania za pomocą klawisza F7
    stop = event.getKeys(keyList=[key])
    if len(stop) > 0:
        win.close()
        core.quit()

#okno dialogowe zbierające dane o badanym
info = {"Identyfikator": "", "Wiek": "", "Płeć": ["Mężczyzna", "Kobieta", "Inne"]}
infoDlg = gui.DlgFromDict(dictionary=info, title="Informacje o badanym")
if not infoDlg.OK:
    core.quit()

def read_text_from_file(file_name: str, insert: str = '') -> str: #czytanie plików, np. komunikatów
    if not isinstance(file_name, str):
        logging.error('Problem with file reading, filename must be a string')
        raise TypeError('file_name must be a string')
    msg = list()
    with codecs.open(file_name, encoding='utf-8', mode='r') as data_file:
        for line in data_file:
            if not line.startswith('#'):
                if line.startswith('<--insert-->'):
                    if insert:
                        msg.append(insert)
                else:
                    msg.append(line)
    return ''.join(msg)

def show_info(win, file_name, insert=''):  # wyświetlanie komunikatów
    msg = read_text_from_file(file_name, insert=insert)
    tekst = visual.TextStim(win, font = "Courier New", color=konf['kolor_czcionki'], text=msg) #height=???, wrapWidth =???
    tekst.draw()
    win.flip()
    key = event.waitKeys(keyList=['space'])
    check_exit(key='f7')
    win.flip()

def punkt_fiksacji():
    krzyzyk = visual.TextStim(win, font="Courier New", color=konf['kolor_fiks_dom'], text="+") #kolory w pliku config
    krzyzyk.draw()
    win.flip()

#def maska():
#    litery = random.choices(string.ascii_uppercase, k=5)
#    Maska = visual.TextStim(win, font="Courier New", color='white', text=''.join(litery))
#    return Maska
# ostatecznie nieużywane?


test=[[1,1],[1,4],[1,6],[1,9],[4,1],[4,4],[4,6],[4,9],[6,1],[6,4],[6,6],[6,9],[9,1],[9,4],[9,6],[9,9]]
wyniki=[]
win = visual.Window(konf['ekran_rozdz'], color=konf['kolor_tla'], fullscr=True)

show_info(win, r"C:\Users\myast\OneDrive\Pulpit\procedura\start.txt")
show_info(win, r"C:\Users\myast\OneDrive\Pulpit\procedura\before_training.txt")
# sesja treningowa
for liczba_klatek in range(konf['czas_fiksacji_dom']):
    punkt_fiksacji('white')
for i in range(konf['ile_prob_tren']-1):
    litery = random.choices(string.ascii_uppercase, k=5)
    Maska = visual.TextStim(win, font="Courier New", color=konf['kolor_czcionki'], text=''.join(litery))
    for liczba_klatek in range(konf['czas_maski']):
        Maska.draw()
        win.flip()
    t=random.sample(test,1)
    test.remove(t[0])
    Pryma = visual.TextStim(win, font="Courier New", color=konf['kolor_czcionki'], text=t[0][0])
    Cel = visual.TextStim(win, font="Courier New", color=konf['kolor_czcionki'], text=t[0][1])
    for liczba_klatek in range(konf['czas_pryma']):
        Pryma.draw()
        win.flip()
    for liczba_klatek in range(konf['czas_maski']):
        Maska.draw()
        win.flip()
    clock=core.Clock()
    win.callOnFlip(clock.reset)
    Cel.draw()
    win.flip()
    keys = event.waitKeys(keyList = [konf['znak_mniejszy'],konf['znak_wiekszy']])
    rt=clock.getTime()
    wyniki.append(rt)
    if t[0][1]==6 or t[0][1]==9:
        if keys[0]=='j':
            for liczba_klatek in range(18):
                punkt_fiksacji('green')
            wyniki.append('1')
        elif keys[0]=='f':
            for liczba_klatek in range(18):
                punkt_fiksacji('red')
            wyniki.append('0')
    elif t[0][1]==1 or t[0][1]==4:
        if keys[0]=='f':
            for liczba_klatek in range(18):
                punkt_fiksacji('green')
            wyniki.append('1')
        else:
            for liczba_klatek in range(18):
                punkt_fiksacji('red')
            wyniki.append('0')
    for liczba_klatek in range(18):
        punkt_fiksacji('white')
print(wyniki)


eksp=[1,2,3,4,6,7,8,9]
wynikireakcja=[]
wynikipopr=[]
wynikiwar=[]
show_info(win, r"C:\Users\myast\OneDrive\Pulpit\procedura\before_experiment.txt")

for j in range(0, 4):
    show_info(win, r"C:\Users\myast\OneDrive\Pulpit\procedura\przerwa.txt" )
    keys2 = event.waitKeys(keyList = ['space'])
    for i in range(0,3):
        for liczba_klatek in range(36):
            punkt_fiksacji('white')
        litery = random.choices(string.ascii_uppercase, k=5)
        Maska = visual.TextStim(win, font="Courier New", color='white', text=''.join(litery))
        for liczba_klatek in range(4):
            Maska.draw()
            win.flip()
        p=random.sample(eksp,1)
        c=random.sample(eksp,1)
        Pryma = visual.TextStim(win, font="Courier New", color='white', text=p[0])
        Cel = visual.TextStim(win, font="Courier New", color='white', text=c[0])
        for liczba_klatek in range(20):
            Pryma.draw()
            win.flip()
        for liczba_klatek in range(4):
            Maska.draw()
            win.flip()
        clock=core.Clock()
        win.callOnFlip(clock.reset)
        Cel.draw()
        win.flip()
        keys = event.waitKeys(keyList = ['f','j'])     
        rt=clock.getTime()
        wynikireakcja.append(rt)
        if c[0]>5:
            if keys[0]=='j':
                wynikipopr.append('1')
            elif keys[0]=='f':
                wynikipopr.append('0')
            if p[0]>5:
                wynikiwar.append('zgodny')
            elif p[0]<5:
                wynikiwar.append('niezgodny')
        elif c[0]<5:
            if keys[0]=='f':
                wynikipopr.append('1')
            else:
                wynikipopr.append('0')
            if p[0]>5:
                wynikiwar.append('niezgodny')
            elif p[0]<5:
                wynikiwar.append('zgodny')
print(wynikireakcja, wynikipopr, wynikiwar)

part_id = "{Identyfikator}_{Wiek}_{Płeć}".format(**info)
with open(f'{part_id}.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Czas reakcji", "Poprawność", "Warunek"])
    for r, p, w in zip(wynikireakcja, wynikipopr, wynikiwar):
        writer.writerow([r, p, w])
show_info(win, r"C:\Users\myast\OneDrive\Pulpit\procedura\end.txt")

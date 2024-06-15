# !/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import yaml
import atexit
import codecs
import random
import string

from os.path import join
from typing import Dict, List
from psychopy import core, event, gui, logging, visual


@atexit.register
def zapisz_wyniki_beh() -> None:
    nazwa_zapisanego = ID_SESJI + '_' + str(random.choice(range(100, 1000))) + '_beh.csv'
    with open(join('results', nazwa_zapisanego), 'w', encoding='utf-8') as beh_file:
        beh_writer = csv.writer(beh_file)
        beh_writer.writerows(WYNIKI)
    logging.flush()


def przerwij_z_bledem(err: str) -> None:
    logging.critical(err)
    raise Exception(err)


def wczytaj_tekst_z_pliku(nazwa_zapisanego: str, insert: str = '') -> str:
    if not isinstance(nazwa_zapisanego, str):
        logging.error('Problem z odczytaniem pliku. Nazwa pliku musi być ciagiem znakow.')
        raise TypeError('nazwa_zapisanego musi byc ciagiem znakow')
    msg = list()
    with codecs.open(nazwa_zapisanego, encoding='utf-8', mode='r') as data_file:
        for line in data_file:
            if not line.startswith('#'):
                if line.startswith('<--insert-->'):
                    if insert:
                        msg.append(insert)
                else:
                    msg.append(line)
    return ''.join(msg)


def pokaz_info(win: visual.Window, nazwa_zapisanego: str, insert: str = '') -> None:
    msg = wczytaj_tekst_z_pliku(nazwa_zapisanego, insert=insert)
    msg = visual.TextStim(win, font='Courier New', color=konf['KOLOR_CZCIONKI'], text=msg, height=40, wrapWidth=1500)
    msg.draw()
    win.flip()
    key = event.waitKeys(keyList=['f7', 'space'])
    if key == ['f7']:
        przerwij_z_bledem('Eksperyment zostal zakonczony przez badanego. Wcisnieto F7.')
    win.flip()


def czy_przerwano(key: str = 'f7') -> None:
    stop = event.getKeys(keyList=[key])
    if stop:
        przerwij_z_bledem('Eksperyment zostal zakonczony przez badanego. Wcisnieto {}.'.format(key))


def uruchom_probe(win, konf, zegar, fiks, pryma, cel, maska, wartosci, czy_treningowa=0):
    # Przygotowanie bodźców losowych
    litery_maska = random.choices(string.ascii_uppercase, k=5)

    # Losowanie odbywa się inaczej dla sesji treningowej i eksperymentalnej
    if czy_treningowa == 1:  # dla sesji treningowej
        para = random.choice(wartosci)  # wylosowanie pary pryma-cel z dostępnych możliwośći
        wart_pryma = para[0]
        wart_cel = para[1]
        wartosci.remove(para)  # losowanie bez zwracania
    else:
        wart_pryma = random.choice(wartosci)  # w części eksperymentalnej losujemy ze zwracaniem
        wart_cel = random.choice(wartosci)

    # Pre-trial
    maska.text = ''.join(litery_maska)
    pryma.text = wart_pryma
    cel.text = wart_cel

    # === Start trial ===
    for ile_klatek in range(konf['CZAS_FIKS']):
        fiks.draw()
        win.flip()
    for ile_klatek in range(konf['CZAS_MASKA']):
        maska.draw()
        win.flip()
    for ile_klatek in range(konf['CZAS_PRYMA']):
        pryma.draw()
        win.flip()
    for ile_klatek in range(konf['CZAS_MASKA']):
        maska.draw()
        win.flip()
    win.callOnFlip(zegar.reset)
    for ile_klatek in range(konf['CZAS_CEL']):
        cel.draw()
        win.flip()
    win.flip()

    klawisz = event.waitKeys(keyList=[konf['ZNAK_MNIEJSZY'], konf['ZNAK_WIEKSZY']], maxWait=konf['CZAS_OCZEKIW'])
    czas_reakcji = zegar.getTime()
    if not klawisz:
        klawisz = ['brak']  # jeśli badany niczego nie wciśnie na czas

    czy_poprawny = 0
    # poprawna reakcja, gdy dla celów większych od 5 badany wciśnie klawisz dla większych i analogicznie dla mniejszych
    if (wart_cel < 5 and klawisz[0] == konf['ZNAK_MNIEJSZY']) or (wart_cel > 5 and klawisz[0] == konf['ZNAK_WIEKSZY']):
        czy_poprawny = 1

    if czy_treningowa == 1:
        if czy_poprawny == 1:  # uczestnicy otrzymują feedback w postaci zmiany koloru punktu fiksacji
            fiks.color = konf['KOLOR_FIKS_ZGOD']
        else:
            fiks.color = konf['KOLOR_FIKS_NZGOD']
        return wartosci, czy_poprawny, wart_pryma, wart_cel

    else:  # w części eksperymentalnej interesuje nas także zgodność i czas reakcji
        czy_zgodny = 0
        # bodziec zgodny, gdy pryma i cel są obie większe lub mniejsze od 5
        if (wart_pryma < 5 and wart_cel < 5) or (wart_pryma > 5 and wart_cel > 5):
            czy_zgodny = 1
        return czas_reakcji, czy_zgodny, czy_poprawny, wart_pryma, wart_cel


# ZMIENNE GLOBALNE


WYNIKI = list()
WYNIKI.append(['ID_SESJI', 'Rodzaj sesji', 'Numer części', 'Numer próby', 'Pryma', 'Cel', 'Zgodność', 'Poprawność',
               'Czas reakcji'])  # Nagłówek wyników
ID_SESJI = ''
EKRAN_ROZDZ = []

# === Dialog popup ===
info: Dict = {'Identyfikator': '', 'Wiek': '', 'Plec': ['Mezczyzna', 'Kobieta', 'Inne']}
dict_dlg = gui.DlgFromDict(dictionary=info, title='Informacje o badanym')
if not dict_dlg.OK:
    przerwij_z_bledem('Zamknieto okno dialogowe.')

zegar = core.Clock()
konf: Dict = yaml.load(open('config.yaml', encoding='utf-8'), Loader=yaml.SafeLoader)
ekran_odsw: int = konf['EKRAN_ODSW']
EKRAN_ROZDZ: List[int] = konf['EKRAN_ROZDZ']
# === Scene init ===
win = visual.Window(EKRAN_ROZDZ, fullscr=True, units='pix', color=konf['KOLOR_TLA'])
event.Mouse(visible=False, newPos=None, win=win)

ID_SESJI = info['Identyfikator'] + info['Plec'] + info['Wiek']
logging.LogFile(join('results', f'{ID_SESJI}.log'), level=logging.INFO)
logging.info('Odswiezanie: {}'.format(ekran_odsw))
logging.info('Rozdzielczosc: {}'.format(EKRAN_ROZDZ))

# === Prepare stimulus here ===
fiks = visual.TextStim(win, text='+', height=50, color=konf['KOLOR_FIKS_DOM'], font='Courier New')
maska = visual.TextStim(win, height=50, color=konf['KOLOR_CZCIONKI'], font='Courier New')
pryma = visual.TextStim(win, height=50, color=konf['KOLOR_CZCIONKI'], font='Courier New')
cel = visual.TextStim(win, height=50, color=konf['KOLOR_CZCIONKI'], font='Courier New')

# === Training ===
pokaz_info(win, join('.', 'messages', 'start.txt'))
pokaz_info(win, join('.', 'messages', 'before_training.txt'))

wartosci = [[i, j] for i in konf['WART_TREN'] for j in konf['WART_TREN']]  # tworzenie wszystkich kombinacji pryma-cel
for numer_proby in range(konf['ILE_PROB_TREN']):
    wartosci, czy_poprawny, wart_pryma, wart_cel = uruchom_probe(win, konf, zegar, fiks, pryma, cel, maska, wartosci, 1)
    WYNIKI.append([ID_SESJI, 'treningowa', '-', numer_proby, '-', wart_pryma, wart_cel, '-', czy_poprawny, '-'])

# === Experiment ===
pokaz_info(win, join('.', 'messages', 'before_experiment.txt'))
fiks.color = konf['KOLOR_FIKS_DOM']  # przywrócenie domyślnego koloru punktu fiksacji
for numer_czesci in range(konf['ILE_CZESCI']):
    for numer_proby in range(konf['ILE_PROB_EKSP']):
        czas_reakcji, czy_zgodny, czy_poprawny, wart_pryma, wart_cel = uruchom_probe(win, konf, zegar, fiks, pryma, cel,
                                                                                     maska, konf['WART_EKSP'])
        WYNIKI.append(
            [ID_SESJI, 'eksperymentalna', numer_czesci, numer_proby, wart_pryma, wart_cel, czy_zgodny, czy_poprawny,
             czas_reakcji * 1000])
    win.flip()
    core.wait(1)
    pokaz_info(win, join('.', 'messages', 'break.txt'))

# === Zamykanie i czyszczenie ===
zapisz_wyniki_beh()
logging.flush()
pokaz_info(win, join('.', 'messages', 'end.txt'))
win.close()

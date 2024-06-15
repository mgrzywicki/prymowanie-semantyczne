# file_name to nazwa_zapisanego
# RESULTS to WYNIKI
# PART_ID to ID_SESJI
# save_beh_results to zapisz_wyniki_beh
# show_info to pokaz_info
# abort_with_error to przerwij_z_bledem
# read_text_from_file to wczytaj_tekst_z_pliku
# check_exit to czy_przerwano
# SCREEN_RES to EKRAN_ROZDZ
# run_trial to uruchom_probe
# trial_no to numer_proby

#!/usr/bin/env python
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


# Zapisywanie wyników w pliku z upewnieniem się, że wyniki zapiszą się nawet przy przerwaniu procedury.
@atexit.register
def zapisz_wyniki_beh() -> None:
    nazwa_zapisanego = ID_SESJI + '_' + str(random.choice(range(100, 1000))) + '_beh.csv' # nazwa_zapisanego: 
                                                                                          # nazwa pliku do zapisu danych
    with open(join('wyniki', nazwa_zapisanego), 'w', encoding='utf-8') as beh_file: # beh_file: ???
        beh_writer = csv.writer(beh_file) # beh_writer: ???
        beh_writer.writerows(WYNIKI)
    logging.flush()


# Przerywanie procedury z błędem.
def przerwij_z_bledem(err: str) -> None:
    logging.critical(err)
    raise Exception(err)


# Czytanie instrukcji z pliku. 
def wczytaj_tekst_z_pliku(nazwa_zapisanego: str, insert: str = '') -> str: # nazwa_zapisanego: nazwa pliku do odczytu
    if not isinstance(nazwa_zapisanego, str):
        logging.error(u'Problem z odczytaniem pliku. Nazwa pliku musi by\u107 ci\u105giem znak\uF3w.')
        raise TypeError(u'nazwa_zapisanego musi by\u107 ci\u105giem znak\uF3w.')
    msg = list() # msg: treść instrukcji
    with codecs.open(nazwa_zapisanego, encoding='utf-8', mode='r') as data_file: # data_file: ???
        for line in data_file:
            if not line.startswith('#'): # jeżeli linijka nie jest komentarzem
                if line.startswith('<--insert-->'):
                    if insert:
                        msg.append(insert)
                else:
                    msg.append(line)
    return ''.join(msg)


# Wyświetlanie instrukcji z pliku.
def pokaz_info(win: visual.Window, nazwa_zapisanego: str, insert: str = '') -> None: # nazwa_zapisanego: nazwa pliku do wyświetlenia
    msg = wczytaj_tekst_z_pliku(nazwa_zapisanego, insert=insert) # msg: treść instrukcji
    msg = visual.TextStim(win, font='Courier New', color=konf['KOLOR_CZCIONKI'], text=msg, height=40, wrapWidth=1000)
    msg.draw()
    win.flip()
    key = event.waitKeys(keyList=['f7', 'space'])
    if key == ['f7']:
        przerwij_z_bledem(u'Eksperyment zosta\u142 zako\u144czony przez badanego. Wci\u15Bni\u119to F7.')
    win.flip()


# Sprawdzenie czy nastąpiło przerwanie procedury poprzez naciśnięcie klawisza f7.
def czy_przerwano(key: str = 'f7') -> None:
    stop = event.getKeys(keyList=[key])
    if stop:
        przerwij_z_bledem(u'Eksperyment zosta\u142 zako\u144czony przez badanego. Wci\u15Bni\u119to {}.'.format(key))


# Uruchamianie próby badawczej.
def uruchom_probe(win, konf, zegar, fiks, pryma, cel, maska, wartosci, czy_treningowa=False):

    # Przygotowanie bodźców losowych.
    litery_maska = random.choices(string.ascii_uppercase, k=5)

    # Losowanie odbywa się inaczej dla sesji treningowej i eksperymentalnej.
    if (czy_treningowa==True): # dla sesji treningowej
        para = random.choice(wartosci) # wylosowanie pary pryma-cel z dostępnych możliwośći
        wart_pryma = para[0] # wart_pryma: ???
        wart_cel = para[1] # wart_cel: ???
        wartosci.remove(para) # losowanie bez zwracania
    else:
        wart_pryma = random.choice(wartosci) # w części eksperymentalnej losujemy ze zwracaniem
        wart_cel = random.choice(wartosci)

    # Przygotowanie do próby.
    maska.text = ''.join(litery_maska)
    pryma.text = wart_pryma
    cel.text = wart_cel

    # Wyświetlanie kolejnych bodźców.
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

    klawisz = event.waitKeys(keyList=[konf['ZNAK_MNIEJSZY'], konf['ZNAK_WIEKSZY']], maxWait=konf['CZAS_OCZEKIW']) 
    # klawisz: klawisz naciśnięty przez badanego
    czas_reakcji = zegar.getTime()

    # Określanie czy klawisz naciśnięty przez badanego był poprawny.
    czy_zgodny = 0
    if (wart_cel < 5 and klawisz == konf['ZNAK_MNIEJSZY']) or (wart_cel > 5 and klawisz == konf['ZNAK_WIEKSZY']):
        czy_zgodny = 1

    if czy_zgodny == 1:
        fiks.color = konf['KOLOR_FIKS_ZGOD'] # punkt fiksacji zmienia się na zielono
    else:
        fiks.color = konf['KOLOR_FIKS_NZGOD'] # punkt fiksacji zmienia się na czerwono

    if (czy_treningowa == True): # jeżeli sesja jest sesją treningową
        return wartosci, czy_zgodny, wart_pryma, wart_cel
    else: 
        return czas_reakcji, czy_zgodny


# ZMIENNE GLOBALNE


WYNIKI = list()
WYNIKI.append(['ID_SESJI', u'Numer pr\uF3by', 'Czas reakcji', u'Poprawno\u15B\u107'])  # nagłówek wyników
ID_SESJI = ''
EKRAN_ROZDZ = []

# Wyświetlanie okna dialogowego.
info: Dict = {'Identyfikator': '', 'Wiek': '', u'P\u142e\u107': [u'Me\u17Cczyzna', 'Kobieta', 'Inne']}
dict_dlg = gui.DlgFromDict(dictionary=info, title='Informacje o badanym.')
if not dict_dlg.OK:
    przerwij_z_bledem(u'Zamkni\u119to okno dialogowe.')

zegar = core.Clock()
konf: Dict = yaml.load(open('config.yaml', encoding='utf-8'), Loader=yaml.SafeLoader)
ekran_odsw: int = konf['EKRAN_ODSW']
EKRAN_ROZDZ: List[int] = konf['EKRAN_ROZDZ']
# === Scene init ===
win = visual.Window(EKRAN_ROZDZ, fullscr=True, units='pix', color=konf['KOLOR_TLA'])
event.Mouse(visible=False, newPos=None, win=win)

ID_SESJI = info['Identyfikator'] + info[u'P\u142e\u107'] + info['Wiek']
logging.LogFile(join('wyniki', f'{ID_SESJI}.log'), level=logging.INFO)
logging.info('Odswiezanie: {}'.format(ekran_odsw))
logging.info('Rozdzielczosc: {}'.format(EKRAN_ROZDZ))

# Przygotowanie bodźców.
fiks = visual.TextStim(win, text='+', height=50, color=konf['KOLOR_FIKS_DOM'], font='Courier New')
maska = visual.TextStim(win, height=50, color=konf['KOLOR_CZCIONKI'], font='Courier New')
pryma = visual.TextStim(win, height=50, color=konf['KOLOR_CZCIONKI'], font='Courier New')
cel = visual.TextStim(win, height=50, color=konf['KOLOR_CZCIONKI'], font='Courier New')

# Wyświetlanie instrukcji oraz sesja treningowa.
pokaz_info(win, join('.', 'messages', 'start.txt'))
pokaz_info(win, join('.', 'messages', 'before_training.txt'))

wartosci = [[i, j] for i in konf['WART_TREN'] for j in konf['WART_TREN']] # tworzenie listy wszystkich kombinacji pryma-cel
for ile_prob in range(konf['ILE_PROB_TREN']):
    wartosci, czy_zgodny, wart_pryma, wart_cel = uruchom_probe(win, konf, zegar, fiks, pryma, cel, maska, wartosci, True)
    WYNIKI.append([ID_SESJI, ile_prob, 'sesja treningowa', czy_zgodny, wart_pryma, wart_cel])

# Sesja eksperymentalna.
pokaz_info(win, join('.', 'messages', 'before_experiment.txt'))
numer_proby = 0
#for ile_czesci in range(konf['ILE_CZESCI']):
#    for ile_prob in range(konf['ILE_PROB_EKSP']):
#       uruchom_probe(win, konf, zegar, fiks, pryma, cel, maska, konf['WART_EKSP'])

# Zamykanie i czyszczenie.
zapisz_wyniki_beh()
logging.flush()
pokaz_info(win, join('.', 'messages', 'end.txt'))
win.close()

# file_name to nazwa_zapisanego
# RESULTS to WYNIKI
# PART_ID to ID_SESJI
# save_beh_results to zapisz_wyniki_beh
# show_info to pokaz_info
# abort_with_error to przerwij_z_bledem
# read_text_from_file to wczytaj_tekst_z_pliku
# check_exit to czy_przerwano
# SCREEN_RES to EKRAN_ROZDZ

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import yaml
import atexit
import codecs
import random

from os.path import join
from typing import Dict, List
from psychopy import core, event, gui, logging, visual


@atexit.register
def zapisz_wyniki_beh() -> None:
    nazwa_zapisanego = ID_SESJI + '_' + str(random.choice(range(100, 1000))) + '_beh.csv'
    with open(join('wyniki', nazwa_zapisanego), 'w', encoding='utf-8') as beh_file:
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
    msg = visual.TextStim(win, font='Courier New', color=konf['KOLOR_CZCIONKI'], text=msg, height=40, wrapWidth=1000)
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


# def run_trial(win, conf, clock, stim):
    '''
    1) przygotowanie bodźców losowych?
    2) stimsy: punkt fiksacji, teksty
    3) próba (draw, flip, reakcje)
    '''

# ZMIENNE GLOBALNE


WYNIKI = list()
WYNIKI.append(['ID_SESJI', 'Trial_no', 'Reaction time', 'Correctness'])  # Nagłówek wyników
ID_SESJI = ''
EKRAN_ROZDZ = []

# === Dialog popup ===
info: Dict = {'Identyfikator': '', 'Wiek': '', 'Plec': ['Mezczyzna', 'Kobieta', 'Inne']}
dict_dlg = gui.DlgFromDict(dictionary=info, title='Informacje o badanym')
if not dict_dlg.OK:
    przerwij_z_bledem('Zamknieto okno dialogowe.')

clock = core.Clock()
konf: Dict = yaml.load(open('config.yaml', encoding='utf-8'), Loader=yaml.SafeLoader)
ekran_odsw: int = konf['EKRAN_ODSW']
EKRAN_ROZDZ: List[int] = konf['EKRAN_ROZDZ']
# === Scene init ===
win = visual.Window(EKRAN_ROZDZ, fullscr=True, units='pix', color=konf['KOLOR_TLA'])
event.Mouse(visible=False, newPos=None, win=win)

ID_SESJI = info['Identyfikator'] + info['Plec'] + info['Wiek']
logging.LogFile(join('wyniki', f'{ID_SESJI}.log'), level=logging.INFO)
logging.info('Odswiezanie: {}'.format(ekran_odsw))
logging.info('Rozdzielczosc: {}'.format(EKRAN_ROZDZ))

# === Training ===
pokaz_info(win, join('.', 'messages', 'start.txt'))
pokaz_info(win, join('.', 'messages', 'before_training.txt'))

# === Zamykanie i czyszczenie ===
zapisz_wyniki_beh()
logging.flush()
pokaz_info(win, join('.', 'messages', 'end.txt'))
win.close()

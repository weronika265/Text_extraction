import os
import glob
import re
from clp3 import clp

from rules import rules
from roles import roles, roles_colors

# wyrazy dla rol, ktore wystapily w tekstach
roles_occurred = {
    'cel': [],
    'zdarzenie': [],
    'sprawca': [],
    'narzedzie': [],
    'miejsce': [],
    'obiekt': [],
}

# lista ze wszystkimi tekstami z podanego foldera
texts_list = []

# tekst ostateczny, pokolorowany
texts_processed = []

# role, ktore wystapily w poszczegolnych tekstach
roles_occurred_texts = []

# oceny dal poszczegolnych tekstow
text_ratings = []

# sciezka do folderu z plikami
dir = './teksty'


def file_to_text(file_path):
    '''
    Funkcja otwiera plik i sczytuje z niego tekst.
    file_path: pelna sciezka do folderu z plikiem
    Zwraca tekst z pliku.
    '''
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

        return text


def split_to_words(file_content):
    '''
    Funkcja dzieli tekst na poszczegolne slowa.
    file_content: zawartosc wskazanego pliku
    Zwraca tekst podzielony na slowa.
    '''
    file_content = file_content.replace('\n', ' ')
    words = re.split(r'(\W+)', file_content)

    return words


def init_roles_occurred(roles_occurred):
    '''
    Funkcja inicjalizuje listy dla rol w slowniku.
    roles_occurred: slownik przechowywujacy liste slow dla poszczegolnych rol z kazdego tekstu
    '''
    for role in roles_occurred:
        roles_occurred[role].append([])


def process_text(words, file_num):
    '''
    Funkcja przetwarza kolejne slowa wystepujace w tekscie.
    words: slowa z obecnie przetwarzanego pliku
    file_num: numer obecnie przetwarzanego pliku
    '''
    for i, word in enumerate(words):
        word_copy = word
        word_bform = None
        if has_special_characters(word):
            word_copy = strip_special_characters(word)
        # znajdz id dla formy podstawowej slowa
        word_id = clp(word_copy.lower())
        # jesli znaleziono forme podstawowa, zwroc ja
        if word_id:
            word_bform = clp.bform(word_id[0])
            
        for role, role_words in roles.items():
            # jesli znaleziono slowo w formie podstawowej i jest ono w slowach dla ktorejs z rol
            if word_bform and word_bform in role_words:
                # jesli slowo nie wystapilo jeszcze w rolach dla aktualnego tekstu, dodaj je
                if word_bform not in roles_occurred[role][file_num]:
                    roles_occurred[role][file_num].append(word_bform)
                # pokoloruj to slowo i podmien pod zwykle
                word_copy = "<span style='background-color: {}'>{}</span>".format(roles_colors[role], word)
                words[i] = word_copy
            # wpp jesli inne ('normalne') slowo znaleziono w ktorejs z rol
            elif word_copy in roles:
                if word_copy not in roles_occurred[role][file_num]:
                    roles_occurred[role][file_num].append(word)
                word_copy = "<span style='background-color: {}'>{}</span>".format(roles_colors[role], word)
                words[i] = word_copy


def get_roles_in_text(roles_occurred_uq, file_num):
    '''
    Funkcja zbiera unikalne role dla aktualnego tekstu.
    roles_occurred_uq: lista z unikalnymi rolami w tekscie
    file_num: numer obecnie przetwarzanego pliku
    '''
    for role in roles_occurred:
        # jesli w roli jest jakies slowo i rola wczesniej sie nie pojawila, dodaj ja
        if roles_occurred[role][file_num] and role not in roles_occurred_uq:
            roles_occurred_uq.append(role)
    # dodaj liste wszystkich unikalnych rol dla konkretnego pliku
    roles_occurred_texts.append(roles_occurred_uq)


# ocen tekst
def generate_rating(rules, roles_occurred_uq):
    '''
    Funkcja zapisuje ocene dla aktualnie przetwarzanego tekstu.
    rules: slownik z zestawami regul i ich ocena
    roles_occurred_uq: lista z unikalnymi rolami w tekscie
    '''
    # inicjalizuj ocene tekstu na 0.0 (jesli nie znajdzie reguly)
    text_ratings.append(0.0)
    for rule, rating in rules.items():
        # jesli znaleziono regule dla slow obecnych w aktualnym tekscie, dodaj ocene dla tego tekstu
        if set(rule) == set(roles_occurred_uq):
            text_ratings[-1] = rating
            break


def words_to_text(words):
    '''
    Funkcja laczy slowa w jeden ciag tekstowy.
    words: kolejene slowa z obecnie przetwarznago pliku
    '''
    file_content_final = ''.join(words)
    texts_processed.append(file_content_final)


def has_special_characters(word):
    '''
    Funkcja sprawdza, czy slowo zawiera znaki specialne.
    word: slowo do przetworzenia
    Zwraca informacje, czy slowo zawiera znaki specjalne.
    '''
    pattern = r'[^\w\s]'
    match = re.search(pattern, word)

    return match is not None


def strip_special_characters(word):
    '''
    Funkcja czysci slowa ze znakow specjalnych.
    word: slowo do przetworzenia
    Zwraca oczyszczone slowo.
    '''
    pattern = r'[^a-zA-Z0-9\s]'
    stripped_word = re.sub(pattern, '', word)

    return stripped_word


# main fn
def analyse_files(dir):
    '''
    Funkcja analizuje teksty, ocenia prawdopodobienstwo nalezenia do tematyki, koloruje wystapienia wybranych slow i wypisuje je jako przypisane do roli.
    dir: wskazany folder z plikami
    '''
    # sortuj pliki po nazwie
    list_of_files = sorted(filter(os.path.isfile, glob.glob(dir + '/*.txt')))

    file_num = 0
    # analizuj kolejne pliki
    for file_path in list_of_files:
        file_content = file_to_text(file_path)
        # dodaj 'czysty' tekst do listy ze wszystkimi tekstami
        texts_list.append(file_content)

        words = split_to_words(file_content)

        init_roles_occurred(roles_occurred)

        process_text(words, file_num)
        
        roles_occurred_uq = []
        get_roles_in_text(roles_occurred_uq, file_num)

        generate_rating(rules, roles_occurred_uq)

        words_to_text(words)

        file_num += 1

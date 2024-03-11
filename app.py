from flask import Flask, render_template

from analyse_files import *

app = Flask(__name__)


@app.route('/')
def index():
    '''
    Funkcja laczy dane o numerach plikow, ich zawartosci, pojawiajacych sie slow dla rol i ocenach.
    Zwraca render szablonu z danymi do wyswietlenia.
    '''
    combined_data = [(
        index, 
        content, 
        roles_occurred['cel'][index], 
        roles_occurred['zdarzenie'][index], 
        roles_occurred['sprawca'][index], 
        roles_occurred['narzedzie'][index], 
        roles_occurred['miejsce'][index], 
        roles_occurred['obiekt'][index],
        text_ratings[index]
        ) for index, content in enumerate(texts_processed)]    
    
    return render_template('index.html', combined_data=combined_data)
    

@app.route('/texts')
def show_texts():
    '''
    Funkcja zwraca teksty do iteracji.
    Zwraca render szablonu z danymi do wyswietlenia.
    '''
    texts = enumerate(texts_list)

    return render_template('texts.html', texts=texts)


@app.route('/roles')
def show_roles():
    '''
    Zwraca render szablonu z danymi do wyswietlenia.
    '''
    return render_template('roles.html', roles=roles)


@app.route('/rules')
def show_rules():
    '''
    Funkcja sortuje reguly z ocenami w kolejnosci malejacej.
    Zwraca render szablonu z danymi do wyswietlenia.
    '''
    rules_desc = sorted(rules.items(), key=lambda x: x[1], reverse=True)

    return render_template('rules.html', rules=rules_desc)


# uruchom program i otworz wyniki na wskazanym hoscie i porcie
if __name__ == '__main__':
    analyse_files(dir)

    app.run(host='wierzba.wzks.uj.edu.pl', port=5249, debug=True)

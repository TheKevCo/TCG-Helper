from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re
import random

app = Flask(__name__)
Bootstrap(app)

# dynamic year for footer
now = datetime.now()  # current date and time
year = now.strftime("%Y")


@app.route("/")
def home():
    return render_template('index.html', year=year)


@app.route("/v1/documentation", methods=["GET", "POST"])
def documentation():
    if request.method == "POST":
        response = requests.get('https://www.justinbasil.com/guide/meta', verify=False)
        meta_web_page = response.text
        soup = BeautifulSoup(meta_web_page, "html.parser")
        titles = soup.find_all('h2')

        for n in range(0, len(titles)):
            titles[n] = titles[n].getText()

        # grabs text for Pokémon cards and removes unnecessary spaces
        decks = soup.find_all("p", attrs={"style": "white-space:pre-wrap;"})

        poke_text = "Pokémon -"
        trainer_text = "Trainer Cards -"
        energy_text = "Energy -"

        text_list = [poke_text, trainer_text, energy_text]

        # this removes all the html tags using regex
        html_pattern = '<[^<]+?>'
        raw_text_poke = []
        raw_text_trainer = []
        raw_text_energy = []
        raw_text_list = [raw_text_poke, raw_text_trainer, raw_text_energy]
        for deck in decks:
            string_text = str(deck)
            for n in range(3):
                if text_list[n] in string_text:
                    outputString = re.sub(html_pattern, " ", string_text)
                    raw_text_list[n].append(outputString)

        # this removes blank spaces left from html text above.
        corrected_list_poke = [re.split("\s", lists) for lists in raw_text_poke]
        corrected_list_trainer = [re.split("\s", lists) for lists in raw_text_trainer]
        corrected_list_energy = [re.split("\s", lists) for lists in raw_text_energy]
        corrected_list_all = [corrected_list_poke, corrected_list_trainer, corrected_list_energy]
        for lists in corrected_list_all:
            for deck in lists:
                for string in deck:
                    if string == "":
                        deck.remove(string)

        # this takes the list of strings and places them back into one string for more regex separation below
        poke_strings = []
        trainer_strings = []
        energy_strings = []
        all_strings = [poke_strings, trainer_strings, energy_strings]
        for n in range(3):
            for deck_lists in corrected_list_all[n]:
                final_string = ""
                if n == 1:
                    for i in range(4, len(deck_lists)):
                        if i == len(deck_lists) - 1:
                            final_string += f"{deck_lists[i]}"
                        else:
                            final_string += f"{deck_lists[i]} "
                    all_strings[n].append(final_string)
                else:
                    for i in range(3, len(deck_lists)):
                        if i == len(deck_lists) - 1:
                            final_string += f"{deck_lists[i]}"
                        else:
                            final_string += f"{deck_lists[i]} "
                    all_strings[n].append(final_string)

        # uses re.findall to create a list of all the cards that were once in one long string.
        # utilized https://www.youtube.com/watch?v=K8L6KVGG-7o&t=2145s to help my brain
        final_poke = []
        final_trainer = []
        final_energy = []
        final_card_list = [final_poke, final_trainer, final_energy]
        for n in range(3):
            for cards in all_strings[n]:
                pattern = re.compile(r"\d[-a-zA-Z'é\s]+\d+")
                card_list = re.findall(pattern, cards)
                final_card_list[n].append(card_list)

        # create dictionaries for json
        final_json_list = []
        card_decks = {}
        for k in range(len(titles)):  # this is the number of decks within the website.
            pokemon_dict = {}
            trainer_dict = {}
            energy_dict = {}
            card_dicts = [pokemon_dict, trainer_dict, energy_dict]
            for i in range(3):  # for each set of cards.
                for n in range(len(final_card_list[i][k])):
                    card_dicts[i][f"{n + 1}"] = final_card_list[i][k][n]
            card_decks[k + 1] = {
                "Deck": titles[k],
                "Pokémon Cards": pokemon_dict,
                "Trainer Cards": trainer_dict,
                "Energy Cards": energy_dict,

            }
        search_text = request.form.get("searchtext").lower()
        range_number = len(titles) - 1
        for r in range(0, range_number):
            if search_text in titles[r].lower():
                return jsonify(Deck=card_decks[r + 1])
        return jsonify(error={
            "Not Found": "Sorry, this was not found in current Meta "
                         "List, try utilizing /decklist GET Request"
        })
    return render_template('documentation.html', year=year)


@app.route("/v1/search", methods=["GET"])
def search():
    response = requests.get('https://www.justinbasil.com/guide/meta', verify=False)
    meta_web_page = response.text
    soup = BeautifulSoup(meta_web_page, "html.parser")
    titles = soup.find_all('h2')

    for n in range(0, len(titles)):
        titles[n] = titles[n].getText()

    # grabs text for Pokémon cards and removes unnecessary spaces
    decks = soup.find_all("p", attrs={"style": "white-space:pre-wrap;"})

    poke_text = "Pokémon -"
    trainer_text = "Trainer Cards -"
    energy_text = "Energy -"

    text_list = [poke_text, trainer_text, energy_text]

    # this removes all the html tags using regex
    html_pattern = '<[^<]+?>'
    raw_text_poke = []
    raw_text_trainer = []
    raw_text_energy = []
    raw_text_list = [raw_text_poke, raw_text_trainer, raw_text_energy]
    for deck in decks:
        string_text = str(deck)
        for n in range(3):
            if text_list[n] in string_text:
                outputString = re.sub(html_pattern, " ", string_text)
                raw_text_list[n].append(outputString)

    # this removes blank spaces left from html text above.
    corrected_list_poke = [re.split("\s", lists) for lists in raw_text_poke]
    corrected_list_trainer = [re.split("\s", lists) for lists in raw_text_trainer]
    corrected_list_energy = [re.split("\s", lists) for lists in raw_text_energy]
    corrected_list_all = [corrected_list_poke, corrected_list_trainer, corrected_list_energy]
    for lists in corrected_list_all:
        for deck in lists:
            for string in deck:
                if string == "":
                    deck.remove(string)

    # this takes the list of strings and places them back into one string for more regex separation below
    poke_strings = []
    trainer_strings = []
    energy_strings = []
    all_strings = [poke_strings, trainer_strings, energy_strings]
    for n in range(3):
        for deck_lists in corrected_list_all[n]:
            final_string = ""
            if n == 1:
                for i in range(4, len(deck_lists)):
                    if i == len(deck_lists) - 1:
                        final_string += f"{deck_lists[i]}"
                    else:
                        final_string += f"{deck_lists[i]} "
                all_strings[n].append(final_string)
            else:
                for i in range(3, len(deck_lists)):
                    if i == len(deck_lists) - 1:
                        final_string += f"{deck_lists[i]}"
                    else:
                        final_string += f"{deck_lists[i]} "
                all_strings[n].append(final_string)

    # uses re.findall to create a list of all the cards that were once in one long string.
    # utilized https://www.youtube.com/watch?v=K8L6KVGG-7o&t=2145s to help my brain
    final_poke = []
    final_trainer = []
    final_energy = []
    final_card_list = [final_poke, final_trainer, final_energy]
    for n in range(3):
        for cards in all_strings[n]:
            pattern = re.compile(r"\d[-a-zA-Z'é\s]+\d+")
            card_list = re.findall(pattern, cards)
            final_card_list[n].append(card_list)

    # create dictionaries for json
    final_json_list = []
    card_decks = {}
    for k in range(len(titles)):  # this is the number of decks within the website.
        pokemon_dict = {}
        trainer_dict = {}
        energy_dict = {}
        card_dicts = [pokemon_dict, trainer_dict, energy_dict]
        for i in range(3):  # for each set of cards.
            for n in range(len(final_card_list[i][k])):
                card_dicts[i][f"{n + 1}"] = final_card_list[i][k][n]
        card_decks[k + 1] = {
            "Deck": titles[k],
            "Pokémon Cards": pokemon_dict,
            "Trainer Cards": trainer_dict,
            "Energy Cards": energy_dict,

        }
    query = request.args.get("query")
    range_number = len(titles) - 1
    for r in range(0, range_number):
        if query in titles[r].lower():
            return jsonify(Deck=card_decks[r + 1])
    return jsonify(error={
        "Not Found": "Sorry, this was not found in current Meta "
                     "List, try utilizing /decklist GET Request"
    })


@app.route("/v1/decklist", methods=["GET"])
def deck_list():
    if request.method == "GET":
        response = requests.get('https://www.justinbasil.com/guide/meta', verify=False)
        meta_web_page = response.text
        soup = BeautifulSoup(meta_web_page, "html.parser")
        titles = soup.find_all('h2')

        for n in range(0, len(titles)):
            titles[n] = titles[n].getText()

        card_titles = {}
        for i in range(len(titles)):
            card_titles[f"{i + 1}"] = str(titles[i])

        decklist = {
            "IDs": card_titles
        }
    return jsonify(Decks=decklist)


@app.route("/v1/random", methods=["GET"])
def random_deck():
    if request.method == "GET":
        response = requests.get('https://www.justinbasil.com/guide/meta', verify=False)
        meta_web_page = response.text
        soup = BeautifulSoup(meta_web_page, "html.parser")
        titles = soup.find_all('h2')

        for n in range(0, len(titles)):
            titles[n] = titles[n].getText()

        # grabs text for Pokémon cards and removes unnecessary spaces
        decks = soup.find_all("p", attrs={"style": "white-space:pre-wrap;"})

        poke_text = "Pokémon -"
        trainer_text = "Trainer Cards -"
        energy_text = "Energy -"

        text_list = [poke_text, trainer_text, energy_text]

        # this removes all the html tags using regex
        html_pattern = '<[^<]+?>'
        raw_text_poke = []
        raw_text_trainer = []
        raw_text_energy = []
        raw_text_list = [raw_text_poke, raw_text_trainer, raw_text_energy]
        for deck in decks:
            string_text = str(deck)
            for n in range(3):
                if text_list[n] in string_text:
                    outputString = re.sub(html_pattern, " ", string_text)
                    raw_text_list[n].append(outputString)

        # this removes blank spaces left from html text above.
        corrected_list_poke = [re.split("\s", lists) for lists in raw_text_poke]
        corrected_list_trainer = [re.split("\s", lists) for lists in raw_text_trainer]
        corrected_list_energy = [re.split("\s", lists) for lists in raw_text_energy]
        corrected_list_all = [corrected_list_poke, corrected_list_trainer, corrected_list_energy]
        for lists in corrected_list_all:
            for deck in lists:
                for string in deck:
                    if string == "":
                        deck.remove(string)

        # this takes the list of strings and places them back into one string for more regex separation below
        poke_strings = []
        trainer_strings = []
        energy_strings = []
        all_strings = [poke_strings, trainer_strings, energy_strings]
        for n in range(3):
            for deck_lists in corrected_list_all[n]:
                final_string = ""
                if n == 1:
                    for i in range(4, len(deck_lists)):
                        if i == len(deck_lists) - 1:
                            final_string += f"{deck_lists[i]}"
                        else:
                            final_string += f"{deck_lists[i]} "
                    all_strings[n].append(final_string)
                else:
                    for i in range(3, len(deck_lists)):
                        if i == len(deck_lists) - 1:
                            final_string += f"{deck_lists[i]}"
                        else:
                            final_string += f"{deck_lists[i]} "
                    all_strings[n].append(final_string)

        # uses re.findall to create a list of all the cards that were once in one long string.
        # utilized https://www.youtube.com/watch?v=K8L6KVGG-7o&t=2145s to help my brain
        final_poke = []
        final_trainer = []
        final_energy = []
        final_card_list = [final_poke, final_trainer, final_energy]
        for n in range(3):
            for cards in all_strings[n]:
                pattern = re.compile(r"\d[-a-zA-Z'é\s]+\d+")
                card_list = re.findall(pattern, cards)
                final_card_list[n].append(card_list)

        # create dictionaries for json
        final_json_list = []
        card_decks = {}
        for k in range(len(titles)):  # this is the number of decks within the website.
            pokemon_dict = {}
            trainer_dict = {}
            energy_dict = {}
            card_dicts = [pokemon_dict, trainer_dict, energy_dict]
            for i in range(3):  # for each set of cards.
                for n in range(len(final_card_list[i][k])):
                    card_dicts[i][f"{n + 1}"] = final_card_list[i][k][n]
            card_decks[k + 1] = {
                "Deck": titles[k],
                "Pokémon Cards": pokemon_dict,
                "Trainer Cards": trainer_dict,
                "Energy Cards": energy_dict,

            }
        choice = random.randint(1, len(card_decks))

    return jsonify(Deck=card_decks[choice])


@app.route("/v1/all", methods=["GET"])
def all_decks():
    if request.method == "GET":
        response = requests.get('https://www.justinbasil.com/guide/meta', verify=False)
        meta_web_page = response.text
        soup = BeautifulSoup(meta_web_page, "html.parser")
        titles = soup.find_all('h2')

        for n in range(0, len(titles)):
            titles[n] = titles[n].getText()

        # grabs text for Pokémon cards and removes unnecessary spaces
        decks = soup.find_all("p", attrs={"style": "white-space:pre-wrap;"})

        poke_text = "Pokémon -"
        trainer_text = "Trainer Cards -"
        energy_text = "Energy -"

        text_list = [poke_text, trainer_text, energy_text]

        # this removes all the html tags using regex
        html_pattern = '<[^<]+?>'
        raw_text_poke = []
        raw_text_trainer = []
        raw_text_energy = []
        raw_text_list = [raw_text_poke, raw_text_trainer, raw_text_energy]
        for deck in decks:
            string_text = str(deck)
            for n in range(3):
                if text_list[n] in string_text:
                    outputString = re.sub(html_pattern, " ", string_text)
                    raw_text_list[n].append(outputString)

        # this removes blank spaces left from html text above.
        corrected_list_poke = [re.split("\s", lists) for lists in raw_text_poke]
        corrected_list_trainer = [re.split("\s", lists) for lists in raw_text_trainer]
        corrected_list_energy = [re.split("\s", lists) for lists in raw_text_energy]
        corrected_list_all = [corrected_list_poke, corrected_list_trainer, corrected_list_energy]
        for lists in corrected_list_all:
            for deck in lists:
                for string in deck:
                    if string == "":
                        deck.remove(string)

        # this takes the list of strings and places them back into one string for more regex separation below
        poke_strings = []
        trainer_strings = []
        energy_strings = []
        all_strings = [poke_strings, trainer_strings, energy_strings]
        for n in range(3):
            for deck_lists in corrected_list_all[n]:
                final_string = ""
                if n == 1:
                    for i in range(4, len(deck_lists)):
                        if i == len(deck_lists) - 1:
                            final_string += f"{deck_lists[i]}"
                        else:
                            final_string += f"{deck_lists[i]} "
                    all_strings[n].append(final_string)
                else:
                    for i in range(3, len(deck_lists)):
                        if i == len(deck_lists) - 1:
                            final_string += f"{deck_lists[i]}"
                        else:
                            final_string += f"{deck_lists[i]} "
                    all_strings[n].append(final_string)

        # uses re.findall to create a list of all the cards that were once in one long string.
        # utilized https://www.youtube.com/watch?v=K8L6KVGG-7o&t=2145s to help my brain
        final_poke = []
        final_trainer = []
        final_energy = []
        final_card_list = [final_poke, final_trainer, final_energy]
        for n in range(3):
            for cards in all_strings[n]:
                pattern = re.compile(r"\d[-a-zA-Z'é\s]+\d+")
                card_list = re.findall(pattern, cards)
                final_card_list[n].append(card_list)

        # create dictionaries for json
        final_json_list = []
        card_decks = {}
        for k in range(len(titles)):  # this is the number of decks within the website.
            pokemon_dict = {}
            trainer_dict = {}
            energy_dict = {}
            card_dicts = [pokemon_dict, trainer_dict, energy_dict]
            for i in range(3):  # for each set of cards.
                for n in range(len(final_card_list[i][k])):
                    card_dicts[i][f"{n + 1}"] = final_card_list[i][k][n]
            card_decks[k + 1] = {
                "Deck": titles[k],
                "Pokémon Cards": pokemon_dict,
                "Trainer Cards": trainer_dict,
                "Energy Cards": energy_dict,

            }

    return jsonify(Deck=card_decks)


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask_wtf import FlaskForm
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)
Bootstrap(app)

now = datetime.now()  # current date and time
year = now.strftime("%Y")


@app.route("/")
def home():
    return render_template('index.html', year=year)


@app.route("/documentation", methods=["GET"])
def documentation():
    if request.method == "GET":
        response = requests.get('https://www.justinbasil.com/guide/meta')
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
                    output_string = re.sub(html_pattern, " ", string_text)
                    raw_text_list[n].append(output_string)

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
            for deck_list in corrected_list_all[n]:
                final_string = ""
                if n == 1:
                    for i in range(4, len(deck_list)):
                        if i == len(deck_list) - 1:
                            final_string += f"{deck_list[i]}"
                        else:
                            final_string += f"{deck_list[i]} "
                    all_strings[n].append(final_string)
                else:
                    for i in range(3, len(deck_list)):
                        if i == len(deck_list) - 1:
                            final_string += f"{deck_list[i]}"
                        else:
                            final_string += f"{deck_list[i]} "
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

        return jsonify(deck={
            # add json stuff later
        })
    return render_template('documentation.html')


if __name__ == "__main__":
    app.run(debug=True)

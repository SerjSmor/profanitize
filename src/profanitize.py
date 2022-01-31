import re
from typing import List, Tuple, Union
import random

import en_core_web_sm

nlp = en_core_web_sm.load()


INTERJECTION = "interjection"

curses = {
    "fuck": {"noun": "fuck", "adverb": "fucking", "interjection": "Fuck!", "adjective": "fucked", "verb": "fucked"},
    "shit": {"noun": "shit", "interjection": ["Shit!", "Crap!"], "adjective": "shitty"},
    "damn": {"interjection": ["Damn!", "Dang!", "Damn it!"], "adjective": "damn"},
    "bloody": {"interjection": "Bloody hell!", "adverb": "bloody"},
    "dick": {"adjective": "a dick"}
}

# improve this by detecting tenses: https://stackoverflow.com/questions/3434144/detect-english-verb-tenses-using-nltk

# according to spacy parts of speech: https://melaniewalsh.github.io/Intro-Cultural-Analytics/05-Text-Analysis/13-POS-Keywords.html
positions_to_insert_positions = {
    "ADJ": "adverb",
    "AUX": "adverb",
    # "PRON": "adverb", # this one doesn't work too good as the order
    "NOUN": "adjective",
    "VERB": "adverb",
    "DET": "adjective" # a, the

}

def profanitize(input_str: str, random_state: int = None) -> str:
    if random_state is not None:
        random.seed(random_state)
    # detect all pos - random if it's
    document = nlp(input_str)

    possible_tokens: List[Tuple[int, str]] = []

    for i, token in enumerate(document):
        if token.pos_ in positions_to_insert_positions.keys():
            possible_tokens.append((i, token.pos_,))
    if len(possible_tokens) == 0:
        return ""

    # random the position of insert
    random.shuffle(possible_tokens)
    token_index = 0
    chosen_part_of_speech = possible_tokens[token_index][1]
    augmented_part_of_speech = positions_to_insert_positions[chosen_part_of_speech]
    # random the augmentation
    all_augmentations = list(curses.values())
    random.shuffle(all_augmentations)
    shuffled_augmentations = all_augmentations
    chosen_word = ""
    for position_to_word_list in shuffled_augmentations:
        curr_parts_of_speech = position_to_word_list.keys()
        if augmented_part_of_speech in curr_parts_of_speech:
            value = position_to_word_list[augmented_part_of_speech]
            if type(value) == list:
                chosen_word = random.shuffle(value)[0]
            else:
                chosen_word = value
            break

    if chosen_word == "":
        print("Didn't find appropriate part of speech to augment")
        return ""

    # improved split: by spaces and punctuation: https://stackoverflow.com/a/367292
    # TODO: improve this - we need an improved split and join 
    word_list = re.findall(r"[\w']+|[.,!?;]", input_str)

    index_to_insert = possible_tokens[token_index][0]
    # "the" .. , "I'm .. "
    if chosen_part_of_speech in ["PRON", "DET"]:
        index_to_insert += 1

    word_list.insert(index_to_insert, chosen_word)
    # random if we need an interjection
    rand_int = random.randint(0, 2)
    if rand_int == 0:
        random.shuffle(shuffled_augmentations)
        chosen_aug = shuffled_augmentations[0]

        if INTERJECTION in chosen_aug:
            chosen_aug = chosen_aug[INTERJECTION]

            if type(chosen_aug) == list:
                random.shuffle(chosen_aug)
                chosen_aug = chosen_aug[0]

            word_list.insert(0, chosen_aug)

    output = " ".join(word_list)

    return output

if __name__ == '__main__':
    sentences = ["I think I'm about to fall", "I keep falling everytime I get up ", "help me stand up "]

    for sentence in sentences:
        print(profanitize(sentence))


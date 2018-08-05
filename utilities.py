"""This file contains some utility functions"""

ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
            'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
def resolve_emoji_from_alphabet(letter):
    """Returns the emoji representation of a letter"""
    return chr(ord(letter) + 127365)

def resolve_letter_from_emoji(emoji):
    """Returns the character representation of a letter emoji (in lowercase)"""
    return chr(ord(emoji) - 127365)

def generate_random_colour():
    """Generates a random colour decimal"""
    letters = "0123456789ABCDEF"
    colour_string = ""
    for i in range(6):
        colour_string += rand.choice(letters)
    return int(colour_string, 16)

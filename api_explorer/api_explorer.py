"""Fetch and display Pokémon information from the public PokéAPI."""

import requests


BASE_URL = "https://pokeapi.co/api/v2/pokemon"
POKEMON_NAMES = ["pikachu", "charizard", "bulbasaur", "pikacu"]


def display_pokemon(name: str) -> None:
    """Fetch one Pokémon and print either its details or a helpful error."""

    print(f"--- {name} ---")

    try:
        response = requests.get(f"{BASE_URL}/{name}", timeout=10)
    except requests.RequestException as error:
        print(f"Error: Could not connect to PokéAPI ({error}).")
        print()
        return

    if response.status_code == 404:
        print(
            f"Error: Pokémon '{name}' not found (Status 404). "
            "Check your spelling!"
        )
        print()
        return

    if response.status_code != 200:
        print(
            f"Error: PokéAPI returned an unexpected status "
            f"({response.status_code})."
        )
        print()
        return

    try:
        data = response.json()
        pokemon_types = [item["type"]["name"] for item in data["types"]]
        types_text = ", ".join(pokemon_types)
        print(f"Name: {data['name']}")
        print(f"Height: {data['height']}")
        print(f"Weight: {data['weight']}")
        print(f"Types: {types_text}")
    except (KeyError, TypeError, ValueError):
        print("Error: PokéAPI returned data in an unexpected format.")

    print()


def main() -> None:
    """Fetch the requested Pokémon one at a time."""

    for pokemon_name in POKEMON_NAMES:
        display_pokemon(pokemon_name)


if __name__ == "__main__":
    main()

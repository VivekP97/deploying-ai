from typing import TypedDict

# --------- get_pokemon_info types ---------
# This object contains the type of a pokemon.
class PokemonType(TypedDict):
    name: str

# This object is an element of the types list.
class PokemonTypeElement(TypedDict):
    type: PokemonType

# This object contains the ability of a pokemon.
class PokemonAbility(TypedDict):
    name: str

# This object is an element of the abilities list.
class PokemonAbilityElement(TypedDict):
    ability: PokemonAbility

# Represents information returned about a pokemon
class PokemonInfoResponseData(TypedDict):
    name: str
    types: list[PokemonTypeElement]
    abilities: list[PokemonAbilityElement]
    height: int # Decimetres (2m)
    weight: int # Hectograms (82kg)


# --------- get_pokemon_ability_info types ---------
# This object represents the "language" property of elements of the effect_entries list
class EffectLanguage(TypedDict):
    name: str # e.g. "en", "fr"

# This object is an element of the effect_entries list
class EffectEntriesElement(TypedDict):
    effect: str
    language: EffectLanguage

# Represents information returned about an ability
class AbilityInfoResponseData(TypedDict):
    name: str
    effect_entries: list[EffectEntriesElement]
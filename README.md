# cards

This project contains
  * a minimal playable app for card games written in pyglet in a functional style complete with animations, UI and extensible rulesets which automatically handle player turns, drawing from the pile, legal moves, etc.
  * an initial attempt to train AI to play the card game Sevens using pytorch (using the same model for game rules and turn simulation!)
  * a completely separate file `calc.py` which uses a combinatorics approach to count the number of distinct initial positions (up to natural symmetries) possible in Sevens

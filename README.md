# 2048 exact solver
An exact Python solver for generalizations of the game 2048.
Supports custom width and height of the rectangular board and custom probability to spawn a 4 instead of a 2.

## Usage
1. Run the script interactively
2. Call evaluate((width, height, probability), sg), where sg is the serialized starting grid - just "I" for game start.
3. Once computations are complete, prints the exact expected score under an optimal policy.
4. To look up the moves dictated by the optimal policy in any given grid state:
   - canonize() and serialize() your 2D grid
   - look up the value of your serialized grid in the "val" dictionary
   - the first element is the serialized grid after pushing into the recommended direction
   - deserialize() this to interpret which direction has been pushed in - grid may be rotated or reflected
   - the second element is the exact expected score still to gain from the current grid state if continued with optimal policy
5. Calling evaluate from a serialized starting grid that's deeper into the game will drastically reduce computation time.

## Notes
Due to combinatorial explosion, larger boards are not practically solveable in a reasonable amount of time and memory.
The practical use of this solver is therefore limited to perfectly and completely solving
- smaller boards
- endgame positions

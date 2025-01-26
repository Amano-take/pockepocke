## list select_action phase
Active Pokémon Selection:
    The names of Pokémon cards that can be placed on the battlefield.
    Example: "[select_active] Pikachuをバトル場に出す"
Bench Pokémon Selection:
    The names of Pokémon cards that can be placed on the bench.
    Example: "[select_bench] [Bulbasaur, Charmander]をベンチに出す"
Attack Selection:
The names of attacks that can be performed on a target Pokémon.
Example: "[attack] ThunderboltをCharmanderに使用"
Retreat Selection:
Options for retreating or not retreating the active Pokémon.
Example: "[select_retreat] 逃げない"
Energy Attachment Selection:
Options for attaching energy to active or bench Pokémon.
Example: "[select_energy] Pikachuにエネルギーをつける"
Goods Usage Selection:
Options for using goods cards.
Example: "[goods] MonsterBallを使用しました"
Trainer Usage Selection:
Options for using trainer cards.
Example: "[trainer] Potionを使用"
Evolution Selection:
Options for evolving Pokémon.
Example: "[evolve] [Pikachu]を進化"

# Monte Carlo Method Implementation for Pokemon Card Game AI

## Current Challenge
The Pokemon card game has multiple decision points within a single turn:
- Selecting which goods cards to use
- Choosing energy attachments
- Deciding on evolution
- Selecting attacks
- etc.

This makes it difficult to implement Monte Carlo Tree Search (MCTS) in a straightforward way.

## Proposed Solution: Action Sequence Approach

### Core Concept
Instead of handling each `select_action` separately, treat an entire turn as a single sequence of actions.

```python
class ActionSequence:
    def __init__(self):
        self.actions = []  # List of actions to take in order
        self.current_phase = 0

    def add_action(self, action_type: str, choice: int):
        self.actions.append((action_type, choice))

    def get_next_action(self) -> tuple[str, int]:
        if self.current_phase >= len(self.actions):
            return None
        action = self.actions[self.current_phase]
        self.current_phase += 1
        return action

class MonteCarloPlayer(Player):
    def __init__(self, deck: Deck, energies: list[Energy]):
        super().__init__(deck, energies)
        self.current_sequence = None

    def select_action(self, selection: dict[int, str], action: dict[int, Callable]):
        # Get action type from the selection string (e.g., "[attack]", "[goods]")
        action_type = self._get_action_type(selection[0])

        if self.current_sequence is None:
            # Generate new sequence using MCTS
            self.current_sequence = self._run_mcts()

        # Get the pre-computed action for current phase
        next_action = self.current_sequence.get_next_action()
        if next_action[0] != action_type:
            # Something unexpected happened, regenerate sequence
            self.current_sequence = self._run_mcts()
            next_action = self.current_sequence.get_next_action()

        return next_action[1]  # Return the choice index

    def _run_mcts(self) -> ActionSequence:
        # Run Monte Carlo Tree Search to generate best action sequence
        sequence = ActionSequence()

        # Simulate multiple games
        for _ in range(NUM_SIMULATIONS):
            game_state = self._clone_current_state()
            actions = self._simulate_game(game_state)
            sequence = self._update_statistics(actions)

        return sequence
```

### Benefits
1. **Simplified State Space**:
   - Instead of having separate MCTS trees for each decision point, maintain one tree for entire turn sequences
   - Reduces complexity of the search space

2. **Better Strategy Learning**:
   - AI can learn relationships between different actions in a turn
   - Example: Saving energy for a powerful attack vs using it for retreat

3. **Easier Implementation**:
   - No need for complex phase management
   - More natural representation of game flow

### Implementation Notes
1. **Action Encoding**:
   - Each action in the sequence should include:
     - Action type (goods, energy, attack, etc.)
     - Choice index within that action type
     - Any required parameters

2. **State Cloning**:
   - Need efficient way to clone game state for simulations
   - Consider implementing serialization methods

3. **Simulation Strategy**:
   - Use random playouts initially
   - Can be enhanced with heuristics later
   - Consider implementing progressive widening for large action spaces

4. **Handling Unexpected States**:
   - Have fallback mechanism when game state doesn't match expected sequence
   - Can regenerate sequence or use simple heuristics

## Next Steps
1. Implement basic ActionSequence class
2. Add state cloning functionality
3. Create simple random playout mechanism
4. Implement MCTS with action sequences
5. Add heuristics to improve playout quality

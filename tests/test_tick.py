"""
tests/test_tick.py – Tests für den deterministischen Tick-Loop.

Geprüft wird:
- tick-Zähler wächst korrekt
- Wertebereiche bleiben nach n Ticks in [0, 1]
- Deterministik: gleicher Seed + gleiche Config → identische Zustände nach N Ticks
- Nicht-Trivialität: Zustand ändert sich über Ticks
"""

import numpy as np
import pytest

from emergent_noise.core.state import GridState, SimConfig
from emergent_noise.core.tick import TickLoop


@pytest.fixture
def small_config() -> SimConfig:
    return SimConfig(height=16, width=16, seed=7)


def test_tick_counter_increments(small_config: SimConfig) -> None:
    """tick muss nach jedem step() um 1 steigen."""
    state = GridState.initialize(small_config)
    loop = TickLoop(small_config)
    for i in range(1, 6):
        loop.step(state)
        assert state.tick == i


def test_value_range_after_ticks(small_config: SimConfig) -> None:
    """Alle Felder müssen nach 50 Ticks in [0, 1] bleiben."""
    state = GridState.initialize(small_config)
    loop = TickLoop(small_config)
    loop.run(state, 50)
    for name, arr in state.as_dict().items():
        assert arr.min() >= 0.0, f"Feld '{name}' < 0 nach 50 Ticks"
        assert arr.max() <= 1.0, f"Feld '{name}' > 1 nach 50 Ticks"


def test_determinism(small_config: SimConfig) -> None:
    """Zwei Läufe mit identischer Config und identischem Seed müssen gleich enden."""
    state_a = GridState.initialize(small_config)
    state_b = GridState.initialize(small_config)
    loop_a = TickLoop(small_config)
    loop_b = TickLoop(small_config)
    loop_a.run(state_a, 30)
    loop_b.run(state_b, 30)
    for name in state_a.as_dict():
        np.testing.assert_array_equal(
            state_a.as_dict()[name],
            state_b.as_dict()[name],
            err_msg=f"Feld '{name}' ist nach 30 Ticks nicht deterministisch",
        )


def test_state_changes_over_ticks(small_config: SimConfig) -> None:
    """Der Zustand muss sich durch Ticks verändern (nicht stationär)."""
    state = GridState.initialize(small_config)
    initial_energy = state.energy.copy()
    loop = TickLoop(small_config)
    loop.run(state, 10)
    assert not np.array_equal(state.energy, initial_energy)


def test_memory_grows_from_zero(small_config: SimConfig) -> None:
    """Gedächtnis startet bei 0 und muss nach Ticks > 0 sein."""
    state = GridState.initialize(small_config)
    assert state.memory.sum() == 0.0
    loop = TickLoop(small_config)
    loop.run(state, 5)
    assert state.memory.sum() > 0.0


def test_callback_called(small_config: SimConfig) -> None:
    """Callbacks müssen nach jedem Tick aufgerufen werden."""
    call_log: list[int] = []
    state = GridState.initialize(small_config)
    loop = TickLoop(small_config, callbacks=[lambda s: call_log.append(s.tick)])
    loop.run(state, 5)
    assert call_log == [1, 2, 3, 4, 5]

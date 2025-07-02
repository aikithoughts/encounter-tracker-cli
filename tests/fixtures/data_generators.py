"""Data generators for creating test encounters and combatants."""

import random
from typing import List, Dict, Any
from dataclasses import asdict

from dnd_encounter_tracker.core.models import Combatant, Encounter


class DataGenerator:
    """Generates test data for encounters and combatants."""
    
    # Sample names for different combatant types
    PLAYER_NAMES = [
        "Thorin Ironforge", "Elara Moonwhisper", "Gareth Stormwind", "Luna Shadowbane",
        "Dain Battlehammer", "Seraphina Lightbringer", "Ragnar Bloodaxe", "Aria Swiftarrow",
        "Thaddeus Goldbeard", "Lyra Starweaver", "Grimm Ironshield", "Celeste Frostborn"
    ]
    
    MONSTER_NAMES = [
        "Goblin Scout", "Orc Warrior", "Skeleton Archer", "Zombie Shambler",
        "Dire Wolf", "Giant Spider", "Hobgoblin Captain", "Bugbear Brute",
        "Gnoll Fang", "Kobold Sorcerer", "Owlbear", "Displacer Beast",
        "Troll Regenerator", "Hill Giant", "Fire Elemental", "Shadow Wraith"
    ]
    
    NPC_NAMES = [
        "Captain Marcus", "Innkeeper Willem", "Merchant Aldric", "Guard Sergeant",
        "Priestess Mira", "Blacksmith Gorin", "Tavern Wench", "City Watch",
        "Noble Lord Ashford", "Wizard Apprentice", "Stable Master", "Town Crier"
    ]
    
    # HP ranges by combatant type
    HP_RANGES = {
        "player": (20, 80),
        "monster": (5, 120),
        "npc": (8, 40)
    }
    
    # Initiative ranges
    INITIATIVE_RANGE = (1, 25)
    
    # Sample notes for different situations
    SAMPLE_NOTES = [
        "Blessed by cleric (+1 AC)",
        "Poisoned (disadvantage on attacks)",
        "Concentrating on spell",
        "Has inspiration",
        "Prone (disadvantage on attacks)",
        "Grappled (speed 0)",
        "Frightened (disadvantage on attacks)",
        "Invisible (advantage on attacks)",
        "Hasted (+1 action)",
        "Stunned (incapacitated)",
        "Charmed (friendly to charmer)",
        "Paralyzed (auto-crit within 5ft)",
        "Restrained (disadvantage on attacks)",
        "Blinded (disadvantage on attacks)",
        "Deafened (can't hear)",
        "Exhausted (level 1)",
        "Petrified (turned to stone)",
        "Unconscious (0 HP)"
    ]
    
    @classmethod
    def create_combatant(
        self,
        name: str = None,
        combatant_type: str = None,
        hp: int = None,
        initiative: int = None,
        notes: List[str] = None,
        current_hp_percentage: float = 1.0
    ) -> Combatant:
        """Create a single combatant with optional parameters.
        
        Args:
            name: Combatant name (random if None)
            combatant_type: Type of combatant (random if None)
            hp: Maximum HP (random within type range if None)
            initiative: Initiative value (random if None)
            notes: List of notes (random selection if None)
            current_hp_percentage: Percentage of max HP for current HP
            
        Returns:
            Generated Combatant instance
        """
        if combatant_type is None:
            combatant_type = random.choice(["player", "monster", "npc"])
        
        if name is None:
            name_pool = {
                "player": self.PLAYER_NAMES,
                "monster": self.MONSTER_NAMES,
                "npc": self.NPC_NAMES
            }
            name = random.choice(name_pool[combatant_type])
        
        if hp is None:
            min_hp, max_hp = self.HP_RANGES[combatant_type]
            hp = random.randint(min_hp, max_hp)
        
        if initiative is None:
            initiative = random.randint(*self.INITIATIVE_RANGE)
        
        current_hp = int(hp * current_hp_percentage)
        
        combatant = Combatant(
            name=name,
            max_hp=hp,
            current_hp=current_hp,
            initiative=initiative,
            combatant_type=combatant_type
        )
        
        # Add random notes if not specified
        if notes is None:
            num_notes = random.randint(0, 3)
            if num_notes > 0:
                selected_notes = random.sample(self.SAMPLE_NOTES, num_notes)
                for note in selected_notes:
                    combatant.add_note(note)
        else:
            for note in notes:
                combatant.add_note(note)
        
        return combatant
    
    @classmethod
    def create_encounter(
        self,
        name: str = None,
        num_players: int = 4,
        num_monsters: int = 6,
        num_npcs: int = 2,
        current_turn: int = 0,
        round_number: int = 1
    ) -> Encounter:
        """Create a complete encounter with multiple combatants.
        
        Args:
            name: Encounter name (random if None)
            num_players: Number of player characters
            num_monsters: Number of monsters
            num_npcs: Number of NPCs
            current_turn: Current turn index
            round_number: Current round number
            
        Returns:
            Generated Encounter instance
        """
        if name is None:
            encounter_names = [
                "Goblin Ambush", "Dragon's Lair", "Bandit Hideout", "Undead Crypt",
                "Forest Encounter", "Tavern Brawl", "City Guard Patrol", "Dungeon Crawl",
                "Orc Raid", "Wizard's Tower", "Pirate Ship Battle", "Temple Assault"
            ]
            name = random.choice(encounter_names)
        
        encounter = Encounter(
            name=name,
            current_turn=current_turn,
            round_number=round_number
        )
        
        # Create players
        used_names = set()
        for _ in range(num_players):
            while True:
                combatant = self.create_combatant(combatant_type="player")
                if combatant.name not in used_names:
                    used_names.add(combatant.name)
                    encounter.add_combatant(combatant)
                    break
        
        # Create monsters
        for _ in range(num_monsters):
            while True:
                combatant = self.create_combatant(combatant_type="monster")
                # Allow duplicate monster names with numbers
                base_name = combatant.name
                counter = 1
                while combatant.name in used_names:
                    combatant.name = f"{base_name} {counter}"
                    counter += 1
                used_names.add(combatant.name)
                encounter.add_combatant(combatant)
                break
        
        # Create NPCs
        for _ in range(num_npcs):
            while True:
                combatant = self.create_combatant(combatant_type="npc")
                if combatant.name not in used_names:
                    used_names.add(combatant.name)
                    encounter.add_combatant(combatant)
                    break
        
        # Sort by initiative
        encounter.sort_by_initiative()
        
        return encounter
    
    @classmethod
    def create_large_encounter(self, size: int = 50) -> Encounter:
        """Create a large encounter for performance testing.
        
        Args:
            size: Total number of combatants
            
        Returns:
            Large Encounter instance
        """
        # Distribute combatants across types
        num_players = max(1, size // 10)  # 10% players
        num_npcs = max(1, size // 20)     # 5% NPCs
        num_monsters = size - num_players - num_npcs  # Rest are monsters
        
        return self.create_encounter(
            name=f"Large Battle ({size} combatants)",
            num_players=num_players,
            num_monsters=num_monsters,
            num_npcs=num_npcs
        )
    
    @classmethod
    def create_sample_encounters(self) -> Dict[str, Encounter]:
        """Create a set of sample encounters for testing and demonstration.
        
        Returns:
            Dictionary of encounter name to Encounter instance
        """
        encounters = {}
        
        # Small encounter - typical party vs few enemies
        encounters["goblin_ambush"] = self.create_encounter(
            name="Goblin Ambush",
            num_players=4,
            num_monsters=3,
            num_npcs=0
        )
        
        # Medium encounter - larger battle
        encounters["orc_raid"] = self.create_encounter(
            name="Orc Raid on Village",
            num_players=5,
            num_monsters=8,
            num_npcs=3
        )
        
        # Large encounter - epic battle
        encounters["dragon_lair"] = self.create_encounter(
            name="Ancient Dragon's Lair",
            num_players=6,
            num_monsters=12,
            num_npcs=2
        )
        
        # Tavern brawl - mostly NPCs
        encounters["tavern_brawl"] = self.create_encounter(
            name="Tavern Brawl",
            num_players=4,
            num_monsters=2,
            num_npcs=8
        )
        
        # Boss fight - single powerful enemy
        boss_encounter = Encounter(name="Boss Fight - Lich King")
        
        # Add players
        for name in self.PLAYER_NAMES[:4]:
            combatant = self.create_combatant(
                name=name,
                combatant_type="player",
                hp=random.randint(40, 80),
                initiative=random.randint(10, 20)
            )
            boss_encounter.add_combatant(combatant)
        
        # Add boss
        boss = self.create_combatant(
            name="Lich King Valdris",
            combatant_type="monster",
            hp=200,
            initiative=25,
            notes=["Legendary Actions", "Lair Actions", "Magic Resistance"]
        )
        boss_encounter.add_combatant(boss)
        
        # Add minions
        for i in range(4):
            minion = self.create_combatant(
                name=f"Skeleton Warrior {i+1}",
                combatant_type="monster",
                hp=random.randint(15, 25),
                initiative=random.randint(8, 15)
            )
            boss_encounter.add_combatant(minion)
        
        boss_encounter.sort_by_initiative()
        encounters["boss_fight"] = boss_encounter
        
        return encounters
    
    @classmethod
    def create_encounter_json_data(self, encounter: Encounter) -> Dict[str, Any]:
        """Convert an encounter to JSON-serializable data.
        
        Args:
            encounter: Encounter to convert
            
        Returns:
            Dictionary suitable for JSON serialization
        """
        from datetime import datetime
        
        data = asdict(encounter)
        
        # Add metadata
        data["metadata"] = {
            "created": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "version": "1.0",
            "generator": "DataGenerator"
        }
        
        return data
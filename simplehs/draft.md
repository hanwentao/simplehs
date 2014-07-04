Design Draft
============

## Classes

### Hierarchy

* Game
* Player
* Object
  * Card
    * MinionCard
    * SpellCard
      * SecretCard
    * WeaponCard
  * Character
    * Hero
    * Minion
  * Weapon
  * Secret
  * HeroPower

### Properties and Methods

* Game
  * turn_num
  * players
  * who (current player)
  + duplicate(source)
  + transform(source, target)
* Player
  * name
  * opponent
  * go_first
  * deck
  * hand
  * mana
  * hero
  * battlefield
  * secrets
  + play(card, [target], [position], [choice])
  + attack(subject, object)
  + end()
  + concede()
  + draw(num_cards=1)
  + discard(cards)
  + obtain(cards)
  + summon(minion, position, [target])
  + equip(weapon, [target])
  + control(minion, one_turn=False)
  + heal(targets, amount)
* Object
  * game
  * id
  * name
  * owner: the owner of all objects is a player except hero power (the owner is a hero).
  * battlecry
  * deathrattle
  * triggers (triggered effects)
  * auras (ongoing_effects)
  + destroy()
* Card
  * cost
  * overload
  * class
  * rarity
  * can_play
  * play_targets
  * [set]
  * [golden]
  * [description]
  * [flavor_text]
  + play([target], [position], [choice])
* MinionCard
  * attack
  * health
  * minion
* WeaponCard
  * attack
  * durability
  * weapon
* SecretCard
  * secret
* Character
  * attack
  * health
  * full_health
  * dying
  * type
  * windfury
  * cannot_attack
  * stealth
  * taunt
  * freeze
  * immune
  * divine_shield
  * spell_immune
  * poison
  * can_attack
  * attack_targets
  + gain_attack(amount, one_turn=False)
  + gain_health(amount)
  + double_attack()
  + double_health()
  + attack_equal_to_health()
  + set_stealth(one_turn=False)
  + attack_(target)
  + take_damage(amount)
  + restore(amount)
  + silence()
* Hero
  * armor
  * weapon
  * power
  + gain(armor)
  + equip(weapon, [target])
* Minion
  * card
  * sleep
  * charge
* Weapon
  * attack
  * durability
  + gain_durability(amount)
  + lose_durability(amount)
* Secret
  + reveal(target)
* HeroPower
  * can_use
  * use_targets
  + use([target])


## Mechanics

### Events

* Record cards played in a turn
* Turn start
* Turn end
* Playing a card
  * Choose One
* Casting a spell
  * Before/after
  * Change target
* Attacking
  * Before/after
  * Change target
* Taking damage
* Restoring Health (healing)
* Creating object
  * Summoning minion
  * Equipping weapon
  * Playing Secret
* Destroying object
  * Destroying minion
  * Destroying weapon
  * Revealing Secret

### Actions

* Restore health (heal)
* Take damage
  * Deal damage
* Gain durability
* Lose durability
* Add Armor
* Silence
* Create object
  * Summon minion
    * Ephemeral
  * Equip weapon
  * Play Secret
* Destroy object
  * Destroy minion
  * Destroy weapon
  * Destroy Secret
* Transform
  * Warlock/Lord Jaraxxus
* Copy minion/card
* Return minion/card
* Swap
* Control/temporary control
* Draw card(s)
* Discard card(s)
* Give Taunt/Divine Shield/Windfury/Stealth
* Lose Divine Shield/Stealth
* Change Hero Power
* Grant Deathrattle
* Mana Crystal
  * Gain
  * Gain empty
  * Destroy
* Tracking

### Enchantments

* Battlecry
* Deathrattle
* Base Attack/full Health
* Main (current) Attack/full Health
* Temporary Attack
* Aura Attack/full Health
  * Old Murk-Eye: reversed aura effect for self from others
  * Enrage
* Double Attack/Health
* Attack equal to Health
* Hero Armor
* Weapon Attack/Durability
  * Aura (Enrage)
* Spell damage +
  * Double aura
  * Give
* Convert restore Health to deal damage
* Adjacent

* Taunt
* Charge
  * Has weapon equipped
  * Aura
* Divine Shield
* Windfury
  * Enrage
* Stealth
  * Temporary
* Enrage
* Freeze
* Poison
* Secret
* Overload
* Immune
  * Minions can't be reduced below 1 Health
  * While attacking
* Can't Attack
* Can't be targeted by Spells or Hero Powers
* 15 seconds

* Card cost
  * Base
  * Current
  * Aura
    * Attack of weapon
    * Portal
  * Cost 0 for a turn
    * Next Secret
  * Giants

#### Aura

### Miscellaneous

* Blessing of Wisdom: has its own master set when playing


## Archive

### Events

* turn_start(player)
* card_played(card)
* spell_casting(card)
* spell_cast(card)
* created(source, target=None): (summon/equip) battlecry
* attacking(source, target)
* taken_damage(target, damage)
* destroying(source): deathrattle
* destroyed(source)
* turn_end(player)

### Secrets

Secrets are also objects, but not characters.

### Attack and Health

* Attack = Main + Aura + Temp
  * Base attack
  * Main attack
  * Aura attack
  * Temp attack
* Max health = Main + Aura
  * Base health
  * Main health
  * Aura health
* Health

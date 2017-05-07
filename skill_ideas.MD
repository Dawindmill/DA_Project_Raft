# Skill Ideas
- The followings are just rough ideas about each skill, feel free to modify them

## Animal

![animal](./Visualization/assets/skill_icons/animal.png)

### Description

- Growing Animals
- Boots up Villager's max health or current health
- Could also benefit Monster's health

### Possible Classes and Methods Related

- Skill.py
	- def skill_handler(self, ...)
	- def animal_handler(self, ...)

- Villager.py
	- def max_health_up(self)
    - def max_health_down(self)
    - def current_health_up(self)
    - def current_health_down(self)

- Monster.py
	- def max_health_up(self)
	- def max_health_down(self)
	- def current_health_up(self)
	- def current_health_down(self)

	## Animal

![armour](./Visualization/assets/skill_icons/armour.png)

### Description

- Villager can put on armour and increase defensive power

### Possible Classes and Methods Related

- Skill.py
	- def skill_handler(self, ...)
	- def armour_handler(self, ...)

- Villager.py
	- def defensive_power_up(self)
    - def defensive_power_down(self)
	- def set_armour_image(self)

![fire](./Visualization/assets/skill_icons/bow.png)

### Description

- Villager can cook and gain additional increase from the foods

### Possible Classes and Methods Related

- Skill.py
	- def skill_handler(self, ...)
	- def fire_handler(self, ...)

- Villager.py
	- def set_food_additional(self)
	- def set_fire_image(self)

![fix](./Visualization/assets/skill_icons/fix.png)

### Description

- Villager can speed up the repair process

### Possible Classes and Methods Related

- Skill.py
	- def skill_handler(self, ...)
	- def repair_handler(self, ...)

- Villager.py
	- def set_repair_speed()

![medicine](./Visualization/assets/skill_icons/medicine.png)

### Description

- Villager can produce medicines to heal themselves

### Possible Classes and Methods Related

- Skill.py
	- def skill_handler(self, ...)
	- def medicine_handler(self, ...)

- Villager.py
	- def set_medicine_production_speed()
	- def set_medicine_image(self)


![plant](./Visualization/assets/skill_icons/plant.png)

### Description

- Villager can grow apple tree and get apple as food

### Possible Classes and Methods Related

- Skill.py
	- def skill_handler(self, ...)
	- def plant_handler(self, ...)

- Villager.py
	- def set_plant_growing_speed()
	- def set_plant_image(self)

![sing](./Visualization/assets/skill_icons/sing.png)

### Description

- Singing lower the chance of the monster to attack

### Possible Classes and Methods Related

- Skill.py
	- def skill_handler(self, ...)
	- def sing_handler(self, ...)

- Monster.py
	- def set_attack_probability()

![sword](./Visualization/assets/skill_icons/sing.png)

### Description

- Villager can hurt monster while monsters are attacking

### Possible Classes and Methods Related

- Skill.py
	- def skill_handler(self, ...)
	- def sing_handler(self, ...)

- Villager.py
	- def set_attack_power()
	- def set_sword_image(self)

![tool](./Visualization/assets/skill_icons/tool.png)

### Description

- Villager can start building their house

### Possible Classes and Methods Related

- Skill.py
	- def skill_handler(self, ...)
	- def tool_handler(self, ...)

- Villager.py
	- def set_house_production_speed()
	- def set_house_image()

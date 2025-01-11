for attack in self.attacks:

            attack.can_attack = lambda: attack.can_attack_hidden(self.energies)
            attack.set_type(self.type)
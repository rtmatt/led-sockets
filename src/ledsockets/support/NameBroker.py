from faker import Faker


class NameBroker():
    def __init__(self):
        self._active_names = set()
        self._faker = Faker()

    def release_name(self, name):
        self._active_names.discard(name)

    def reserve_name(self, name):
        self._active_names.add(name)

    def name_available(self, name):
        return name not in self._active_names

    def _generate_name(self):
        return self._faker.name()

    def get_name(self, preferred: str | None = None):
        candidate = preferred if preferred else self._generate_name()

        while not self.name_available(candidate):
            candidate = self._generate_name()

        self.reserve_name(candidate)
        return candidate

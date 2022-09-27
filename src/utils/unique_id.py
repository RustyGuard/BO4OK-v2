class UniqueIdGenerator:
    last_id = 0

    @classmethod
    def generate_id(cls) -> str:
        cls.last_id += 1
        return str(cls.last_id)

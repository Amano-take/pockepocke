def load_pkl(self):
        with open("./player.pkl", "rb") as f:
            self = pickle.load(f)

    def select_action(
        self, selection: Dict[int, str], action: Dict[int, Callable] = {}
    ) -> int:
        """RuleBaseによる自動選択"""
        if len(selection) == 1:
            return 0

        # picklesave
        with open("./player.pkl", "wb") as f:
            pickle.dump(self, f)

        id_ = id(self)
        hash_ = hash(self)

        scores = {}
        for key in selection.keys():
            action[key]()
            scores[key] = self.calculate_action_score()
            self.load_pkl()

class LabelDiff():
    def __init__(self):
        self.last_seen = set()

    def printDiff(self, labels):
        cur_visible = {i["name"] for i in labels}

        for i in cur_visible.difference(self.last_seen):
            print("+", i)

        for i in self.last_seen.difference(cur_visible):
            print("-", i)

        self.last_seen = cur_visible
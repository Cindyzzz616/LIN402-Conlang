from lambeq import BobcatParser

parser = BobcatParser("/Users/cindyzhang/LIN402-Conlang/.cache/lambeq/bobcat")
diagram = parser.sentence2diagram("That time, the language of all places is one")
print(diagram)
diagram.draw(path="diagram.png", show=False)

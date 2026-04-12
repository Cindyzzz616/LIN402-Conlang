from lambeq import BobcatParser

parser = BobcatParser("/Users/cindyzhang/LIN402-Conlang/.cache/lambeq/bobcat")
diagram = parser.sentence2diagram("While people moved to east, they found a plain around Shinar and settled in there")
print(diagram)
diagram.draw(path="diagram2.png", show=False)

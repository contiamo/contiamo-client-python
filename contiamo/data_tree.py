class Tree(dict):

  def add_node(self, class_, parent=None):
    self[class_.name] = Node(class_, parent)
    if parent:
      self[parent].children.append(self[class_.name])


class Node:

  def __init__(self, class_, parent=None):
    self.class_ = class_
    self.parent = parent
    self.children = []

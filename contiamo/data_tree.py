from contiamo.errors import InvalidRequestError


class Tree(dict):

  def add_node(self, class_, parent=None):
    self[class_.name] = Node(class_, parent)
    if parent:
      self[parent].children.append(self[class_.name])

  def get_nested_classes(self, class_name):
    """Returns top level first, includes current class (last)."""
    if class_name not in self:
      raise InvalidRequestError('Requested resource (%s) is not part of the Contiamo data tree.' % class_name)
    nested_classes = [class_name]
    while self[nested_classes[-1]].parent is not None:
      nested_classes.append(self[nested_classes[-1]].parent)
    return nested_classes[::-1]


class Node:

  def __init__(self, class_, parent=None):
    self.class_ = class_
    self.parent = parent
    self.children = []

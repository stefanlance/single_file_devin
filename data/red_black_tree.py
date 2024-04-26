class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.parent = None
        self.color = "RED"

class RedBlackTree:
    def __init__(self):
        self.nil = Node(None)
        self.nil.color = "BLACK"
        self.root = self.nil

    def insert(self, value):
        new_node = Node(value)
        new_node.left = self.nil
        new_node.right = self.nil

        parent = None
        current = self.root
        while current != self.nil:
            parent = current
            if new_node.value < current.value:
                current = current.left
            elif new_node.value > current.value:
                current = current.right
            else:
                raise ValueError("Duplicate value")

        new_node.parent = parent
        if parent is None:
            self.root = new_node
        elif new_node.value < parent.value:
            parent.left = new_node
        else:
            parent.right = new_node

        self._insert_fixup(new_node)

    def _insert_fixup(self, node):
        while node.parent and node.parent.color == "RED":
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                if uncle.color == "RED":
                    node.parent.color = "BLACK"
                    uncle.color = "BLACK"
                    node.parent.parent.color = "RED"
                    node = node.parent.parent
                else:
                    if node == node.parent.right:
                        node = node.parent
                        self._left_rotate(node)
                    node.parent.color = "BLACK"
                    node.parent.parent.color = "RED"
                    self._right_rotate(node.parent.parent)
            else:
                uncle = node.parent.parent.left
                if uncle.color == "RED":
                    node.parent.color = "BLACK"
                    uncle.color = "BLACK"
                    node.parent.parent.color = "RED"
                    node = node.parent.parent
                else:
                    if node == node.parent.left:
                        node = node.parent
                        self._right_rotate(node)
                    node.parent.color = "BLACK"
                    node.parent.parent.color = "RED"
                    self._left_rotate(node.parent.parent)

        self.root.color = "BLACK"

    def _left_rotate(self, node):
        right_child = node.right
        node.right = right_child.left
        if right_child.left != self.nil:
            right_child.left.parent = node
        else:
            right_child.left = self.nil

        right_child.parent = node.parent
        if node.parent is None:
            self.root = right_child
        elif node == node.parent.left:
            node.parent.left = right_child
        else:
            node.parent.right = right_child

        right_child.left = node
        node.parent = right_child

    def _right_rotate(self, node):
        left_child = node.left
        node.left = left_child.right
        if left_child.right != self.nil:
            left_child.right.parent = node
        else:
            left_child.right = self.nil

        left_child.parent = node.parent
        if node.parent is None:
            self.root = left_child
        elif node == node.parent.right:
            node.parent.right = left_child
        else:
            node.parent.left = left_child

        left_child.right = node
        node.parent = left_child

import pytest

def test_insert_single_node():
    tree = RedBlackTree()
    tree.insert(10)
    assert tree.root.value == 10
    assert tree.root.color == "BLACK"

def test_insert_multiple_nodes():
    tree = RedBlackTree()
    values = [10, 20, 5, 15, 25, 3, 8]
    for value in values:
        tree.insert(value)
    assert tree.root.value == 10
    assert tree.root.color == "BLACK"

def test_insert_duplicate_node():
    tree = RedBlackTree()
    tree.insert(10)
    with pytest.raises(ValueError):
        tree.insert(10)

def test_left_rotate():
    tree = RedBlackTree()
    tree.root = Node(10)
    tree.root.left = Node(5)
    tree.root.left.parent = tree.root
    tree.root.right = Node(20)
    tree.root.right.parent = tree.root
    tree._left_rotate(tree.root)
    assert tree.root.value == 20
    assert tree.root.left.value == 10
    assert tree.root.left.left.value == 5

def test_right_rotate():
    tree = RedBlackTree()
    tree.root = Node(10)
    tree.root.left = Node(5)
    tree.root.left.parent = tree.root
    tree.root.right = Node(20)
    tree.root.right.parent = tree.root
    tree._right_rotate(tree.root)
    assert tree.root.value == 5
    assert tree.root.right.value == 10
    assert tree.root.right.right.value == 20
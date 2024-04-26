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
            else:
                current = current.right

        new_node.parent = parent
        if parent is None:
            self.root = new_node
        elif new_node.value < parent.value:
            parent.left = new_node
        else:
            parent.right = new_node

        self._insert_fixup(new_node)

    def _insert_fixup(self, node):
        while node.parent is not None and node.parent.color == "RED":
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
    tree.insert(5)
    assert tree.root.value == 5
    assert tree.root.color == "BLACK"

def test_insert_multiple_nodes():
    tree = RedBlackTree()
    tree.insert(5)
    tree.insert(3)
    tree.insert(7)
    tree.insert(1)
    assert tree.root.value == 5
    assert tree.root.color == "BLACK"
    assert tree.root.left.value == 3
    assert tree.root.left.color == "BLACK"
    assert tree.root.right.value == 7
    assert tree.root.right.color == "BLACK"
    assert tree.root.left.left.value == 1
    assert tree.root.left.left.color == "RED"

def test_insert_fixup_case1():
    tree = RedBlackTree()
    tree.insert(5)
    tree.insert(3)
    tree.insert(7)
    tree.insert(6)
    assert tree.root.value == 5
    assert tree.root.color == "BLACK"
    assert tree.root.left.value == 3
    assert tree.root.left.color == "BLACK"
    assert tree.root.right.value == 7
    assert tree.root.right.color == "BLACK"
    assert tree.root.right.left.value == 6
    assert tree.root.right.left.color == "RED"

def test_insert_fixup_case2():
    tree = RedBlackTree()
    tree.insert(5)
    tree.insert(3)
    tree.insert(7)
    tree.insert(8)
    assert tree.root.value == 5
    assert tree.root.color == "BLACK"
    assert tree.root.left.value == 3
    assert tree.root.left.color == "BLACK"
    assert tree.root.right.value == 7
    assert tree.root.right.color == "BLACK"
    assert tree.root.right.right.value == 8
    assert tree.root.right.right.color == "RED"

def test_insert_fixup_case3():
    tree = RedBlackTree()
    tree.insert(5)
    tree.insert(3)
    tree.insert(7)
    tree.insert(2)
    tree.insert(4)
    assert tree.root.value == 5
    assert tree.root.color == "BLACK"
    assert tree.root.left.value == 3
    assert tree.root.left.color == "BLACK"
    assert tree.root.left.left.value == 2
    assert tree.root.left.left.color == "RED"
    assert tree.root.left.right.value == 4
    assert tree.root.left.right.color == "RED"
    assert tree.root.right.value == 7
    assert tree.root.right.color == "BLACK"

def test_insert_fixup_case4():
    tree = RedBlackTree()
    tree.insert(5)
    tree.insert(3)
    tree.insert(7)
    tree.insert(8)
    tree.insert(9)
    assert tree.root.value == 5
    assert tree.root.color == "BLACK"
    assert tree.root.left.value == 3
    assert tree.root.left.color == "BLACK"
    assert tree.root.right.value == 8
    assert tree.root.right.color == "BLACK"
    assert tree.root.right.left.value == 7
    assert tree.root.right.left.color == "RED"
    assert tree.root.right.right.value == 9
    assert tree.root.right.right.color == "RED"
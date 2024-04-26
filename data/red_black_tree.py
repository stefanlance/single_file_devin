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

@pytest.fixture
def tree():
    return RedBlackTree()

def test_insert_single_node(tree):
    tree.insert(10)
    assert tree.root.value == 10
    assert tree.root.color == "BLACK"
    assert tree.root.left == tree.nil
    assert tree.root.right == tree.nil

def test_insert_multiple_nodes(tree):
    values = [10, 20, 5, 15, 25, 3, 8]
    for value in values:
        tree.insert(value)

    assert tree.root.value == 10
    assert tree.root.color == "BLACK"
    assert tree.root.left.value == 5
    assert tree.root.right.value == 20
    assert tree.root.left.left.value == 3
    assert tree.root.left.right.value == 8
    assert tree.root.right.left.value == 15
    assert tree.root.right.right.value == 25

def test_insert_duplicate_value(tree):
    tree.insert(10)
    tree.insert(10)
    assert tree.root.value == 10
    assert tree.root.color == "BLACK"
    assert tree.root.left == tree.nil
    assert tree.root.right == tree.nil

def test_left_rotate(tree):
    tree.insert(10)
    tree.insert(20)
    tree.insert(5)
    tree._left_rotate(tree.root)
    assert tree.root.value == 20
    assert tree.root.left.value == 10
    assert tree.root.right == tree.nil
    assert tree.root.left.left.value == 5
    assert tree.root.left.right == tree.nil

def test_right_rotate(tree):
    tree.insert(10)
    tree.insert(5)
    tree.insert(20)
    tree._right_rotate(tree.root)
    assert tree.root.value == 5
    assert tree.root.left == tree.nil
    assert tree.root.right.value == 10
    assert tree.root.right.left == tree.nil
    assert tree.root.right.right.value == 20

def test_insert_fixup(tree):
    values = [10, 20, 5, 15, 25, 3, 8]
    for value in values:
        tree.insert(value)

    assert tree.root.color == "BLACK"
    assert all(node.color != "RED" or
               (node.left.color == "BLACK" and node.right.color == "BLACK")
               for node in tree.traverse_inorder() if node != tree.nil)
    assert all(node.color == "RED" or
               (node.left.color == "BLACK" and node.right.color == "BLACK")
               for node in tree.traverse_inorder() if node != tree.nil)

def test_traverse_inorder(tree):
    values = [10, 20, 5, 15, 25, 3, 8]
    for value in values:
        tree.insert(value)

    traversal = [node.value for node in tree.traverse_inorder() if node != tree.nil]
    assert traversal == sorted(values)

def test_traverse_preorder(tree):
    values = [10, 20, 5, 15, 25, 3, 8]
    for value in values:
        tree.insert(value)

    traversal = [node.value for node in tree.traverse_preorder() if node != tree.nil]
    expected = [10, 5, 3, 8, 20, 15, 25]
    assert traversal == expected

def test_traverse_postorder(tree):
    values = [10, 20, 5, 15, 25, 3, 8]
    for value in values:
        tree.insert(value)

    traversal = [node.value for node in tree.traverse_postorder() if node != tree.nil]
    expected = [3, 8, 5, 15, 25, 20, 10]
    assert traversal == expected

def tree_traverse_inorder(self):
    stack = []
    node = self.root
    while stack or node != self.nil:
        if node != self.nil:
            stack.append(node)
            node = node.left
        else:
            node = stack.pop()
            yield node
            node = node.right

def tree_traverse_preorder(self):
    stack = [self.root]
    while stack:
        node = stack.pop()
        if node != self.nil:
            yield node
            stack.append(node.right)
            stack.append(node.left)

def tree_traverse_postorder(self):
    stack = []
    node = self.root
    last_visited = None
    while stack or node != self.nil:
        if node != self.nil:
            stack.append(node)
            node = node.left
        else:
            peek = stack[-1]
            if peek.right != self.nil and last_visited != peek.right:
                node = peek.right
            else:
                last_visited = stack.pop()
                yield last_visited

RedBlackTree.traverse_inorder = tree_traverse_inorder
RedBlackTree.traverse_preorder = tree_traverse_preorder
RedBlackTree.traverse_postorder = tree_traverse_postorder
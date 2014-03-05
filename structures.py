import pickle
import os

class Node(object):
    
    def __init__(self, t):
        self.num_keys = 0;
        self.ident = 0;
        self.leaf = True;
        self.root = None;
        self.keys = [None for k in range(2*t-1)];
        self.ptrs = [None for p in range(2*t)];

    def serialize(self):
        return pickle.dumps(self)

    def __str__(self):
        ret_val = 'Node:'+str(self.ident)+'Keys:'
        ret_val += ', '.join([str(k) for k in self.keys[:self.num_keys]])
        '''
        ret_val += '\n' + ', '.join( [j.__repr__() for j in self.ptrs[:self.num_keys + 1]] )
        ret_val += '\n'
        for m in range(self.num_keys + 1):
            if self.ptrs[m]:
                ret_val += '\n'
                ret_val += self.ptrs[m].__str__()
        '''
        return ret_val

class B_Tree(object):
    
    def __init__(self, t):
        self.path = "/Volumes/Macintosh_HD_2/tmp"
        self.filename = "_node.obj"
        self.t = t
        self.root = -1 
        self.node_count = 0

    def create(self):
        x = self.create_node()
        x.leaf = True
        x.num_keys= 0
        self.root = x.ident
        self.write_bytes(x)
        del x

    def create_node(self):
        new_node = Node(self.t)
        self.node_count += 1
        new_node.ident = self.node_count
        return new_node

    def write_bytes(self, node):
        print "Write bytes()"
        path = os.path.join(self.path, str(node.ident) + self.filename)
        with open(path, 'wb') as file_out:
            pickle.dump(node, file_out)

    def read_bytes(self, node_ident):
        print "Read bytes(",node_ident,")"
        path = os.path.join(self.path, str(node_ident) + self.filename)
        with open(path, 'rb') as file_in:
            ret_val = pickle.load(file_in)
        return ret_val

    def search(self, node_ident, key):
        i=0
        node = self.read_bytes(node_ident)
        print '    ',node
        while ((i < node.num_keys) and (key > node.keys[i])):
            i += 1
        if (i < node.num_keys) and (key == node.keys[i]):
            return (node, i)
        if node.leaf:
            return "Not found"
        else:
            child_ident = node.ptrs[i]
            del node
            return self.search(child_ident, key)

    def split_child(self, parent, idx, child):
        new_node = self.create_node()
        new_node.leaf = child.leaf
        new_node.num_keys = self.t - 1
        # Assign values to new nodes keys
        for j in range(self.t-1):
            new_node.keys[j] = child.keys[j + self.t]
        if not child.leaf:
            # If child was not leaf reassign its ptrs array
            for k in range(self.t):
                new_node.ptrs[k] = self.read_bytes(child.ptrs[k + self.t]).ident
        # Set size of child keys to 1 less than half t
        child.num_keys = self.t - 1
        # Move all parent's ptrs up one to make room for median
        for m in range(parent.num_keys, idx, -1):
            parent.ptrs[m + 1] = self.read_bytes(parent.ptrs[m]).ident
        # Set parents just over middle ptr to the new node
        parent.ptrs[idx + 1] = new_node.ident
        # Shuffle all parent's keys up one
        for p in range(parent.num_keys - 1, idx - 1, -1):
            parent.keys[p + 1] = parent.keys[p]
        # Set parents key to median
        parent.keys[idx] = child.keys[self.t - 1]
        # Increment parents keys count
        parent.num_keys += 1
        self.write_bytes(child)
        self.write_bytes(new_node)
        self.write_bytes(parent)

    def insert(self, key):
        r = self.read_bytes(self.root)
        if r.num_keys == ((2 * self.t) - 1):
            new_node = self.create_node()
            self.root = new_node.ident
            new_node.leaf = False
            new_node.num_keys = 0
            new_node.ptrs[0] = r.ident
            self.split_child(new_node, 0, r)
            self.insert_nonfull(new_node, key)
        else:
            self.insert_nonfull(r, key)

    def insert_nonfull(self, node, key):
        idx = node.num_keys - 1
        if node.leaf:
            while idx >= 0 and key < node.keys[idx]:
                node.keys[idx + 1] = node.keys[idx]
                idx -= 1
            node.keys[idx + 1] = key
            node.num_keys += 1
            self.write_bytes(node)
        else:
            while idx >= 0 and key < node.keys[idx]:
                idx -= 1
            idx += 1
            child = self.read_bytes(node.ptrs[idx])
            if child.num_keys == ((2 * self.t) - 1):
                self.split_child(node, idx, child)
                if key > node.keys[idx]:
                    idx += 1
            self.insert_nonfull(child, key)

    def __str__(self):
        return self.root.__str__()

if __name__ == '__main__':
    import random
    my_tree = B_Tree(4)
    my_tree.create()
    for x in range(4000):
        my_tree.insert(x)
    print "Root: ",my_tree.read_bytes(my_tree.root)
    for y in range(10):
        key = random.randint(0,4000)
        print "Search for ",key,":",my_tree.search(my_tree.root, key)

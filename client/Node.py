from typing import Self
from hashlib import sha256


class Node:
    """
    Build a node for a Merkle quadtree. Updates to a Node's 
    Merkle hash indicate changes in the data stored in that Node.
    """

    def __init__(self, geocode: list = []) -> None:
        """
        Args:
            merkle (str): the node's Merkle hash
            geocode (list): a list containing the geospatial index/indices 
                           associated with the Node
        """
        self._hashcode = sha256().hexdigest() # Note: since it is on the empty string, it'll always be the same hash
        if isinstance(geocode, str):
            self._geocode = [geocode]
        else:
            self._geocode = geocode
        self._children = [None, None, None, None]
        self._data = list()
        self._parent = None

    ######### ACCESSORS #########
    @property
    def hashcode(self) -> str:
        """Get or set the current Merkle hash."""
        return self._hashcode
    
    @property
    def parent(self) -> Self:
        """Get or set the parent of the current Node."""
        return self._parent

    @property
    def geocode(self) -> list:
        """Get or set the list of geospatial indices."""
        return self._geocode
    
    @property
    def children(self) -> dict:
        """Get the node's children."""
        return self._children
    
    @property
    def data(self) -> list:
        """Get, set, or delete the list of assets."""
        return self._data
    
    def number_children(self) -> int:
        """Determine how many children hold data."""
        number = 0
        for child in self._children:
            if child is not None:
                number += 1
        return number
    
    def in_data(self, named_data: str) -> bool:
        """
        Determine if the string being sought is in the node's 
        list of data. 

        Returns:
            bool: True if the data is in the node's data list;
                  False otherwise
        """
        #print(f'LOOKING FOR: {named_data}')
        for element in self._data:
            #print(f'ELEMENT: {element}')
            data_string = element.split('/')
            data_without_geocode = '/'.join(data_string[:-1])
            #print(f'DATA WITHOUT GEOCODE: {data_without_geocode}')
            if data_without_geocode == named_data.lower():
                return True
        #print(f'RETURNING FALSE')
        return False
    
    def length_geocode(self) -> int:
        length = 0
        if self._geocode:
            # if it isn't empty, all geocodes have the same length
            length = len(self._geocode[0])
        return length
    
    ######### MUTATORS #########
    @parent.setter
    def parent(self, parent_node: Self) -> None:
        self._parent = parent_node

    def add_geocode(self, geocode: str) -> None:
        """Add a geocode to the set of geocodes associated with this node."""
        if geocode not in self._geocode:
            self._geocode.append(geocode)

    def delete_data(self, named_data: str) -> None:
        """Delete a piece of named data from the node."""
        
        if named_data.lower() in self._data:
            self._data.remove(named_data)
            self.generate_hash()

    def add_child(self, node_to_add: Self) -> int:
        """
        Adds a child Node to the list of children.

        Args:
            node_to_add (Self): the child being added

        Returns:
            int: the index where the child Node was 
                 inserted in the children list
        """
        geocode_to_add = node_to_add.geocode[0]
        geocode_char = geocode_to_add[-1].lower()
        print(f'GEOCODE CHAR: {geocode_char}')
        index = None
        if geocode_char in '01234567':
            index = 0
            if self._children[0] is None:
                node_to_add.parent = self
                self._children[0] = node_to_add
            else:
                self._children[0].add_geocode(geocode_to_add)
                print(f'IT EXISTS, SO APPENDING to: {self._children[0]}')
        elif geocode_char in '89bcdefg':
            index = 1
            if self._children[1] is None:
                node_to_add.parent = self
                self._children[1] = node_to_add
            else:
                self._children[1].add_geocode(geocode_to_add)
                print(f'IT EXISTS, SO APPENDING to: {self._children[1]}')
        elif geocode_char in 'hjkmnpqr':
            index = 2
            if self._children[2] is None:
                node_to_add.parent = self
                self._children[2] = node_to_add
            else:
                self._children[2].add_geocode(geocode_to_add)
                print(f'IT EXISTS, SO APPENDING to: {self._children[2]}')
        elif geocode_char in 'stuvwxyz':
            index = 3
            if self._children[3] is None:
                node_to_add.parent = self
                self._children[3] = node_to_add
            else:
                self._children[3].add_geocode(geocode_to_add)
                print(f'IT EXISTS, SO APPENDING to: {self._children[3]}')
        else:
            print(f'NO INDEX ADDED...')

        return index

    def insert_data(self, named_data: str) -> None:
        """
        Inserts new named data into the list of data. 
        Checks if the new data is a version of previous data or new data.
        The expectation is that the final value in a hierarchical named data
        string is fully numeric only when being used to indicate a version
        number or timestamp.

        Args:
            named_data (str): the named data object's name
        """
        existing_data = self._data
        named_data = named_data.lower() # all names added to a list should follow the same format
        
        # if the list is empty, we can safely insert the data
        if len(existing_data) == 0:
            self._data.append(named_data)
            # print(f'ADDING NAMED DATA: {named_data} TO NODE {self._geocode}')
            # print(f'THE DATA IS STORED: {self._data} in {self.geocode}')
            self.generate_hash()
        else:
            # split the string to be inserted; get a version number if there is one
            split_data = named_data.split('/')
            if split_data[-1].isnumeric():
                data_to_check = ''.join(split_data[0:-1])
                insert_version = split_data[-1]
            else:
                data_to_check = ''.join(split_data)
                insert_version = None

            for i in range(len(existing_data)):
                # the data is already stored; do nothing
                if existing_data[i] == named_data:
                    return
                
                # split the named data element in the list and check if there is a version
                element_split = existing_data[i].split('/')
                if element_split[-1].isnumeric():
                    element_without_version = ''.join(element_split[0:-1])
                    current_version = element_split[-1]
                else:
                    element_without_version = ''.join(element_split)
                    current_version = None

                # the hierarchical names match
                if element_without_version == data_to_check:
                    if insert_version is not None:
                        if current_version is not None:
                            # the current version is older than the one to be inserted
                            if current_version < insert_version:
                                self._data[i] = named_data
                                #print(f'ADDING NAMED DATA: {named_data} TO NODE {self._geocode} ')
                                self.generate_hash()
                                return
                            elif current_version >= insert_version:
                                return
                        # current version must be older, as it didn't have a version number
                        elif current_version is None:
                            self._data[i] = named_data
                            #print(f'ADDING NAMED DATA: {named_data} TO NODE {self._geocode} ')
                            self.generate_hash()
                            return
                    # the current version is already up-to-date   
                    elif current_version is not None:
                        return
                    
            # the data is new and should be added
            #print(f'ADDING NAMED DATA: {named_data} TO NODE {self._geocode} ')
            self._data.append(named_data)
            self.generate_hash()

    def generate_hash(self) -> None:
        """Uses the Node's list of data to generate a hashcode for the Node."""
        # leaf nodes store data, so we generate hashes on the data
        hash_value = sha256()
        if self._data:
            for named_data in self._data:
                #print(f'GENERATING DATA HASH for {self._geocode}')
                hash_value.update(named_data.encode())

        # internal nodes don't store data, so their hash is a combination of child hashes
        else:
            #print(f'GENERATING PARENT HASH...')
            for child in self._children:
                if child is not None:
                    #print(f'THE CHILD HASH: {child.hashcode}')
                    hash_value.update(child.hashcode.encode())
                    #print(f'HASH WHILE CALCULATING: {hash_value.hexdigest()}')
        
        self._hashcode = hash_value.hexdigest()
        #print(f'THE GENERATED HASH... {hash_value.hexdigest()} for {self._geocode}')

    ######### DELETERS #########
    def remove_children(self) -> None:
        """
        Remove all children from the node. 
        Turns the node into a leaf node.
        """
        self._children = [None, None, None, None]

    def remove_child(self, child_to_remove: int) -> None:
        """
        Remove the child stored at the index passed.

        Args:
            child_to_remove (int): the index of the removed child
        """
        self._children[child_to_remove] = None
    
    ######### COMPARISONS #########
    def __eq__(self, node: Self) -> bool:
        """Check if another Node has the same Merkle hash as this Node."""
        return self._hashcode == node.hashcode

    ######### STRINGS #########
    def __str__(self) -> str:
        return f'\nNode hash: {self._hashcode}\nNode geocode: {self._geocode}' +\
              ''.join(f'\nChild: {child}' for child in self._children)
        
# TESTING
if __name__ == '__main__':
    print(f'\nTesting Node...\n')
    # node = Node(['ABCD'])

    # print(f'\n######### After construction #########\n {node}')
    # node.add_child(Node('EFGH'))
    # node.add_child(Node('IJKL'))
    # node.add_child(Node('MNOP'))

    # print(f'\n######### After adding children #########\n {node}')
    # node.remove_child(3)

    # print(f'\n######### After deleting the front_left child #########\n {node}')
    # node.remove_children()
    # node.add_child(Node('QRST'))

    # print(f'\n######### After removing all children and adding a child: #########\n {node}')
    # node.add_child(Node('EFGH'))
    # node.add_child(Node('0128'))

    # print(f'\n######### Comparison tests #########\n')
    # print(f'Child 2 and Child 3 have the same Merkle hash? {node.children[2].hashcode == node.children[3].hashcode}')
    # print(f'Child 1 and Child 2 have the same Merkle hash? {node.children[1].hashcode == node.children[2].hashcode}')

    # print(f'\n######### Geocode Test #########\n')
    # for i in range(len(node.children)):
    #     print(f'The child: {node.children[i]}')
    #     if node.children[i] is not None:
    #         print(f"The Node's geocode is: {node.children[i].geocode}")
    #     else:
    #         print(f"The Node is empty.")

    # print(f'\n######### Testing data insertion and hashcodes #########\n')
    # print(f'MERKLE HASH before first insertion of data: {node.children[2].hashcode}')
    # node.children[2].insert_data('/Name/to/add/to/list')
    # print(f'MERKLE HASH after first insertion of data: {node.children[2].hashcode}')
    # node.children[2].insert_data('/name/To/add/to/list')
    # print(f'MERKLE HASH after the same data inserted (should match previous hash): {node.children[2].hashcode}')
    # node.children[2].insert_data('/name/to/Add/to/list/again/2')
    # print(f'MERKLE HASH after new data (should NOT match previous hash): {node.children[2].hashcode}')
    # node.children[2].insert_data('/some/new/Name/001')
    # node.children[2].insert_data('/some/NeW/name/002')
    # node.children[2].insert_data('/name/to/Add/to/list/2')
    # node.children[2].insert_data('/name/to/add/to/list/1')
    # node.children[2].insert_data('/some/new/name')
    # print(f'Data stored in Child 2: {node.children[2].data}')
    # print(f'MERKLE HASH after all data entered: {node.children[2].hashcode}')
    # node.children[2].delete_data('/some/new/name/002')
    # print(f"Data stored in Child 2 after deletion of '/some/new/name/002': {node.children[2].data}")
    # print(f'MERKLE HASH after deletion: {node.children[2].hashcode}')
    # print(f'Geocode: {type(node.geocode)}')
    # print(f'PARENT MERKLE HASH before generating one: {node.hashcode}')
    # node.generate_hash()
    # print(f'PARENT MERKLE HASH after generating: {node.hashcode}')
    # print(f'CHILD 3 HASH before insertion of data: {node.children[3].hashcode}')
    # node.children[3].insert_data('/testing/hashing')
    # print(f'CHILD 3 DATA: {node.children[3].data}')
    # print(f'CHILD 3 HASH after insertion of data: {node.children[3].hashcode}')
 
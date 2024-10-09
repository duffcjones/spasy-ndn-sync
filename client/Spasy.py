from SpasyTree import *
from pympler import asizeof
from random import randint, seed
from pprint import pprint
from heapq import heappush, heappushpop, heapify

class Spasy:
    """
    Spatial Sync (SPASY) is a Named Data Networking (NDN) Sync protocol meant for 
    use in augmented reality environments (and eventually the Metaverse). 

    Uses a SpasyTree to identify where all digital assets are within a given
    area and maintain synchronization of assets between users.

    Assumes SpasyTree root is at Geohash Level 6 and data is stored in leaves
    at Geohash Level 11.
    """

    def __init__(self, geocode: str) -> None:
        
        self._tree = SpasyTree(10, Node(geocode))
        self._recent_updates = [] # a list that will be treated as a heap
        self._max_number_recent_updates = 25 # maximum size of priority queue
    
    ######### ACCESSORS #########
    @property
    def tree(self) -> SpasyTree:
        """Get or set the data SpasyTree data structure."""
        return self._tree
    
    @property
    def recent_updates(self) -> list:
        """Get the recent updates that have been made to SPASY's tree."""
        return self._recent_updates

    @property
    def max_number_recent_updates(self) -> int:
        return self._max_number_recent_updates

    @max_number_recent_updates.setter
    def max_number_recent_updates(self, value: int) -> None:
        self._max_number_recent_updates = value
    
    def build_tree(self, size: int=0) -> None:
        """Insert elements into the tree to automate the building of trees.

        Args:
            size (int, optional): the number of names to insert in the tree. 
                                  Defaults to 0.
        """
        # get the string value of the root's geocode
        tree_geocode = ''.join(self._tree.root.geocode)
        # generate a name with a geocode and insert it in the tree
        seed_value = 0 # we want the tree to always be the same for experiments
        for i in range(size):
            
            name = self._generate_name(seed_value) + self._generate_geocode(seed_value, tree_geocode)
            #print(f'Name being inserted: {name}')
            self._tree.insert(name)
            insert_info = (time.time(), 'i', name)
            self._add_to_recent_updates(insert_info)
            seed_value += 1000 # increment the seed to make sure it doesn't generate the same string and geocode
                               # multiple times for the same tree
            #print(f'\n######### RECENT UPDATES #########\n')
            #pprint(self._recent_updates)

    def _generate_name(self, seed_value: int, max_length: int=10) -> str:
        """
        Generates a randomized string of named data from a list of common English words. 
        This is a helper method for building randomized trees.
        (The list of words is found in words.txt and can be found at 
        https://gist.github.com/deekayen/4148741.)

        Args:
            seed_value (int): a random number seed to ensure the generated trees are always
                              the same (for experimental purposes.)
            max_length (int, optional): the number of elements in the hierarchical name. 
                                        Defaults to 4.

        Returns:
            str: the named_data string.
        """
        # read the list of common English-language words into a list
        seed(seed_value) 
        word_list = []
        with open('spatialsync/client/words.txt') as file:
            for word in file:
                word_list.append(word.strip())

        number_elements = randint(2, max_length) # determine the number of elements in the named data string
        name = ""

        # generate the hierarchical name
        for i in range(number_elements):
            name = name + '/' + word_list[randint(0,len(word_list)-1)]
        print(f'THE GENERATED NAME: {name}')

        # if the length of the string is even, add a version number between 1 and 10
        if number_elements % 2 == 0:
            version_number = 'a' + str(randint(1,10))
            name = name + '/' + version_number

        # create a divider to accommodate the geocode
        name = name + '/'

        return name

    def _generate_geocode(self, seed_value: int, geocode: str) -> str:
        """
        Generates a geocode for inserting named data in a tree.
        This is a helper method for building randomized trees. 

        Args:
            seed_value (int): a random number seed to ensure the generated trees are always
                              the same (for experimental purposes.)
            geocode (str): the Level 6 geocode that serves as the tree's root.

        Returns:
            str: the geocode which will be appended to the name.
        """
        seed_increment = seed_value
        insert_geocode = geocode
        valid_characters = '0123456789bcdefghjkmnpqrstuvwxyz'

        max_geocode_length = self.tree.max_depth
        # print(max_geocode_length)
        while len(insert_geocode) <= max_geocode_length:
            seed(seed_increment)
            insert_geocode = insert_geocode + valid_characters[randint(0, len(valid_characters) - 1)]
            seed_increment += 100

        print(f'THE GENERATED GEOCODE: {insert_geocode}')
        return insert_geocode

    
    ######### MUTATORS #########
    def _add_to_recent_updates(self, updated_item: tuple) -> None:        
        """
        Add tuples containing timestamps, actions, and new_items to a priority queue of 
        recent changes. The oldest element is removed when new elements are added to the 
        priority queue.

        Args:
            updated_item (tuple): contains a timestamp, action (i.e., 'i' or 'd'),
                                  and the data being inserted or deleted. 
        """
        # if the priority queue is larger than the default size, pop an element while pushing
        if len(self.recent_updates) >= self._max_number_recent_updates:
            heappushpop(self.recent_updates, updated_item)
        # just push an element
        else:
            heappush(self.recent_updates, updated_item)


    def replace_tree(self, replacement_tree: SpasyTree) -> None:
        """
        Replace the current SpasyTree with a new version of a SpasyTree received from
        another Spasy group member.

        Args:
            replacement_tree (SpasyTree): the newer version of the SpasyTree.
        """
        self._tree = replacement_tree

    def update_tree(self, other_hash: str, recent_changes: list) -> None:
        """
        Uses a priority queue that stores recent changes to another user's SpasyTree to 
        update the current user's SpasyTree. When done, the Merkle hash of the current
        user's SpasyTree root should match the hash of the other user's SpasyTree.

        Args:
            other_hash (str): the Merkle hash of another user's SpasyTree. That user's
                              SpasyTree was recently updated.
            recent_changes (list): the priority queue that stores the recent changes.
        """
        # convert recent changes to a set in order to do set difference
        current_set = set(self.recent_updates)
        # print(f'\n######### THE CURRENT SET #########\n')
        # pprint(current_set)
        update_set = set(recent_changes)
        # print(f'\n######### THE UPDATE SET #########\n')
        # pprint(update_set)

        # find differences
        set_difference = update_set.difference(current_set)
        # print(f'\n########## SET DIFFERENCE #########\n')
        # pprint(set_difference)
        # print(f'\n######### HANDLING CHANGES #########\n')
        
        # handle differences if there are any
        if set_difference:
            for element in set_difference:
                timestamp = element[0]
                data = element[2]
                # print(f'ELEMENT: {element}')
                if element[1] == 'i':
                    # print(f'INSERT: {data}')
                    self.add_data_to_tree(data, timestamp)
                    # print(f'TIMESTAMP: {timestamp}')
                elif element[1] == 'd':
                    # print(f'DELETE: {data}')
                    # print(f'TIMESTAMP: {timestamp}')
                    self.remove_data_from_tree(data, timestamp)

        # check that the hashes match 

    def add_data_to_tree(self, data_to_add: str, timestamp: str="") -> None:
        """
        Inserts named data in the SpasyTree.

        Args:
            data_to_add (str): the named data to be inserted in the SpasyTree.
            timestamp (str, optional): the timestamp from when the data was added 
                                       to another tree. 
                                       Defaults to "", which occurs when the caller 
                                       is the data's publisher.
        """
        if timestamp == "":
            timestamp = time.time()
        self._tree.insert(data_to_add)
        self._add_to_recent_updates((timestamp, 'i', data_to_add))

    def remove_data_from_tree(self, delete_data: str, timestamp: str="") -> None:
        """
        Deletes named data from the SpasyTree.

        Args:
            delete_data (str): the named data to delete.
            timestamp (str, optional): the timestamp from when the data was deleted 
                                       from another tree. 
                                       Defaults to "", which occurs when the caller is 
                                       the one publishing the deletion. 
        """
        if timestamp == "":
            timestamp = time.time()
        self._tree.delete(self._tree.root, delete_data, self._tree.root.length_geocode())
        self._add_to_recent_updates((timestamp, 'd', delete_data))
    
    ######### OTHER #########
    def is_newer_tree(self, sync_tree_hash: str) -> bool:
        """
        When a Sync Interest is received, the hashcodes must be compared.

        Args:
            sync_tree_hash (str): the root hashcode of a SpasyTree.

        Returns:
            bool: True if they match;
                  False otherwise.
        """
        if self._tree.root.hashcode == sync_tree_hash:
            print(f'The tree is already up-to-date.')
            return False
        # # THIS DOES NOT APPLY TO THE CURRENT VERSION, AS OLD HASHES AREN'T KEPT
        # elif sync_tree_hash in self._tree._recent_changes:
        #     print(f'That is an older version of the tree.')
        #     return False
        else:
            print(f'This is a newer version of the tree. Send an Interest packet.')
            return True

    def search(self, data_to_find: str) -> bool:
        """
        Find all of the geohashes in which the named data is stored.

        Args:
            data_to_find (str): the named data being sought.

        Returns:
            list: a list of geohashes where the data is stored.
        """
        return self._tree.find_data(data_to_find)
    
    def search_without_geocode(self, data_to_find: str, geocode_list: list | None = None) -> list:
        """
        Checks for data in the tree independently of the geocode it is associated with. For example,
        if a user is looking for /some/data, that may exist as /some/data/dpwhwts0123 and 
        /some/data/dpwhwt0bcqr. This method will find both.

        Args:
            data_to_find (str): the named data (independent of geocode) being sought.
            geocode_list (list | None, optional): a list of geocodes where the named data can be found. 
                                                  Defaults to None.

        Returns:
            list: a list of geocodes where the named data can be found.
        """
        return self._tree.find_data_without_geocode(self._tree.root, data_to_find, geocode_list)
    
    def gather_all_data_by_namespace(self) -> dict:
        """
        Takes all of the data from the SpasyTree and organizes it by namespace.

        Returns:
            dict: a dictionary containing all of the data in the tree
                  organized into namespaces.  
        """
        return self._tree.find_data_by_namespace(self._tree.root)
    
    def gather_all_data_by_geocode(self) -> dict:
        """
        Takes all of the data from the SpasyTree and organizes it by geocode.

        Returns:
            dict: a dictionary containing all of the data in the tree
                  organized into geocodes. 
        """
        return self._tree.find_data_by_geocode(self._tree.root)
    
# testing
if __name__ == '__main__':
    print(f'\nTesting SPASY...\n')
    spasy = Spasy('dpwhwt')
    spasy.build_tree(10) # build a tree with six elements
    print(spasy.tree.root)
    spasy2 = Spasy('dpwhwt')
    spasy2.build_tree(10)
    print(spasy2.tree.root)

    # spasy2 = Spasy('dpwhwt')
    # for element in spasy.recent_updates:
    #     data = element[2]
    #     timestamp = element[0]
    #     spasy2.add_data_to_tree(data, timestamp)

    # print(f'\n######### TESTING THE RECENT UPDATES #########\n')
    # print(f'\n######### NEWER TREE? #########\n')
    # spasy2.add_data_to_tree('/some/test/data/dpwhwtmpz0v') # add something to the second tree

    # print(f'\n######### DO THE TREES HAVE THE SAME HASH BEFORE THE UPDATE? {spasy.tree.root.hashcode == spasy2.tree.root.hashcode}')

    # start = time.time()
    # spasy.update_tree(spasy2.tree.root.hashcode, spasy2.recent_updates) # update the first tree
    # end = time.time()
    
    # print(f'\n######### THE FIRST TREE #########\n')
    # print(spasy.tree.root)

    # print(f'\n######### THE SECOND TREE #########\n')
    # print(spasy2.tree.root)

    # print(f'\n######### DO THE TREES HAVE THE SAME HASH AFTER THE UPDATE? Spasy1: {spasy.tree.root.hashcode == spasy2.tree.root.hashcode}')
    # print(f'\n######### HOW LONG DID IT TAKE TO UPDATE THE TREE? {end - start}')

    # # TESTING REMAINING METHODS
    # print(f'\n######### TESTING OTHER METHODS #########')
    # print(spasy.search('/some/test/data'))
    # print(spasy.search('/some/test/data/dpwhwtmpz0v'))
    # print(spasy.search_without_geocode('/some/test/data'))
    # print(f'DATA BY GEOCODE:')
    # pprint(spasy.gather_all_data_by_geocode())
    # print(f'DATA BY NAMESPACE:')
    # pprint(spasy.gather_all_data_by_namespace())
    # spasy.remove_data_from_tree('/some/test/data/dpwhwtmpz0v')
    # print(f'DATA BY NAMESPACE AFTER REMOVAL:')
    # pprint(spasy.gather_all_data_by_namespace())
    # print(f'RECENT UPDATES:')
    # pprint(spasy2.recent_updates)
    # pprint(spasy.recent_updates)
    # print(f'SIZE: {asizeof.asizeof(spasy2.tree)}')

    

    


    # print(spasy.tree.root)
    # pprint(spasy.gather_all_data_by_namespace())
    # pprint(spasy.gather_all_data_by_geocode())
    # print(f'Time to build tree: {end - start}')
    # print(spasy.tree.recent_changes)
    # other_tree = SpasyTree(10, Node('dpwhwts'))

    # # compare trees
    # print(f"\n######### COMPARE TREES BEFORE ADDING NEW DATA #########\n")
    # start = time.time()
    # print(spasy.is_newer_tree(other_tree.root.hashcode))
    # end = time.time()
    # print(end - start)

    # # add data, then compare trees
    # print(f"\n######### COMPARE TREES AFTER ADDING NEW DATA #########\n")
    # other_tree.insert('/data/test/dpwhwtsh000')
    # print(spasy.is_newer_tree(other_tree.root.hashcode))

    # # Sync related things to be added
    # print(f'\n######### SEND A SYNC INTEREST #########\n')

    # # replace tree
    # print(f'\n######### THE TREE BEFORE REPLACING IT #########\n')
    # print(spasy.tree.root)
    # geohash_tree.insert('/second/piece/of/data/dpwhwtsh000')
    # geohash_tree.insert('/extra/data/dpwhwtsh000')
    # geohash_tree.insert('/some/data/dpwhwts0214')
    # geohash_tree.insert('/extra/data/to/add/dpwhwtsp000')
    # geohash_tree.insert('/some/data/dpwhwtsz001')
    # geohash_tree.insert('/some/more/data/dpwhwtsb009')
    # geohash_tree.insert('/some/testing/data/dpwhwtsm00h')
    # geohash_tree.insert('/some/data/dpwhwtsn00s')
    # geohash_tree.insert('/second/piece/of/data/dpwhwts1000')
    # geohash_tree.insert('/extra/data/dpwhwts2000')
    # geohash_tree.insert('/extra/data/to/add/dpwhwtsh000')
    # geohash_tree.insert('/some/data/dpwhwtsh001')
    # geohash_tree.insert('/some/more/data/dpwhwtsh009')
    # geohash_tree.insert('/some/testing/data/dpwhwtsh00h')
    # geohash_tree.insert('/some/data/dpwhwtshpqs')
    # geohash_tree.insert('/second/piece/of/data/dpwhwtsprtu')
    # geohash_tree.insert('/extra/data/dpwhwts9bzx')
    # geohash_tree.insert('/extra/data/to/add/dpwhwtspc18')
    # geohash_tree.insert('/some/data/dpwhwtspcdq')
    # geohash_tree.insert('/some/more/data/dpwhwtsmnz4')
    # geohash_tree.insert('/some/testing/data/dpwhwtsm00h')
    # geohash_tree.insert('/some/data/dpwhwtsp00s')
    # geohash_tree.insert('/second/piece/of/data/dpwhwtsq000')
    # geohash_tree.insert('/extra/data/dpwhwtsvw0z')
    # geohash_tree.insert('/some/data/dpwhwtsm0p1')
    # print(geohash_tree.root)

    # start = time.time()
    # spasy.is_newer_tree(geohash_tree.root.hashcode)
    # spasy.replace_tree(geohash_tree)
    # end = time.time()
    # print(f'end: {end}, start: {start}; calculation = {end - start}')
    # print(f'The tree contains {asizeof.asizeof(geohash_tree)} bytes.')
    # print(f'\n######### THE TREE AFTER REPLACING IT #########\n')

    # # ADD, DELETE, AND FIND DATA
    # spasy.add_data_to_tree('/add/data/dpwhwtsh401')
    # print(f'\n########## THE TREE WITH ADDED DATA #########\n')
    # #print(spasy.tree.root)
    # print(f"FIND WITHOUT GEOCODE '/add/data' (should be ['dpwhwtsh300', 'dpwhwtsh001', 'dpwhwtsh000', 'dpwhwtsp000',"
    #       f" 'dpwhwtsq000', 'dpwtsh401']): {spasy.search('/add/data')}")
    # spasy.add_data_to_tree('/data/test/dpwhwtsb900')
    # print(f'\n######### THE TREE BEFORE REMOVAL #########\n')
    # print(spasy.tree.root)
    # spasy.remove_data_from_tree('/data/test/dpwhwtsb900')
    # print(f'\n########## THE TREE WITH DATA REMOVED #########\n')
    # print(spasy.tree.root)
    # print(f"FIND '/add/data/dpwhwtsh401' (should be True): {spasy.search('/add/data/dpwhwtsh401')}")
    # print(f"FIND '/data/test' (should be []): {spasy.search_without_geocode('/data/test')}")
    # print(f"FIND WITHOUT GEOCODE '/add/data' (should be ['dpwhwtsh300', 'dpwhwtsh001', 'dpwhwtsh000', 'dpwhwtsp000',"
    #       f" 'dpwhwtsq000', 'dpwtsh401']): {spasy.search_without_geocode('/add/data')}")
    # start = time.time()
    # print(f"\n#########FIND ALL DATA #########\n: {spasy.gather_all_data_by_namespace()}")
    # end = time.time()
    # print(f'THE TIME TO CONVERT TO NAMESPACE DICTIONARY: {end - start}')
    # start = time.time()
    # print(f'\n######### ORGANIZE ALL DATA BY GEOCODE #########\n: {spasy.gather_all_data_by_geocode()}')
    # end = time.time()
    # print(f'THE TIME TO CONVERT TO GEOCODE DICTIONARY: {end - start}')

    # TESTING recent_updates
    # updates_to_test = [(1727803768.6485171, 'insert', '/extra/data/to/add/dpwhwtsh900'), (1727803768.648532, 'insert', '/some/data/dpwhwtsh001'), \
    #                    (1727803768.648543, 'insert', '/some/more/data/dpwhwtsh009')]
    # heapify(updates_to_test)
    # print(f'\n######### UPDATE HEAP #########\n')
    # pprint(updates_to_test)
    # # testing tree merging
    # spasy1 = Spasy('dpwhwt')
    # count = 0
    # for element in updates_to_test:
    #     timestamp = element[0]
    #     data = element[2]
    #     count += 1
    #     spasy1.add_data_to_tree(data, timestamp)
    #     print(f'Count: {count}, and recent updates: {spasy1.recent_updates}')

    # print(f'COUNT AFTER ADDING TO SPASY 1: {count}')
    # print(f'SPASY 1 RECENT UPDATES')
    # pprint(spasy1.recent_updates)
    
    # spasy2 = Spasy('dpwhwt')
    # count = 0
    # for element in updates_to_test:
    #     timestamp = element[0]
    #     data = element[2]
    #     count += 1
    #     spasy2.add_data_to_tree(data, timestamp)

    # print(f'COUNT AFTER ADDING TO SPASY 2: {count}')
    # print(f'SPASY 2 RECENT UPDATES:')
    # pprint(spasy2.recent_updates)


    # print(f'\n######### TREE BEFORE UPDATE #########\n')
    # print(spasy1.tree.root)
    #spasy1.update_tree(spasy2.tree.root, spasy2.tree.recent_changes)
    # print(f'\n######### TREE AFTER UPDATE #########\n')
    # print(spasy1.tree.root)
    # print(f'\n######### TREE AFTER DELETE ##########\n')
    # spasy1.remove_data_from_tree('/extra/data/to/add/dpwhwtsh900')
    # spasy2.update_tree(spasy1.tree.root, spasy1.recent_updates)
    # spasy2.add_data_to_tree('/new/data/a1/dpwhwtqrp0h')
    #spasy2.update_tree(spasy1.tree.root, spasy1.tree.recent_changes)
    # print(spasy2.tree.root)
    # print(f'\n######### FIRST TREE CHANGES #########\n')
    # pprint(spasy1.tree.recent_changes)
    # print(f'\n######### SECOND TREE CHANGES #########\n')
    # pprint(spasy2.tree.recent_changes)
    # print(f'\n######### RECENT UPDATES #########\n')
    # print(f'SPASY 1: ')
    # pprint(spasy1.recent_updates)
    # print(f'SPASY 2')
    # pprint(spasy2.recent_updates)

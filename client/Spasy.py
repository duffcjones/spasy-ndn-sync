from SpasyTree import *
from pympler import asizeof
from random import randint
from pprint import pprint

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
    
    ######### ACCESSORS #########
    @property
    def tree(self) -> SpasyTree:
        """Get or set the data SpasyTree data structure."""
        return self._tree
    
    def build_tree(self, size: int=0) -> None:
        """Insert elements into the tree to automate the building of trees.

        Args:
            size (int, optional): The number of names to insert in the tree. 
                                  Defaults to 0.
        """
        # get the string value of the root's geocode
        tree_geocode = ''.join(self._tree.root.geocode)

        # generate a name with a geocode and insert it in the tree
        for i in range(size):
            name = self._generate_name(5) + self._generate_geocode(tree_geocode)
            print(f'Name being inserted: {name}')
            self._tree.insert(name)

    def _generate_name(self, max_length: int=4) -> str:
        """
        A helper to generate a randomized string of named data from a list
        of common English words.

        Args:
            max_length (int, optional): The number of elements in the hierarchical name. 
                                        Defaults to 4.

        Returns:
            str: The named_data string
        """
        # read the list of common English-language words into a list
        word_list = []
        with open('client/words.txt') as file:
            for word in file:
                word_list.append(word.strip())

        number_elements = randint(2, max_length) # determine the number of elements in the named data string
        name = ""

        # generate the hierarchical name
        for i in range(number_elements):
            name = name + '/' + word_list[randint(0,len(word_list)-1)]

        # if the length of the string is even, add a version number between 1 and 10
        if number_elements % 2 == 0:
            version_number = 'a' + str(randint(1,10))
            name = name + '/' + version_number

        # create a divider to accommodate the geocode
        name = name + '/'

        return name

    def _generate_geocode(self, geocode: str) -> str:
        """
        A helper to generate a geocode for inserting named data in a tree. 

        Args:
            geocode (str): The Level 6 geocode that serves as the tree's root.

        Returns:
            str: The geocode which will be appended to the name.
        """
        insert_geocode = geocode
        valid_characters = '0123456789bcdefghjkmnpqrstuvwxyz'

        max_geocode_length = self.tree.max_depth
        # print(max_geocode_length)
        while len(insert_geocode) <= max_geocode_length:
            insert_geocode = insert_geocode + valid_characters[randint(0, len(valid_characters) - 1)]

        return insert_geocode

    
    ######### MUTATORS #########
    def replace_tree(self, replacement_tree: SpasyTree) -> None:
        """
        Replace the current SpasyTree with a new version of a SpasyTree received from
        another Spasy group member.

        Args:
            replacement_tree (SpasyTree): the newer version of the SpasyTree
        """
        self._tree = replacement_tree

    def update_tree(self, other_hash: str, recent_changes: deque) -> None:
        """
        Uses a deque that stores recent changes to another user's SpasyTree to 
        update the current user's SpasyTree. When done, the Merkle hash of the current
        user's SpasyTree root should match the hash of the other user's SpasyTree.

        Args:
            other_hash (str): The Merkle hash of another user's SpasyTree. That user's
                              SpasyTree was recently updated.
            recent_changes (deque): The deque that stores the recent changes.
        """
        # convert recent changes to a set in order to do set difference
        current_set = set(self.tree.recent_changes)
        print(f'\n######### THE CURRENT SET #########\n')
        pprint(current_set)
        update_set = set(recent_changes)
        print(f'\n######### THE UPDATE SET #########\n')
        pprint(update_set)

        # find differences
        set_difference = update_set.difference(current_set)
        print(f'\n########## SET DIFFERENCE #########\n')
        pprint(set_difference)

        print(f'\n######### HANDLING CHANGES #########\n')
        # handle differences if there are any
        if set_difference:
            for element in set_difference:
                print(f'ELEMENT: {element}')
                if element[1] == 'insert':
                    print(f'INSERT: {element[2]}')
                    self.add_data_to_tree(element[2])
                elif element[1] == 'delete':
                    print(f'DELETE: {element[1]}')
                    self.remove_data_from_tree(element[2])

    def add_data_to_tree(self, data_to_add: str) -> None:
        """
        Inserts named data in the SpasyTree.

        Args:
            data_to_add (str): the named data to be inserted in the SpasyTree
        """
        self._tree.insert(data_to_add)

    def remove_data_from_tree(self, delete_data: str) -> None:
        """
        Deletes named data from the SpasyTree.

        Args:
            delete_data (str): the named data to delete.
            delete_geocode (str): the geocode from which the data should be deleted.
        """
        self._tree.delete(self._tree.root, delete_data, self._tree.root.length_geocode())
    
    ######### OTHER #########
    def is_newer_tree(self, sync_tree_hash: str) -> bool:
        """
        When a Sync Interest is received, the hashcodes must be compared.

        Args:
            sync_tree_hash (str): the root hashcode of a SpasyTree

        Returns:
            bool: True if they match
                  False otherwise
        """
        if self._tree.root.hashcode == sync_tree_hash:
            print(f'The tree is already up-to-date.')
            return False
        elif sync_tree_hash in self._tree._recent_changes:
            print(f'That is an older version of the tree.')
            return False
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

        return self._tree.find_data_without_geocode(self._tree.root, data_to_find, geocode_list)
    
    def gather_all_data_by_namespace(self) -> dict:
        """
        Takes all of the data from the SpasyTree and organizes it by
        namespace.

        Returns:
            dict: a dictionary containing all of the data in the tree
                  organized into namespaces  
        """
        return self._tree.find_data_by_namespace(self._tree.root)
    

    def gather_all_data_by_geocode(self) -> dict:

        return self._tree.find_data_by_geocode(self._tree.root)
    

    ######### NAMED DATA NETWORKING #########
        
    # TODO: build a method for constructing Sync Interests
    def create_sync_interest(self) -> None:
        pass

    # TODO: build a method for sending Interest packets to replace trees
    def send_interest(self) -> None:
        pass

    # TODO: build a method for receiving Data packets
    def receive_data(self) -> None:
        pass
    


# testing
if __name__ == '__main__':
    print(f'\nTesting SPASY...\n')
    spasy = Spasy('dpwhwt')
    # start = time.time()
    # spasy.build_tree(11)
    # end = time.time()

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

    # # add, delete and find data
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


    # testing tree merging
    spasy1 = Spasy('dpwhwt')
    spasy1.add_data_to_tree('/extra/data/to/add/dpwhwtsh900')
    spasy1.add_data_to_tree('/some/data/dpwhwtsh001')
    spasy1.add_data_to_tree('/some/more/data/dpwhwtsh009')
    spasy1.add_data_to_tree('/some/testing/data/dpwhwtsh00h')

    spasy2 = Spasy('dpwhwt')
    for element in spasy1.tree.recent_changes:
        print(f'CONVERSION ELEMENT: {element}')
        spasy2.tree.recent_changes.append(element)

    spasy2.add_data_to_tree(spasy1.tree.recent_changes[0][2])
    spasy2.add_data_to_tree('/second/piece/of/data/dpwhwtsh000')

    print(f'\n######### TREE BEFORE UPDATE #########\n')
    print(spasy1.tree.root)
    spasy1.update_tree(spasy2.tree.root, spasy2.tree.recent_changes)
    print(f'\n######### TREE AFTER UPDATE #########\n')
    print(spasy1.tree.root)
    print(f'\n######### TREE AFTER DELETE ##########\n')
    spasy1.remove_data_from_tree('/extra/data/to/add/dpwhwtsh900')
    spasy2.update_tree(spasy1.tree.root, spasy1.tree.recent_changes)
    print(spasy2.tree.root)
    print(f'\n######### FIRST TREE CHANGES #########\n')
    pprint(spasy1.tree.recent_changes)
    print(f'\n######### SECOND TREE CHANGES #########\n')
    pprint(spasy2.tree.recent_changes)


    



    

